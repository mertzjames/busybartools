"""Live-text styles for the cards, shared with the app (generated show.ts) and the mockup (docs/DECISIONS.md D7).

    time  clock font  y=2   rows 2-14   "18:05"
    date  big         y=4   rows 4-11   "MON 6 SEP"
    head  big         y=0   rows 0-7    "284 DAYS", "HAPPY", "THANK YOU"
    sub   big         y=8   rows 8-15   "TO LABOR DAY", "LABOR DAY", "WORKERS"

Two big lines fill the 16 rows exactly (each 7 rows plus a 1 px shadow). The widest, "TO LABOR DAY", is 67 px.
The palette is hard-hat gold over a dark brown shadow for the first line and a summer-sky blue over a navy shadow
for the second, on the dark card backdrops.
"""

GOLD = {"top": [255, 246, 214], "bottom": [255, 186, 44], "shadow": [70, 30, 8]}
SKY = {"top": [226, 242, 255], "bottom": [110, 184, 255], "shadow": [10, 18, 64]}

LAYOUT = {
    "time": {"font": "clock", "y": 2, **GOLD},
    "date": {"font": "big", "y": 4, **GOLD},
    "head": {"font": "big", "y": 0, **GOLD},
    "sub": {"font": "big", "y": 8, **SKY},
}

# The on-the-day cards as (text, style) pages, for review strips. The app's source of truth is DAY_CARDS in
# app/shared/laborday.ts; tests/text_parity.py checks the two agree.
_GREETING = [("HAPPY", "head"), ("LABOR DAY", "sub")]
DAY_TEXT = [
    [_GREETING, [("THANK YOU", "head"), ("WORKERS", "sub")]],
    [_GREETING, [("ENJOY", "head"), ("THE DAY", "sub")]],
    [_GREETING, [("SO LONG", "head"), ("SUMMER", "sub")]],
]
