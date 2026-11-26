#!/usr/bin/env python3
"""Live-text parity test: the on-bar app, the mockup and the renderer must draw identical card pixels.

Runs the app's real TypeScript (the kit's xpmtext.ts, app/shared/memorial.ts and the generated show.ts)
under Node 24, decodes the XPM bitmaps it produces for every card text style, and compares them pixel-for-pixel
with the shared busybar.font drawing the same text with this app's tone-mapped LAYOUT (build.draw_live, which the
review strips use). Also checks that the app's on-the-day cards match the renderer's review copy (DAY_TEXT plus
HALF_TEXT before noon and FULL_TEXT from noon), that the widest date fits, and that the generated scenes and
backdrops match the renderer and exist on disk. See docs/DECISIONS.md D7 and D8.

    python3 tests/text_parity.py
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

from busybar.canvas import new  # noqa: E402
from busybar.font import text_width  # noqa: E402

import build  # noqa: E402
from busybar.font import FONTS  # noqa: E402
from scenes import ALL, CLOCK_BG, COUNT_BG, services  # noqa: E402
from scenes.text import DAY_TEXT, FULL_TEXT, HALF_TEXT  # noqa: E402

TS = """
import { textBitmap, type Font, type TextSpec } from "%(repo)s/lib/ts/busybar/xpmtext.ts";
import { parseLocal } from "%(repo)s/lib/ts/busybar/walltime.ts";
import { MODES, dayCards, cardPages } from "%(shared)s/memorial.ts";
import { FONTS, LAYOUT, SHOW } from "%(shared)s/generated/show.ts";
const L = LAYOUT as unknown as Record<string, TextSpec>;
const lines: [string, string][] = [];
for (const iso of ["2026-11-26T18:05:00-05:00", "2027-05-31T11:59:00-04:00", "2027-05-31T12:00:00-04:00",
                   "2027-06-01T23:59:00-04:00", "2027-05-30T07:41:00-04:00"]) {
  const t = parseLocal(iso)!;
  for (const mode of MODES)
    for (const name of ["clock", "count", "day0", "day1", "day2"])
      for (const page of cardPages(name, t, mode)) for (const l of page.lines) lines.push([l.text, l.style]);
}
lines.push(["365 DAYS", "head"], ["WED 28 SEP", "date"], ["00:00", "time"]);
const bitmaps = lines.map(([txt, style]) => {
  const b = textBitmap(txt, FONTS[L[style].font] as Font, L[style]);
  return { txt, style, data: b.data, x: b.x, y: b.y };
});
console.log(JSON.stringify({
  bitmaps,
  morning: dayCards(parseLocal("2027-05-31T11:59:00-04:00")!).map((card) => card.map((p) => p.lines.map((l) => [l.text, l.style]))),
  afternoon: dayCards(parseLocal("2027-05-31T12:00:00-04:00")!).map((card) => card.map((p) => p.lines.map((l) => [l.text, l.style]))),
  scenes: SHOW.scenes.map((s) => [s.name, s.ms, s.path]),
  backdrops: SHOW.backdrops,
}));
"""


def run_app_code() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "parity.mts"
        script.write_text(TS % {"shared": (APP_DIR / "app" / "shared").as_posix(), "repo": REPO.as_posix()})
        out = subprocess.run(build.node_cmd() + ["--experimental-strip-types", "--no-warnings", str(script)],
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


def renderer_pixels(txt: str, style: str):
    img = new()
    build.draw_live(img, txt, style)
    return {(x, y): img.getpixel((x, y))[:3] for y in range(16) for x in range(72)
            if img.getpixel((x, y))[:3] != (0, 0, 0)}


def widest_date() -> tuple[str, int]:
    days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    font = build.layout()["date"]["font"]
    best = max((f"{d} {n} {m}" for d in days for n in range(1, 32) for m in months),
               key=lambda s: text_width(s, font))
    return best, text_width(best, font)


def main() -> int:
    res = run_app_code()
    failures = 0
    seen = set()
    for b in res["bitmaps"]:
        key = (b["txt"], b["style"])
        if key in seen:
            continue
        seen.add(key)
        ok = xpm_pixels(b["data"], b["x"], b["y"]) == renderer_pixels(b["txt"], b["style"])
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {b['style']:5} {b['txt']!r}")
    date, width = widest_date()
    expected = [[m.NAME, int(m.SECONDS * 1000), f"animations/{m.NAME}.anim"] for m in ALL]

    def day_text(flag):
        cards = [list(card) for card in DAY_TEXT]
        cards[-1] = cards[-1] + [flag]
        return [[[list(line) for line in page] for page in card] for card in cards]
    paths = [p for _, _, p in res["scenes"]] + list(res["backdrops"].values())
    checks = [
        (res["morning"] == day_text(HALF_TEXT), "app day cards before noon match the renderer's DAY_TEXT + HALF_TEXT"),
        (res["afternoon"] == day_text(FULL_TEXT), "app day cards from noon match the renderer's DAY_TEXT + FULL_TEXT"),
        (width + 1 <= 72, f"widest date {date!r} fits ({width} px + shadow)"),
        (res["scenes"] == expected, "generated playlist matches renderer"),
        (sorted(res["backdrops"]) == sorted([CLOCK_BG.NAME, COUNT_BG.NAME]), "both card backdrops are exported"),
        (all((APP_DIR / "app" / "src" / p).is_file() for p in paths), "every .anim exists"),
        (all(text_width(c, "big") + 1 <= 72 and all(ch in FONTS["big"][0] for ch in c)
             for c in services.CAPTIONS), "every service name fits in the big font with its shadow"),
    ]
    for ok, name in checks:
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print("text parity: " + ("PASS" if not failures else f"{failures} FAILURE(S)"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
