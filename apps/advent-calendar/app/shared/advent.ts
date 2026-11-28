// Advent Calendar logic: pure functions of the bar's local time, unit-tested in tests/advent.test.mts and mirrored
// by the mockup (tests check both agree). docs/DECISIONS.md D5-D7.
//
// Seasons, by the bar's local date:
//   pre        Jan 1 - Nov 30   winter scene + "N DAYS / TO ADVENT"
//   advent     Dec 1 - Dec 23   door + day N + "N DAYS / TO CHRISTMAS"
//   eve        Dec 24           door + day 24 + "HH:MM / TO GO" (time left until midnight)
//   christmas  Dec 25           door + finale + "MERRY / CHRISTMAS"
//   post       Dec 26 - Dec 31  finale + "SEE YOU / NEXT YEAR!"

import { daysUntil, pad2, secondsToMidnight, type LocalTime } from "./vendor/busybar/walltime.ts";

export type Season = "pre" | "advent" | "eve" | "christmas" | "post";
export type Style = "date" | "head" | "sub" | "top" | "bot";

export interface Line {
  text: string;
  style: Style;
}

export type Step =
  | { kind: "door"; day: number }
  | { kind: "scene"; day: number } // day 1..25; 0 = the out-of-season winter scene
  | { kind: "card" };

/** The day of the finale vignette. */
export const FINALE = 25;

export function season(t: LocalTime): Season {
  if (t.month < 12) return "pre";
  if (t.day <= 23) return "advent";
  if (t.day === 24) return "eve";
  if (t.day === 25) return "christmas";
  return "post";
}

/** How many doors are open: 0 before December, the date in Dec 1-25, all 25 afterwards. */
export function openedDays(t: LocalTime): number {
  const s = season(t);
  if (s === "pre") return 0;
  if (s === "post") return FINALE;
  return t.day;
}

/** "DEC 7": the date written into the door at the start of each loop. */
export function dateLabel(day: number): string {
  return "DEC " + day;
}

const plural = (n: number, unit: string) => n + " " + unit + (n === 1 ? "" : "S");

/** The countdown card for the bar's current time (always about today, even while browsing older days). */
export function cardLines(t: LocalTime): Line[] {
  switch (season(t)) {
    case "pre":
      return [
        { text: plural(daysUntil(t, t.year, 12, 1), "DAY"), style: "head" },
        { text: "TO ADVENT", style: "sub" },
      ];
    case "advent":
      return [
        { text: plural(daysUntil(t, t.year, 12, 25), "DAY"), style: "head" },
        { text: "TO CHRISTMAS", style: "sub" },
      ];
    case "eve": {
      const minutes = Math.ceil(secondsToMidnight(t) / 60);
      return [
        { text: pad2(Math.floor(minutes / 60)) + ":" + pad2(minutes % 60), style: "head" },
        { text: "TO GO", style: "sub" },
      ];
    }
    case "christmas":
      return [
        { text: "MERRY", style: "top" },
        { text: "CHRISTMAS", style: "bot" },
      ];
    default:
      return [
        { text: "SEE YOU", style: "top" },
        { text: "NEXT YEAR!", style: "bot" },
      ];
  }
}

/** Milliseconds until cardLines(t) next changes: the next minute on Christmas Eve, otherwise midnight. */
export function msUntilCardChange(t: LocalTime): number {
  if (season(t) === "eve") return (60 - t.second) * 1000;
  return secondsToMidnight(t) * 1000;
}

/**
 * One pass of the show. `view` is a browsed day (1..25), or null to follow today. Browsing always opens that day's
 * door; following today skips the door when there is no new door to open (before Advent, and after Christmas).
 */
export function cycleSteps(t: LocalTime, view: number | null): Step[] {
  if (view !== null) return [{ kind: "door", day: view }, { kind: "scene", day: view }, { kind: "card" }];
  switch (season(t)) {
    case "pre":
      return [{ kind: "scene", day: 0 }, { kind: "card" }];
    case "post":
      return [{ kind: "scene", day: FINALE }, { kind: "card" }];
    default:
      return [{ kind: "door", day: t.day }, { kind: "scene", day: t.day }, { kind: "card" }];
  }
}

/**
 * The encoder: step through the opened days (1..openedDays), clamped at both ends. Returns the new view, where
 * null means "today" (landing on today's date in season goes back to following it).
 */
export function browse(t: LocalTime, view: number | null, delta: number): number | null {
  const opened = openedDays(t);
  if (opened === 0) return null;
  const current = view ?? opened;
  const next = Math.max(1, Math.min(opened, current + delta));
  if (season(t) !== "post" && next === t.day) return null;
  if (season(t) === "post" && view === null && next === current) return null;
  return next;
}
