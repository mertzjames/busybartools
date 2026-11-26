"""Live-text layout shared by the app, the mockup and the parity test (exported, tone-mapped, by build.py).

The app draws every date and countdown as an xpmbitmap from these styles (docs/DECISIONS.md D4). Rows, with the
1 px shadow included:

  date   big  y=4   rows 4-11   the intro's "DEC 7"
  head   big  y=1   rows 1-8    "18 DAYS", "06:42"
  sub    tiny y=10  rows 10-15  "TO CHRISTMAS", "TO GO"
  top    big  y=0   rows 0-7    "MERRY", "SEE YOU"
  bot    big  y=8   rows 8-15   "CHRISTMAS", "NEXT YEAR!"
"""

GOLD = {"top": [255, 242, 176], "bottom": [242, 168, 40], "shadow": [110, 30, 10]}
ICE = {"top": [236, 246, 255], "bottom": [150, 200, 255], "shadow": [20, 40, 110]}
HOLLY = {"top": [255, 120, 120], "bottom": [220, 30, 50], "shadow": [70, 10, 20]}

STYLES = {
    "date": {"font": "big", "y": 4, **GOLD},
    "head": {"font": "big", "y": 1, **GOLD},
    "sub": {"font": "tiny", "y": 10, **ICE},
    "top": {"font": "big", "y": 0, **HOLLY},
    "bot": {"font": "big", "y": 8, **GOLD},
}

TEXT_FONTS = ["big", "tiny"]

# How long a countdown card stays up.
CARD_MS = 5500
