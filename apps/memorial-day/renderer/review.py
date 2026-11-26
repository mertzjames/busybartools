"""Review helpers for this app: LED-style keyframe strips, tone-mapped like the bar.

    python3 renderer/review.py scene flag_half previews/ [every_seconds [start end]]
    python3 renderer/review.py all previews/        (every scene and both backdrops, at their keyframes)
    python3 renderer/review.py cards previews/      (every card page over its backdrop, before and on the day)

Card strips draw the live text exactly as the app does (build.draw_live), over the tone-mapped backdrop.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "lib" / "python"))

from busybar.canvas import FPS  # noqa: E402
from busybar.preview import strip  # noqa: E402
from busybar.showbuild import apply_tone, tone_lut  # noqa: E402

GAMMA = 0.8  # the same as build.py
LUT = tone_lut(GAMMA)


def tone(img):
    return apply_tone(img, LUT)


def module(name: str):
    from scenes import ALL, CLOCK_BG, COUNT_BG
    for m in list(ALL) + [CLOCK_BG, COUNT_BG]:
        if m.NAME == name:
            return m
    raise SystemExit(f"no scene {name!r}; scenes: {', '.join(m.NAME for m in ALL)}")


def review(name: str, out_dir: Path, every: float | None = None, start: float = 0.0, end: float | None = None,
           cell: int = 9) -> Path:
    """Render a scene and write a strip of its keyframes (or every N seconds, optionally within start..end)."""
    m = module(name)
    frames = [tone(f.convert("RGB")) for f in m.render()]
    if every:
        stop = len(frames) / FPS if end is None else end
        picks = [min(len(frames) - 1, int((start + i * every) * FPS)) for i in range(int((stop - start) / every) + 1)]
    else:
        picks = [min(len(frames) - 1, int(s * FPS)) for s, _ in m.KEYFRAMES]
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / (f"review_{name}.png" if not every else f"review_{name}_{start:g}-{end or 'end'}.png")
    strip(frames, picks, p, cell=cell)
    print(f"{name}: {len(frames)} frames -> {p}")
    return p


def cards(out_dir: Path) -> Path:
    """Every card page: the clock, the countdown, and the three on-the-day cards (morning and afternoon)."""
    import build
    from scenes import CLOCK_BG, COUNT_BG
    from scenes.text import DAY_TEXT, HALF_TEXT, FULL_TEXT
    clock = [tone(f.convert("RGB")) for f in CLOCK_BG.render()]
    count = [tone(f.convert("RGB")) for f in COUNT_BG.render()]
    pages = [(clock, [("09:05", "time")]), (clock, [("MON 31 MAY", "date")]),
             (count, [("186 DAYS", "head"), ("TO MEMORIAL DAY", "sub")]),
             (count, [("1 DAY", "head"), ("TO MEMORIAL DAY", "sub")])]
    for card in DAY_TEXT:
        for page in card:
            pages.append((count, page))
    pages += [(count, HALF_TEXT), (count, FULL_TEXT)]
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
    args = sys.argv[1:]
    if args[:1] == ["scene"] and len(args) >= 3:
        review(args[1], Path(args[2]), float(args[3]) if len(args) > 3 else None,
               float(args[4]) if len(args) > 4 else 0.0, float(args[5]) if len(args) > 5 else None)
    elif args[:1] == ["all"] and len(args) >= 2:
        from scenes import ALL, CLOCK_BG, COUNT_BG
        for mod in list(ALL) + [CLOCK_BG, COUNT_BG]:
            review(mod.NAME, Path(args[1]))
        cards(Path(args[1]))
    elif args[:1] == ["cards"] and len(args) >= 2:
        cards(Path(args[1]))
    else:
        print(__doc__)
