"""Scene registry. Each scene module (or SimpleNamespace variant) exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import bugler, clock_bg, count_bg, flag, flyover, headstones, poppies, services, tomb, wall

# Every scene the app ships, in show order (docs/DECISIONS.md D3). The flag has two variants (D5): the app's
# playlist plays one of them in the first slot, half-staff on the morning of Memorial Day and full staff otherwise.
FLAG_VARIANTS = [flag.HALF, flag.FULL]
ALL = FLAG_VARIANTS + [services, poppies, headstones, bugler, flyover, tomb, wall]
CLOCK_BG = clock_bg
COUNT_BG = count_bg
