"""Live-text styles for the cards, shared with the app (generated show.ts) and the mockup (docs/DECISIONS.md D7).

    time  clock font  y=2   rows 2-14   "18:05"
    date  big         y=4   rows 4-11   "MON 15 FEB"
    head  big         y=1   rows 1-8    "81 DAYS", "HAPPY"
    sub   tiny        y=10  rows 10-15  "TO PRESIDENTS' DAY", "PRESIDENTS' DAY"
    word  big         y=4   rows 4-11   "LIBERTY", "UNION", "FREEDOM"

The palette is navy, red, cream and gold: cream into gold over a dark-red shadow for the big lines, and a pale
red-white for the small line, all over the navy card backdrops.
"""

GOLD = {"top": [255, 246, 222], "bottom": [255, 192, 84], "shadow": [70, 10, 26]}
REDWHITE = {"top": [255, 226, 226], "bottom": [255, 120, 124], "shadow": [16, 22, 70]}

LAYOUT = {
    "time": {"font": "clock", "y": 2, **GOLD},
    "date": {"font": "big", "y": 4, **GOLD},
    "head": {"font": "big", "y": 1, **GOLD},
    "sub": {"font": "tiny", "y": 10, **REDWHITE},
    "word": {"font": "big", "y": 4, **GOLD},
}

# The on-the-day cards as (text, style) pages, for review strips. The app's source of truth is DAY_CARDS in
# app/shared/presidents.ts; tests/text_parity.py checks the two agree.
_GREETING = [("HAPPY", "head"), ("PRESIDENTS' DAY", "sub")]
DAY_TEXT = [
    [_GREETING, [("LIBERTY", "word")]],
    [_GREETING, [("UNION", "word")]],
    [_GREETING, [("FREEDOM", "word")]],
]
