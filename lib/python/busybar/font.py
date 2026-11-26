"""Original pixel fonts.

- BIG:   7 px tall, variable width (headlines baked into scenes; the clock card's date)
- TINY:  5 px tall, 3 px wide (small captions)
- CLOCK: 12 px tall, 7 px wide digits with 2 px strokes (the live 24-hour clock)

The same glyph tables are exported to JSON (export_json) so an app's on-device JS and its
browser mockup draw identical text. Apps add their own glyphs or fonts with register_font()
instead of editing this shared module. Characters missing from a font are skipped silently.
"""

from __future__ import annotations

from .canvas import mix, put


def _parse(table: str, rows: int) -> dict[str, list[str]]:
    """Glyph table format: a line with the character in brackets, then `rows` lines of '#'/'.'."""
    glyphs: dict[str, list[str]] = {}
    lines = [ln.rstrip() for ln in table.strip("\n").splitlines()]
    i = 0
    while i < len(lines):
        ln = lines[i].strip()
        if not ln:
            i += 1
            continue
        assert ln.startswith("[") and ln.endswith("]"), f"bad glyph header {ln!r}"
        ch = ln[1:-1]
        ch = " " if ch == "space" else ch
        g = [r.strip() for r in lines[i + 1:i + 1 + rows]]
        assert len(g) == rows and len({len(r) for r in g}) == 1, f"glyph {ch!r} malformed"
        glyphs[ch] = g
        i += 1 + rows
    return glyphs


BIG = _parse("""
[A]
.###.
#...#
#...#
#####
#...#
#...#
#...#
[B]
####.
#...#
#...#
####.
#...#
#...#
####.
[C]
.###.
#...#
#....
#....
#....
#...#
.###.
[D]
####.
#...#
#...#
#...#
#...#
#...#
####.
[E]
#####
#....
#....
####.
#....
#....
#####
[F]
#####
#....
#....
####.
#....
#....
#....
[G]
.###.
#...#
#....
#.###
#...#
#...#
.####
[H]
#...#
#...#
#...#
#####
#...#
#...#
#...#
[I]
###
.#.
.#.
.#.
.#.
.#.
###
[J]
..###
...#.
...#.
...#.
#..#.
#..#.
.##..
[K]
#...#
#..#.
#.#..
##...
#.#..
#..#.
#...#
[L]
#....
#....
#....
#....
#....
#....
#####
[M]
#...#
##.##
#.#.#
#.#.#
#...#
#...#
#...#
[N]
#...#
#...#
##..#
#.#.#
#..##
#...#
#...#
[O]
.###.
#...#
#...#
#...#
#...#
#...#
.###.
[P]
####.
#...#
#...#
####.
#....
#....
#....
[Q]
.###.
#...#
#...#
#...#
#.#.#
#..#.
.##.#
[R]
####.
#...#
#...#
####.
#.#..
#..#.
#...#
[S]
.####
#....
#....
.###.
....#
....#
####.
[T]
#####
..#..
..#..
..#..
..#..
..#..
..#..
[U]
#...#
#...#
#...#
#...#
#...#
#...#
.###.
[V]
#...#
#...#
#...#
#...#
#...#
.#.#.
..#..
[W]
#...#
#...#
#...#
#.#.#
#.#.#
#.#.#
.#.#.
[X]
#...#
#...#
.#.#.
..#..
.#.#.
#...#
#...#
[Y]
#...#
#...#
.#.#.
..#..
..#..
..#..
..#..
[Z]
#####
....#
...#.
..#..
.#...
#....
#####
[0]
.###.
#...#
#..##
#.#.#
##..#
#...#
.###.
[1]
.#.
##.
.#.
.#.
.#.
.#.
###
[2]
.###.
#...#
....#
...#.
..#..
.#...
#####
[3]
####.
....#
....#
.###.
....#
....#
####.
[4]
...#.
..##.
.#.#.
#..#.
#####
...#.
...#.
[5]
#####
#....
####.
....#
....#
#...#
.###.
[6]
.###.
#....
#....
####.
#...#
#...#
.###.
[7]
#####
....#
...#.
..#..
.#...
.#...
.#...
[8]
.###.
#...#
#...#
.###.
#...#
#...#
.###.
[9]
.###.
#...#
#...#
.####
....#
....#
.###.
[!]
#
#
#
#
#
.
#
[.]
.
.
.
.
.
.
#
[,]
..
..
..
..
..
.#
#.
[:]
.
.
#
.
.
#
.
[-]
...
...
...
###
...
...
...
[']
#
#
.
.
.
.
.
[?]
.###.
#...#
....#
...#.
..#..
.....
..#..
[space]
...
...
...
...
...
...
...
""", 7)

TINY = _parse("""
[A]
.#.
#.#
###
#.#
#.#
[B]
##.
#.#
##.
#.#
##.
[C]
.##
#..
#..
#..
.##
[D]
##.
#.#
#.#
#.#
##.
[E]
###
#..
##.
#..
###
[F]
###
#..
##.
#..
#..
[G]
.##
#..
#.#
#.#
.##
[H]
#.#
#.#
###
#.#
#.#
[I]
###
.#.
.#.
.#.
###
[J]
..#
..#
..#
#.#
.#.
[K]
#.#
#.#
##.
#.#
#.#
[L]
#..
#..
#..
#..
###
[M]
#.#
###
###
#.#
#.#
[N]
##.
#.#
#.#
#.#
#.#
[O]
.#.
#.#
#.#
#.#
.#.
[P]
##.
#.#
##.
#..
#..
[Q]
.#.
#.#
#.#
##.
.##
[R]
##.
#.#
##.
#.#
#.#
[S]
.##
#..
.#.
..#
##.
[T]
###
.#.
.#.
.#.
.#.
[U]
#.#
#.#
#.#
#.#
###
[V]
#.#
#.#
#.#
#.#
.#.
[W]
#.#
#.#
###
###
#.#
[X]
#.#
#.#
.#.
#.#
#.#
[Y]
#.#
#.#
.#.
.#.
.#.
[Z]
###
..#
.#.
#..
###
[0]
###
#.#
#.#
#.#
###
[1]
.#.
##.
.#.
.#.
###
[2]
##.
..#
.#.
#..
###
[3]
##.
..#
.#.
..#
##.
[4]
#.#
#.#
###
..#
..#
[5]
###
#..
##.
..#
##.
[6]
.##
#..
###
#.#
###
[7]
###
..#
.#.
.#.
.#.
[8]
###
#.#
###
#.#
###
[9]
###
#.#
###
..#
##.
[!]
#
#
#
.
#
[.]
.
.
.
.
#
[:]
.
#
.
#
.
[-]
...
...
###
...
...
[?]
##.
..#
.#.
...
.#.
[']
#
#
.
.
.
[space]
..
..
..
..
..
""", 5)

CLOCK = _parse("""
[0]
.#####.
#######
##...##
##...##
##...##
##...##
##...##
##...##
##...##
##...##
#######
.#####.
[1]
...##..
..###..
.####..
...##..
...##..
...##..
...##..
...##..
...##..
...##..
.######
.######
[2]
.#####.
#######
##...##
.....##
....###
...###.
..###..
.###...
###....
##.....
#######
#######
[3]
.#####.
#######
##...##
.....##
.....##
..####.
..####.
.....##
.....##
##...##
#######
.#####.
[4]
....##.
...###.
..####.
.##.##.
##..##.
##..##.
#######
#######
....##.
....##.
....##.
....##.
[5]
#######
#######
##.....
##.....
######.
#######
.....##
.....##
.....##
##...##
#######
.#####.
[6]
.#####.
#######
##...##
##.....
######.
#######
##...##
##...##
##...##
##...##
#######
.#####.
[7]
#######
#######
.....##
....##.
....##.
...##..
...##..
..##...
..##...
..##...
..##...
..##...
[8]
.#####.
#######
##...##
##...##
##...##
.#####.
.#####.
##...##
##...##
##...##
#######
.#####.
[9]
.#####.
#######
##...##
##...##
##...##
#######
.######
.....##
.....##
##...##
#######
.#####.
[:]
..
..
..
##
##
..
..
##
##
..
..
..
""", 12)

FONTS = {"big": (BIG, 7, 1), "tiny": (TINY, 5, 1), "clock": (CLOCK, 12, 1)}


def register_font(name: str, table, height: int, gap: int = 1, extend: bool = False) -> None:
    """Add an app-local font, or extra glyphs for an existing one, without editing this shared module.

    table:  a glyph table string in the format above ("[A]" then `height` rows of '#'/'.'), or {char: [rows]}.
    extend: merge the glyphs into the existing font `name` (its height must match) instead of replacing it.

        register_font("big", {"+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."]}, 7, extend=True)
        register_font("snow", SNOW_TABLE, 9)        # a new font, exported by export_json() too
    """
    glyphs = _parse(table, height) if isinstance(table, str) else {k: list(v) for k, v in table.items()}
    for ch, rows in glyphs.items():
        assert len(rows) == height and len({len(r) for r in rows}) == 1, f"{name}: glyph {ch!r} malformed"
    if extend:
        base, base_h, base_gap = FONTS[name]
        assert base_h == height, f"{name}: extend height {height} != {base_h}"
        FONTS[name] = ({**base, **glyphs}, base_h, base_gap)
    else:
        FONTS[name] = (glyphs, height, gap)


def text_width(text: str, font: str = "big") -> int:
    glyphs, _, gap = FONTS[font]
    widths = [len(glyphs[c][0]) for c in text.upper() if c in glyphs]
    return sum(widths) + gap * max(0, len(widths) - 1)


def draw_text(img, text: str, x: int, y: int, color, font: str = "big", shadow=None,
              alpha: float = 1.0, gradient=None, reveal: int | None = None) -> int:
    """Draw text; returns the x after the last glyph.

    gradient: optional (top_color, bottom_color) vertical gradient instead of `color`.
    shadow: optional color drawn 1 px down-right first.
    reveal: draw only the first N columns (for wipe-in effects).
    """
    glyphs, rows, gap = FONTS[font]
    cx = x
    col = 0
    for ch in text.upper():
        g = glyphs.get(ch)
        if g is None:
            continue
        for gy, row in enumerate(g):
            c = color
            if gradient:
                c = mix(gradient[0], gradient[1], gy / max(1, rows - 1))
            for gx, bit in enumerate(row):
                if bit != "#":
                    continue
                if reveal is not None and col + gx >= reveal:
                    continue
                if shadow is not None:
                    put(img, cx + gx + 1, y + gy + 1, shadow, alpha)
                put(img, cx + gx, y + gy, c, alpha)
        cx += len(g[0]) + gap
        col += len(g[0]) + gap
    return cx - gap


def export_json(names=None) -> dict:
    """Glyph tables for the JS app and mockup: {font: {height, gap, glyphs: {ch: [rows]}}}.

    names: export only these fonts (default: every registered font), to keep generated TS small.
    """
    return {name: {"height": rows, "gap": gap, "glyphs": glyphs} for name, (glyphs, rows, gap) in FONTS.items()
            if names is None or name in names}
