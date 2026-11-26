"""Live-text styles for the cards, shared with the app (generated show.ts) and the mockup (docs/DECISIONS.md D8).

    time  clock font  y=2   rows 2-14   "18:05"
    date  big         y=4   rows 4-11   "THU 26 NOV"
    head  big         y=1   rows 1-8    "205 DAYS", "FREEDOM DAY", "CELEBRATE"
    sub   tiny        y=10  rows 10-15  "TO JUNETEENTH", "JUNE 19", "FREEDOM"
    mid   big         y=4   rows 4-11   "JUNETEENTH" (alone, centered)
    top   big         y=0   rows 0-7    "HAPPY"
    bot   big         y=8   rows 8-15   "JUNETEENTH"

The Juneteenth flag's colors over a deep navy night (D8): starlight white into gold for the time, date and
headlines, a lit coral red for the small line and for HAPPY. Shadows are dark and of another hue (a deep crimson
under gold, a deep navy under red), so they read as shadows and not as part of the letters.
"""

STARLIGHT = {"top": [255, 250, 236], "bottom": [255, 196, 70], "shadow": [72, 14, 30]}
CORAL = {"top": [255, 178, 164], "bottom": [255, 92, 88], "shadow": [16, 22, 84]}
RED = {"top": [255, 130, 116], "bottom": [236, 44, 52], "shadow": [16, 22, 84]}

LAYOUT = {
    "time": {"font": "clock", "y": 2, **STARLIGHT},
    "date": {"font": "big", "y": 4, **STARLIGHT},
    "head": {"font": "big", "y": 1, **STARLIGHT},
    "sub": {"font": "tiny", "y": 10, **CORAL},
    "mid": {"font": "big", "y": 4, **STARLIGHT},
    "top": {"font": "big", "y": 0, **RED},
    "bot": {"font": "big", "y": 8, **STARLIGHT},
}

# Baked captions in the scenes use the same looks, as (top, bottom, shadow) tuples.
def look(style: dict) -> tuple:
    return tuple(style["top"]), tuple(style["bottom"]), tuple(style["shadow"])


# Words baked into the scenes (one source, so tests/text_parity.py can check they fit and every glyph exists).
NEWS_DATE = "JUNE 19, 1865"  # big has a comma glyph; tiny does not
NEWS_PLACE = "GALVESTON TEXAS"
RED_TOP, RED_BOTTOM = "RED FOR", "RESILIENCE"
FINALE_TOP, FINALE_BOTTOM, FINALE_MID = "HAPPY", "JUNETEENTH", "FREEDOM DAY"
SCENE_CAPTIONS = [(NEWS_DATE, "big"), (NEWS_PLACE, "tiny"), (RED_TOP, "big"), (RED_BOTTOM, "big"),
                  (FINALE_TOP, "big"), (FINALE_BOTTOM, "big"), (FINALE_MID, "big")]


# The on-the-day cards as (text, style) pages, for review strips. The app's source of truth is DAY_CARDS in
# app/shared/juneteenth.ts; tests/text_parity.py checks the two agree.
DAY_TEXT = [
    [[("JUNETEENTH", "mid")], [("FREEDOM DAY", "head"), ("JUNE 19", "sub")]],
    [[("HAPPY", "top"), ("JUNETEENTH", "bot")], [("CELEBRATE", "head"), ("FREEDOM", "sub")]],
]
