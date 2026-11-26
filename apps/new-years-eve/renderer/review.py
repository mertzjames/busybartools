"""Review helpers: LED-style strips of scenes, backdrops and the live screens, plus a sprite sheet.

    python3 renderer/review.py scene disco_ball [out_dir] [every_seconds]   keyframes (or every N s) of one module
    python3 renderer/review.py all [out_dir]                                every scene and backdrop
    python3 renderer/review.py live [out_dir]                               live screens, as the bar shows them
    python3 renderer/review.py sprites [out.png]

Strips are written under previews/ by default (git-ignored). `live` runs the app's real TypeScript
(app/shared/screens.ts) under Node 24 and composites its xpmbitmaps over the built .anim frames, so build first.
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "lib" / "python"))

from PIL import Image  # noqa: E402

from busybar.anim import read_anim  # noqa: E402
from busybar.canvas import FPS  # noqa: E402
from busybar.preview import led, strip  # noqa: E402

PREVIEWS = ROOT / "previews"


def node_cmd() -> list[str]:
    try:
        local = subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.startswith("v24.")
    except FileNotFoundError:
        local = False
    return ["node"] if local else ["npx", "-y", "-p", "node@24", "node"]


def sheet(path: Path) -> None:
    import sprites
    tiles = [led(s.img(i), cell=8) for s in sprites.ALL for i in range(len(s))]
    pad, cols = 8, 6
    tw, th = max(t.width for t in tiles), max(t.height for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad) + pad), (40, 40, 48))
    for i, t in enumerate(tiles):
        out.paste(t, (pad + (i % cols) * (tw + pad), pad + (i // cols) * (th + pad)))
    out.save(path)
    print(f"wrote {path} ({len(tiles)} frames)")


def review_module(m, out_dir: Path, every: float | None = None) -> Path:
    import build
    frames = [build.tone(f) for f in m.render()]
    if every:
        picks = [int(i * every * FPS) for i in range(int(len(frames) / (every * FPS)) + 1)]
    else:
        picks = [int(s * FPS) for s, _ in m.KEYFRAMES]
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"review_{m.NAME}.png"
    strip(frames, picks, p)
    print(f"{m.NAME}: {len(frames)} frames -> {p}")
    return p


def find_module(name: str):
    from scenes import BACKDROPS, PLAYLIST
    for m in PLAYLIST + list(BACKDROPS.values()):
        if m.NAME == name:
            return m
    return importlib.import_module(f"scenes.{name}")


LIVE_TS = """
import { screenAt, overlayAt, composeBitmap } from "%(shared)s/screens.ts";
import { FONTS, LAYOUT, SHOW } from "%(shared)s/generated/show.ts";
import { parseLocal } from "%(lib)s/walltime.ts";
const out: any[] = [];
const samples: [string, string, string, number][] = %(samples)s;
for (const [label, kind, iso, startedAt] of samples) {
  const t = parseLocal(iso)!;
  const s = screenAt(kind as any, t, startedAt, LAYOUT as any, FONTS as any);
  out.push({ label, stage: s.stage, bmp: composeBitmap(s.layers, FONTS as any) });
}
const odo = SHOW.scenes.find((s: any) => s.overlay)!;
for (const ms of [500, 3000, 6100, 6600]) {
  const layers = overlayAt((odo as any).overlay, ms, parseLocal("2026-12-31T22:00:00")!, LAYOUT as any, FONTS as any);
  out.push({ label: "odometer +" + ms + " ms", scene: odo.name, ms, bmp: layers ? composeBitmap(layers, FONTS as any) : null });
}
console.log(JSON.stringify(out));
"""

LIVE_SAMPLES = [
    ("Card: 2 h 14 min to go", "card", "2026-12-31T21:45:12", 0),
    ("Card: last hour", "card", "2026-12-31T23:42:05", 0),
    ("Final minute (pre-roll)", "final", "2026-12-31T23:58:52", 0),
    ("Final minute: 45", "final", "2026-12-31T23:59:15", 0),
    ("Final minute: 20 (fast lights)", "final", "2026-12-31T23:59:40", 0),
    ("Final minute: 11", "final", "2026-12-31T23:59:49", 0),
    ("Final ten: 10", "final10", "2026-12-31T23:59:50", 0),
    ("Final ten: 7", "final10", "2026-12-31T23:59:53", 0),
    ("Final ten: 1", "final10", "2026-12-31T23:59:59", 0),
    ("Midnight: 0", "celebrate", "2027-01-01T00:00:00", 0),
    ("Midnight: burst", "celebrate", "2027-01-01T00:00:02", 0),
    ("Celebration: greeting", "celebrate", "2027-01-01T00:00:04", 0),
    ("Celebration: year", "celebrate", "2027-01-01T00:00:08", 0),
    ("After midnight card", "card", "2027-01-01T00:42:00", 0),
    ("Off-season card", "card", "2026-11-25T20:15:00", 0),
]


def xpm_pixels(data: str, x0: int, y0: int) -> dict:
    lines = data.split("\n")
    w, h, n, _ = map(int, lines[1].split())
    pal = {}
    for ln in lines[2:2 + n]:
        ch, _, val = ln.split(" ")
        pal[ch] = None if val == "none" else tuple(int(val[i:i + 2], 16) for i in (1, 3, 5))
    rows = lines[2 + n:2 + n + h]
    return {(x0 + x, y0 + y): pal[c] for y, r in enumerate(rows) for x, c in enumerate(r) if pal[c]}


def overlay(frame: Image.Image, bmp) -> Image.Image:
    img = frame.convert("RGB").copy()
    if bmp:
        for (x, y), c in xpm_pixels(bmp["data"], bmp["x"], bmp["y"]).items():
            img.putpixel((x, y), c)
    return img


def run_live() -> list:
    shared = (ROOT / "app" / "shared").as_posix()
    lib = (HERE.parents[2] / "lib" / "ts" / "busybar").as_posix()
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "live.mts"
        script.write_text(LIVE_TS % {"shared": shared, "lib": lib, "samples": json.dumps(LIVE_SAMPLES)})
        res = subprocess.run(node_cmd() + ["--experimental-strip-types", "--no-warnings", str(script)],
                             capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


def live(out_dir: Path) -> Path:
    anim_dir = ROOT / "app" / "src" / "animations"
    cache: dict[str, list] = {}

    def frames_of(name):
        if name not in cache:
            a = read_anim(anim_dir / f"{name}.anim")
            cache[name] = [Image.frombytes("RGBA", (72, 16), bytes(b)).convert("RGB") for b in
                           [bgra_to_rgba(f) for f in a["frames"]]]
        return cache[name]

    tiles = []
    for s in run_live():
        if "scene" in s:
            fr = frames_of(s["scene"])[min(int(s["ms"] * FPS / 1000), len(frames_of(s["scene"])) - 1)]
        else:
            from scenes import BACKDROPS
            name = BACKDROPS[s["stage"]].NAME
            fr = frames_of(name)[0 if s["stage"] in ("burst", "final10") else 7]
            if s["label"] == "Midnight: burst":
                fr = frames_of(name)[22]
            elif s["stage"] == "final10":
                fr = frames_of(name)[3]
        tiles.append(overlay(fr, s["bmp"]))
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "review_live.png"
    strip(tiles, list(range(len(tiles))), p)
    print(f"live screens: {len(tiles)} -> {p}")
    for i, s in enumerate(run_live()):
        print(f"  {i:2d} {s['label']}")
    return p


def bgra_to_rgba(b: bytes) -> bytes:
    out = bytearray(b)
    out[0::4], out[2::4] = b[2::4], b[0::4]
    return bytes(out)


if __name__ == "__main__":
    cmd = sys.argv[1:2]
    if cmd == ["sprites"]:
        sheet(Path(sys.argv[2]) if len(sys.argv) > 2 else PREVIEWS / "sprites.png")
    elif cmd == ["scene"]:
        review_module(find_module(sys.argv[2]), Path(sys.argv[3]) if len(sys.argv) > 3 else PREVIEWS,
                      float(sys.argv[4]) if len(sys.argv) > 4 else None)
    elif cmd == ["all"]:
        from scenes import BACKDROPS, PLAYLIST
        for m in PLAYLIST + list(BACKDROPS.values()):
            review_module(m, Path(sys.argv[2]) if len(sys.argv) > 2 else PREVIEWS)
    elif cmd == ["live"]:
        live(Path(sys.argv[2]) if len(sys.argv) > 2 else PREVIEWS)
    else:
        print(__doc__)
