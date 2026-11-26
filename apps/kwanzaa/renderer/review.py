"""Review helpers for this app: LED-style strips of scenes and cards.

    python3 renderer/review.py scene harvest previews/ [every_seconds [start end]]
    python3 renderer/review.py kinara 3 previews/ [every_seconds [start end]]     (one kinara variant, 0..7)
    python3 renderer/review.py cards previews/      (every card page: clock, before Kwanzaa, each day's pages)
    python3 renderer/review.py all previews/        (every scene and kinara variant at its keyframes, plus cards)

Strips are tone-mapped with the build's GAMMA, so they look like what the bar shows. Card strips draw the live
text exactly as the app draws it, over the backdrop.
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

import build  # noqa: E402


def picks_for(m, n_frames: int, every: float | None, start: float, end: float | None) -> list[int]:
    if every:
        stop = n_frames / FPS if end is None else end
        return [int((start + i * every) * FPS) for i in range(int(round((stop - start) / every)) + 1)]
    return [int(s * FPS) for s, _ in m.KEYFRAMES]


def review(m, out_dir: Path, every: float | None = None, start: float = 0.0, end: float | None = None) -> Path:
    frames = [build.tone(f.convert("RGB")) for f in m.render()]
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"review_{m.NAME}.png"
    strip(frames, picks_for(m, len(frames), every, start, end), p, cell=9)
    print(f"{m.NAME}: {len(frames)} frames -> {p}")
    return p


def cards(out_dir: Path) -> Path:
    """Every card page over the backdrop: the clock, the countdown, then each day's principle pages."""
    from scenes import CARD_BG
    from scenes.text import count_pages
    styles = build.text_styles()
    bg = [build.tone(f.convert("RGB")) for f in CARD_BG.render()]
    pages = [[("time", "18:05")], [("date", "SAT 26 DEC")]]
    pages += [lines for _, lines in count_pages(0, 30)]
    for day in range(1, 8):
        pages += [lines for _, lines in count_pages(day, 0)]
    frames = []
    for k, lines in enumerate(pages):
        img = bg[(k * 7) % len(bg)].convert("RGBA")
        for style, text in lines:
            build.draw_live(img, text, styles[style])
        frames.append(img.convert("RGB"))
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "review_cards.png"
    strip(frames, list(range(len(frames))), p, cell=6)
    print(f"cards: {len(frames)} pages -> {p}")
    return p


def _args(i: int):
    a = sys.argv
    return (float(a[i]) if len(a) > i else None, float(a[i + 1]) if len(a) > i + 1 else 0.0,
            float(a[i + 2]) if len(a) > i + 2 else None)


if __name__ == "__main__":
    cmd = sys.argv[1:2]
    if cmd == ["scene"]:
        review(importlib.import_module(f"scenes.{sys.argv[2]}"), Path(sys.argv[3]), *_args(4))
    elif cmd == ["kinara"]:
        from scenes import KINARA
        review(KINARA[int(sys.argv[2])], Path(sys.argv[3]), *_args(4))
    elif cmd == ["cards"]:
        cards(Path(sys.argv[2] if len(sys.argv) > 2 else "."))
    elif cmd == ["all"]:
        from scenes import KINARA, PLAYLIST
        out = Path(sys.argv[2] if len(sys.argv) > 2 else ".")
        for mod in KINARA + PLAYLIST:
            review(mod, out)
        cards(out)
    else:
        print(__doc__)
