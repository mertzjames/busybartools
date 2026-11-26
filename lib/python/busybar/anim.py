"""Writes BUSY Bar .anim files ("bicycle1" format), plus a reader for round-trip checks.

Adapted from devrsw/busybar-skill templates/make_anim.py
(https://github.com/devrsw/busybar-skill), MIT License, Copyright (c) 2026 devrsw.
The reader (`read_anim`) and the Pillow helper (`image_to_bgra`) are additions in this repo.

The format is defined in the firmware repo busy-app/busybar-firmware:
lib/anim_file/anim_file_format.h. Encoding used here: BGRA8888 raw pixels, the
first frame of each section whole, and later frames as only the changed pixels
with a per-pixel bitmap mask (MSB first). See apps/wizard-thanksgiving/docs/DECISIONS.md D4
and docs/DEVELOPMENT.md#making-animations-anim.
"""

from __future__ import annotations

import struct
from pathlib import Path

MAGIC = b"bicycle1"
COLOR_BGRA8888 = 2  # "argb8888" in seq2anim.py; bytes per pixel are B, G, R, A
# magic, flags, width, height, color mode, max mask len, max pixels len, fps, pad,
# sections chunk len, frames chunk len, section count, frame count
HEADER = "<8s BBBB HHBB II II"

MASK_FULLY_BLACK = 0  # no pixels present: same as previous frame
MASK_FULLY_WHITE = 1  # every pixel present
MASK_BITMAP = 4


def rgba_to_bgra(pixels: bytes) -> bytes:
    """RGBA bytes -> BGRA bytes. Fully transparent pixels become all zero."""
    out = bytearray()
    for i in range(0, len(pixels), 4):
        r, g, b, a = pixels[i:i + 4]
        out.extend((b, g, r, a) if a else (0, 0, 0, 0))
    return bytes(out)


def image_to_bgra(img) -> bytes:
    """Pillow image -> BGRA8888 bytes (forced opaque RGB frames stay opaque)."""
    return rgba_to_bgra(img.convert("RGBA").tobytes())


def frame_bytes(pixels: bytes, previous: bytes | None):
    """One frame: everything when `previous` is None (a keyframe), else only changed pixels."""
    if previous is None:
        mask_enc, mask_bits, mask_data, changed = MASK_FULLY_WHITE, 0, b"", pixels
    else:
        flags = [pixels[i:i + 4] != previous[i:i + 4] for i in range(0, len(pixels), 4)]
        changed = b"".join(pixels[i * 4:i * 4 + 4] for i, f in enumerate(flags) if f)
        if not any(flags):
            mask_enc, mask_bits, mask_data = MASK_FULLY_BLACK, 0, b""
        elif all(flags):
            mask_enc, mask_bits, mask_data = MASK_FULLY_WHITE, 0, b""
        else:
            bitmap = bytearray()
            for i in range(0, len(flags), 8):
                byte = 0
                for j, f in enumerate(flags[i:i + 8]):
                    byte |= (128 >> j) if f else 0
                bitmap.append(byte)
            mask_enc, mask_bits, mask_data = MASK_BITMAP, len(flags), bytes(bitmap)
    pixel_enc = 0  # Raw
    header = struct.pack("<BHH", pixel_enc | (mask_enc << 4), mask_bits, len(changed))
    return header + mask_data + changed, mask_bits, len(changed)


def write_anim(path, frames: list[bytes], width: int, height: int, fps: int, sections=None) -> int:
    """Writes an .anim and returns its size in bytes.

    frames: list of BGRA8888 byte strings, width*height*4 each.
    sections: list of (name, first_frame, last_frame); defaults to one "default" section.
    """
    assert 0 < width <= 255 and 0 < height <= 255, "width/height are stored in one byte each"
    assert frames, "need at least one frame"
    assert all(len(f) == width * height * 4 for f in frames), "every frame must be width*height*4 bytes"
    sections = sections or [("default", 0, len(frames) - 1)]
    starts = {start for _, start, _ in sections}

    encoded, offsets, max_mask, max_pixels, previous = [], [], 0, 0, None
    for i, pixels in enumerate(frames):
        data, mask_bits, pixel_len = frame_bytes(pixels, None if i in starts else previous)
        encoded.append(data)
        max_mask, max_pixels, previous = max(max_mask, mask_bits), max(max_pixels, pixel_len), pixels

    section_chunk_len = sum(12 + len(name.encode()) + 1 for name, _, _ in sections)
    offset = struct.calcsize(HEADER) + section_chunk_len
    for data in encoded:
        offsets.append(offset)
        offset += len(data)

    section_chunk = b"".join(
        struct.pack("<III", start, end, offsets[start]) + name.encode() + b"\0" for name, start, end in sections
    )
    frames_chunk = b"".join(encoded)
    header = struct.pack(
        HEADER, MAGIC,
        0, width, height, COLOR_BGRA8888,
        max_mask, max_pixels, fps, 0,
        len(section_chunk), len(frames_chunk), len(sections), len(frames),
    )
    blob = header + section_chunk + frames_chunk
    Path(path).write_bytes(blob)
    assert len(section_chunk) == section_chunk_len
    return len(blob)


def read_anim(path):
    """Decode an .anim written by write_anim (raw pixel encoding only).

    Returns dict(width, height, fps, sections, frames=[BGRA bytes...]).
    """
    blob = Path(path).read_bytes()
    hsize = struct.calcsize(HEADER)
    (magic, _flags, width, height, color_mode, _max_mask, _max_pixels, fps, _pad,
     sec_len, frames_len, sec_count, frame_count) = struct.unpack(HEADER, blob[:hsize])
    assert magic == MAGIC, magic
    assert color_mode == COLOR_BGRA8888
    pos = hsize
    sections = []
    for _ in range(sec_count):
        start, end, off = struct.unpack("<III", blob[pos:pos + 12])
        pos += 12
        nul = blob.index(b"\0", pos)
        sections.append((blob[pos:nul].decode(), start, end, off))
        pos = nul + 1
    assert pos == hsize + sec_len
    npix = width * height
    frames, prev = [], None
    for _ in range(frame_count):
        enc, mask_bits, pix_len = struct.unpack("<BHH", blob[pos:pos + 5])
        pos += 5
        pixel_enc, mask_enc = enc & 0xF, enc >> 4
        assert pixel_enc == 0, "only raw pixels supported"
        if mask_enc == MASK_FULLY_BLACK:
            frames.append(prev)
            pos += pix_len
            continue
        if mask_enc == MASK_FULLY_WHITE:
            cur = blob[pos:pos + pix_len]
            assert len(cur) == npix * 4
            pos += pix_len
        else:
            assert mask_enc == MASK_BITMAP and mask_bits == npix
            nbytes = (mask_bits + 7) // 8
            mask = blob[pos:pos + nbytes]
            pos += nbytes
            data = blob[pos:pos + pix_len]
            pos += pix_len
            out = bytearray(prev)
            k = 0
            for i in range(npix):
                if mask[i // 8] & (128 >> (i % 8)):
                    out[i * 4:i * 4 + 4] = data[k:k + 4]
                    k += 4
            assert k == len(data)
            cur = bytes(out)
        frames.append(cur)
        prev = cur
    assert pos == len(blob), (pos, len(blob))
    assert pos - hsize - sec_len == frames_len
    return {"width": width, "height": height, "fps": fps, "sections": sections, "frames": frames}
