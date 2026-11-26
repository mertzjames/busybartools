"""LED-matrix style previews (round dots on black) for storyboards and sprite sheets."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

BG = (8, 8, 10)


def led(img: Image.Image, cell: int = 10, gap: int = 2) -> Image.Image:
    """Render a small image as an LED matrix: each pixel becomes a round dot."""
    src = img.convert("RGBA")
    out = Image.new("RGB", (src.width * cell, src.height * cell), BG)
    d = ImageDraw.Draw(out)
    px = src.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = px[x, y]
            if a == 0:
                c = (22, 22, 26)  # unlit LED
            else:
                k = a / 255
                c = (int(r * k), int(g * k), int(b * k))
                if max(c) < 18:
                    c = (22, 22, 26)
            x0, y0 = x * cell + gap // 2, y * cell + gap // 2
            d.ellipse((x0, y0, x0 + cell - gap - 1, y0 + cell - gap - 1), fill=c)
    return out


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


if __name__ == "__main__":
    sheet(Path(sys.argv[1] if len(sys.argv) > 1 else "sprites.png"))


def strip(frames, picks, path: Path, cell: int = 6) -> None:
    """Stack LED renders of the chosen frame indices vertically (for quick visual review)."""
    tiles = [led(frames[min(i, len(frames) - 1)], cell=cell) for i in picks]
    pad = 6
    out = Image.new("RGB", (tiles[0].width + 2 * pad, len(tiles) * (tiles[0].height + pad) + pad), (40, 40, 48))
    for k, t in enumerate(tiles):
        out.paste(t, (pad, pad + k * (t.height + pad)))
    out.save(path)


def review(module_name: str, out_dir: Path, every: float | None = None) -> None:
    """Render a scene and write a strip of its keyframes (or every N seconds)."""
    import importlib
    from canvas import FPS
    m = importlib.import_module(f"scenes.{module_name}")
    frames = m.render()
    if every:
        picks = [int(i * every * FPS) for i in range(int(len(frames) / (every * FPS)) + 1)]
    else:
        picks = [int(s * FPS) for s, _ in m.KEYFRAMES]
    p = out_dir / f"review_{module_name}.png"
    strip(frames, picks, p)
    print(f"{module_name}: {len(frames)} frames -> {p}")
