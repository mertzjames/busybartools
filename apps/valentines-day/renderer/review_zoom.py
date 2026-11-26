"""Zoomed LED view of one region of a scene at chosen times (for checking small sprites).

    python3 renderer/review_zoom.py <scene> <out.png> <x0> <x1> <t1,t2,...>
"""
import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "lib" / "python"))

from busybar.canvas import FPS  # noqa: E402
from busybar.preview import strip  # noqa: E402

import build  # noqa: E402

name, out, x0, x1, ts = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
m = importlib.import_module(f"scenes.{name}")
frames = [build.tone(f.convert("RGB")).crop((x0, 0, x1, 16)) for f in m.render()]
strip(frames, [min(len(frames) - 1, int(float(t) * FPS)) for t in ts.split(",")], out, cell=18)
print(out)
