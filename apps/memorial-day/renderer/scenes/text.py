"""Live-text styles for the cards, shared with the app (generated show.ts) and the mockup (docs/DECISIONS.md D8).

    time   clock font  y=2   rows 2-14   "09:05"
    date   big         y=4   rows 4-11   "MON 31 MAY"
    head   big         y=1   rows 1-8    "186 DAYS", "HALF-STAFF", "FULL STAFF"
    sub    tiny        y=10  rows 10-15  "TO MEMORIAL DAY", "UNTIL NOON", "RAISED AT NOON"
    word   big         y=4   rows 4-11   "MEMORIAL DAY", "WE REMEMBER"
    upper  big         y=0   rows 0-7    "HONOR AND"
    lower  big         y=8   rows 8-15   "REMEMBER"

Calm colors only: warm white into pale silver over a deep-navy shadow, and a muted poppy rose for the small line.
"""

SILVER = {"top": [250, 246, 236], "bottom": [196, 204, 226], "shadow": [22, 24, 64]}
ROSE = {"top": [246, 200, 192], "bottom": [222, 150, 150], "shadow": [40, 18, 40]}

LAYOUT = {
    "time": {"font": "clock", "y": 2, **SILVER},
    "date": {"font": "big", "y": 4, **SILVER},
    "head": {"font": "big", "y": 1, **SILVER},
    "sub": {"font": "tiny", "y": 10, **ROSE},
    "word": {"font": "big", "y": 4, **SILVER},
    "upper": {"font": "big", "y": 0, **SILVER},
    "lower": {"font": "big", "y": 8, **SILVER},
}

# The on-the-day cards as (text, style) pages, for review strips and the parity test. The app's source of truth is
# app/shared/memorial.ts; tests/text_parity.py checks the two agree. The third card's last page depends on the time
# of day (the flag custom, D5): HALF_TEXT before noon, FULL_TEXT from noon.
HALF_TEXT = [("HALF-STAFF", "head"), ("UNTIL NOON", "sub")]
FULL_TEXT = [("FULL STAFF", "head"), ("RAISED AT NOON", "sub")]
DAY_TEXT = [
    [[("MEMORIAL DAY", "word")], [("WE REMEMBER", "word")]],
    [[("MEMORIAL DAY", "word")], [("HONOR AND", "upper"), ("REMEMBER", "lower")]],
    [[("MEMORIAL DAY", "word")]],  # + HALF_TEXT or FULL_TEXT
]
