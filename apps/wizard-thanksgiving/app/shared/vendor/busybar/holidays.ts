// Holiday dates and countdowns (shared render kit).
//
// Every rule returns a calendar date [month, day] for a Gregorian year, computed with offset-free UTC arithmetic,
// so it works on the bar's local wall-clock fields (walltime.ts). Rules:
//   fixed dates              Valentine's Day, St. Patrick's Day, Juneteenth, Independence Day, Halloween, ...
//   nth weekday of a month   MLK Day, Presidents' Day, Mother's Day, Memorial Day, Father's Day, Labor Day, ...
//   Easter                   the Gregorian computus (Western Easter)
//   Hanukkah                 the arithmetic Hebrew calendar (25 Kislev), so it never needs a table update
//   Lunar New Year           a table (it depends on astronomical new moons); null outside the table

import { daysUntil, weekday, type LocalTime } from "./walltime.ts";

/** A calendar date in a year: [month 1-12, day 1-31]. */
export type MonthDay = [number, number];
export type DateRule = (year: number) => MonthDay | null;

const DAY_MS = 86400000;

/** Calendar date `days` after (month, day) of `year` (negative goes back), as [year, month, day]. */
export function shiftDate(year: number, month: number, day: number, days: number): [number, number, number] {
  const d = new Date(Date.UTC(year, month - 1, day) + days * DAY_MS);
  return [d.getUTCFullYear(), d.getUTCMonth() + 1, d.getUTCDate()];
}

/**
 * Day of the month of the nth `wd` (0 = Sunday … 6 = Saturday) in `month` of `year`. n = 1…5, or -1 for the last.
 * nthWeekday(2027, 1, 1, 3) = 18 (MLK Day 2027: the third Monday of January).
 */
export function nthWeekday(year: number, month: number, wd: number, n: number): number {
  if (n > 0) {
    const first = weekday(year, month, 1);
    return 1 + ((wd - first + 7) % 7) + (n - 1) * 7;
  }
  const last = new Date(Date.UTC(year, month, 0)).getUTCDate();
  return last - ((weekday(year, month, last) - wd + 7) % 7);
}

/** Western (Gregorian) Easter Sunday, by the anonymous Gregorian algorithm (Meeus/Jones/Butcher). */
export function easter(year: number): MonthDay {
  const a = year % 19;
  const b = Math.floor(year / 100);
  const c = year % 100;
  const d = Math.floor(b / 4);
  const e = b % 4;
  const f = Math.floor((b + 8) / 25);
  const g = Math.floor((b - f + 1) / 3);
  const h = (19 * a + b - d - g + 15) % 30;
  const i = Math.floor(c / 4);
  const k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7;
  const m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31);
  const day = ((h + l - 7 * m + 114) % 31) + 1;
  return [month, day];
}

// --- Hebrew calendar (Dershowitz & Reingold, "Calendrical Calculations") ---------------------------------------

const HEBREW_EPOCH = -1373427; // R.D. of 1 Tishri AM 1
const RD_UNIX_EPOCH = 719163; // R.D. of 1970-01-01

function hebrewElapsedDays(y: number): number {
  const months = Math.floor((235 * y - 234) / 19);
  const parts = 12084 + 13753 * months;
  const days = 29 * months + Math.floor(parts / 25920);
  return (3 * (days + 1)) % 7 < 3 ? days + 1 : days;
}

function hebrewNewYear(y: number): number {
  const ny0 = hebrewElapsedDays(y - 1);
  const ny1 = hebrewElapsedDays(y);
  const ny2 = hebrewElapsedDays(y + 1);
  const correction = ny2 - ny1 === 356 ? 2 : ny1 - ny0 === 382 ? 1 : 0;
  return HEBREW_EPOCH + ny1 + correction;
}

function rdToDate(rd: number): [number, number, number] {
  const d = new Date((rd - RD_UNIX_EPOCH) * DAY_MS);
  return [d.getUTCFullYear(), d.getUTCMonth() + 1, d.getUTCDate()];
}

/**
 * The evening the first Hanukkah candle is lit in Gregorian `year`: the day before 25 Kislev (Jewish days begin at
 * sundown). Hanukkah lasts eight nights; night n (1-8) begins on the evening of this date + (n - 1) days.
 * hanukkahFirstNight(2026) = [12, 4].
 */
export function hanukkahFirstNight(year: number): MonthDay {
  const hy = year + 3761; // the Hebrew year whose Kislev falls in this December (or late November)
  const len = hebrewNewYear(hy + 1) - hebrewNewYear(hy);
  const marheshvan = len === 355 || len === 385 ? 30 : 29;
  const kislev25 = hebrewNewYear(hy) + 30 + marheshvan + 24; // Tishri (30) + Marheshvan + 24 days into Kislev
  const [, m, d] = rdToDate(kislev25 - 1);
  return [m, d];
}

// --- Lunar New Year ---------------------------------------------------------------------------------------------

/** Lunar (Chinese) New Year's Day, [month, day] by Gregorian year. Verified against several published tables. */
export const LUNAR_NEW_YEAR: Record<number, MonthDay> = {
  2025: [1, 29], 2026: [2, 17], 2027: [2, 6], 2028: [1, 26], 2029: [2, 13], 2030: [2, 3],
  2031: [1, 23], 2032: [2, 11], 2033: [1, 31], 2034: [2, 19], 2035: [2, 8], 2036: [1, 28],
};

export const ZODIAC = ["RAT", "OX", "TIGER", "RABBIT", "DRAGON", "SNAKE", "HORSE", "GOAT", "MONKEY", "ROOSTER", "DOG",
  "PIG"];

/** The zodiac animal of the lunar year that begins in Gregorian `year` (2027 = GOAT). */
export function zodiac(year: number): string {
  return ZODIAC[(((year - 4) % 12) + 12) % 12];
}

export function lunarNewYear(year: number): MonthDay | null {
  return LUNAR_NEW_YEAR[year] ?? null;
}

// --- The holidays ----------------------------------------------------------------------------------------------

const fixed = (month: number, day: number): DateRule => () => [month, day];
const nth = (month: number, wd: number, n: number): DateRule => (year) => [month, nthWeekday(year, month, wd, n)];

/** Date rules for the holidays the apps in this repo celebrate. */
export const HOLIDAYS = {
  newYearsDay: fixed(1, 1),
  mlkDay: nth(1, 1, 3), // third Monday of January
  lunarNewYear,
  groundhogDay: fixed(2, 2),
  valentinesDay: fixed(2, 14),
  presidentsDay: nth(2, 1, 3), // third Monday of February
  stPatricksDay: fixed(3, 17),
  easter,
  mothersDay: nth(5, 0, 2), // second Sunday of May
  memorialDay: nth(5, 1, -1), // last Monday of May
  juneteenth: fixed(6, 19),
  fathersDay: nth(6, 0, 3), // third Sunday of June
  independenceDay: fixed(7, 4),
  laborDay: nth(9, 1, 1), // first Monday of September
  halloween: fixed(10, 31),
  veteransDay: fixed(11, 11),
  thanksgiving: nth(11, 4, 4), // fourth Thursday of November
  hanukkah: hanukkahFirstNight, // the evening of the first candle
  christmas: fixed(12, 25),
  kwanzaa: fixed(12, 26), // Dec 26 - Jan 1
} satisfies Record<string, DateRule>;

export type HolidayKey = keyof typeof HOLIDAYS;

export interface Occurrence {
  year: number;
  month: number;
  day: number;
  /** Days from t's date to the start: positive before, 0 on the first day, negative on later days of a span. */
  days: number;
  /** Day of the holiday t falls on (1 = first day), or 0 when t is before it. */
  dayOf: number;
}

/**
 * The occurrence of a holiday that t is in, or the next one. `spanDays` is how many calendar days it lasts
 * (Kwanzaa 7, Hanukkah 9 counting from the first evening's date); a span may cross into the next year.
 * Returns null only when the rule has no date for the years it needs (Lunar New Year outside its table).
 */
export function nextOccurrence(t: LocalTime, rule: DateRule, spanDays = 1): Occurrence | null {
  for (const year of [t.year - 1, t.year, t.year + 1]) {
    const md = rule(year);
    if (!md) continue;
    const days = daysUntil(t, year, md[0], md[1]);
    if (days > 0 || days > -spanDays) {
      return { year, month: md[0], day: md[1], days, dayOf: days > 0 ? 0 : 1 - days };
    }
  }
  return null;
}

/** "1 DAY" / "18 DAYS" for countdown cards. */
export function daysLabel(n: number): string {
  return n + (n === 1 ? " DAY" : " DAYS");
}
