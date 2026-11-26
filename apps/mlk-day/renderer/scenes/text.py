"""Live-text styles for the cards, shared with the app (generated show.ts) and the mockup (docs/DECISIONS.md D7).

    time  clock font  y=2   rows 2-14   "18:05"
    date  big         y=4   rows 4-11   "MON 18 JAN"
    head  big         y=1   rows 1-8    "53 DAYS", "A DAY ON"
    sub   tiny        y=10  rows 10-15  "TO MLK DAY", "NOT A DAY OFF"
    word  big         y=4   rows 4-11   "MLK DAY", "DREAM", "EQUALITY", "SERVICE"

Calm colors only (D7): warm white into dawn gold over a deep-blue shadow, and a pale sky blue for the small line.
No rainbow gradients.
"""

GOLD = {"top": [255, 240, 200], "bottom": [255, 182, 70], "shadow": [34, 44, 120]}
SKYBLUE = {"top": [206, 220, 255], "bottom": [150, 178, 240], "shadow": [26, 30, 80]}

LAYOUT = {
    "time": {"font": "clock", "y": 2, **GOLD},
    "date": {"font": "big", "y": 4, **GOLD},
    "head": {"font": "big", "y": 1, **GOLD},
    "sub": {"font": "tiny", "y": 10, **SKYBLUE},
    "word": {"font": "big", "y": 4, **GOLD},
}

# The on-the-day cards as (text, style) pages, for review strips. The app's source of truth is DAY_CARDS in
# app/shared/mlk.ts; tests/text_parity.py checks the two agree.
DAY_TEXT = [
    [[("MLK DAY", "word")], [("DREAM", "word")]],
    [[("MLK DAY", "word")], [("EQUALITY", "word")]],
    [[("MLK DAY", "word")], [("SERVICE", "word")], [("A DAY ON", "head"), ("NOT A DAY OFF", "sub")]],
]
