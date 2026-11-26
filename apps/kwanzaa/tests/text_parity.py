#!/usr/bin/env python3
"""Live-text parity: the bar app and the renderer must draw identical text pixels and the same card texts.

Runs the app's real TypeScript (app/shared/kit.ts textBitmap, app/shared/kwanzaa.ts countPages, the generated
show.ts) under Node 24, decodes the XPM bitmaps it produces, and compares them pixel-for-pixel with busybar.font
drawing the same text in the same tone-mapped style (build.text_styles). Every card text the app can show is
covered, and the TS card pages must equal the renderer's count_pages (used by the review strips) for every day.
See docs/DECISIONS.md D6 and D11.

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
from scenes import CARD_BG, KINARA, PLAYLIST  # noqa: E402
from scenes.text import count_pages  # noqa: E402

DAYS = [(0, 1), (0, 30), (0, 358)] + [(d, 0) for d in range(1, 8)]
EXTRA = [("18:05", "time"), ("00:00", "time"), ("23:59", "time"), ("SAT 26 DEC", "date"), ("WED 30 DEC", "date"),
         ("FRI 1 JAN", "date")]

TS = """
import { textBitmap, type Font } from "%(shared)s/kit.ts";
import { countPages } from "%(shared)s/kwanzaa.ts";
import { FONTS, SHOW } from "%(shared)s/generated/show.ts";
const days: [number, number][] = %(days)s;
const extra: [string, string][] = %(extra)s;
const pages = days.map(([d, n]) => countPages(d, n).map((p) => [p.ms, p.lines.map((l) => [l.style, l.text])]));
const samples = new Map<string, [string, string]>();
for (const ps of pages) for (const [, lines] of ps) for (const [style, text] of lines as [string, string][]) samples.set(style + "|" + text, [text, style]);
for (const [text, style] of extra) samples.set(style + "|" + text, [text, style]);
const bitmaps = [...samples.values()].map(([txt, style]) => {
  const spec = (SHOW.styles as any)[style];
  const b = textBitmap(txt, FONTS[spec.font] as Font, spec);
  return { txt, style, data: b.data, x: b.x, y: b.y };
});
console.log(JSON.stringify({ pages, bitmaps, scenes: SHOW.scenes.map((s) => [s.name, s.ms, s.path]), card: SHOW.card.path }));
"""


def run_app_code() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "parity.mts"
        script.write_text(TS % {"shared": (APP_DIR / "app" / "shared").as_posix(), "days": json.dumps(DAYS),
                                "extra": json.dumps(EXTRA)})
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


def main() -> int:
    res = run_app_code()
    styles = build.text_styles()
    failures = 0
    for b in res["bitmaps"]:
        app_px = xpm_pixels(b["data"], b["x"], b["y"])
        ref_px = renderer_pixels(b["txt"], styles[b["style"]])
        ok = app_px == ref_px and len(app_px) > 0
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {b['style']:5} {b['txt']!r:22} {len(app_px)} px")
    ref_pages = [[[ms, [list(line) for line in lines]] for ms, lines in count_pages(d, n)] for d, n in DAYS]
    expected = [[m.NAME, int(m.SECONDS * 1000), f"animations/{m.NAME}.anim"] for m in KINARA + PLAYLIST]
    anims = [APP_DIR / "app" / "src" / p for _, _, p in res["scenes"]] + [APP_DIR / "app" / "src" / res["card"]]
    checks = [
        (res["pages"] == ref_pages, "card pages: app (kwanzaa.ts) == renderer (text.py) for every day"),
        (res["scenes"] == expected, "generated scene list matches the renderer"),
        (res["card"] == f"animations/{CARD_BG.NAME}.anim", "card backdrop path"),
        (all(p.is_file() for p in anims), "every .anim exists"),
    ]
    for ok, name in checks:
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
    print("text parity: " + ("PASS" if not failures else f"{failures} FAILURE(S)"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
