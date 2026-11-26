"""Live-text styles for the cards, shared with the app (generated show.ts) and the mockup (docs/DECISIONS.md D7).

    time    clock font  y=2   rows 2-14   "18:05"
    date    big         y=4   rows 4-11   "TUE 17 MAR"
    head    big         y=1   rows 1-8    "111 DAYS", "HAPPY"
    sub     tiny        y=10  rows 10-15  "TO ST. PATRICK'S", "ST. PATRICK'S DAY"
    word    big         y=4   rows 4-11   "HAPPY"
    top     big         y=0   rows 0-7    "ST. PATRICK'S", "ERIN GO"
    bottom  big         y=8   rows 8-15   "DAY", "BRAGH"

Gold for the main line, shamrock green for the second, both over a deep-green shadow, so they read on the dark
green backdrops.
"""

GOLD = {"top": [255, 240, 170], "bottom": [255, 178, 40], "shadow": [6, 44, 18]}
GREEN = {"top": [196, 255, 176], "bottom": [84, 214, 96], "shadow": [6, 40, 16]}

LAYOUT = {
    "time": {"font": "clock", "y": 2, **GOLD},
    "date": {"font": "big", "y": 4, **GOLD},
    "head": {"font": "big", "y": 1, **GOLD},
    "sub": {"font": "tiny", "y": 10, **GREEN},
    "word": {"font": "big", "y": 4, **GOLD},
    "top": {"font": "big", "y": 0, **GOLD},
    "bottom": {"font": "big", "y": 8, **GREEN},
}

# The on-the-day cards as (text, style) pages, for review strips. The app's source of truth is DAY_CARDS in
# app/shared/stpatricks.ts; tests/text_parity.py checks the two agree.
DAY_TEXT = [
    [[("HAPPY", "word")], [("ST. PATRICK'S", "top"), ("DAY", "bottom")]],
    [[("ERIN GO", "top"), ("BRAGH", "bottom")], [("HAPPY", "head"), ("ST. PATRICK'S DAY", "sub")]],
]
