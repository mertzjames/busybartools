"""Live text for the cards: styles (layout and colors), timing, and the Nguzo Saba texts.

Single source of truth: build.py exports all of this (with tone-mapped colors) into app/shared/generated/show.ts
and the mockup, so the app, the mockup and the review strips draw the same pixels (tests/text_parity.py).
"""

# Layout over the card backdrop (border on rows 0 and 15):
#   head  big   rows 1-7 (+ shadow 8)     the Swahili word, "18 DAYS", "HABARI GANI?"
#   sub   tiny  rows 9-13 (+ shadow 14)   the English, "TO KWANZAA"
#   time  clock rows 2-13 (+ shadow 14)   24-hour HH:MM
#   date  big   rows 4-10                 "SAT 26 DEC"
STYLES = {
    "head": {"font": "big", "y": 1, "top": [255, 236, 150], "bottom": [240, 166, 40], "shadow": [150, 24, 24]},
    "sub": {"font": "tiny", "y": 9, "top": [206, 255, 196], "bottom": [110, 220, 120], "shadow": [16, 70, 30]},
    "time": {"font": "clock", "y": 2, "top": [255, 244, 200], "bottom": [255, 180, 60], "shadow": [150, 24, 24]},
    "date": {"font": "big", "y": 4, "top": [255, 236, 150], "bottom": [236, 160, 40], "shadow": [20, 110, 44]},
}
TEXT_FONTS = ("big", "tiny", "clock")

# Page timings (ms)
TIMING = {
    "time": 4500, "date": 3500,  # clock card
    "count": 4500, "dates": 3500,  # before Kwanzaa: "N DAYS / TO KWANZAA", then "KWANZAA / DEC 26 - JAN 1"
    "greet": 3500, "principle": 4000, "principle2": 3000, "day": 3000,  # during
}

# The Nguzo Saba, one per day, as the official Kwanzaa website gives them (docs/DECISIONS.md D6). The English is
# split into lines that fit the tiny font (18 characters); a second line becomes a second page.
PRINCIPLES = [
    {"word": "UMOJA", "english": ["UNITY"]},
    {"word": "KUJICHAGULIA", "english": ["SELF-DETERMINATION"]},
    {"word": "UJIMA", "english": ["COLLECTIVE WORK", "AND RESPONSIBILITY"]},
    {"word": "UJAMAA", "english": ["COOPERATIVE", "ECONOMICS"]},
    {"word": "NIA", "english": ["PURPOSE"]},
    {"word": "KUUMBA", "english": ["CREATIVITY"]},
    {"word": "IMANI", "english": ["FAITH"]},
]

GREETING = ["HABARI GANI?", "WHAT'S THE NEWS?"]  # the day's greeting; the answer is the day's principle


def days_label(n: int) -> str:
    """Mirrors daysLabel in lib/ts/busybar/holidays.ts."""
    return f"{n} DAY" if n == 1 else f"{n} DAYS"


def count_pages(day: int, days: int) -> list:
    """The "count" card's pages: [(ms, [(style, text), ...]), ...]. Mirrors countPages in app/shared/kwanzaa.ts
    (tests/text_parity.py checks that they agree for every day).

    day:  1..7 during Kwanzaa, else 0
    days: days until Dec 26 (used when day == 0)
    """
    if not day:
        return [(TIMING["count"], [("head", days_label(days)), ("sub", "TO KWANZAA")]),
                (TIMING["dates"], [("head", "KWANZAA"), ("sub", "DEC 26 - JAN 1")])]
    p = PRINCIPLES[day - 1]
    pages = [(TIMING["greet"], [("head", GREETING[0]), ("sub", GREETING[1])]),
             (TIMING["principle"], [("head", p["word"]), ("sub", p["english"][0])])]
    for line in p["english"][1:]:
        pages.append((TIMING["principle2"], [("head", p["word"]), ("sub", line)]))
    if day == 6:
        pages.append((TIMING["day"], [("head", "KARAMU"), ("sub", "DAY 6: THE FEAST")]))
    else:
        pages.append((TIMING["day"], [("head", "KWANZAA"), ("sub", f"DAY {day} OF 7")]))
    return pages
