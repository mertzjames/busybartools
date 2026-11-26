"""Live-text styles for the cards, shared with the app (generated show.ts) and the mockup (docs/DECISIONS.md D7).

    time  clock font  y=2   rows 2-14   "18:05"
    date  big         y=4   rows 4-11   "SUN 20 JUN"
    head  big         y=1   rows 1-8    "206 DAYS"
    sub   tiny        y=10  rows 10-15  "TO FATHER'S DAY"
    top   big         y=0   rows 0-7    "HAPPY", "BEST DAD", "REEL COOL"   (first of two big lines)
    bot   big         y=8   rows 8-15   "FATHER'S DAY", "EVER", "DAD"      (second of two big lines)
    word  big         y=4   rows 4-11   "THANKS DAD"

Summer colors: cream into a sunset orange over a deep-navy shadow for the big lines, and a pale sky blue for the
small line, all over the evening-blue card backdrops.

The big font gains one app-local glyph, '#', for the finale's "#1 DAD" (font.register_font, never lib/). It is
exported with the live fonts too, so the app could draw it, but no card text uses it.
"""

from busybar import font

font.register_font("big", {"#": [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."]}, 7, extend=True)

SUNSET = {"top": [255, 246, 222], "bottom": [255, 156, 64], "shadow": [12, 20, 58]}
SKY = {"top": [232, 246, 255], "bottom": [120, 204, 255], "shadow": [10, 18, 50]}

LAYOUT = {
    "time": {"font": "clock", "y": 2, **SUNSET},
    "date": {"font": "big", "y": 4, **SUNSET},
    "head": {"font": "big", "y": 1, **SUNSET},
    "sub": {"font": "tiny", "y": 10, **SKY},
    "top": {"font": "big", "y": 0, **SUNSET},
    "bot": {"font": "big", "y": 8, **SUNSET},
    "word": {"font": "big", "y": 4, **SUNSET},
}

# The on-the-day cards as (text, style) pages, for review strips. The app's source of truth is DAY_CARDS in
# app/shared/fathers.ts; tests/text_parity.py checks the two agree.
_GREETING = [("HAPPY", "top"), ("FATHER'S DAY", "bot")]
DAY_TEXT = [
    [_GREETING, [("BEST DAD", "top"), ("EVER", "bot")]],
    [_GREETING, [("THANKS DAD", "word")]],
    [_GREETING, [("REEL COOL", "top"), ("DAD", "bot")]],
]
