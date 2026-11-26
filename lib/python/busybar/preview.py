"""LED-matrix style previews (round dots on black) of small RGB(A) frames.

Shared by every app in this repo: storyboards, GIF previews and device screenshots.
"""

from __future__ import annotations

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


def strip(frames, picks, path: Path, cell: int = 6) -> None:
    """Stack LED renders of the chosen frame indices vertically (for quick visual review)."""
    tiles = [led(frames[min(i, len(frames) - 1)], cell=cell) for i in picks]
    pad = 6
    out = Image.new("RGB", (tiles[0].width + 2 * pad, len(tiles) * (tiles[0].height + pad) + pad), (40, 40, 48))
    for k, t in enumerate(tiles):
        out.paste(t, (pad, pad + k * (t.height + pad)))
    out.save(path)
