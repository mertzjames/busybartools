"""Scene: Rows of Honor. Symmetrical rows of plain white headstones run toward the horizon, each near one marked by a
small flag. The sunset fades into twilight, the first stars come out, and the small flags stir in the evening air.
No names or inscriptions: every stone is the same."""

from busybar.canvas import FPS, H, W, ease_in_out, mix, phase, put, sec
from busybar.fx import Stars
from mdfx import NAVY, RED, STONE, WHITE, quant, sky

NAME = "headstones"
TITLE = "Rows of Honor"
SECONDS = 16
KEYFRAMES = [(0.5, "White headstones at sunset"), (6.0, "Small flags stir in the evening air"),
             (11.0, "Twilight"), (15.0, "The first stars")]

HORIZON = 8
CX = 36  # the scene is symmetrical about this column (between columns 35 and 36)

SUNSET = [(0, (44, 44, 104)), (4, (104, 72, 120)), (8, (210, 124, 104))]
TWILIGHT = [(0, (12, 16, 46)), (4, (30, 32, 80)), (8, (90, 60, 100))]

# straight rows of stones, far to near, each row centred on CX: (foot row, width, height, spacing, fade, stagger)
ROWS = [(9, 1, 1, 3, 0.4, 0.5), (11, 1, 2, 5, 0.15, 0.5), (15, 3, 4, 10, 0.0, 0.5)]


def stone(img, x: int, foot: int, w: int, h: int, c) -> None:
    """A headstone with its left edge at x and its foot at row `foot`; tall ones get rounded shoulders."""
    for dy in range(h):
        for dx in range(w):
            put(img, x + dx, foot - dy, c, 0.5 if (h >= 3 and dy == h - 1 and dx != w // 2) else 1.0)


def small_flag(img, x: int, top: int, f: int, k: int, left: bool) -> None:
    """A small flag (2 x 2 cloth) on a short dim staff, flying away from the centre; it stirs now and then."""
    sx, hoist, fly = (x + 2, x + 1, x) if left else (x, x + 1, x + 2)
    for y in range(top + 1, top + 5):
        put(img, sx, y, (110, 100, 92))
    stir = (f // 5 + k * 4) % 13 < 2
    put(img, hoist, top, NAVY)
    put(img, hoist, top + 1, RED)
    put(img, fly, top - (1 if stir else 0), RED)
    put(img, fly, top + 1 - (1 if stir else 0), WHITE)


def render():
    stars = Stars(seed=17, n=16, ymax=5, period=FPS * 4, color=(220, 226, 255), dim=0.1, bright=0.7)
    frames = []
    for f in range(sec(SECONDS)):
        dusk = quant(ease_in_out(phase(f, sec(1.0), sec(14.0))), 40)
        img = sky([(r, mix(a, b, dusk)) for (r, a), (_, b) in zip(SUNSET, TWILIGHT)])
        stars.draw(img, f, alpha=quant(phase(f, sec(9.0), sec(15.0)), 20))
        grass_far, grass_near = mix((50, 76, 54), (30, 48, 42), dusk), mix((34, 60, 40), (20, 38, 32), dusk)
        for y in range(HORIZON + 1, H):
            for x in range(W):
                put(img, x, y, mix(grass_far, grass_near, (y - HORIZON - 1) / (H - HORIZON - 2)))
        for x in range(W):  # the last light along the horizon line
            put(img, x, HORIZON, mix((200, 140, 110), (70, 60, 96), dusk))
        lit = mix(STONE, (176, 182, 204), dusk)  # pale stones stay lit into twilight
        for foot, w, h, gap, fade, stagger in ROWS:
            c = mix(lit, grass_far, fade)
            for i in range(20):
                off = int(gap * (i + stagger) + 0.5)
                if off - w > CX:
                    break
                xs = (CX + off, CX - off - w) if off else (CX - w // 2 - 1,)
                for k, x in enumerate(xs):
                    stone(img, x, foot, w, h, c)
                    if foot == 15:  # a small flag before each of the nearest stones, mirrored about the centre
                        fx = x + w if k == 0 else x - 3
                        if 0 <= fx and fx + 2 < W:
                            small_flag(img, fx, foot - 4, f, i + 5 * k, k == 1)
        frames.append(img)
    return frames
