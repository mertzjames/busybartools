"""Review helpers: LED-style keyframe strips of scenes, and a contact sheet of sprites.

    python3 renderer/review.py scene day07 [out_dir] [every_seconds [start end]]   (out_dir defaults to previews/)
    python3 renderer/review.py all [out_dir]                            every scene's keyframes
    python3 renderer/review.py cards [out_dir]                          door + every countdown card with live text
    python3 renderer/review.py sprites [out.png]

Strips are tone-mapped with the build's GAMMA, so they look like what the bar shows.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "lib" / "python"))

from PIL import Image  # noqa: E402

from busybar.canvas import FPS  # noqa: E402
from busybar.preview import led, strip  # noqa: E402

PREVIEWS = HERE.parent / "previews"


def _tone(frames):
    import build
    return [build.tone(f) for f in frames]


def scene_module(name: str):
    import scenes
    for m in scenes.ALL:
        if m.NAME == name or m.__name__.split(".")[-1] == name:
            return m
    return importlib.import_module(f"scenes.{name}")


def review(name: str, out_dir: Path, every: float | None = None, start: float = 0.0,
           end: float | None = None) -> Path:
    """Keyframes by default; with `every`, a frame every N seconds (optionally only between start and end)."""
    m = scene_module(name)
    frames = _tone(m.render())
    if every:
        stop = len(frames) / FPS if end is None else end
        n = int(round((stop - start) / every))
        picks = [min(len(frames) - 1, int(round((start + i * every) * FPS))) for i in range(n + 1)]
    else:
        picks = [int(s * FPS) for s, _ in m.KEYFRAMES]
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"_{start:g}-{end:g}s" if every and end is not None else ""
    p = out_dir / f"review_{m.NAME}{suffix}.png"
    strip(frames, picks, p)
    print(f"{m.NAME}: {len(frames)} frames -> {p}")
    return p


CARD_SAMPLES = [  # what the app's cardLines() returns on these dates (tests/advent.test.mts checks the logic)
    [("11 DAYS", "head"), ("TO ADVENT", "sub")],
    [("18 DAYS", "head"), ("TO CHRISTMAS", "sub")],
    [("1 DAY", "head"), ("TO ADVENT", "sub")],
    [("06:42", "head"), ("TO GO", "sub")],
    [("MERRY", "top"), ("CHRISTMAS", "bot")],
    [("SEE YOU", "top"), ("NEXT YEAR!", "bot")],
]


def cards(out_dir: Path) -> Path:
    """The door intro with a live date, and every countdown card variant, as the bar draws them."""
    import build
    from busybar.font import draw_text, text_width
    from scenes import CARD, DOOR

    styles = build.text_styles()

    def write(img, txt, style):
        s = styles[style]
        draw_text(img, txt, (72 - text_width(txt, s["font"])) // 2, s["y"], None, font=s["font"],
                  gradient=(tuple(s["top"]), tuple(s["bottom"])), shadow=tuple(s["shadow"]))
        return img

    door = _tone(DOOR.render())
    card = _tone(CARD.render())
    frames = [door[int(0.2 * FPS)], door[int(0.9 * FPS)]]
    for label in ("DEC 1", "DEC 7", "DEC 25"):
        frames.append(write(door[int(2.0 * FPS)].convert("RGBA"), label, "date"))
    for lines in CARD_SAMPLES:
        img = card[0].convert("RGBA")
        for txt, style in lines:
            write(img, txt, style)
        frames.append(img)
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "review_cards.png"
    strip(frames, list(range(len(frames))), p)
    print(f"cards -> {p}")
    return p


def sheet(path: Path) -> None:
    import props
    import scenes
    from busybar.sprite import Sprite
    found = {}
    for mod in [props] + scenes.ALL:  # sprites are defined next to the scene that uses them
        for v in vars(mod).values():
            if isinstance(v, Sprite):
                found.setdefault(v.name, v)
    tiles = [led(s.img(i), cell=8) for s in found.values() for i in range(len(s))]
    pad, cols = 8, 6
    tw, th = max(t.width for t in tiles), max(t.height for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad) + pad), (40, 40, 48))
    for i, t in enumerate(tiles):
        out.paste(t, (pad + (i % cols) * (tw + pad), pad + (i // cols) * (th + pad)))
    out.save(path)
    print(f"wrote {path} ({len(tiles)} frames)")


if __name__ == "__main__":
    cmd = sys.argv[1:2]
    if cmd == ["scene"]:
        review(sys.argv[2], Path(sys.argv[3]) if len(sys.argv) > 3 else PREVIEWS,
               float(sys.argv[4]) if len(sys.argv) > 4 else None,
               float(sys.argv[5]) if len(sys.argv) > 5 else 0.0,
               float(sys.argv[6]) if len(sys.argv) > 6 else None)
    elif cmd == ["all"]:
        import scenes
        for m in scenes.ALL:
            review(m.NAME, Path(sys.argv[2]) if len(sys.argv) > 2 else PREVIEWS)
    elif cmd == ["cards"]:
        cards(Path(sys.argv[2]) if len(sys.argv) > 2 else PREVIEWS)
    elif cmd == ["sprites"]:
        PREVIEWS.mkdir(exist_ok=True)
        sheet(Path(sys.argv[2]) if len(sys.argv) > 2 else PREVIEWS / "sprites.png")
    else:
        print(__doc__)
