"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import card_bg, drums, harvest, karamu, kente, kinara, unity_cup

# The kinara scene has one variant per day (index 0 = unlit, before and after Kwanzaa; 1..7 = the day's candles) for
# the default lighting order, plus days 2-7 for the center-out order (docs/DECISIONS.md D14).
KINARA = kinara.VARIANTS
KINARA_CENTER = kinara.CENTER_VARIANTS
# The scenes that follow the kinara in every cycle (docs/DECISIONS.md D2). Cards go between them.
PLAYLIST = [harvest, unity_cup, drums, kente, karamu]
CARD_BG = card_bg
