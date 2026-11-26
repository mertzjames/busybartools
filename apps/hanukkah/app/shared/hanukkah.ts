// Hanukkah logic: pure functions of the bar's local time, unit-tested in tests/logic.test.mts and mirrored by the
// mockup (the tests check that both agree). docs/DECISIONS.md D2-D4, D7.
//
// The first candle is lit on the evening of HOLIDAYS.hanukkah (the day before 25 Kislev). The bar has no sunset
// table, so 17:00 local stands in for sundown: each evening's new candle appears at 17:00 and the count stays at 8
// through the eighth day. A span of 9 calendar days covers the first evening through the last day.
//
//   before    more than a day to go         "18 DAYS" / "TO HANUKKAH"
//   tomorrow  the day before the first evening   "TOMORROW" / "HANUKKAH BEGINS"
//   tonight   the first evening's date, before 17:00   "TONIGHT" / "HANUKKAH BEGINS"
//   during    1-8 candles                    "NIGHT 3" / "HAPPY HANUKKAH", then "NIGHT 3" / "CHAG SAMEACH"
//
// After the last day, nextOccurrence moves on to next year's Hanukkah, so the count starts again.

import { HOLIDAYS, daysLabel, nextOccurrence, type LocalTime } from "./kit.ts";

export const SUNDOWN_HOUR = 17;
export const SPAN_DAYS = 9;

export type Season = "before" | "tomorrow" | "tonight" | "during";
export type Entry = { kind: "scene"; name: string } | { kind: "card"; card: "clock" | "count" };

/** Tonight's candle count (0-8, not counting the shamash) for the bar's local time. */
export function candles(t: LocalTime): number {
  const occ = nextOccurrence(t, HOLIDAYS.hanukkah, SPAN_DAYS);
  if (!occ || occ.dayOf === 0) return 0;
  return Math.min(8, occ.dayOf - 1 + (t.hour >= SUNDOWN_HOUR ? 1 : 0));
}

/** Days until the first evening (0 on its date, negative during). */
export function daysToHanukkah(t: LocalTime): number {
  const occ = nextOccurrence(t, HOLIDAYS.hanukkah, SPAN_DAYS);
  return occ ? occ.days : 0;
}

/** The candle count to show: the holiday-mode preview night (1-8) when set, otherwise tonight's. */
export function night(t: LocalTime, preview: number): number {
  return preview > 0 ? preview : candles(t);
}

export function season(t: LocalTime, preview: number): Season {
  if (night(t, preview) > 0) return "during";
  const days = daysToHanukkah(t);
  if (days === 0) return "tonight";
  if (days === 1) return "tomorrow";
  return "before";
}

/** The count card's pages, each [headline, small line]. */
export function countPages(t: LocalTime, preview: number): [string, string][] {
  const n = night(t, preview);
  switch (season(t, preview)) {
    case "during":
      return [["NIGHT " + n, "HAPPY HANUKKAH"], ["NIGHT " + n, "CHAG SAMEACH"]];
    case "tonight":
      return [["TONIGHT", "HANUKKAH BEGINS"]];
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
export function playlist(t: LocalTime, preview: number): Entry[] {
  const n = night(t, preview);
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
