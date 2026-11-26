"""Scene: Cupid's Arrow. A little winged cherub flutters in over evening clouds, nocks an arrow with a heart tip,
draws the bow and lets fly. The arrow streaks across the sky and bursts into a big heart, which beats while small
hearts drift up from it. The cherub claps its wings and flutters away."""

import math

from busybar.canvas import FPS, H, W, add, blit, ease_in_out, ease_out, lerp, put, sec
from busybar.fx import Stars, puff
from busybar.party import Confetti
from sprites import CHERUB, CHERUB_HAND
from vfx import (BLUSH, GOLD, GOLD_LIGHT, PINK, RED, ROSE, WARM_WHITE, gradient, heart_c, heart_glow, twinkle)

NAME = "cupid"
TITLE = "Cupid's Arrow"
SECONDS = 15
KEYFRAMES = [(1.6, "A cherub flutters in"), (4.6, "It draws the bow"), (5.8, "The arrow flies"),
             (6.7, "It bursts into a heart"), (9.0, "The heart beats"), (12.8, "The cherub flutters away")]

HOME_X, HOME_Y = 4, 2  # the cherub's top-left while it shoots
NOCK, DRAW_END, RELEASE = 3.4, 4.8, 5.3  # seconds
HIT_X, HIT_Y = 54, 7.5
FLIGHT = 0.75  # seconds from release to hit
HIT = RELEASE + FLIGHT
LEAVE = 11.2
GROW = (3, 5, 7, 9, 11)

ARROW_HEAD = ["##..", "###.", ".###", "###.", "##.."]  # a sideways heart, tip to the right
BOW = [(-1, -5), (0, -4), (0, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (0, 3), (0, 4), (-1, 5)]
BOW_GOLD = (255, 150, 40)


def cherub_at(t: float):
    """(x, y, wing frame) of the cherub's sprite."""
    flap = (int(t * FPS) // 3) % 2
    bob = math.sin(t * 2 * math.pi * 0.9) * 0.8
    if t < 2.6:
        p = ease_out(t / 2.6)
        return lerp(-14, HOME_X, p), HOME_Y + 2 * math.sin(p * math.pi * 2) * (1 - p) + bob, flap
    if t < LEAVE:
        return HOME_X, HOME_Y + bob, flap if t > HIT + 0.6 or t < NOCK else (int(t * FPS) // 5) % 2
    p = (t - LEAVE) / (SECONDS - LEAVE)
    e = p * p
    return HOME_X - 20 * e + 4 * math.sin(p * math.pi), HOME_Y + bob - 12 * e, (int(t * FPS) // 2) % 2


def draw_bow(img, hx: int, hy: int, pull: float, nocked: bool) -> None:
    for dx, dy in BOW:
        put(img, hx + dx, hy + dy, BOW_GOLD)
    put(img, hx + 1, hy - 1, GOLD_LIGHT)
    top, bot = (hx - 1, hy - 5), (hx - 1, hy + 5)
    px = hx - 1 - pull
    for k in range(1, 5):  # the string: two straight runs to the pull point
        u = k / 5
        put(img, lerp(top[0], px, u), lerp(top[1], hy, u), (240, 230, 255), 0.75)
        put(img, lerp(bot[0], px, u), lerp(bot[1], hy, u), (240, 230, 255), 0.75)
    if nocked:
        draw_arrow(img, px, hy, length=4 + pull)


def draw_arrow(img, tail_x: float, y: float, length: float = 6, trail: float = 0.0) -> None:
    tail_x, y = int(math.floor(tail_x + 0.5)), int(math.floor(y + 0.5))
    for k in range(int(length) + 1):
        put(img, tail_x + k, y, GOLD_LIGHT if k > 1 else GOLD)
    put(img, tail_x - 1, y - 1, WARM_WHITE, 0.9)  # fletching
    put(img, tail_x - 1, y + 1, WARM_WHITE, 0.9)
    put(img, tail_x, y - 1, BLUSH, 0.7)
    put(img, tail_x, y + 1, BLUSH, 0.7)
    hx = tail_x + int(length) + 1
    for dy, row in enumerate(ARROW_HEAD):
        for dx, bit in enumerate(row):
            if bit == "#":
                put(img, hx + dx, y - 2 + dy, RED)
    put(img, hx, y - 1, PINK)
    for k in range(int(trail)):  # a fading gold trail behind it
        add(img, tail_x - 2 - k, y, GOLD, 0.6 * (1 - k / max(1, trail)))


def heart_width(t: float) -> int:
    if t < HIT:
        return 0
    k = int((t - HIT) / 0.08)
    if k < len(GROW):
        return GROW[k]
    u = (t - HIT - len(GROW) * 0.08) % 1.4
    return 13 if (u < 0.12 or 0.26 <= u < 0.36) else 11


def render():
    bg = gradient([(0, (16, 10, 48)), (8, (52, 22, 78)), (15, (110, 40, 96))])
    for cx, cy, r in ((4, 15, 3.5), (12, 16, 4), (24, 16, 3), (38, 15.5, 3.5), (50, 16, 4.5), (63, 15, 3.5),
                      (70, 16, 3)):  # evening clouds along the bottom
        puff(bg, cx, cy, r, (150, 80, 130), 0.55)
    stars = Stars(seed=9, n=14, ymax=9, period=FPS * 3, color=(230, 220, 255), dim=0.12, bright=0.7)
    spray = Confetti(seed=5, t0=sec(HIT + 0.3), x=HIT_X, y=HIT_Y - 2, n=18, vx=(-0.9, 0.9), vy=(-1.6, -0.4),
                     fall=(0.02, 0.06), colors=(ROSE, PINK, BLUSH, GOLD_LIGHT), stagger=sec(4))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        stars.draw(img, f)
        hw = heart_width(t)
        if hw:
            heart_glow(img, HIT_X, HIT_Y + 0.5, 9, (130, 20, 70), 0.75)
            spray.draw(img, f, 0.9)
            heart_c(img, HIT_X, HIT_Y + (0.5 if hw >= 13 else 0), hw, RED, halo=(44, 6, 40))
            if t - HIT < 0.25:  # the flash where the arrow turns into the heart
                k = 1 - (t - HIT) / 0.25
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        d = abs(dx) + abs(dy)
                        if d <= 3:
                            add(img, HIT_X + dx, HIT_Y + dy, WARM_WHITE, k * (1 - d / 4))
            if t > HIT + 1.2:
                for i, (x, y) in enumerate(((45, 2), (63, 3), (44, 12), (64, 12), (54, 0))):
                    twinkle(img, x, y, f, GOLD_LIGHT, 0.85, period=21, ph=i / 5)
        x, y, wing = cherub_at(t)
        blit(img, CHERUB.img(wing), x, y)
        hx, hy = int(math.floor(x + 0.5)) + CHERUB_HAND[0], int(math.floor(y + 0.5)) + CHERUB_HAND[1]
        if t < LEAVE:
            pull = 0.0
            if NOCK <= t < RELEASE:
                pull = 3 * ease_in_out((t - NOCK) / (DRAW_END - NOCK))
            elif RELEASE <= t < RELEASE + 0.15:  # the string twangs
                pull = -1 if int(t * FPS) % 2 else 1
            draw_bow(img, hx, hy, max(0.0, pull) if t < RELEASE else 0.0, NOCK <= t < RELEASE)
            if RELEASE <= t < HIT:
                p = (t - RELEASE) / FLIGHT
                tail = lerp(hx - 2, HIT_X - 8, p)
                draw_arrow(img, tail, lerp(hy, HIT_Y, p), 4, trail=min(8, p * 20))
        else:  # it carries the bow away
            draw_bow(img, hx, hy + 1, 0, False)
        frames.append(img)
    return frames
