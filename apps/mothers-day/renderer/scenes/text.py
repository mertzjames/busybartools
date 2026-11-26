"""Live-text styles for the cards, shared with the app (generated show.ts) and the mockup (docs/DECISIONS.md D7).

    time  clock font  y=2   rows 2-14   "18:05"
    date  big         y=4   rows 4-11   "SUN 9 MAY"
    head  big         y=1   rows 1-8    "164 DAYS", "HAPPY", "THANK YOU"
    sub   tiny        y=10  rows 10-15  "TO MOTHER'S DAY", "MOTHER'S DAY", "FOR ALL YOU DO"
    word  big         y=4   rows 4-11   "LOVE YOU MOM" (71 px: the widest text, edge to edge)

Warm cream into soft pink over a deep plum shadow for the big lines, and pale lavender for the small line, all over
the dark rose and plum card backdrops.
"""

BLUSH = {"top": [255, 246, 232], "bottom": [255, 140, 186], "shadow": [70, 12, 48]}
LILAC = {"top": [240, 230, 255], "bottom": [192, 160, 255], "shadow": [30, 10, 52]}

LAYOUT = {
    "time": {"font": "clock", "y": 2, **BLUSH},
    "date": {"font": "big", "y": 4, **BLUSH},
    "head": {"font": "big", "y": 1, **BLUSH},
    "sub": {"font": "tiny", "y": 10, **LILAC},
    "word": {"font": "big", "y": 4, **BLUSH},
}

# The on-the-day cards as (text, style) pages, for review strips. The app's source of truth is DAY_CARDS in
# app/shared/mothersday.ts; tests/text_parity.py checks the two agree.
_GREETING = [("HAPPY", "head"), ("MOTHER'S DAY", "sub")]
DAY_TEXT = [
    [_GREETING, [("LOVE YOU MOM", "word")]],
    [_GREETING, [("THANK YOU", "head"), ("FOR ALL YOU DO", "sub")]],
    [_GREETING, [("BIG HUGS", "head"), ("TODAY AND ALWAYS", "sub")]],
]
