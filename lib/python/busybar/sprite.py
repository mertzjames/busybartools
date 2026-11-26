"""Text-grid pixel art: a palette {char: "#RRGGBB"} and one or more frames; '.' is transparent.

Each frame is a multi-line string, one character per pixel:

    OWL = Sprite("owl", {"W": "#F4F4FF", "Y": "#FFC21A"}, ".WW.\\nWYYW")
    OWL.img(0)                             # RGBA Pillow image
    OWL.img(0, flip=True)                  # mirrored (sprites conventionally face right)
    OWL.recolor("owl_gold", W="#FFD84A")   # same pixels, palette entries swapped
"""

from __future__ import annotations

from PIL import Image, ImageOps

from .canvas import hexc


class Sprite:
    def __init__(self, name: str, palette: dict[str, str], *frames: str):
        self.name = name
        self.palette = {k: hexc(v) for k, v in palette.items()}
        self._src = (dict(palette), frames)
        self.frames = [self._rows(f) for f in frames]
        w = {len(r) for f in self.frames for r in f}
        assert len(w) == 1, f"{name}: ragged rows {w}"
        self.w = w.pop()
        hs = {len(f) for f in self.frames}
        assert len(hs) == 1, f"{name}: frames differ in height {hs}"
        self.h = hs.pop()
        for f in self.frames:
            for r in f:
                for ch in r:
                    assert ch == "." or ch in self.palette, f"{name}: unknown color {ch!r}"
        self._imgs = [self._render(f) for f in self.frames]

    @staticmethod
    def _rows(s: str) -> list[str]:
        return [ln.strip() for ln in s.strip("\n").splitlines() if ln.strip()]

    def _render(self, rows: list[str]) -> Image.Image:
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        px = img.load()
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch != ".":
                    px[x, y] = self.palette[ch] + (255,)
        return img

    def recolor(self, name: str, **colors: str) -> "Sprite":
        """Same pixels, some palette entries swapped (e.g. scarf colors)."""
        palette, frames = self._src
        return Sprite(name, {**palette, **colors}, *frames)

    def img(self, i: int = 0, flip: bool = False) -> Image.Image:
        im = self._imgs[i % len(self._imgs)]
        return ImageOps.mirror(im) if flip else im

    def __len__(self) -> int:
        return len(self.frames)
