"""Live-text styles for the cards, shared with the app (generated show.ts) and the mockup (docs/DECISIONS.md D6).

    time  clock font  y=2   rows 2-14   "18:05"
    date  big         y=4   rows 4-11   "SAT 4 JUL"
    head  big         y=0   rows 0-7    "220 DAYS", "HAPPY"                 gold
    sub   big         y=8   rows 8-15   "TO JULY 4TH", "4TH OF JULY"        red-white
    lead  big         y=0   rows 0-7    "FIREWORKS IN", "ENJOY THE"         blue-white
    num   big         y=8   rows 8-15   "02:15", "FIREWORKS!"               gold

Two big lines fit 16 rows exactly (y 0 and y 8, each 7 rows plus a 1-row shadow). Every line is at most
"FIREWORKS IN", 65 px plus the shadow. Gold is cream into gold, the second lines are pale red or pale blue, all over a
dark shadow so they read over the night-blue backdrops.
"""

GOLD = {"top": [255, 246, 222], "bottom": [255, 190, 70], "shadow": [40, 8, 22]}
REDWHITE = {"top": [255, 232, 232], "bottom": [255, 104, 112], "shadow": [14, 18, 64]}
BLUEWHITE = {"top": [236, 242, 255], "bottom": [130, 170, 255], "shadow": [40, 8, 22]}

LAYOUT = {
    "time": {"font": "clock", "y": 2, **GOLD},
    "date": {"font": "big", "y": 4, **GOLD},
    "head": {"font": "big", "y": 0, **GOLD},
    "sub": {"font": "big", "y": 8, **REDWHITE},
    "lead": {"font": "big", "y": 0, **BLUEWHITE},
    "num": {"font": "big", "y": 8, **GOLD},
}

# Card pages as (text, style) lines, for review strips. The app's source of truth is app/shared/july4.ts;
# tests/text_parity.py checks these samples match what it returns at the same times.
SAMPLE_PAGES = [
    ("2026-11-26T18:05:00", [("18:05", "time")]),
    ("2026-11-26T18:05:00", [("THU 26 NOV", "date")]),
    ("2026-11-26T18:05:00", [("220 DAYS", "head"), ("TO JULY 4TH", "sub")]),
    ("2027-07-05T08:00:00", [("365 DAYS", "head"), ("TO JULY 4TH", "sub")]),
    ("2027-07-04T18:45:00", [("HAPPY", "head"), ("4TH OF JULY", "sub")]),
    ("2027-07-04T18:45:00", [("FIREWORKS IN", "lead"), ("02:15", "num")]),
    ("2027-07-04T20:59:00", [("FIREWORKS IN", "lead"), ("00:01", "num")]),
    ("2027-07-04T21:00:00", [("ENJOY THE", "lead"), ("FIREWORKS!", "num")]),
]
