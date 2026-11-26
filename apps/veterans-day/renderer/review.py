"""Review helpers for this app: LED-style strips and labeled grids, tone-mapped like the bar.

    python3 renderer/review.py scene parade previews/ [every_seconds [start end]]   a strip (keyframes or every N s)
    python3 renderer/review.py grid salute previews/ 1 [start end]                   a labeled 2-column grid
    python3 renderer/review.py zoom thank_you previews/ 6.0 20 52                    one frame, cell 18, columns 20-52
    python3 renderer/review.py all previews/        every scene and backdrop at its keyframes, plus every card page
    python3 renderer/review.py cards previews/      every card page over its backdrop (before, on the day, 11:00)

Card strips draw the live text exactly as the app does (build.draw_live), over the tone-mapped backdrop.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "lib" / "python"))

from busybar.canvas import FPS  # noqa: E402
from busybar.preview import led, strip  # noqa: E402
from busybar.showbuild import apply_tone, tone_lut  # noqa: E402

GAMMA = 0.8  # the same as build.py
LUT = tone_lut(GAMMA)


def tone(img):
    return apply_tone(img, LUT)


def module(name: str):
    import importlib
    from scenes import ALL, BACKDROPS
    for m in list(ALL) + list(BACKDROPS):
        if m.NAME == name:
            return m
    try:
        return importlib.import_module(f"scenes.{name}")
    except ModuleNotFoundError:
        raise SystemExit(f"no scene {name!r}; scenes: {', '.join(m.NAME for m in ALL)}")


def frames_of(name: str):
    return [tone(f.convert("RGB")) for f in module(name).render()]


def review(name: str, out_dir: Path, every: float | None = None, start: float = 0.0, end: float | None = None,
           cell: int = 9) -> Path:
    """Render a scene and write a strip of its keyframes (or every N seconds, optionally within start..end)."""
    m = module(name)
    frames = frames_of(name)
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


def grid(name: str, out_dir: Path, every: float, start: float = 0.0, end: float | None = None) -> Path:
    """A 2-column grid of LED frames every `every` seconds, each labeled with its time."""
    from PIL import Image, ImageDraw
    frames = frames_of(name)
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
    p = out_dir / f"grid_{name}.png"
    out.save(p)
    print(f"{name}: grid of {len(tiles)} -> {p}")
    return p


def zoom(name: str, out_dir: Path, at: float, x0: int = 0, x1: int = 71) -> Path:
    """One frame, cropped to columns x0..x1 and drawn large (cell 18), for checking small sprites."""
    frames = frames_of(name)
    img = frames[min(len(frames) - 1, int(at * FPS))].crop((x0, 0, x1 + 1, 16))
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"zoom_{name}_{at:g}.png"
    led(img, cell=18).save(p)
    print(f"{name}: zoom -> {p}")
    return p


def cards(out_dir: Path) -> Path:
    """Every card page: the clock, the countdown, the three on-the-day cards and the 11:00 moment."""
    import build
    from scenes import CLOCK_BG, COUNT_BG, MOMENT_BG
    from scenes.text import DAY_TEXT, MOMENT_TEXT
    clock = frames_of(CLOCK_BG.NAME)
    count = frames_of(COUNT_BG.NAME)
    moment = frames_of(MOMENT_BG.NAME)
    pages = [(clock, [("09:05", "time")]), (clock, [("WED 11 NOV", "date")]),
             (count, [("350 DAYS", "head"), ("TO VETERANS DAY", "sub")]),
             (count, [("1 DAY", "head"), ("TO VETERANS DAY", "sub")])]
    for card in DAY_TEXT:
        for page in card:
            pages.append((count, page))
    for page in MOMENT_TEXT:
        pages.append((moment, page))
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
    num = lambda i, d: float(args[i]) if len(args) > i else d  # noqa: E731
    if args[:1] == ["scene"] and len(args) >= 3:
        review(args[1], Path(args[2]), num(3, None), num(4, 0.0), num(5, None))
    elif args[:1] == ["grid"] and len(args) >= 3:
        grid(args[1], Path(args[2]), num(3, 1.0), num(4, 0.0), num(5, None))
    elif args[:1] == ["zoom"] and len(args) >= 4:
        zoom(args[1], Path(args[2]), float(args[3]), int(num(4, 0)), int(num(5, 71)))
    elif args[:1] == ["all"] and len(args) >= 2:
        from scenes import ALL, BACKDROPS
        for mod in list(ALL) + list(BACKDROPS):
            review(mod.NAME, Path(args[1]))
        cards(Path(args[1]))
    elif args[:1] == ["cards"] and len(args) >= 2:
        cards(Path(args[1]))
    else:
        print(__doc__)
