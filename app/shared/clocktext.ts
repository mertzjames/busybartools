// Clock card text: turns our pixel-font glyph tables into XPM2 bitmaps (docs/DECISIONS.md D10),
// and reads local wall time from the bar's /api/time timestamp (D7).
//
// Drawing order matches renderer/font.py and the mockup exactly: for every lit glyph pixel the
// shadow goes 1 px down-right first, then the gradient color, so all three render identically.

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

const DAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
const MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
const SCREEN_W = 72;

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

/** Renders `text` centered on the 72 px screen as an XPM2 bitmap (transparent background). */
export function textBitmap(text: string, font: Font, spec: TextSpec): Bitmap {
  const tw = textWidth(text, font);
  const width = tw + 1; // +1 for the shadow column
  const height = font.height + 1; // +1 for the shadow row
  const grid: string[][] = [];
  for (let y = 0; y < height; y++) {
    const row: string[] = [];
    for (let x = 0; x < width; x++) row.push(".");
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
  return { data: lines.join("\n"), width, height, x: Math.floor((SCREEN_W - tw) / 2), y: spec.y };
}

export interface WallClock {
  hhmm: string;
  date: string;
  /** Milliseconds until the minute changes. */
  msToNextMinute: number;
}

const pad = (n: number) => (n < 10 ? "0" : "") + n;

/**
 * Parses the bar's ISO 8601 local timestamp (e.g. "2026-11-26T18:05:42+04:00"). The wall-clock fields
 * are already local to the bar's timezone, so no offset math is needed for display.
 */
export function parseWallClock(iso: string): WallClock | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})/.exec(iso);
  if (!m) return null;
  const y = Number(m[1]);
  const mo = Number(m[2]);
  const d = Number(m[3]);
  const h = Number(m[4]);
  const mi = Number(m[5]);
  const s = Number(m[6]);
  const weekday = new Date(Date.UTC(y, mo - 1, d)).getUTCDay();
  return {
    hhmm: pad(h) + ":" + pad(mi),
    date: DAYS[weekday] + " " + d + " " + MONTHS[mo - 1],
    msToNextMinute: (60 - s) * 1000,
  };
}

/** Adds one minute to "HH:MM" (used when the minute rolls over mid-card without another request). */
export function nextMinute(hhmm: string): string {
  let h = Number(hhmm.slice(0, 2));
  let m = Number(hhmm.slice(3, 5)) + 1;
  if (m === 60) {
    m = 0;
    h = (h + 1) % 24;
  }
  return pad(h) + ":" + pad(m);
}
