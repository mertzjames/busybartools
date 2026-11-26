"""Live-text styles for the cards, shared with the app (generated show.ts) and the mockup, plus every word on screen
as review copies for the parity test (docs/DECISIONS.md D7, D8).

    time   clock font  y=2   rows 2-14   "09:05"
    date   big         y=4   rows 4-11   "WED 11 NOV"
    head   big         y=1   rows 1-8    "350 DAYS", "THANK YOU", "ARMISTICE"
    sub    tiny        y=10  rows 10-15  "TO VETERANS DAY", "FOR YOUR SERVICE", "NOV 11 1918"
    word   big         y=4   rows 4-11   "VETERANS DAY", "11TH HOUR"
    upper  big         y=0   rows 0-7    "THANK YOU", "HONOR ALL", "11TH DAY"
    lower  big         y=8   rows 8-15   "VETERANS", "WHO SERVED", "11TH MONTH"

Calm, warm colors: ivory into a pale gold over a deep-navy shadow, and a soft poppy rose for the small line.
"""

IVORY = {"top": [255, 248, 232], "bottom": [236, 210, 156], "shadow": [22, 24, 64]}
ROSE = {"top": [250, 206, 196], "bottom": [228, 150, 146], "shadow": [40, 18, 44]}

LAYOUT = {
    "time": {"font": "clock", "y": 2, **IVORY},
    "date": {"font": "big", "y": 4, **IVORY},
    "head": {"font": "big", "y": 1, **IVORY},
    "sub": {"font": "tiny", "y": 10, **ROSE},
    "word": {"font": "big", "y": 4, **IVORY},
    "upper": {"font": "big", "y": 0, **IVORY},
    "lower": {"font": "big", "y": 8, **IVORY},
}

# The on-the-day cards and the 11:00 moment card as (text, style) pages, for review strips and the parity test. The
# app's source of truth is app/shared/veterans.ts; tests/text_parity.py checks the two agree.
DAY_TEXT = [
    [[("VETERANS DAY", "word")], [("THANK YOU", "upper"), ("VETERANS", "lower")]],
    [[("VETERANS DAY", "word")], [("HONOR ALL", "upper"), ("WHO SERVED", "lower")]],
    [[("VETERANS DAY", "word")], [("THANK YOU", "head"), ("FOR YOUR SERVICE", "sub")]],
]
MOMENT_TEXT = [
    [("11TH HOUR", "word")],
    [("11TH DAY", "upper"), ("11TH MONTH", "lower")],
    [("ARMISTICE", "head"), ("NOV 11 1918", "sub")],
    [("THANK YOU", "upper"), ("VETERANS", "lower")],
]

# Captions baked into scenes: (text, font, x or None for centered, y). The parity test checks every glyph exists and
# that each caption fits the columns it is given.
SCENE_CAPTIONS = {
    "thank_you": [("THANK YOU", "tiny", 34, 1)],
    "finale": [("THANK YOU", "big", None, 0), ("VETERANS", "big", None, 8)],
}
