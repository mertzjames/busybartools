"""The build pipeline shared by scene-based apps (render kit).

An app's renderer/build.py renders its scene modules and calls these helpers to produce:

  app/src/animations/<scene>.anim   tone-mapped, encoded, and verified by decoding again
  app/shared/generated/*.ts         constants for the on-device app (playlist, fonts, layouts)
  mockup/index.html                 a self-contained simulator built from mockup/template.html
  previews/<scene>.gif              LED-style GIF previews (optional)

Scene module contract: NAME (file-safe id), TITLE, SECONDS, KEYFRAMES [(seconds, caption)], render() -> frames,
where frames are 72x16 RGBA Pillow images at canvas.FPS. Everything is deterministic, so CI can re-render the
same bytes.
"""

from __future__ import annotations

import base64
import io
import json
import time
from pathlib import Path

from PIL import Image

from .anim import image_to_bgra, read_anim, write_anim
from .canvas import FPS, H, W, flatten
from .preview import led


# --- tone curve ----------------------------------------------------------------------------------------------

def tone_lut(gamma: float) -> list[int]:
    """v' = 255 * (v/255) ** gamma. 1.0 = unchanged; lower = brighter darks and midtones (black stays black)."""
    return [min(255, int(255 * (v / 255) ** gamma + 0.5)) for v in range(256)]


def apply_tone(img: Image.Image, lut: list[int]) -> Image.Image:
    """Tone-map a frame. RGBA (or other) frames are flattened to RGB first; frames are always opaque on the bar."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img.point(lut * 3)


def tone_rgb(color, lut: list[int]) -> list[int]:
    return [lut[v] for v in color]


# --- encoding ------------------------------------------------------------------------------------------------

def encode_anim(path: Path, frames, lut: list[int], fps: int = FPS, name: str = "") -> dict:
    """Flatten, tone-map, write the .anim, then decode it and assert a pixel-perfect round trip.

    Returns {"flat": [RGB frames as written], "bytes": file size}.
    """
    flat = [apply_tone(flatten(f), lut) for f in frames]
    bgra = [image_to_bgra(f) for f in flat]
    size = write_anim(path, bgra, W, H, fps)
    back = read_anim(path)
    assert back["width"] == W and back["height"] == H and back["fps"] == fps
    assert len(back["frames"]) == len(bgra)
    for i, (a, b) in enumerate(zip(bgra, back["frames"])):
        assert a == b, f"{name or path}: frame {i} round-trip mismatch"
    return {"flat": flat, "bytes": size}


def sheet_b64(flat) -> str:
    """All frames stacked vertically into one PNG (base64, for the mockup's data URIs)."""
    sheet = Image.new("RGB", (W, H * len(flat)))
    for i, f in enumerate(flat):
        sheet.paste(f, (0, i * H))
    buf = io.BytesIO()
    sheet.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def gif(path: Path, flat, fps: int = FPS) -> None:
    frames = [led(f, cell=5, gap=1) for f in flat]
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0, optimize=True)


def build_scenes(modules, anim_dir: Path, lut: list[int], previews_dir: Path | None = None,
                 only: set[str] | None = None, keep=()) -> list[dict]:
    """Render, encode and verify each scene module; returns one metadata dict per scene, in order.

    only:  render just these NAMEs (modules in `keep` are always rendered).
    Each dict: name, title, ms, frames, keyframes [{s, caption}], sheet (base64 PNG), bytes.
    """
    anim_dir.mkdir(parents=True, exist_ok=True)
    if previews_dir:
        previews_dir.mkdir(parents=True, exist_ok=True)
    metas, total = [], 0
    for m in modules:
        if only and m.NAME not in only and m not in keep:
            continue
        t0 = time.time()
        frames = m.render()
        assert len(frames) == round(m.SECONDS * FPS), f"{m.NAME}: {len(frames)} frames, expected {m.SECONDS * FPS}"
        out = encode_anim(anim_dir / f"{m.NAME}.anim", frames, lut, name=m.NAME)
        total += out["bytes"]
        metas.append({
            "name": m.NAME, "title": m.TITLE, "ms": int(m.SECONDS * 1000), "frames": len(frames),
            "keyframes": [{"s": s, "caption": c} for s, c in m.KEYFRAMES], "sheet": sheet_b64(out["flat"]),
            "bytes": out["bytes"],
        })
        if previews_dir:
            gif(previews_dir / f"{m.NAME}.gif", out["flat"])
        print(f"  {m.NAME:14s} {len(frames):4d} frames  {out['bytes'] / 1024:7.1f} KiB  ({time.time() - t0:.1f}s)")
    print(f"  total .anim size {total / 1024:.1f} KiB; round-trip OK")
    return metas


# --- generated files ------------------------------------------------------------------------------------------

def ts_module(consts, generator: str = "renderer/build.py") -> str:
    """TypeScript source exporting constants.

    consts: [(name, value, ts_type_or_None, indent_or_None, as_const)], emitted in order, separated by blank lines.
    """
    parts = []
    for name, value, ts_type, indent, as_const in consts:
        typ = f": {ts_type}" if ts_type else ""
        tail = " as const" if as_const else ""
        parts.append(f"export const {name}{typ} = {json.dumps(value, indent=indent)}{tail};\n")
    return f"// GENERATED by {generator} — do not edit by hand.\n/* eslint-disable */\n" + "\n".join(parts)


FONT_TS_TYPE = "Record<string, { height: number; gap: number; glyphs: Record<string, string[]> }>"


def fill_template(template: Path, out: Path, data: dict) -> None:
    """Replace the `/*__SHOW_DATA__*/null` placeholder in an HTML template with compact JSON."""
    html = template.read_text().replace("/*__SHOW_DATA__*/null", json.dumps(data, separators=(",", ":")))
    out.write_text(html)


def save_icon(path: Path, palette: dict[str, str], grid: str) -> None:
    """App menu icon from a text grid (front: 8x8 color; back: 11x11 single grey #888888)."""
    from .sprite import Sprite
    path.parent.mkdir(parents=True, exist_ok=True)
    Sprite(path.stem, palette, grid).img().save(path)
