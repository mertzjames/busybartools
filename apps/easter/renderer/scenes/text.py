"""Live-text styles for the cards, shared with the app (generated show.ts) and the mockup (docs/DECISIONS.md D7).

    time  clock font  y=2   rows 2-14   "18:05"
    date  big         y=4   rows 4-11   "THU 26 NOV"
    head  big         y=1   rows 1-8    "122 DAYS", "EGG HUNT", "HOPPY", "SPRING IS"
    sub   tiny        y=10  rows 10-15  "TO EASTER", "TIME!", "EASTER!", "HERE!"
    top   big         y=0   rows 0-7    "HAPPY"
    bot   big         y=8   rows 8-15   "EASTER"

Spring colors over a deep backdrop (D7): cream into sunny yellow for the time, date and headline, pastel pink for
the small line, and on the day a pink HAPPY over a lemon EASTER. Every shadow is a deep violet, lit enough to read
as a shadow and not a hole.
"""

SUNNY = {"top": [255, 248, 214], "bottom": [255, 200, 60], "shadow": [70, 30, 110]}
BLOSSOM = {"top": [255, 206, 232], "bottom": [255, 140, 196], "shadow": [60, 20, 80]}
PINKY = {"top": [255, 196, 228], "bottom": [255, 96, 176], "shadow": [70, 20, 90]}
LEMONY = {"top": [255, 250, 180], "bottom": [255, 196, 40], "shadow": [70, 30, 110]}

LAYOUT = {
    "time": {"font": "clock", "y": 2, **SUNNY},
    "date": {"font": "big", "y": 4, **SUNNY},
    "head": {"font": "big", "y": 1, **SUNNY},
    "sub": {"font": "tiny", "y": 10, **BLOSSOM},
    "top": {"font": "big", "y": 0, **PINKY},
    "bot": {"font": "big", "y": 8, **LEMONY},
}

# The on-the-day cards as (text, style) pages, for review strips. The app's source of truth is DAY_CARDS in
# app/shared/easter.ts; tests/text_parity.py checks the two agree.
_HAPPY = [("HAPPY", "top"), ("EASTER", "bot")]
DAY_TEXT = [
    [_HAPPY, [("EGG HUNT", "head"), ("TIME!", "sub")]],
    [_HAPPY, [("HOPPY", "head"), ("EASTER!", "sub")]],
    [_HAPPY, [("SPRING IS", "head"), ("HERE!", "sub")]],
]
