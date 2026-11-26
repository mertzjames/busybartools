"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import clock_bg, count_bg, finale, main_street, moment_bg, parade, poppies, salute, services, thank_you

# Every scene the app ships, in show order (docs/DECISIONS.md D3).
ALL = [main_street, parade, services, salute, poppies, thank_you, finale]
CLOCK_BG = clock_bg
COUNT_BG = count_bg
MOMENT_BG = moment_bg
BACKDROPS = [CLOCK_BG, COUNT_BG, MOMENT_BG]
