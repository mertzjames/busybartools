"""Scene: Lighting the Kinara. The Kwanzaa table (mkeka, kinara, mazao, muhindi and the unity cup) in a warm room.
A taper lights the day's candles one by one in the official order (docs/DECISIONS.md D3), the room warms with
each flame, and the day is captioned.

There are eight variants (docs/DECISIONS.md D4): kinara_0 (before and after Kwanzaa: the candles wait, unlit,
captioned with the start date) and kinara_1 .. kinara_7 (day N lights N candles). The app's steps(t) picks the
day's variant. Each variant is a module-like object with the scene contract (NAME, TITLE, SECONDS, KEYFRAMES,
render()).
"""

from __future__ import annotations

import math
from types import SimpleNamespace

from busybar.canvas import FPS, W, add, ease_in_out, lerp, put, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import SPARKLE, Particles
from busybar.party import glitter
from kfx import (GOLD_HI, LIGHT_ORDERS, ROOM_BOTTOM, ROOM_TOP, Kinara, basket, corn_lying, fruit, mkeka,
                 room_glow, unity_cup)

SECONDS = 14
KIN = Kinara(36, 13)
T_TAPER_IN = 1.6  # the taper appears
T_LIGHT0 = 2.4  # first candle catches
T_LIGHT_END = 10.4  # the last candle has caught by here
T_CAPTION = 11.0


def table(img) -> None:
    """The static Kwanzaa table: mat, fruit basket with corn on the left, unity cup and corn on the right."""
    mkeka(img, 14)
    # mazao: a basket of fruit, two ears of corn standing behind it
    for kind, x, y in (("orange", 4, 9), ("apple", 7, 8), ("lime", 10, 9), ("plum", 13, 9), ("yam", 6, 10),
                       ("banana", 10, 7)):
        fruit(img, kind, x, y)
    basket(img, 3, 11, w=14, h=3)
    # the unity cup, and muhindi (ears of corn) lying on the mat
    unity_cup(img, 56, 13)
    corn_lying(img, 61, 12, 7)
    corn_lying(img, 64, 9, 6, flip=True)


def taper_path(n: int):
    """Times (s) at which each of the first n candles catches, evenly spread over the lighting window."""
    if n == 0:
        return []
    span = min(1.4, (T_LIGHT_END - T_LIGHT0) / max(1, n - 1)) if n > 1 else 0
    return [T_LIGHT0 + k * span for k in range(n)]


def draw_taper(img, x: float, y: float, f: int, a: float = 1.0) -> None:
    """A long taper reaching in from the upper right, its flame at (x, y)."""
    for k in range(1, 30):
        px, py = x + k * 0.9, y - k * 0.45
        put(img, px, py, (226, 196, 150) if k % 5 else (196, 160, 110), a)
    put(img, x, y, (255, 230, 120), a)
    add(img, x, y - 1, (255, 250, 210), 0.7 * a * (0.7 + 0.3 * math.sin(f * 1.7)))
    for dx, dy in ((-1, 0), (1, 0), (0, 1)):
        add(img, x + dx, y + dy, (140, 70, 10), 0.4 * a)


def render_day(day: int, light: str = "official"):
    n = day
    order = LIGHT_ORDERS[light][:n]
    times = taper_path(n)
    bg = vgradient(ROOM_TOP, ROOM_BOTTOM)
    table(bg)
    sp = Particles(seed=300 + day)
    frames = []
    hold = sec(0.35)  # the taper dwells at each wick
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        lit = [p for p, tt in zip(order, times) if t >= tt]
        ignite = {p: f - sec(tt) for p, tt in zip(order, times) if 0 <= f - sec(tt) < 6}
        room_glow(img, KIN, lit, f)
        KIN.draw(img, f, lit=lit, ignite=ignite)
        unity_cup_shine = max(0.0, math.sin(t * 1.3)) ** 6 * min(1.0, len(lit) / 3)
        if unity_cup_shine > 0.05:
            add(img, 54, 8, (255, 255, 230), 0.7 * unity_cup_shine)

        # the taper: in from the upper right, visiting each wick, then away
        if n:
            stops = [KIN.wick(p) for p in order]
            enter = (80.0, -4.0)
            leave_t = times[-1] + 0.6
            if T_TAPER_IN <= t < leave_t + 1.0:
                if t < times[0] - 0.35:
                    u = ease_in_out((t - T_TAPER_IN) / max(0.01, times[0] - 0.35 - T_TAPER_IN))
                    tx, ty = lerp(enter[0], stops[0][0], u), lerp(enter[1], stops[0][1] - 1, u)
                elif t >= leave_t:
                    u = ease_in_out((t - leave_t) / 1.0)
                    tx, ty = lerp(stops[-1][0], enter[0], u), lerp(stops[-1][1] - 1, enter[1], u)
                else:
                    # between candles: dwell at each wick, then glide to the next
                    k = max(i for i, tt in enumerate(times) if t >= tt - 0.35)
                    t_at = times[k] - 0.35
                    if k + 1 < n and t > times[k] + hold / FPS:
                        u = ease_in_out((t - times[k] - hold / FPS) / max(0.01, times[k + 1] - 0.35 - times[k]
                                                                           - hold / FPS))
                        tx = lerp(stops[k][0], stops[k + 1][0], u)
                        ty = lerp(stops[k][1], stops[k + 1][1], u) - 1 - 2 * math.sin(math.pi * u)
                    else:
                        dip = 1 if t >= t_at + 0.2 else 0
                        tx, ty = stops[k][0], stops[k][1] - 1 + dip
                draw_taper(img, tx, ty, f)
            for p, tt in zip(order, times):
                if f == sec(tt):
                    x, y = KIN.wick(p)
                    sp.emit(x, y - 1, 6, vx=(-0.6, 0.6), vy=(-0.9, -0.2), life=(4, 9), colors=SPARKLE, glow=True)
        sp.step_draw(img)

        # caption: the day, top left (over the corn's dark sky)
        if t >= T_CAPTION:
            a = min(1.0, (t - T_CAPTION) / 0.5)
            if day:  # top left, over the fruit basket
                draw_text(img, f"DAY {day}", 1, 0, GOLD_HI, font="tiny", shadow=(70, 20, 10), alpha=a)
            else:  # top right, over the unity cup: when the lighting begins
                draw_text(img, "DEC 26", W - text_width("DEC 26", "tiny") - 1, 1, GOLD_HI, font="tiny",
                          shadow=(70, 20, 10), alpha=a)
            if day:
                glitter(img, 40 + day, f, n=6, period=45, area=(KIN.x0 - 2, 0, KIN.x0 + 28, 4), strength=0.5)
        frames.append(img)
    return frames


def _variant(day: int, light: str = "official"):
    center = light == "center_out"
    if day == 0:
        title = "The Kinara Waits"
        keys = [(1.0, "The Kwanzaa table: mkeka, kinara, mazao, muhindi, unity cup"),
                (12.0, "The candles wait for Dec 26")]
    else:
        title = f"Lighting the Kinara: Day {day}" + (" (from the center)" if center else "")
        times = taper_path(day)
        keys = [(1.0, "The Kwanzaa table"), (times[0] + 0.4, "The black candle first: Umoja")]
        if day > 1:
            keys.append((times[-1] + 0.4, f"Day {day}: the last candle catches"))
        keys.append((12.5, f"DAY {day}"))
    name = f"kinara_center_{day}" if center else f"kinara_{day}"
    return SimpleNamespace(NAME=name, TITLE=title, SECONDS=SECONDS, KEYFRAMES=keys,
                           render=lambda d=day, o=light: render_day(d, o))


# The default (official-site) order: kinara_0 (unlit) .. kinara_7
VARIANTS = [_variant(d) for d in range(8)]
# The center-out order (docs/DECISIONS.md D14). The unlit kinara and day 1 (the black candle alone) are the same in
# both orders, so they reuse kinara_0 and kinara_1. Days 2-7 are rendered again: days 6 and 7 end with the same
# candles lit, but the taper lights them in a different order on the way.
CENTER_VARIANTS = [_variant(d, "center_out") for d in range(2, 8)]


def variant_names(light: str) -> list[str]:
    """The .anim name for each day 0..7 in a lighting order."""
    if light == "center_out":
        return ["kinara_0", "kinara_1"] + [m.NAME for m in CENTER_VARIANTS]
    return [m.NAME for m in VARIANTS]


# caption guards: "DAY N" stays left of the first candle; "DEC 26" stays right of the last one
assert text_width("DAY 7", "tiny") + 2 < KIN.candle_x(0)
assert W - text_width("DEC 26", "tiny") - 1 > KIN.candle_x(6) + 1
