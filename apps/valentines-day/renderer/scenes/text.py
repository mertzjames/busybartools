"""Live-text styles for the cards, shared with the app (generated show.ts) and the mockup (docs/DECISIONS.md D7).

    time   clock font  y=2   rows 2-14   "18:05"
    date   big         y=4   rows 4-11   "SAT 14 FEB"
    head   big         y=1   rows 1-8    "80 DAYS", "HAPPY"
    sub    tiny        y=10  rows 10-15  "TO VALENTINE'S DAY", "VALENTINE'S DAY"
    candy  big         y=4   rows 4-11   "BE MINE", "XOXO", ... (between the two candy hearts of count_bg)

Warm white into rose pink over a deep berry shadow; the small line is gold; candy phrases are blush pink with a
crimson shadow, like the printed words on a candy heart.
"""

ROSE = {"top": [255, 240, 236], "bottom": [255, 120, 160], "shadow": [96, 8, 44]}
GOLD = {"top": [255, 236, 180], "bottom": [255, 186, 84], "shadow": [80, 10, 36]}
CANDY = {"top": [255, 214, 228], "bottom": [255, 104, 150], "shadow": [130, 10, 52]}

LAYOUT = {
    "time": {"font": "clock", "y": 2, **ROSE},
    "date": {"font": "big", "y": 4, **ROSE},
    "head": {"font": "big", "y": 1, **ROSE},
    "sub": {"font": "tiny", "y": 10, **GOLD},
    "candy": {"font": "big", "y": 4, **CANDY},
}

# The widest candy phrase that fits between count_bg's candy hearts (columns 11..60, shadow included).
CANDY_MAX = 48

# The on-the-day cards as (text, style) pages, for review strips. The app's source of truth is DAY_CARDS in
# app/shared/valentine.ts; tests/text_parity.py checks the two agree.
GREETING = [("HAPPY", "head"), ("VALENTINE'S DAY", "sub")]
DAY_TEXT = [
    [GREETING, [("BE MINE", "candy")], [("XOXO", "candy")]],
    [GREETING, [("HUG ME", "candy")], [("LOVE YOU", "candy")]],
    [GREETING, [("BE TRUE", "candy")], [("SO SWEET", "candy")]],
]
