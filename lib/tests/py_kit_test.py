#!/usr/bin/env python3
"""Smoke tests for the shared Python render kit (lib/python/busybar). Run by lib/tests/check.sh."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from busybar import font  # noqa: E402
from busybar.canvas import FPS, H, W, mix, new, put  # noqa: E402
from busybar.fx import Particles, Stars  # noqa: E402
from busybar.showbuild import build_scenes, tone_lut, ts_module  # noqa: E402
from busybar.sprite import Sprite  # noqa: E402


def test_mix_rounds_half_up() -> None:
    # Must match JS Math.round, so app/mockup/renderer agree (see AGENTS.md).
    assert mix((0, 0, 0), (1, 3, 5), 0.5) == (1, 2, 3)


def test_register_font() -> None:
    font.register_font("big", {"+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."]}, 7, extend=True)
    assert "+" in font.FONTS["big"][0] and "A" in font.FONTS["big"][0]
    font.register_font("test2", "[X]\n#.#\n.#.\n#.#", 3)
    assert font.text_width("XX", "test2") == 7
    assert set(font.export_json(["test2"])) == {"test2"}
    del font.FONTS["test2"]


def test_sprite_recolor_and_flip() -> None:
    s = Sprite("t", {"A": "#FF0000", "B": "#00FF00"}, "AB.")
    r = s.recolor("t2", A="#0000FF")
    assert s.img(0).getpixel((0, 0))[:3] == (255, 0, 0)
    assert r.img(0).getpixel((0, 0))[:3] == (0, 0, 255)
    assert s.img(0, flip=True).getpixel((2, 0))[:3] == (255, 0, 0)


class _Scene:
    NAME, TITLE, SECONDS, KEYFRAMES = "demo", "Demo", 1, [(0.5, "half")]

    @staticmethod
    def render():
        stars, sp, frames = Stars(seed=1, n=5), Particles(seed=2), []
        for f in range(FPS):
            img = new((5, 5, 20))
            stars.draw(img, f)
            put(img, f % W, H // 2, (255, 200, 0))
            sp.emit(10, 8, 1, vx=(-1, 1), vy=(-1, 1), life=(3, 6))
            sp.step_draw(img)
            frames.append(img)
        return frames


def test_build_scenes_deterministic() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        a = build_scenes([_Scene], Path(tmp) / "a", tone_lut(0.8))
        b = build_scenes([_Scene], Path(tmp) / "b", tone_lut(0.8))
        assert (Path(tmp) / "a/demo.anim").read_bytes() == (Path(tmp) / "b/demo.anim").read_bytes()
        assert a[0]["frames"] == FPS and a[0]["keyframes"] == [{"s": 0.5, "caption": "half"}]


def test_ts_module_format() -> None:
    src = ts_module([("A", {"x": 1}, None, 2, True), ("B", [1], "number[]", None, False)])
    assert 'export const A = {\n  "x": 1\n} as const;\n\nexport const B: number[] = [1];\n' in src


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"  ok   {name}")
    print("python kit: PASS")
