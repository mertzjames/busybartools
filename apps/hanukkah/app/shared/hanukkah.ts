// Hanukkah logic: pure functions of the bar's local time, unit-tested in tests/logic.test.mts and mirrored by the
// mockup (the tests check that both agree). docs/DECISIONS.md D2, D4, D7, D11.
//
// The first candle is lit on the evening of HOLIDAYS.hanukkah (the day before 25 Kislev). Each evening's new candle
// appears at that date's candle time (D11): sunset at the bar's location setting, or estimated from the bar's time
// zone, unless the "Candle time" setting picks a fixed hour. The count stays at 8 through the eighth day. A span of
// 9 calendar days covers the first evening through the last day.
//
//   before    more than a day to go         "18 DAYS" / "TO HANUKKAH"
//   tomorrow  the day before the first evening   "TOMORROW" / "HANUKKAH BEGINS"
//   tonight   the first evening's date, before candle time   "TONIGHT" / "HANUKKAH BEGINS", then "CANDLES AT 16:28"
//   during    1-8 candles                    "NIGHT 3" / "HAPPY HANUKKAH", then "NIGHT 3" / "CHAG SAMEACH"
//
// After the last day, nextOccurrence moves on to next year's Hanukkah, so the count starts again.

import {
  HOLIDAYS, daysLabel, enumValue, hhmmFromMinutes, locationFromOffset, nextOccurrence, readGeolocation, sunTimes,
  usDst, type GeoPoint, type LocalTime,
} from "./kit.ts";

export const SPAN_DAYS = 9;

/** The "Candle time" setting's options (app/src/appmeta/settings.json). */
export const SUNDOWN_OPTIONS = ["sunset", "16:00", "16:30", "17:00", "17:30", "18:00"] as const;
export type Sundown = (typeof SUNDOWN_OPTIONS)[number];

/** Used when there is nothing to compute a sunset from (no offset in the timestamp, or a polar night). */
export const FALLBACK_MINUTES = 17 * 60;

/** What decides the candle time: the settings, and the bar's UTC offset in minutes (null if unknown). */
export interface Sky {
  sundown: Sundown;
  location: GeoPoint | null;
  offset: number | null;
}

/** The "sunset by time zone" default, before settings or the bar's offset are known. */
export const DEFAULT_SKY: Sky = { sundown: "sunset", location: null, offset: null };

/** loadSettings defaults (app/src/appmeta/settings.json): sunset, at whatever location the bar has. */
export const SETTINGS_DEFAULTS: { sundown: string; location: unknown } = { sundown: "sunset", location: null };

/** The candle-time rule from the stored settings and the bar's UTC offset (null if its timestamp had none). */
export function skyFromSettings(values: { sundown: unknown; location: unknown }, offset: number | null): Sky {
  return {
    sundown: enumValue(values.sundown, SUNDOWN_OPTIONS, "sunset"),
    location: readGeolocation(values.location),
    offset,
  };
}

/** Candle time on t's date, in minutes after local midnight. */
export function sundownFor(t: LocalTime, sky: Sky): number {
  if (sky.sundown !== "sunset") {
    const [h, m] = sky.sundown.split(":").map(Number);
    return h * 60 + m;
  }
  if (sky.offset === null) return FALLBACK_MINUTES;
  const at = sky.location ?? locationFromOffset(sky.offset, usDst(t.year, t.month, t.day));
  const sunset = sunTimes(t.year, t.month, t.day, at, sky.offset).sunset;
  return sunset === null ? FALLBACK_MINUTES : sunset;
}

export type Season = "before" | "tomorrow" | "tonight" | "during";
export type Entry = { kind: "scene"; name: string } | { kind: "card"; card: "clock" | "count" };

/** Tonight's candle count (0-8, not counting the shamash) for the bar's local time. */
export function candles(t: LocalTime, sky: Sky): number {
  const occ = nextOccurrence(t, HOLIDAYS.hanukkah, SPAN_DAYS);
  if (!occ || occ.dayOf === 0) return 0;
  const lit = t.hour * 60 + t.minute >= sundownFor(t, sky) ? 1 : 0;
  return Math.min(8, occ.dayOf - 1 + lit);
}

/** Days until the first evening (0 on its date, negative during). */
export function daysToHanukkah(t: LocalTime): number {
  const occ = nextOccurrence(t, HOLIDAYS.hanukkah, SPAN_DAYS);
  return occ ? occ.days : 0;
}

/** The candle count to show: the holiday-mode preview night (1-8) when set, otherwise tonight's. */
export function night(t: LocalTime, preview: number, sky: Sky): number {
  return preview > 0 ? preview : candles(t, sky);
}

export function season(t: LocalTime, preview: number, sky: Sky): Season {
  if (night(t, preview, sky) > 0) return "during";
  const days = daysToHanukkah(t);
  if (days === 0) return "tonight";
  if (days === 1) return "tomorrow";
  return "before";
}

/** The count card's pages, each [headline, small line]. */
export function countPages(t: LocalTime, preview: number, sky: Sky): [string, string][] {
  const n = night(t, preview, sky);
  switch (season(t, preview, sky)) {
    case "during":
      return [["NIGHT " + n, "HAPPY HANUKKAH"], ["NIGHT " + n, "CHAG SAMEACH"]];
    case "tonight":
      return [["TONIGHT", "HANUKKAH BEGINS"], ["TONIGHT", "CANDLES AT " + hhmmFromMinutes(sundownFor(t, sky))]];
    case "tomorrow":
      return [["TOMORROW", "HANUKKAH BEGINS"]];
    default:
      return [[daysLabel(daysToHanukkah(t)), "TO HANUKKAH"]];
  }
}

/**
 * One cycle of the show. The count card opens it, then scenes alternate with the clock and count cards. The
 * menorah and the window show tonight's candles; the finale plays only while candles are lit.
 */
export function playlist(t: LocalTime, preview: number, sky: Sky): Entry[] {
  const n = night(t, preview, sky);
  const scenes = ["menorah_" + n, "dreidel", "latkes", "sufganiyot", "gelt", "window_" + n];
  if (n > 0) scenes.push("finale");
  const out: Entry[] = [{ kind: "card", card: "count" }];
  scenes.forEach((name, i) => {
    out.push({ kind: "scene", name });
    if (i < scenes.length - 1) out.push({ kind: "card", card: i % 2 ? "count" : "clock" });
  });
  out.push({ kind: "card", card: "clock" });
  return out;
}

/** START in holiday mode: night 1, 2, ... 8, then back to following the date (0). */
export function nextPreview(preview: number): number {
  return preview >= 8 ? 0 : preview + 1;
}
