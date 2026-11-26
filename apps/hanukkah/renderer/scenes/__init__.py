"""Scene registry. Each scene module (or namespace) exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)

The menorah and the window come in nine variants each (0-8 candles; docs/DECISIONS.md D2). The app picks the
playlist and the variants from the bar's date (app/shared/hanukkah.ts).
"""

from . import dreidel, finale, gelt, latkes, menorah, sufganiyot, window
from .cards import CLOCK_BG, COUNT_BG, LAYOUT

# Every scene, in the order of the generated SHOW.scenes (the app finds them by name).
SCENES = menorah.VARIANTS + window.VARIANTS + [dreidel, latkes, sufganiyot, gelt, finale]
CARDS = [CLOCK_BG, COUNT_BG]

__all__ = ["SCENES", "CARDS", "CLOCK_BG", "COUNT_BG", "LAYOUT"]
