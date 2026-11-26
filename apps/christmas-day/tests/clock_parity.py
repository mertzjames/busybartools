#!/usr/bin/env python3
"""Live-text parity test: the on-bar app, the mockup and the renderer must draw identical clock pixels.

Runs the app's real TypeScript (app/shared/clocktext.ts + generated show.ts) under Node 24, decodes the XPM
bitmaps it produces, and compares them pixel-for-pixel with the shared busybar.font drawing the same text with
this app's tone-mapped clock LAYOUT. Also checks the bar-timestamp parser, the minute rollover, that every date
the card can show fits the display, and that the generated playlist matches the renderer's. See
docs/DECISIONS.md D7 and D8.

    python3 tests/clock_parity.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR / "renderer"))
sys.path.insert(0, str(APP_DIR.parents[1] / "lib" / "python"))

from busybar.canvas import new  # noqa: E402
from busybar.font import draw_text, text_width  # noqa: E402

import build  # noqa: E402  (for the exported, tone-mapped clock layout)
from scenes import PLAYLIST  # noqa: E402

SAMPLES = [("18:05", "time"), ("00:00", "time"), ("23:59", "time"), ("07:41", "time"),
           ("FRI 25 DEC", "date"), ("THU 24 DEC", "date"), ("WED 30 DEC", "date"), ("SAT 1 JAN", "date")]

TS = """
import { textBitmap, parseWallClock, nextMinute, type Font } from "%(shared)s/clocktext.ts";
import { FONTS, SHOW } from "%(shared)s/generated/show.ts";
const samples: [string, "time" | "date"][] = %(samples)s;
const bitmaps = samples.map(([txt, kind]) => {
  const spec = SHOW.clock[kind] as any;
  const b = textBitmap(txt, FONTS[spec.font] as Font, spec);
  return { txt, kind, data: b.data, x: b.x, y: b.y };
});
console.log(JSON.stringify({
  bitmaps,
  scenes: SHOW.scenes.map((s) => [s.name, s.ms, s.path]),
  clockPath: SHOW.clock.path,
  parse1: parseWallClock("2026-12-25T18:05:42+00:00"),
  parse2: parseWallClock("2026-12-24T23:59:59-12:00"),
  roll1: nextMinute("23:59"), roll2: nextMinute("09:09"),
}));
"""


def run_app_code() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "parity.mts"
        script.write_text(TS % {"shared": (APP_DIR / "app" / "shared").as_posix(), "samples": json.dumps(SAMPLES)})
        local = subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.startswith("v24.")
        node = ["node"] if local else ["npx", "-y", "-p", "node@24", "node"]
        out = subprocess.run(node + ["--experimental-strip-types", "--no-warnings", str(script)],
                             capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def xpm_pixels(data: str, x0: int, y0: int):
    lines = data.split("\n")
    assert lines[0] == "! XPM2", "missing XPM2 signature"
    w, h, n, cpp = map(int, lines[1].split())
    assert n <= 32 and cpp == 1, "firmware limits: <=32 colors"
    pal = {}
    for ln in lines[2:2 + n]:
        ch, _, val = ln.split(" ")
        pal[ch] = None if val == "none" else tuple(int(val[i:i + 2], 16) for i in (1, 3, 5))
    rows = lines[2 + n:2 + n + h]
    assert len(rows) == h and all(len(r) == w for r in rows)
    assert x0 >= 0 and y0 >= 0 and x0 + w <= 72 and y0 + h <= 16, "bitmap must fit the 72x16 display"
    return {(x0 + x, y0 + y): pal[c] for y, r in enumerate(rows) for x, c in enumerate(r) if pal[c]}


def renderer_pixels(txt: str, spec: dict):
    img = new()
    draw_text(img, txt, (72 - text_width(txt, spec["font"])) // 2, spec["y"], None, font=spec["font"],
              gradient=(tuple(spec["top"]), tuple(spec["bottom"])), shadow=tuple(spec["shadow"]))
    return {(x, y): img.getpixel((x, y))[:3] for y in range(16) for x in range(72)
            if img.getpixel((x, y))[:3] != (0, 0, 0)}


def widest_date() -> tuple[str, int]:
    days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    font = build.clock_layout()["date"]["font"]
    best = max((f"{d} {n} {m}" for d in days for n in range(1, 32) for m in months),
               key=lambda s: text_width(s, font))
    return best, text_width(best, font)


def main() -> int:
    res = run_app_code()
    layout = build.clock_layout()
    failures = 0
    for b in res["bitmaps"]:
        app_px = xpm_pixels(b["data"], b["x"], b["y"])
        ref_px = renderer_pixels(b["txt"], layout[b["kind"]])
        ok = app_px == ref_px
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {b['txt']!r:14} {len(app_px)} px")
    date, width = widest_date()
    expected = [[m.NAME, int(m.SECONDS * 1000), f"animations/{m.NAME}.anim"] for m in PLAYLIST]
    anims = [APP_DIR / "app" / "src" / p for _, _, p in res["scenes"]] + [APP_DIR / "app" / "src" / res["clockPath"]]
    checks = [
        (res["parse1"] == {"hhmm": "18:05", "date": "FRI 25 DEC", "msToNextMinute": 18000}, "parse local timestamp"),
        (res["parse2"]["date"] == "THU 24 DEC" and res["parse2"]["hhmm"] == "23:59", "wall clock ignores offset"),
        (res["roll1"] == "00:00" and res["roll2"] == "09:10", "minute rollover"),
        (width + 1 <= 72, f"widest date {date!r} fits ({width} px + shadow)"),
        (res["scenes"] == expected, "generated playlist matches renderer"),
        (all(p.is_file() for p in anims), "every playlist .anim exists"),
    ]
    for ok, name in checks:
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print("clock parity: " + ("PASS" if not failures else f"{failures} FAILURE(S)"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
