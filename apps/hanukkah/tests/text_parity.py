#!/usr/bin/env python3
"""Live-text parity test: the on-bar app, the mockup and the renderer must draw identical card pixels.

Runs the app's real TypeScript (the shared xpmtext.ts through app/shared/kit.ts, and the generated show.ts) under
Node 24, decodes the XPM bitmaps it produces, and compares them pixel-for-pixel with busybar.font drawing the same
text with this app's tone-mapped LAYOUT (renderer/scenes/cards.py). Also checks that the widest date fits and that
the generated scene list matches the renderer's. See docs/DECISIONS.md D8.

    python3 tests/text_parity.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR / "renderer"))
sys.path.insert(0, str(APP_DIR.parents[1] / "lib" / "python"))

from busybar.canvas import new  # noqa: E402
from busybar.font import draw_text, text_width  # noqa: E402

import build  # noqa: E402  (for the exported, tone-mapped layout)
from scenes import CARDS, SCENES  # noqa: E402

SAMPLES = [("18:05", "time"), ("00:00", "time"), ("23:59", "time"), ("FRI 4 DEC", "date"), ("WED 30 DEC", "date"),
           ("8 DAYS", "head"), ("376 DAYS", "head"), ("1 DAY", "head"), ("NIGHT 3", "head"), ("TOMORROW", "head"),
           ("TONIGHT", "head"), ("TO HANUKKAH", "sub"), ("HAPPY HANUKKAH", "sub"), ("CHAG SAMEACH", "sub"),
           ("HANUKKAH BEGINS", "sub"), ("CANDLES AT 16:38", "sub")]

TS = """
import { textBitmap, type Font } from "%(shared)s/kit.ts";
import { FONTS, SHOW } from "%(shared)s/generated/show.ts";
const samples: [string, string][] = %(samples)s;
const bitmaps = samples.map(([txt, kind]) => {
  const spec = (SHOW.layout as any)[kind];
  const b = textBitmap(txt, FONTS[spec.font] as Font, spec);
  return { txt, kind, data: b.data, x: b.x, y: b.y };
});
console.log(JSON.stringify({
  bitmaps,
  scenes: SHOW.scenes.map((s) => [s.name, s.ms, s.path]),
  cards: SHOW.cards,
}));
"""


def run_app_code() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "parity.mts"
        script.write_text(TS % {"shared": (APP_DIR / "app" / "shared").as_posix(), "samples": json.dumps(SAMPLES)})
        local = subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.startswith("v24.")
        node = ["node"] if local else ["npx", "-y", "-p", "node@24", "node"]
        out = subprocess.run(node + ["--experimental-strip-types", "--no-warnings", str(script)],
                             capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def xpm_pixels(data: str, x0: int, y0: int):
    lines = data.split("\n")
    assert lines[0] == "! XPM2", "missing XPM2 signature"
    w, h, n, cpp = map(int, lines[1].split())
    assert n <= 32 and cpp == 1, "firmware limits: <=32 colors"
    pal = {}
    for ln in lines[2:2 + n]:
        ch, _, val = ln.split(" ")
        pal[ch] = None if val == "none" else tuple(int(val[i:i + 2], 16) for i in (1, 3, 5))
    rows = lines[2 + n:2 + n + h]
    assert len(rows) == h and all(len(r) == w for r in rows)
    assert x0 >= 0 and y0 >= 0 and x0 + w <= 72 and y0 + h <= 16, "bitmap must fit the 72x16 display"
    return {(x0 + x, y0 + y): pal[c] for y, r in enumerate(rows) for x, c in enumerate(r) if pal[c]}


def renderer_pixels(txt: str, spec: dict):
    img = new()
    draw_text(img, txt, (72 - text_width(txt, spec["font"])) // 2, spec["y"], None, font=spec["font"],
              gradient=(tuple(spec["top"]), tuple(spec["bottom"])), shadow=tuple(spec["shadow"]))
    return {(x, y): img.getpixel((x, y))[:3] for y in range(16) for x in range(72)
            if img.getpixel((x, y))[:3] != (0, 0, 0)}


def widest_date() -> tuple[str, int]:
    days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    font = build.layout()["date"]["font"]
    best = max((f"{d} {n} {m}" for d in days for n in range(1, 32) for m in months),
               key=lambda s: text_width(s, font))
    return best, text_width(best, font)


def main() -> int:
    res = run_app_code()
    layout = build.layout()
    failures = 0
    for b in res["bitmaps"]:
        app_px = xpm_pixels(b["data"], b["x"], b["y"])
        ref_px = renderer_pixels(b["txt"], layout[b["kind"]])
        ok = app_px == ref_px and len(app_px) > 0
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {b['kind']:5} {b['txt']!r:18} {len(app_px)} px")
    date, width = widest_date()
    expected = [[m.NAME, int(m.SECONDS * 1000), f"animations/{m.NAME}.anim"] for m in SCENES]
    cards = {m.NAME.removesuffix("_bg"): f"animations/{m.NAME}.anim" for m in CARDS}
    files = [APP_DIR / "app" / "src" / p for _, _, p in res["scenes"]] + \
        [APP_DIR / "app" / "src" / p for p in res["cards"].values()]
    checks = [
        (width + 1 <= 72, f"widest date {date!r} fits ({width} px + shadow)"),
        (res["scenes"] == expected, "generated scene list matches the renderer"),
        (res["cards"] == cards, "generated card backdrops match the renderer"),
        (all(p.is_file() for p in files), "every .anim exists"),
    ]
    for ok, name in checks:
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print("text parity: " + ("PASS" if not failures else f"{failures} FAILURE(S)"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
