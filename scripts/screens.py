#!/usr/bin/env python3
"""Capture what the BUSY Bar front display is showing, as LED-style PNGs.

    python3 scripts/screens.py --count 20 --every 2 --out screens/

GET /api/screen?display=0 returns the 72x16 front frame (base64 of BGR bytes, or raw bytes).
Writes one strip image of all captures plus the individual frames. Config: BUSYBAR_ADDR / BUSYBAR_TOKEN
(env or .env), same as scripts/deploy.sh. Keep --every >= 1 s: every capture is a request the bar's web
server has to handle.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "renderer"))

from PIL import Image  # noqa: E402

from preview import led, strip  # noqa: E402

W, H = 72, 16


def load_env() -> None:
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def grab(addr: str, token: str) -> Image.Image:
    req = urllib.request.Request(f"http://{addr}/api/screen?display=0")
    if token:
        req.add_header("X-API-Token", token)
    raw = urllib.request.urlopen(req, timeout=5).read()
    if len(raw) != W * H * 3:
        try:
            raw = base64.b64decode(raw.strip(), validate=True)
        except binascii.Error as e:
            raise SystemExit(f"unexpected /api/screen payload ({len(raw)} bytes): {e}")
    if len(raw) != W * H * 3:
        raise SystemExit(f"unexpected frame size {len(raw)} bytes (want {W * H * 3})")
    rgb = bytearray(len(raw))
    rgb[0::3], rgb[1::3], rgb[2::3] = raw[2::3], raw[1::3], raw[0::3]  # BGR -> RGB
    return Image.frombytes("RGB", (W, H), bytes(rgb))


def main() -> None:
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--every", type=float, default=2.0)
    ap.add_argument("--out", default=str(ROOT / "screens"))
    args = ap.parse_args()
    addr = os.environ.get("BUSYBAR_ADDR", "10.0.4.20")
    token = os.environ.get("BUSYBAR_TOKEN", "")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    frames = []
    t0 = time.time()
    for i in range(args.count):
        target = t0 + i * args.every
        time.sleep(max(0.0, target - time.time()))
        img = grab(addr, token)
        frames.append(img)
        led(img, cell=10).save(out / f"screen_{i:03d}.png")
        print(f"{time.time() - t0:6.1f}s  captured screen_{i:03d}.png", flush=True)
    strip(frames, list(range(len(frames))), out / "strip.png")
    print(f"wrote {out / 'strip.png'}")


if __name__ == "__main__":
    main()
