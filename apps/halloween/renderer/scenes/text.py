"""Live-text styles for the cards, shared with the app (generated show.ts) and the mockup (docs/DECISIONS.md D7).

    time   clock font  y=2   rows 2-14   "18:05"
    date   big         y=4   rows 4-11   "SAT 31 OCT"
    head   big         y=1   rows 1-8    "30 NIGHTS"
    sub    tiny        y=10  rows 10-15  "TO HALLOWEEN"
    hi     big         y=0   rows 0-7    "HAPPY", "TRICK OR"      (two big lines fill the display exactly)
    lo     big         y=8   rows 8-15   "HALLOWEEN", "TREAT!"
    boo    big         y=4   rows 4-11   "BOO!"

Candle-glow orange (pale gold into pumpkin orange) and slime green over a deep violet shadow (a dark shadow, not
a same-hue one, keeps gold text crisp); BOO! is ghost white into mint.
"""

PUMPKIN = {"top": [255, 238, 150], "bottom": [255, 122, 18], "shadow": [44, 4, 56]}
SLIME = {"top": [214, 255, 120], "bottom": [96, 214, 40], "shadow": [30, 4, 50]}
GHOST = {"top": [255, 255, 255], "bottom": [160, 255, 200], "shadow": [70, 12, 100]}

LAYOUT = {
    "time": {"font": "clock", "y": 2, **PUMPKIN},
    "date": {"font": "big", "y": 4, **PUMPKIN},
    "head": {"font": "big", "y": 1, **PUMPKIN},
    "sub": {"font": "tiny", "y": 10, **SLIME},
    "hi": {"font": "big", "y": 0, **PUMPKIN},
    "lo": {"font": "big", "y": 8, **SLIME},
    "boo": {"font": "big", "y": 4, **GHOST},
}

# Both backdrops keep their corner art (cobwebs, candles, little jack-o'-lanterns) in columns 0-7 and 64-71, so
# every text line, its 1 px shadow included, must stay inside columns TEXT_GAP[0]..TEXT_GAP[1] (56 px).
TEXT_GAP = (8, 63)

# The on-the-day cards as (text, style) pages, for review strips. The app's source of truth is DAY_CARDS in
# app/shared/halloween.ts; tests/text_parity.py checks the two agree.
GREETING = [("HAPPY", "hi"), ("HALLOWEEN", "lo")]
DAY_TEXT = [
    [GREETING, [("TRICK OR", "hi"), ("TREAT!", "lo")]],
    [GREETING, [("BOO!", "boo")]],
    [GREETING, [("SPOOKY", "hi"), ("SEASON", "lo")]],
    [GREETING, [("HAPPY", "hi"), ("HAUNTING", "lo")]],
]

# Words baked into scenes (checked by tests/text_parity.py: every glyph exists and each fits its place).
SCENE_TEXT = {"tombstone": ("RIP", "tiny"), "ghost": ("BOO!", "big"), "trick": ("TRICK OR TREAT!", "tiny")}
