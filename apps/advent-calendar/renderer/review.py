"""Review helpers: LED-style keyframe strips of scenes, and a contact sheet of sprites.

    python3 renderer/review.py scene day07 [out_dir] [every_seconds]   (out_dir defaults to previews/)
    python3 renderer/review.py all [out_dir]                            every scene's keyframes
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


def review(name: str, out_dir: Path, every: float | None = None) -> Path:
    m = scene_module(name)
    frames = _tone(m.render())
    if every:
        picks = [int(i * every * FPS) for i in range(int(len(frames) / (every * FPS)) + 1)]
    else:
        picks = [int(s * FPS) for s, _ in m.KEYFRAMES]
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"review_{m.NAME}.png"
    strip(frames, picks, p)
    print(f"{m.NAME}: {len(frames)} frames -> {p}")
    return p


def sheet(path: Path) -> None:
    import sprites
    tiles = [led(s.img(i), cell=8) for s in sprites.ALL for i in range(len(s))]
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
               float(sys.argv[4]) if len(sys.argv) > 4 else None)
    elif cmd == ["all"]:
        import scenes
        for m in scenes.ALL:
            review(m.NAME, Path(sys.argv[2]) if len(sys.argv) > 2 else PREVIEWS)
    elif cmd == ["sprites"]:
        PREVIEWS.mkdir(exist_ok=True)
        sheet(Path(sys.argv[2]) if len(sys.argv) > 2 else PREVIEWS / "sprites.png")
    else:
        print(__doc__)
