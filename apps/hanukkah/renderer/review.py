"""Review helpers for this app: LED-style keyframe strips, tone-mapped like the bar.

    python3 renderer/review.py scene dreidel previews/ [every_seconds [start end]]
    python3 renderer/review.py scene menorah_3 previews/ 0.2 2 6     (every 0.2 s between 2 s and 6 s)
    python3 renderer/review.py all previews/       (every scene and variant at its keyframes, plus the cards)
    python3 renderer/review.py nights previews/    (the end of the menorah and window scenes for nights 0-8)

The card strips draw the live text exactly as the app does.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "lib" / "python"))

from busybar.canvas import FPS  # noqa: E402
from busybar.preview import strip  # noqa: E402

import build  # noqa: E402
from scenes import CARDS, SCENES  # noqa: E402

BY_NAME = {m.NAME: m for m in SCENES + CARDS}
CARD_PAGES = {
    "clock_bg": ([{"time": "18:05"}, {"date": "FRI 4 DEC"}], 2000),
    "count_bg": ([{"head": "8 DAYS", "sub": "TO HANUKKAH"}, {"head": "TOMORROW", "sub": "HANUKKAH BEGINS"},
                  {"head": "TONIGHT", "sub": "HANUKKAH BEGINS"}, {"head": "NIGHT 3", "sub": "HAPPY HANUKKAH"},
                  {"head": "NIGHT 3", "sub": "CHAG SAMEACH"}], 2000),
}


def review(name: str, out_dir: Path, every: float | None = None, start: float = 0.0,
           end: float | None = None) -> Path:
    m = BY_NAME[name]
    frames = [build.tone(f.convert("RGB")) for f in m.render()]
    if name in CARD_PAGES:
        pages, ms = CARD_PAGES[name]
        frames, picks = build.card_preview(frames, pages, ms)
    elif every:
        stop = len(frames) / FPS if end is None else end
        picks = [int((start + i * every) * FPS) for i in range(int((stop - start) / every) + 1)]
    else:
        picks = [int(s * FPS) for s, _ in m.KEYFRAMES]
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"review_{name}.png"
    strip(frames, picks, p, cell=9)
    print(f"{name}: {len(frames)} frames -> {p}")
    return p


def nights(out_dir: Path) -> Path:
    frames = []
    for kind in ("menorah", "window"):
        for n in range(9):
            fr = BY_NAME[f"{kind}_{n}"].render()
            frames.append(build.tone(fr[-8].convert("RGB")))
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "review_nights.png"
    strip(frames, list(range(len(frames))), p, cell=9)
    print(f"nights -> {p}")
    return p


if __name__ == "__main__":
    out = Path(sys.argv[3] if sys.argv[1:2] == ["scene"] and len(sys.argv) > 3 else
               (sys.argv[2] if len(sys.argv) > 2 else "previews"))
    if sys.argv[1:2] == ["scene"]:
        review(sys.argv[2], out, float(sys.argv[4]) if len(sys.argv) > 4 else None,
               float(sys.argv[5]) if len(sys.argv) > 5 else 0.0, float(sys.argv[6]) if len(sys.argv) > 6 else None)
    elif sys.argv[1:2] == ["all"]:
        for m in SCENES + CARDS:
            review(m.NAME, out)
        nights(out)
    elif sys.argv[1:2] == ["nights"]:
        nights(out)
    else:
        print(__doc__)
