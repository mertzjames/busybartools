// Pixel-font text -> XPM2 bitmaps for the BUSY Bar `xpmbitmap` element (shared render kit).
//
// Fonts come from the Python render kit (lib/python/busybar/font.py, exported into each app's generated TS),
// so the app, its mockup and its renderer draw identical text. Drawing order matches font.draw_text exactly:
// for every lit glyph pixel the shadow goes 1 px down-right first, then the gradient color.
// Limits from the firmware: <= 32 colors (this uses font.height + 2), width/height within the display.

export interface TextSpec {
  font: string;
  y: number;
  top: readonly number[];
  bottom: readonly number[];
  shadow: readonly number[];
}

export interface Font {
  height: number;
  gap: number;
  glyphs: Record<string, string[]>;
}

export interface Bitmap {
  data: string;
  width: number;
  height: number;
  x: number;
  y: number;
}

/** Front display width in pixels. */
export const SCREEN_W = 72;

function hex2(n: number): string {
  const s = Math.max(0, Math.min(255, Math.round(n))).toString(16).toUpperCase();
  return s.length < 2 ? "0" + s : s;
}

function rgb(c: readonly number[]): string {
  return "#" + hex2(c[0]) + hex2(c[1]) + hex2(c[2]);
}

function mix(a: readonly number[], b: readonly number[], t: number): number[] {
  return [0, 1, 2].map((k) => Math.round(a[k] + (b[k] - a[k]) * t));
}

/** Width in pixels of `text` in `font` (characters missing from the font are skipped). */
export function textWidth(text: string, font: Font): number {
  let w = 0;
  let n = 0;
  for (let i = 0; i < text.length; i++) {
    const g = font.glyphs[text[i]];
    if (!g) continue;
    w += g[0].length;
    n++;
  }
  return w + font.gap * Math.max(0, n - 1);
}

/**
 * Renders `text` as an XPM2 bitmap with a transparent background, a vertical gradient (spec.top -> spec.bottom)
 * and a 1 px shadow. Horizontally centered on the 72 px screen unless `x` is given.
 */
export function textBitmap(text: string, font: Font, spec: TextSpec, x?: number): Bitmap {
  const tw = textWidth(text, font);
  const width = tw + 1; // +1 for the shadow column
  const height = font.height + 1; // +1 for the shadow row
  const grid: string[][] = [];
  for (let y = 0; y < height; y++) {
    const row: string[] = [];
    for (let xx = 0; xx < width; xx++) row.push(".");
    grid.push(row);
  }
  // Palette: '.' none, '#' shadow, 'a'.. one per glyph row (vertical gradient).
  const rowChar = (gy: number) => String.fromCharCode(97 + gy);
  let cx = 0;
  for (let i = 0; i < text.length; i++) {
    const g = font.glyphs[text[i]];
    if (!g) continue;
    for (let gy = 0; gy < g.length; gy++) {
      const line = g[gy];
      for (let gx = 0; gx < line.length; gx++) {
        if (line[gx] !== "#") continue;
        grid[gy + 1][cx + gx + 1] = "#";
        grid[gy][cx + gx] = rowChar(gy);
      }
    }
    cx += g[0].length + font.gap;
  }
  const colors = [". c none", "# c " + rgb(spec.shadow)];
  for (let gy = 0; gy < font.height; gy++) {
    colors.push(rowChar(gy) + " c " + rgb(mix(spec.top, spec.bottom, gy / Math.max(1, font.height - 1))));
  }
  const lines = ["! XPM2", `${width} ${height} ${colors.length} 1`].concat(colors);
  for (let y = 0; y < height; y++) lines.push(grid[y].join(""));
  return { data: lines.join("\n"), width, height, x: x ?? Math.floor((SCREEN_W - tw) / 2), y: spec.y };
}
