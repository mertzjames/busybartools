"""Review helpers for this app: a sprite contact sheet and keyframe strips of a scene.

    python3 renderer/review.py sprites out.png
    python3 renderer/review.py scene dragon_roast out_dir/ [every_seconds]
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
    cols = 6
    tw = max(t.width for t in tiles)
    th = max(t.height for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad) + pad), (40, 40, 48))
    for i, t in enumerate(tiles):
        out.paste(t, (pad + (i % cols) * (tw + pad), pad + (i // cols) * (th + pad)))
    out.save(path)
    print(f"wrote {path} ({len(tiles)} frames)")


def review(module_name: str, out_dir: Path, every: float | None = None) -> None:
    """Render a scene and write a strip of its keyframes (or every N seconds)."""
    import importlib
    from busybar.canvas import FPS
    m = importlib.import_module(f"scenes.{module_name}")
    frames = m.render()
    if every:
        picks = [int(i * every * FPS) for i in range(int(len(frames) / (every * FPS)) + 1)]
    else:
        picks = [int(s * FPS) for s, _ in m.KEYFRAMES]
    p = out_dir / f"review_{module_name}.png"
    strip(frames, picks, p)
    print(f"{module_name}: {len(frames)} frames -> {p}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["sprites"]:
        sheet(Path(sys.argv[2] if len(sys.argv) > 2 else "sprites.png"))
    elif sys.argv[1:2] == ["scene"]:
        review(sys.argv[2], Path(sys.argv[3] if len(sys.argv) > 3 else "."),
               float(sys.argv[4]) if len(sys.argv) > 4 else None)
    else:
        print(__doc__)
