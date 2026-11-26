"""Review helpers for this app: a sprite contact sheet and keyframe strips of a scene.

    python3 renderer/review.py sprites out.png
    python3 renderer/review.py cast out.png        # the four students: every frame + a lineup
    python3 renderer/review.py scene dragon_roast out_dir/ [every_seconds]
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "lib" / "python"))

from PIL import Image  # noqa: E402

from busybar.preview import led, strip  # noqa: E402


def sheet(path: Path) -> None:
    """Contact sheet of every sprite frame."""
    import sprites

    tiles = []
    for s in sprites.ALL:
        for i in range(len(s)):
            tiles.append(led(s.img(i), cell=8))
    pad = 8
    cols = 6
    tw = max(t.width for t in tiles)
    th = max(t.height for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad) + pad), (40, 40, 48))
    for i, t in enumerate(tiles):
        out.paste(t, (pad + (i % cols) * (tw + pad), pad + (i // cols) * (th + pad)))
    out.save(path)
    print(f"wrote {path} ({len(tiles)} frames)")


def cast_sheet(path: Path) -> None:
    """Every frame of each student and of the old wizard (one row each), plus a lineup at true relative height."""
    from busybar.canvas import new
    import cast

    bg = (14, 12, 34)  # a typical night-sky backdrop, so dark colors are judged in context
    rows = []
    for spr in [st.sprite for st in cast.CAST] + [cast.ELDER]:
        tiles = []
        for i in range(len(spr)):
            im = new(bg).crop((0, 0, spr.w + 2, 17))
            im.alpha_composite(spr.img(i), (1, 17 - spr.h))
            tiles.append(led(im, cell=10))
        rows.append(tiles)
    lineup_sprites = [st.sprite for st in cast.CAST[:2]] + [cast.ELDER] + [st.sprite for st in cast.CAST[2:]]
    lineup = Image.new("RGBA", (sum(s.w + 4 for s in lineup_sprites) + cast.SCARLET_BROOM.w + 4, 16), bg + (255,))
    x = 2
    for spr in lineup_sprites:
        lineup.alpha_composite(spr.img(0), (x, 16 - spr.h))
        x += spr.w + 4
    lineup.alpha_composite(cast.SCARLET_BROOM.img(0), (x, 3))
    pad = 10
    width = max(sum(t.width + pad for t in r) for r in rows) + pad
    lt = led(lineup, cell=10)
    width = max(width, lt.width + 2 * pad)
    height = sum(max(t.height for t in r) + pad for r in rows) + lt.height + 2 * pad
    out = Image.new("RGB", (width, height), (40, 40, 48))
    y = pad
    for r in rows:
        x = pad
        for t in r:
            out.paste(t, (x, y))
            x += t.width + pad
        y += max(t.height for t in r) + pad
    out.paste(lt, (pad, y + pad))
    out.save(path)
    print(f"wrote {path}")


def review(module_name: str, out_dir: Path, every: float | None = None) -> None:
    """Render a scene and write a strip of its keyframes (or every N seconds)."""
    import importlib
    from busybar.canvas import FPS
    m = importlib.import_module(f"scenes.{module_name}")
    frames = m.render()
    if every:
        picks = [int(i * every * FPS) for i in range(int(len(frames) / (every * FPS)) + 1)]
    else:
        picks = [int(s * FPS) for s, _ in m.KEYFRAMES]
    p = out_dir / f"review_{module_name}.png"
    strip(frames, picks, p)
    print(f"{module_name}: {len(frames)} frames -> {p}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["sprites"]:
        sheet(Path(sys.argv[2] if len(sys.argv) > 2 else "sprites.png"))
    elif sys.argv[1:2] == ["cast"]:
        cast_sheet(Path(sys.argv[2] if len(sys.argv) > 2 else "cast.png"))
    elif sys.argv[1:2] == ["scene"]:
        review(sys.argv[2], Path(sys.argv[3] if len(sys.argv) > 3 else "."),
               float(sys.argv[4]) if len(sys.argv) > 4 else None)
    else:
        print(__doc__)
