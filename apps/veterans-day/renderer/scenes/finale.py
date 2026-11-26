"""Scene: the finale. The flag fills the display, its thirteen stripes rippling slowly in the breeze. Then it dims
gently behind THANK YOU / VETERANS in warm ivory (docs/DECISIONS.md D3, D7, D10). Calm: no fireworks or confetti."""

from busybar.canvas import W, ease_in_out, ease_out, new, phase, sec
from busybar.font import draw_text, text_width

from scenes.text import SCENE_CAPTIONS
from vfx import CAPTION_GRAD, CAPTION_SHADOW, big_flag_color, darken, draw_flag, quant

NAME = "finale"
TITLE = "Thank You, Veterans"
SECONDS = 16
KEYFRAMES = [(1.0, "The flag fills the display"), (5.0, "Thirteen stripes in the breeze"),
             (8.4, "The flag dims"), (10.5, "THANK YOU"), (14.5, "THANK YOU VETERANS")]

DIM = (sec(7.0), sec(9.0))
LINE1 = sec(9.0)
LINE2 = sec(10.6)


def render():
    n = sec(SECONDS)
    frames = []
    fw = W + 2
    color = lambda u, v: big_flag_color(u, v, fw)  # noqa: E731
    for f in range(n):
        img = new((14, 16, 40))
        # one cycle every 4 s; the cloth is shifted by whole rows and shaded in 3 steps (a smaller .anim)
        draw_flag(img, -1, 1, fw, 13, f / sec(4.0), amp=1.0, wavelength=36, shade_levels=3, shade_k=0.18,
                  color=color)
        darken(img, 0.84 * quant(ease_in_out(phase(f, *DIM)), 12))
        for (text, font, x, y), t0 in zip(SCENE_CAPTIONS[NAME], (LINE1, LINE2)):
            a = quant(ease_out(phase(f, t0, t0 + sec(1.4))), 10)
            if a > 0:
                x = (W - text_width(text, font)) // 2 if x is None else x
                draw_text(img, text, x, y, None, font=font, gradient=CAPTION_GRAD, shadow=CAPTION_SHADOW, alpha=a)
        frames.append(img)
    return frames
