"""Review helpers for this app: LED-style keyframe strips, tone-mapped like the bar.

    python3 renderer/review.py scene dawn previews/ [every_seconds [start end]]
    python3 renderer/review.py all previews/        (every scene and the card backdrops, at their keyframes)
    python3 renderer/review.py cards previews/      (every card page over its backdrop, before and on the day)
    python3 renderer/review.py zoom dawn previews/ 3.0,6.5 0 40   (close-ups at cell 18 of columns 0-40)

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


def cards(out_dir: Path) -> Path:
    """Every card page: the clock, the countdown (before and after), and the on-the-day cards."""
    import build
    from scenes import CLOCK_BG, COUNT_BG, DAY_BG
    clock = [build.tone(f.convert("RGB")) for f in CLOCK_BG.render()]
    count = [build.tone(f.convert("RGB")) for f in COUNT_BG.render()]
    day = [build.tone(f.convert("RGB")) for f in DAY_BG.render()]
    pages = [(clock, [("18:05", "time")]), (clock, [("WED 28 SEP", "date")]),
             (count, [("205 DAYS", "head"), ("TO JUNETEENTH", "sub")]),
             (count, [("1 DAY", "head"), ("TO JUNETEENTH", "sub")]),
             (count, [("365 DAYS", "head"), ("TO JUNETEENTH", "sub")])]
    for card in build.DAY_TEXT:
        for page in card:
            pages.append((day, page))
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


def zoom(module_name: str, out_dir: Path, times: list[float], x0: int, x1: int) -> Path:
    """Close-ups of small sprites: chosen moments of a scene, cropped to columns x0..x1, at cell 18."""
    import build
    m = importlib.import_module(f"scenes.{module_name}")
    frames = [build.tone(f.convert("RGB")).crop((x0, 0, x1 + 1, 16)) for f in m.render()]
    picks = [min(len(frames) - 1, int(s * FPS)) for s in times]
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"zoom_{module_name}.png"
    strip(frames, picks, p, cell=18)
    print(f"{module_name}: zoom {times} cols {x0}-{x1} -> {p}")
    return p


if __name__ == "__main__":
    out = Path(sys.argv[3] if sys.argv[1:2] in (["scene"], ["zoom"]) and len(sys.argv) > 3 else
               sys.argv[2] if len(sys.argv) > 2 else ".")
    if sys.argv[1:2] == ["scene"]:
        review(sys.argv[2], out, float(sys.argv[4]) if len(sys.argv) > 4 else None,
               float(sys.argv[5]) if len(sys.argv) > 5 else 0.0,
               float(sys.argv[6]) if len(sys.argv) > 6 else None)
    elif sys.argv[1:2] == ["all"]:
        from scenes import CLOCK_BG, COUNT_BG, DAY_BG, PLAYLIST
        for mod in PLAYLIST + [CLOCK_BG, COUNT_BG, DAY_BG]:
            review(mod.NAME, out)
        cards(out)
    elif sys.argv[1:2] == ["cards"]:
        cards(out)
    elif sys.argv[1:2] == ["zoom"]:
        zoom(sys.argv[2], Path(sys.argv[3]), [float(v) for v in sys.argv[4].split(",")], int(sys.argv[5]),
             int(sys.argv[6]))
    else:
        print(__doc__)
