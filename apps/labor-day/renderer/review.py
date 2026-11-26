"""Review helpers for this app: LED-style strips, tone-mapped like the bar.

    python3 renderer/review.py scene steel previews/ [every_seconds [start end]]
    python3 renderer/review.py zoom steel previews/ <x0> <x1> <seconds,...>   (cell 18 crops of columns x0..x1)
    python3 renderer/review.py all previews/        (every scene and both cards, at their keyframes)
    python3 renderer/review.py cards previews/      (every card page over its backdrop, before and on the day)

Card strips draw the live text exactly as the app does (build.draw_live), over the tone-mapped backdrop.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "lib" / "python"))

from busybar.canvas import FPS  # noqa: E402
from busybar.preview import led, strip  # noqa: E402
from busybar.showbuild import apply_tone, tone_lut  # noqa: E402

LUT = tone_lut(0.8)  # the same curve as build.GAMMA


def frames_of(module_name: str):
    m = importlib.import_module(f"scenes.{module_name}")
    return m, [apply_tone(f.convert("RGB"), LUT) for f in m.render()]


def review(module_name: str, out_dir: Path, every: float | None = None, start: float = 0.0,
           end: float | None = None) -> Path:
    """Render a scene and write a strip of its keyframes (or every N seconds, optionally within start..end)."""
    m, frames = frames_of(module_name)
    if every:
        stop = len(frames) / FPS if end is None else end
        picks = [min(len(frames) - 1, int((start + i * every) * FPS)) for i in range(int((stop - start) / every) + 1)]
    else:
        picks = [min(len(frames) - 1, int(s * FPS)) for s, _ in m.KEYFRAMES]
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"review_{module_name}{'_t' if every else ''}.png"
    strip(frames, picks, p, cell=9)
    print(f"{module_name}: {len(frames)} frames -> {p}")
    return p


def zoom(module_name: str, out_dir: Path, x0: int, x1: int, times) -> Path:
    """Big crops (cell 18) of columns x0..x1 at the given seconds, side by side: for checking small sprites."""
    _, frames = frames_of(module_name)
    tiles = [led(frames[min(len(frames) - 1, int(s * FPS))].crop((x0, 0, x1 + 1, 16)), cell=18) for s in times]
    pad = 6
    out = Image.new("RGB", (len(tiles) * (tiles[0].width + pad) + pad, tiles[0].height + 2 * pad), (40, 40, 48))
    for k, t in enumerate(tiles):
        out.paste(t, (pad + k * (t.width + pad), pad))
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"zoom_{module_name}_{x0}_{x1}.png"
    out.save(p)
    print(f"{module_name}: zoom -> {p}")
    return p


def cards(out_dir: Path) -> Path:
    """Every card page: the clock, the countdown (the widest too), and the on-the-day cards."""
    import build
    from scenes import CLOCK_BG, COUNT_BG
    clock = [build.tone(f.convert("RGB")) for f in CLOCK_BG.render()]
    count = [build.tone(f.convert("RGB")) for f in COUNT_BG.render()]
    pages = [(clock, [("18:05", "time")]), (clock, [("WED 28 SEP", "date")]),
             (count, [("284 DAYS", "head"), ("TO LABOR DAY", "sub")]),
             (count, [("370 DAYS", "head"), ("TO LABOR DAY", "sub")])]
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
    cmd = sys.argv[1:2]
    if cmd == ["scene"]:
        review(sys.argv[2], Path(sys.argv[3]), float(sys.argv[4]) if len(sys.argv) > 4 else None,
               float(sys.argv[5]) if len(sys.argv) > 5 else 0.0, float(sys.argv[6]) if len(sys.argv) > 6 else None)
    elif cmd == ["zoom"]:
        zoom(sys.argv[2], Path(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]),
             [float(s) for s in sys.argv[6].split(",")])
    elif cmd == ["all"]:
        from scenes import CLOCK_BG, COUNT_BG, PLAYLIST
        out = Path(sys.argv[2])
        for mod in PLAYLIST + [CLOCK_BG, COUNT_BG]:
            review(mod.NAME, out)
        cards(out)
    elif cmd == ["cards"]:
        cards(Path(sys.argv[2]))
    else:
        print(__doc__)
