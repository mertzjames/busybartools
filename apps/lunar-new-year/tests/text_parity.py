#!/usr/bin/env python3
"""Live-text parity: the bar app and the renderer must draw identical card text pixels.

Runs the app's real TypeScript (app/shared/kit.ts textBitmap + the generated show.ts) under Node 24, decodes the XPM
bitmaps it produces, and compares them pixel-for-pixel with busybar.font.draw_text drawing the same text in the same
tone-mapped style. Covers every text style the app uses, the widest texts, and the widest date the clock card can
show. See docs/DECISIONS.md D7.

    python3 tests/text_parity.py
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

import build  # noqa: E402  (for the exported, tone-mapped text styles)

ANIMALS = ["RAT", "OX", "TIGER", "RABBIT", "DRAGON", "SNAKE", "HORSE", "GOAT", "MONKEY", "ROOSTER", "DOG", "PIG"]
SAMPLES = [
    ("18:05", "time"), ("00:00", "time"), ("23:59", "time"),
    ("SAT 6 FEB", "date"), ("WED 28 SEP", "date"), ("THU 1 JAN", "date"),
    ("72 DAYS", "head"), ("1 DAY", "head"), ("339 DAYS", "head"),
    ("TO LUNAR NEW YEAR", "sub"), ("YEAR OF THE", "small"),
    ("HAPPY", "top"), ("NEW YEAR", "bot"), ("GONG XI", "top"), ("FA CAI", "bot"), ("LANTERN", "top"),
    ("FESTIVAL", "bot"), ("GUNG HEI", "top"), ("FAT CHOI", "bot"), ("CHUC MUNG", "top"), ("NAM MOI", "bot"),
    ("SAEHAE BOK", "head"), ("MANI BADEUSEYO", "sub"),
] + [(a, "name") for a in ANIMALS]

TS = """
import { textBitmap, type Font } from "%(shared)s/kit.ts";
import { FONTS, SHOW } from "%(shared)s/generated/show.ts";
const samples: [string, string][] = %(samples)s;
console.log(JSON.stringify(samples.map(([txt, style]) => {
  const spec = (SHOW.styles as any)[style];
  const b = textBitmap(txt, FONTS[spec.font] as Font, spec);
  return { txt, style, data: b.data, x: b.x, y: b.y };
})));
"""


def run_app_code() -> list:
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


def widest_date(font: str) -> tuple[str, int]:
    days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    best = max((f"{d} {n} {m}" for d in days for n in range(1, 32) for m in months), key=lambda s: text_width(s, font))
    return best, text_width(best, font)


def main() -> int:
    styles = build.text_styles()
    failures = 0
    for b in run_app_code():
        app_px = xpm_pixels(b["data"], b["x"], b["y"])
        ref_px = renderer_pixels(b["txt"], styles[b["style"]])
        ok = app_px == ref_px and len(app_px) > 0
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {b['style']:5} {b['txt']!r:20} {len(app_px)} px")
    date, width = widest_date(styles["date"]["font"])
    ok = width + 1 <= 72
    failures += not ok
    print(f"  {'ok  ' if ok else 'FAIL'} widest date {date!r} fits ({width} px + shadow)")
    print("text parity: " + ("PASS" if not failures else f"{failures} FAILURE(S)"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
