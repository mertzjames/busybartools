"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
OVERLAY   optional: live text the app draws on top (only the odometer)
"""

from . import backdrops, ball_drop, champagne, clock_tower, dance_floor, disco_ball, fireworks, odometer, poppers

# Party loop order (docs/DECISIONS.md D13). A card follows every scene.
PLAYLIST = [disco_ball, champagne, clock_tower, poppers, odometer, dance_floor, ball_drop, fireworks]

# Live-screen backdrops, keyed as the app refers to them (screens.ts StageKey).
BACKDROPS = {
    "card": backdrops.CARD,
    "final": backdrops.FINAL,
    "final_fast": backdrops.FINAL_FAST,
    "final10": backdrops.FINAL10,
    "burst": backdrops.BURST,
    "fireworks": backdrops.FIREWORKS,
}
