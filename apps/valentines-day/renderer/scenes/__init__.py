"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import candy_hearts, chocolates, clock_bg, count_bg, cupid, floating_hearts, love_letter, lovebirds, rose

# Playlist order (docs/DECISIONS.md D3). Cards alternate between scenes (clock, count).
PLAYLIST = [floating_hearts, cupid, love_letter, lovebirds, chocolates, rose, candy_hearts]
CLOCK_BG = clock_bg
COUNT_BG = count_bg
