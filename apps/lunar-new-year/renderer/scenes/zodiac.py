"""Year of the <animal>: one short scene per zodiac animal (docs/DECISIONS.md D5). The app's steps(t) picks the
animal of the current or upcoming lunar year.

Each scene: the animal arrives on the left of a wine-red stage with a gold papercut border, does its own little
action (the rabbit hops, the rooster crows, the monkey waves, the dragon and the snake undulate), and
`YEAR OF THE` / `<ANIMAL>` wipes in on the right with gold glints. Six seconds, so twelve of them stay small.
"""

from __future__ import annotations

import math

from busybar.canvas import FPS, H, add, blit, ease_out, mix, phase, put, sec, vgradient
from busybar.font import text_width
from busybar.party import glitter

import lnyfx as fx
import sprites
import textstyle

SECONDS = 6
N = sec(SECONDS)
ARRIVE = sec(1.6)
PANEL_X0 = 28  # the text panel: x 28..71
GROUND = 14  # animals stand with their feet on row 14

# Animals in busybar holidays.ZODIAC order, with their action after arriving.
ANIMALS = [("RAT", "scurry"), ("OX", "stomp"), ("TIGER", "pounce"), ("RABBIT", "hop"), ("DRAGON", "fly"),
           ("SNAKE", "slither"), ("HORSE", "rear"), ("GOAT", "butt"), ("MONKEY", "wave"), ("ROOSTER", "crow"),
           ("DOG", "wag"), ("PIG", "trot")]


def text_panel(img, animal: str, f: int) -> None:
    small = textstyle.STYLES["small"]
    name = textstyle.STYLES["name"]
    cx = PANEL_X0 + (72 - PANEL_X0) // 2
    w1 = text_width("YEAR OF THE", "tiny")
    w2 = text_width(animal, "big")
    r1 = int((w1 + 2) * ease_out(phase(f, sec(0.9), sec(1.5))))
    r2 = int((w2 + 2) * ease_out(phase(f, sec(1.7), sec(2.3))))
    if r1 > 0:
        textstyle.draw(img, "YEAR OF THE", small, x=cx - w1 // 2, reveal=r1, y=2)
    if r2 > 0:
        textstyle.draw(img, animal, name, x=cx - w2 // 2, reveal=r2, y=7)
        if r2 < w2 + 2:  # a glint riding the wipe
            add(img, cx - w2 // 2 + r2, 9, fx.GOLD_LIGHT, 0.9)
            add(img, cx - w2 // 2 + r2, 11, fx.GOLD_LIGHT, 0.6)
    if f >= sec(2.3):
        glitter(img, seed=len(animal) * 7, f=f, n=6, period=45, area=(cx - w2 // 2 - 1, 6, cx + w2 // 2 + 2, 15),
                strength=0.7)


def serpent(img, x_head: float, f: int, length: int, amp: float, yc: float, body, belly, spine=None,
            thick: int = 2, wave: float = 0.45, speed: float = 0.35) -> list[tuple[int, float]]:
    """A wavy body from the tail (left) to the neck at x_head; returns the (x, y) centerline."""
    pts = []
    for i in range(length):
        x = int(round(x_head)) - i
        taper = min(1.0, (length - i) / 6)
        y = yc + amp * taper * math.sin(wave * x - speed * f)
        pts.append((x, y))
        t = thick if (length - i) > 3 else 1
        top = int(round(y - t / 2))
        for k in range(t):
            c = body if k < t - 1 or t == 1 else belly
            if (x + k) % 4 == 0 and t > 1 and k == 0:
                c = mix(body, (255, 255, 255), 0.25)  # scale glints
            put(img, x, top + k, c)
        if spine and t > 1 and x % 3 == 0:
            put(img, x, top - 1, spine)
    return pts


class ZodiacScene:
    """A scene module (NAME, TITLE, SECONDS, KEYFRAMES, render) for one animal."""

    def __init__(self, index: int, animal: str, action: str):
        self.index, self.ANIMAL, self.action = index, animal, action
        self.NAME = "zodiac_" + animal.lower()
        self.TITLE = "Year of the " + animal.title()
        self.SECONDS = SECONDS
        self.KEYFRAMES = [(0.8, f"The {animal.lower()} arrives"), (2.6, f"YEAR OF THE {animal}"),
                          (4.6, self._action_caption())]

    def _action_caption(self) -> str:
        return {
            "scurry": "It scurries and twitches its nose", "stomp": "It stamps a hoof", "pounce": "It crouches",
            "hop": "It hops", "fly": "The dragon undulates", "slither": "The snake sways",
            "rear": "The horse rears", "butt": "The goat lowers its horns", "wave": "The monkey waves",
            "crow": "The rooster crows", "wag": "The dog wags its tail", "pig": "It trots",
            "trot": "The pig trots in place",
        }[self.action]

    def backdrop(self):
        bg = vgradient(fx.WINE_TOP, fx.WINE_BOTTOM)
        # a soft warm glow behind the animal
        for y in range(H):
            for x in range(PANEL_X0):
                d = math.hypot((x - 13) / 1.6, y - 8)
                if d < 9:
                    put(bg, x, y, (110, 22, 26), 0.5 * (1 - d / 9))
        return bg

    def draw_animal(self, img, f: int) -> None:
        a = self.action
        t_arrive = ease_out(phase(f, 0, ARRIVE))
        if a in ("fly", "slither"):
            self._draw_serpent(img, f, t_arrive)
            return
        spr = sprites.ZODIAC_SPRITES[self.ANIMAL]
        x_end = (PANEL_X0 - spr.w) // 2
        x = -spr.w + (x_end + spr.w) * t_arrive
        y = GROUND + 1 - spr.h
        moving = f < ARRIVE - 2
        frame = (f // 3) % 2 if moving else 0
        after = f - ARRIVE
        if not moving and after >= 0:
            if a == "hop":
                k = (after // 14) % 2 == 0 and after < sec(3.6)
                hop = abs(math.sin(math.pi * (after % 14) / 14)) if (after // 14) % 2 == 0 else 0
                y -= int(round(3 * hop)) if after < sec(3.6) else 0
                frame = 1 if (hop > 0.2 and k) else 0
            elif a == "crow":
                frame = 1 if sec(1.2) <= after < sec(2.4) else 0
                if frame:
                    for i in range(3):  # little "sound" arcs from the beak
                        k = ((after - sec(1.2)) / 4 - i) % 3
                        if k < 1:
                            put(img, x + spr.w + 1 + i * 2, y + 3 + (i % 2), fx.GOLD_LIGHT, 0.7)
            elif a == "wave":
                frame = (after // 5) % 2 if after < sec(3) else 0
            elif a in ("scurry", "trot", "stomp"):
                period = 4 if a == "scurry" else 6
                frame = (after // period) % 2 if sec(1.4) <= after < sec(2.6) else 0
                if a == "scurry" and (after // 3) % 6 == 0:
                    put(img, x + spr.w, y + 5, (255, 200, 210), 0.8)  # nose twitch
            elif a == "rear":
                if sec(1.4) <= after < sec(2.6):
                    lift = math.sin(math.pi * (after - sec(1.4)) / sec(1.2))
                    y -= int(round(2 * lift))
                    frame = 1
            elif a == "pounce":
                if sec(1.6) <= after < sec(2.0):
                    y += 1  # crouch
                elif sec(2.0) <= after < sec(2.6):
                    y -= int(round(2 * math.sin(math.pi * (after - sec(2.0)) / sec(0.6))))
                    x += 1
            elif a == "butt":
                if sec(1.4) <= after < sec(2.2):
                    x += int(round(2 * math.sin(math.pi * (after - sec(1.4)) / sec(0.8))))
            elif a == "wag":
                frame = (after // 3) % 2
                if frame:
                    put(img, x + 2, y + 4, (224, 170, 90))  # tail up
                    put(img, x + 1, y + 3, (224, 170, 90))
            if a in ("stomp",) and sec(1.4) <= after < sec(2.6) and (after // 6) % 2 == 1:
                put(img, x + 15, GROUND + 1, fx.GOLD_DARK, 0.6)  # dust
        blit(img, spr.img(frame), x, y)

    def _draw_serpent(self, img, f: int, t_arrive: float) -> None:
        if self.action == "slither":
            head = sprites.SNAKE_HEAD
            x_neck = -2 + 24 * t_arrive
            pts = serpent(img, x_neck, f, 20, 2.0, 11, (90, 210, 80), (230, 240, 120), thick=2, wave=0.5,
                          speed=0.4)
            hy = pts[0][1] - 3 + (1 if (f // 10) % 2 else 0)
            blit(img, head.img(0), x_neck - 1, hy)
            return
        head = sprites.DRAGON_HEAD
        x_neck = -4 + 17 * t_arrive
        pts = serpent(img, x_neck, f, 30, 2.0, 9, fx.RED, fx.GOLD, spine=(60, 200, 120), thick=4, wave=0.32,
                      speed=0.3)
        for i in (5, 15):  # little gold claws
            if i < len(pts):
                px, py = pts[i]
                put(img, px, py + 2, fx.GOLD)
                put(img, px + 1, py + 3, fx.GOLD_DARK)
        # the tail tuft
        tx, ty = pts[-1]
        put(img, tx - 1, ty - 1, (60, 200, 120))
        put(img, tx - 1, ty + 1, (60, 200, 120))
        hy = pts[0][1] - 6
        blit(img, head.img((f // 8) % 2), x_neck - 1, hy)

    def render(self):
        bg = self.backdrop()
        frames = []
        for f in range(N):
            img = bg.copy()
            fx.border(img, f)
            # glints drifting in the warm glow
            glitter(img, seed=self.index * 13 + 1, f=f, n=5, period=60, area=(1, 1, PANEL_X0 - 1, 9), strength=0.5)
            self.draw_animal(img, f)
            text_panel(img, self.ANIMAL, f)
            frames.append(img)
        return frames


SCENES = [ZodiacScene(i, name, action) for i, (name, action) in enumerate(ANIMALS)]
assert FPS * SECONDS == N
