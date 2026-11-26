"""Review helpers for this app: a sprite contact sheet and LED-style keyframe strips.

    python3 renderer/review.py sprites previews/sprites.png
    python3 renderer/review.py scene sleigh_ride previews/ [every_seconds [start end]]
    python3 renderer/review.py all previews/            (every scene + the clock card, at their keyframes)

Strips are tone-mapped with the build's GAMMA, so they look like what the bar shows. The clock card strip
includes the live time and date drawn exactly as the app draws them.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "lib" / "python"))

from PIL import Image  # noqa: E402

from busybar.preview import led, strip  # noqa: E402


def sheet(path: Path) -> None:
    """Contact sheet of every sprite frame."""
    import sprites

    tiles = []
    for s in sprites.ALL:
        for i in range(len(s)):
            tiles.append(led(s.img(i), cell=8))
    pad = 8
    cols = 8
    tw = max(t.width for t in tiles)
    th = max(t.height for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad) + pad), (40, 40, 48))
    for i, t in enumerate(tiles):
        out.paste(t, (pad + (i % cols) * (tw + pad), pad + (i // cols) * (th + pad)))
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print(f"wrote {path} ({len(tiles)} frames)")


def review(module_name: str, out_dir: Path, every: float | None = None, start: float = 0.0,
           end: float | None = None) -> Path:
    """Render a scene and write a strip of its keyframes (or every N seconds, optionally within start..end)."""
    import importlib

    import build
    from busybar.canvas import FPS
    m = importlib.import_module(f"scenes.{module_name}")
    frames = [build.tone(f.convert("RGB")) for f in m.render()]
    if module_name == "clock_bg":
        frames, picks = build.clock_preview(frames)
    elif every:
        stop = len(frames) / FPS if end is None else end
        picks = [int((start + i * every) * FPS) for i in range(int((stop - start) / every) + 1)]
    else:
        picks = [int(s * FPS) for s, _ in m.KEYFRAMES]
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"review_{module_name}.png"
    strip(frames, picks, p, cell=9)
    print(f"{module_name}: {len(frames)} frames -> {p}")
    return p


if __name__ == "__main__":
    if sys.argv[1:2] == ["sprites"]:
        sheet(Path(sys.argv[2] if len(sys.argv) > 2 else "sprites.png"))
    elif sys.argv[1:2] == ["scene"]:
        review(sys.argv[2], Path(sys.argv[3] if len(sys.argv) > 3 else "."),
               float(sys.argv[4]) if len(sys.argv) > 4 else None,
               float(sys.argv[5]) if len(sys.argv) > 5 else 0.0,
               float(sys.argv[6]) if len(sys.argv) > 6 else None)
    elif sys.argv[1:2] == ["all"]:
        from scenes import CLOCK_BG, PLAYLIST
        for mod in PLAYLIST + [CLOCK_BG]:
            review(mod.NAME, Path(sys.argv[2] if len(sys.argv) > 2 else "."))
    else:
        print(__doc__)
