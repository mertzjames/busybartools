#!/usr/bin/env python3
"""Live-text parity: the app's xpmbitmaps must match the renderer's busybar.font.draw_text pixel for pixel.

Runs the app's real TypeScript (app/shared/screens.ts + generated show.ts) under Node 24 for a set of live screens
(countdown cards, the final minute with its bar, the final-ten digits in the app-local "huge" font, the celebration,
the odometer mid-roll with clipping), decodes each composed XPM, and compares it with the same layers drawn by the
Python kit. Also checks the exported layout is the tone-mapped one build.py produces, and that each font the app
uses matches font.export_json(). See docs/DECISIONS.md D9.

    python3 tests/live_parity.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
REPO = APP_DIR.parents[1]
sys.path.insert(0, str(APP_DIR / "renderer"))
sys.path.insert(0, str(REPO / "lib" / "python"))

from busybar.canvas import new, put  # noqa: E402
from busybar.font import draw_text, export_json  # noqa: E402

import build  # noqa: E402  (registers the huge font; tone-mapped layout)
import live  # noqa: E402

SAMPLES = [  # (kind, bar time, startedAt)
    ("card", "2026-12-31T21:45:12", 0), ("card", "2026-12-31T00:00:00", 0), ("card", "2026-12-31T23:42:05", 0),
    ("card", "2027-01-01T00:42:00", 0), ("card", "2026-11-25T20:15:00", 0), ("card", "2027-01-01T07:00:00", 0),
    ("final", "2026-12-31T23:58:52", 0), ("final", "2026-12-31T23:59:15", 0), ("final", "2026-12-31T23:59:41", 0),
    ("final", "2026-12-31T23:59:49", 0),
] + [("final10", f"2026-12-31T23:59:{50 + k}", 0) for k in range(10)] + [
    ("celebrate", "2027-01-01T00:00:00", 0), ("celebrate", "2027-01-01T00:00:04", 0),
    ("celebrate", "2027-01-01T00:00:08", 0), ("celebrate", "2100-01-01T00:00:30", 30),
]

TS = """
import { screenAt, composeBitmap, odometerLayers } from "%(shared)s/screens.ts";
import { FONTS, LAYOUT } from "%(shared)s/generated/show.ts";
import { parseLocal } from "%(lib)s/walltime.ts";
const samples: [string, string, number][] = %(samples)s;
const out: any[] = [];
for (const [kind, iso, startedAt] of samples) {
  const layers = screenAt(kind as any, parseLocal(iso)!, startedAt, LAYOUT as any, FONTS as any).layers;
  out.push({ label: kind + " " + iso, layers, bmp: composeBitmap(layers, FONTS as any) });
}
for (const [a, b, p] of [[2026, 2027, 0], [2026, 2027, 0.5], [2029, 2030, 0.5], [2099, 2100, 0.25], [2026, 2027, 1]]) {
  const layers = odometerLayers(a, b, p, LAYOUT as any, FONTS as any);
  out.push({ label: `odometer ${a}->${b} @${p}`, layers, bmp: composeBitmap(layers, FONTS as any) });
}
console.log(JSON.stringify({ out, layout: LAYOUT, fonts: FONTS }));
"""


def node_cmd() -> list[str]:
    try:
        local = subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.startswith("v24.")
    except FileNotFoundError:
        local = False
    return ["node"] if local else ["npx", "-y", "-p", "node@24", "node"]


def run_app_code() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "parity.mts"
        script.write_text(TS % {"shared": (APP_DIR / "app" / "shared").as_posix(),
                                "lib": (REPO / "lib" / "ts" / "busybar").as_posix(), "samples": json.dumps(SAMPLES)})
        out = subprocess.run(node_cmd() + ["--experimental-strip-types", "--no-warnings", str(script)],
                             capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def xpm_pixels(bmp) -> dict:
    if bmp is None:
        return {}
    lines = bmp["data"].split("\n")
    assert lines[0] == "! XPM2", "missing XPM2 signature"
    w, h, n, cpp = map(int, lines[1].split())
    assert n <= 32 and cpp == 1, "firmware limits: <= 32 colors, 1 char per pixel"
    pal = {}
    for ln in lines[2:2 + n]:
        ch, _, val = ln.split(" ")
        pal[ch] = None if val == "none" else tuple(int(val[i:i + 2], 16) for i in (1, 3, 5))
    rows = lines[2 + n:2 + n + h]
    x0, y0 = bmp["x"], bmp["y"]
    assert len(rows) == h and all(len(r) == w for r in rows)
    assert x0 >= 0 and y0 >= 0 and x0 + w <= 72 and y0 + h <= 16, "bitmap must fit the 72x16 display"
    return {(x0 + x, y0 + y): pal[c] for y, r in enumerate(rows) for x, c in enumerate(r) if pal[c]}


def renderer_pixels(layers) -> dict:
    """The same layers drawn by the Python kit: draw_text on a scratch canvas, then pasted through the clip."""
    marker = (1, 2, 3)  # an "unset" color no layer uses
    img = new(marker)
    for ly in layers:
        if ly["kind"] == "rect":
            for y in range(ly["y"], ly["y"] + ly["h"]):
                for x in range(ly["x"], ly["x"] + ly["w"]):
                    put(img, x, y, ly["color"])
            continue
        s = ly["spec"]
        scratch = new(marker)
        draw_text(scratch, ly["text"], ly["x"], ly["y"], None, font=s["font"],
                  gradient=(tuple(s["top"]), tuple(s["bottom"])), shadow=tuple(s["shadow"]))
        x0, y0, x1, y1 = ly.get("clip") or (0, 0, 72, 16)
        for y in range(max(0, y0), min(16, y1)):
            for x in range(max(0, x0), min(72, x1)):
                c = scratch.getpixel((x, y))[:3]
                if c != marker:
                    img.putpixel((x, y), c + (255,))
    return {(x, y): img.getpixel((x, y))[:3] for y in range(16) for x in range(72)
            if img.getpixel((x, y))[:3] != marker}


def main() -> int:
    res = run_app_code()
    failures = 0
    for s in res["out"]:
        app_px = xpm_pixels(s["bmp"])
        ref_px = renderer_pixels(s["layers"])
        ok = app_px == ref_px and len(app_px) > 0
        failures += not ok
        texts = " ".join(ly.get("text", "[bar]") for ly in s["layers"])
        print(f"  {'ok  ' if ok else 'FAIL'} {s['label']:34} {texts!r:28} {len(app_px)} px")
    checks = [
        (res["layout"] == build.layout(), "generated LAYOUT is the tone-mapped renderer layout"),
        (res["fonts"] == export_json(live.FONTS_USED), "generated FONTS match the renderer fonts (incl. huge)"),
        ("huge" in res["fonts"] and res["fonts"]["huge"]["height"] == 15, "app-local huge font exported"),
    ]
    for ok, name in checks:
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print("live parity: " + ("PASS" if not failures else f"{failures} FAILURE(S)"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
