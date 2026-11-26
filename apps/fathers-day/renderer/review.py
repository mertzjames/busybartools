"""Review helpers for this app: LED-style keyframe strips, tone-mapped like the bar.

    python3 renderer/review.py scene grill previews/ [every_seconds [start end]]
    python3 renderer/review.py all previews/        (every scene and both cards, at their keyframes)
    python3 renderer/review.py cards previews/      (every card page over its backdrop, before and on the day)
    python3 renderer/review.py grid catch previews/ 0.5 [start end]   (a labeled 2-column grid, for fine timing)

Card strips draw the live text exactly as the app does (build.draw_live), over the tone-mapped backdrop.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "lib" / "python"))

from busybar.canvas import FPS  # noqa: E402
from busybar.preview import strip  # noqa: E402


def review(module_name: str, out_dir: Path, every: float | None = None, start: float = 0.0,
           end: float | None = None) -> Path:
    """Render a scene and write a strip of its keyframes (or every N seconds, optionally within start..end)."""
    import build
    m = importlib.import_module(f"scenes.{module_name}")
    frames = [build.tone(f.convert("RGB")) for f in m.render()]
    if every:
        stop = len(frames) / FPS if end is None else end
        picks = [min(len(frames) - 1, int((start + i * every) * FPS)) for i in range(int((stop - start) / every) + 1)]
    else:
        picks = [min(len(frames) - 1, int(s * FPS)) for s, _ in m.KEYFRAMES]
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"review_{module_name}.png"
    strip(frames, picks, p, cell=9)
    print(f"{module_name}: {len(frames)} frames -> {p}")
    return p


def grid(module_name: str, out_dir: Path, every: float, start: float = 0.0, end: float | None = None) -> Path:
    """A 2-column grid of LED frames every `every` seconds, each labeled with its time (easier to read than a
    long strip when checking fine timing)."""
    from PIL import Image, ImageDraw

    from busybar.preview import led

    import build
    m = importlib.import_module(f"scenes.{module_name}")
    frames = [build.tone(f.convert("RGB")) for f in m.render()]
    stop = len(frames) / FPS if end is None else end
    times = [start + i * every for i in range(int((stop - start) / every + 1e-6) + 1)]
    tiles = [led(frames[min(len(frames) - 1, int(t * FPS))], cell=6) for t in times]
    tw, th, pad, lab = tiles[0].width, tiles[0].height, 6, 14
    rows = (len(tiles) + 1) // 2
    out = Image.new("RGB", (2 * tw + 3 * pad, rows * (th + lab + pad) + pad), (40, 40, 48))
    d = ImageDraw.Draw(out)
    for k, (t, tile) in enumerate(zip(times, tiles)):
        x = pad + (k % 2) * (tw + pad)
        y = pad + (k // 2) * (th + lab + pad)
        d.text((x, y), f"{t:.1f} s", fill=(220, 220, 230))
        out.paste(tile, (x, y + lab))
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"grid_{module_name}.png"
    out.save(p)
    print(f"{module_name}: grid of {len(tiles)} -> {p}")
    return p


def cards(out_dir: Path) -> Path:
    """Every card page: the clock, the countdown, and the three on-the-day cards."""
    import build
    from scenes import CLOCK_BG, COUNT_BG
    clock = [build.tone(f.convert("RGB")) for f in CLOCK_BG.render()]
    count = [build.tone(f.convert("RGB")) for f in COUNT_BG.render()]
    pages = [(clock, [("18:05", "time")]), (clock, [("WED 28 SEP", "date")]),
             (count, [("206 DAYS", "head"), ("TO FATHER'S DAY", "sub")]),
             (count, [("370 DAYS", "head"), ("TO FATHER'S DAY", "sub")])]
    for card in build.DAY_TEXT:
        for page in card:
            pages.append((count, page))
    frames = []
    for i, (bg, lines) in enumerate(pages):
        img = bg[(i * 13) % len(bg)].convert("RGBA")
        for text, style in lines:
            build.draw_live(img, text, style)
        frames.append(img.convert("RGB"))
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "review_cards.png"
    strip(frames, list(range(len(frames))), p, cell=9)
    print(f"cards: {len(frames)} pages -> {p}")
    return p


if __name__ == "__main__":
    out = Path(sys.argv[3] if sys.argv[1:2] == ["scene"] and len(sys.argv) > 3 else
               sys.argv[2] if len(sys.argv) > 2 else ".")
    if sys.argv[1:2] == ["scene"]:
        review(sys.argv[2], out, float(sys.argv[4]) if len(sys.argv) > 4 else None,
               float(sys.argv[5]) if len(sys.argv) > 5 else 0.0,
               float(sys.argv[6]) if len(sys.argv) > 6 else None)
    elif sys.argv[1:2] == ["grid"]:
        grid(sys.argv[2], Path(sys.argv[3]), float(sys.argv[4]),
             float(sys.argv[5]) if len(sys.argv) > 5 else 0.0, float(sys.argv[6]) if len(sys.argv) > 6 else None)
    elif sys.argv[1:2] == ["all"]:
        from scenes import CLOCK_BG, COUNT_BG, PLAYLIST
        for mod in PLAYLIST + [CLOCK_BG, COUNT_BG]:
            review(mod.NAME, out)
        cards(out)
    elif sys.argv[1:2] == ["cards"]:
        cards(out)
    else:
        print(__doc__)
