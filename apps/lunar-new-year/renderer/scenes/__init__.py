"""Scene registry. Each scene module (or zodiac.ZodiacScene) exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import card_bg, dragon_dance, dumplings, finale, firecrackers, lanterns, lion_dance, red_envelopes, zodiac

# The seven festival scenes (docs/DECISIONS.md D2), then the twelve zodiac scenes (D5) and the card backdrop.
PLAYLIST = [lanterns, dragon_dance, lion_dance, red_envelopes, dumplings, firecrackers, finale]
ZODIAC_SCENES = zodiac.SCENES
CARD_BG = card_bg
ALL_SCENES = PLAYLIST + ZODIAC_SCENES + [CARD_BG]

# The two playlists the app picks from (D6). "ZODIAC" is the scene of the current or upcoming animal; "clock" and
# "count" are cards. The app reads these from the generated show.ts, and so does the mockup.
PLAYLISTS = {
    "countdown": ["lanterns", "clock", "ZODIAC", "count", "dragon_dance", "clock", "red_envelopes", "count",
                  "lion_dance", "clock", "dumplings", "count", "firecrackers", "clock", "finale", "count"],
    "festival": ["ZODIAC", "count", "dragon_dance", "clock", "lion_dance", "count", "red_envelopes", "clock",
                 "dumplings", "count", "firecrackers", "clock", "lanterns", "count", "finale", "clock"],
}
