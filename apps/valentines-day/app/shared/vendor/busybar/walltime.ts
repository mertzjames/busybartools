// The bar's local wall-clock time, from `device.TimeGet()` (shared render kit).
//
// /api/time returns ISO 8601 with the bar's own offset, e.g. "2026-12-31T23:59:42-05:00". The wall-clock fields
// are already local to the bar, so read them directly: never use JS Date local-time methods (the runtime does
// not know the bar's time zone). Date.UTC is used only for calendar arithmetic, which is offset-free.

export interface LocalTime {
  year: number;
  month: number; // 1-12
  day: number; // 1-31
  hour: number;
  minute: number;
  second: number;
}

export interface WallClock {
  hhmm: string;
  date: string;
  /** Milliseconds until the minute changes. */
  msToNextMinute: number;
}

export const DAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
export const MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];

export const pad2 = (n: number) => (n < 10 ? "0" : "") + n;

/** Parses the wall-clock fields of the bar's ISO timestamp; null if it isn't one. */
export function parseLocal(iso: string): LocalTime | null {
  const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})/.exec(iso);
  if (!m) return null;
  return {
    year: Number(m[1]), month: Number(m[2]), day: Number(m[3]),
    hour: Number(m[4]), minute: Number(m[5]), second: Number(m[6]),
  };
}

/** Day of the week, 0 = Sunday. */
export function weekday(year: number, month: number, day: number): number {
  return new Date(Date.UTC(year, month - 1, day)).getUTCDay();
}

/** "THU 26 NOV" */
export function formatDate(t: LocalTime): string {
  return DAYS[weekday(t.year, t.month, t.day)] + " " + t.day + " " + MONTHS[t.month - 1];
}

/** Whole calendar days from t's date to (year, month, day): 0 on that day, negative after it. */
export function daysUntil(t: LocalTime, year: number, month: number, day: number): number {
  return Math.round((Date.UTC(year, month - 1, day) - Date.UTC(t.year, t.month - 1, t.day)) / 86400000);
}

/** Seconds from t to the next local midnight (86400 at exactly 00:00:00). */
export function secondsToMidnight(t: LocalTime): number {
  return 86400 - (t.hour * 3600 + t.minute * 60 + t.second);
}

/** Seconds from t to local midnight at the start of (year, month, day); negative once it has passed. */
export function secondsUntilDate(t: LocalTime, year: number, month: number, day: number): number {
  return daysUntil(t, year, month, day) * 86400 - (t.hour * 3600 + t.minute * 60 + t.second);
}

/** Adds `seconds` to a local time, carrying across days, months and years. */
export function addSeconds(t: LocalTime, seconds: number): LocalTime {
  const base = Date.UTC(t.year, t.month - 1, t.day, t.hour, t.minute, t.second) + seconds * 1000;
  const d = new Date(base);
  return {
    year: d.getUTCFullYear(), month: d.getUTCMonth() + 1, day: d.getUTCDate(),
    hour: d.getUTCHours(), minute: d.getUTCMinutes(), second: d.getUTCSeconds(),
  };
}

/** Wizarding Thanksgiving's clock card fields (kept for compatibility). */
export function parseWallClock(iso: string): WallClock | null {
  const t = parseLocal(iso);
  if (!t) return null;
  return {
    hhmm: pad2(t.hour) + ":" + pad2(t.minute),
    date: formatDate(t),
    msToNextMinute: (60 - t.second) * 1000,
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
  return pad2(h) + ":" + pad2(m);
}
