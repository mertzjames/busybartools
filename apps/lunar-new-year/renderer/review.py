"""Review helpers for this app: a sprite contact sheet and LED-style strips.

    python3 renderer/review.py sprites previews/sprites.png
    python3 renderer/review.py scene dragon_dance previews/ [every_seconds [start end]]
    python3 renderer/review.py zodiac previews/          (all 12 zodiac scenes, three moments each, one strip)
    python3 renderer/review.py cards previews/           (the clock and count cards with live text)
    python3 renderer/review.py all previews/             (every scene + the cards, at their keyframes)

Strips are tone-mapped with the build's GAMMA, so they look like what the bar shows. Card strips include the live
text drawn exactly as the app draws it.
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
    """Contact sheet of every sprite frame, on the zodiac backdrop color."""
    import sprites
    from busybar.canvas import blit
    import lnyfx

    tiles = []
    for s in sprites.ALL:
        for i in range(len(s)):
            bg = Image.new("RGBA", (s.w + 2, s.h + 2), lnyfx.WINE_BOTTOM + (255,))
            blit(bg, s.img(i), 1, 1)
            tiles.append(led(bg, cell=8))
    pad = 8
    cols = 6
    tw = max(t.width for t in tiles)
    th = max(t.height for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad) + pad), (40, 40, 48))
    for i, t in enumerate(tiles):
        out.paste(t, (pad + (i % cols) * (tw + pad), pad + (i // cols) * (th + pad)))
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print(f"wrote {path} ({len(tiles)} frames)")


def frames_of(name: str):
    import build
    from scenes import ALL_SCENES
    m = next(s for s in ALL_SCENES if s.NAME == name)
    return m, [build.tone(f.convert("RGB")) for f in m.render()]


def review(name: str, out_dir: Path, every: float | None = None, start: float = 0.0,
           end: float | None = None) -> Path:
    """Render a scene and write a strip of its keyframes (or every N seconds, optionally within start..end)."""
    from busybar.canvas import FPS
    m, frames = frames_of(name)
    if every:
        stop = len(frames) / FPS if end is None else end
        picks = [int((start + i * every) * FPS) for i in range(int(round((stop - start) / every)) + 1)]
    else:
        picks = [int(s * FPS) for s, _ in m.KEYFRAMES]
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"review_{name}.png"
    strip(frames, picks, p, cell=9)
    print(f"{name}: {len(frames)} frames -> {p}")
    return p


def zodiac(out_dir: Path) -> Path:
    """All twelve zodiac scenes: walking in, the name, the action."""
    from busybar.canvas import FPS
    from scenes import ZODIAC_SCENES
    rows = []
    for m in ZODIAC_SCENES:
        import build
        frames = [build.tone(f.convert("RGB")) for f in m.render()]
        tiles = [led(frames[int(s * FPS)], cell=6) for s in (0.8, 2.6, 4.6)]
        row = Image.new("RGB", (sum(t.width for t in tiles) + 4 * 6, tiles[0].height + 6), (40, 40, 48))
        x = 6
        for t in tiles:
            row.paste(t, (x, 3))
            x += t.width + 6
        rows.append(row)
    out = Image.new("RGB", (rows[0].width, sum(r.height for r in rows)), (40, 40, 48))
    y = 0
    for r in rows:
        out.paste(r, (0, y))
        y += r.height
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "review_zodiac.png"
    out.save(p)
    print(f"zodiac -> {p}")
    return p


def cards(out_dir: Path) -> Path:
    """The cards as the bar draws them, for several dates."""
    import build
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = build.card_previews()
    p = out_dir / "review_cards.png"
    strip(frames, list(range(len(frames))), p, cell=9)
    print(f"cards -> {p}")
    return p


if __name__ == "__main__":
    arg = sys.argv[1:2]
    out = Path(sys.argv[2] if len(sys.argv) > 2 else ".")
    if arg == ["sprites"]:
        sheet(Path(sys.argv[2] if len(sys.argv) > 2 else "sprites.png"))
    elif arg == ["scene"]:
        review(sys.argv[2], Path(sys.argv[3] if len(sys.argv) > 3 else "."),
               float(sys.argv[4]) if len(sys.argv) > 4 else None,
               float(sys.argv[5]) if len(sys.argv) > 5 else 0.0,
               float(sys.argv[6]) if len(sys.argv) > 6 else None)
    elif arg == ["zodiac"]:
        zodiac(out)
    elif arg == ["cards"]:
        cards(out)
    elif arg == ["all"]:
        from scenes import PLAYLIST
        for mod in PLAYLIST:
            review(mod.NAME, out)
        zodiac(out)
        cards(out)
    else:
        print(__doc__)
