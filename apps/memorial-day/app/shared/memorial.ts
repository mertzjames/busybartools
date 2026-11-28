// Memorial Day card, flag and playlist logic: pure functions of the bar's local time (docs/DECISIONS.md D5, D9).
//
// Shared by the app (main.ts), the mockup (renderer/build.py inlines this file, type-stripped, with the kit's
// walltime.ts and holidays.ts) and the tests (tests/logic.test.mts), so all three show the same flag and words on
// the same dates. Card text is returned as styles + strings; main.ts maps each style to a TextSpec from LAYOUT.

import { HOLIDAYS, daysLabel, nextOccurrence } from "./vendor/busybar/holidays.ts";
import { formatDate, pad2, type LocalTime } from "./vendor/busybar/walltime.ts";

/** Text styles, matching LAYOUT in renderer/scenes/text.py. */
export type Style = "time" | "date" | "head" | "sub" | "word" | "upper" | "lower";

export interface TextLine {
  style: Style;
  text: string;
}

export interface TextPage {
  ms: number;
  lines: TextLine[];
}

/** A playlist step (structurally the show runner's Step). */
export type PlayStep = { kind: "scene"; scene: number } | { kind: "card"; card: string };

/**
 * Holiday mode (START): "off" follows the calendar; "morning" and "afternoon" preview Memorial Day before and after
 * noon on any date. Each press moves to the next mode: off, morning, afternoon, off (D9).
 */
export type Mode = "off" | "morning" | "afternoon";

export const MODES: readonly Mode[] = ["off", "morning", "afternoon"];

export function nextMode(mode: Mode): Mode {
  return MODES[(MODES.indexOf(mode) + 1) % MODES.length];
}

/** The flag is raised from half-staff to full staff at noon, local time (D5). */
export const NOON_HOUR = 12;

export const CLOCK_TIME_MS = 4500;
export const CLOCK_DATE_MS = 3500;
export const COUNT_MS = 6000;
export const WORD_MS = 4000;
export const PAIR_MS = 5000;

const word = (text: string): TextPage => ({ ms: WORD_MS, lines: [{ style: "word", text }] });

/** Days from t's date to the next Memorial Day (the last Monday of May): 0 on the day. */
export function daysToMemorialDay(t: LocalTime): number {
  const occ = nextOccurrence(t, HOLIDAYS.memorialDay);
  return occ ? occ.days : 0; // the rule always has a date
}

/** True on Memorial Day itself, or any day in holiday mode. */
export function isMemorialDay(t: LocalTime, mode: Mode = "off"): boolean {
  return mode !== "off" || daysToMemorialDay(t) === 0;
}

/**
 * Whether the flag flies at half-staff: from the start of Memorial Day until noon, then full staff for the rest of
 * the day. Every other day it flies at full staff, its normal position (D6). Holiday mode forces the morning or the
 * afternoon of the day.
 */
export function halfStaff(t: LocalTime, mode: Mode = "off"): boolean {
  if (mode === "morning") return true;
  if (mode === "afternoon") return false;
  return daysToMemorialDay(t) === 0 && t.hour < NOON_HOUR;
}

/** The clock card: the time, then the date. */
export function clockPages(t: LocalTime): TextPage[] {
  return [
    { ms: CLOCK_TIME_MS, lines: [{ style: "time", text: pad2(t.hour) + ":" + pad2(t.minute) }] },
    { ms: CLOCK_DATE_MS, lines: [{ style: "date", text: formatDate(t) }] },
  ];
}

/** The countdown card: "186 DAYS" / "TO MEMORIAL DAY" (after the day it counts to next year's). */
export function countPages(t: LocalTime): TextPage[] {
  return [{
    ms: COUNT_MS,
    lines: [{ style: "head", text: daysLabel(daysToMemorialDay(t)) }, { style: "sub", text: "TO MEMORIAL DAY" }],
  }];
}

/** The flag's page on the day: half-staff until noon, then full staff. */
export function flagPage(t: LocalTime, mode: Mode = "off"): TextPage {
  const half = halfStaff(t, mode);
  return {
    ms: PAIR_MS,
    lines: half
      ? [{ style: "head", text: "HALF-STAFF" }, { style: "sub", text: "UNTIL NOON" }]
      : [{ style: "head", text: "FULL STAFF" }, { style: "sub", text: "RAISED AT NOON" }],
  };
}

/**
 * The on-the-day cards, taken in turn by the count slots in the playlist: MEMORIAL DAY, then a few words (D7). The
 * cycle has four count slots, so the fourth (after the memorial wall, whose caption is WE REMEMBER) shows the first
 * card again: HONOR AND REMEMBER (D14).
 */
export function dayCards(t: LocalTime, mode: Mode = "off"): TextPage[][] {
  return [
    [word("MEMORIAL DAY"),
      { ms: PAIR_MS, lines: [{ style: "upper", text: "HONOR AND" }, { style: "lower", text: "REMEMBER" }] }],
    [word("MEMORIAL DAY"), word("WE REMEMBER")],
    [word("MEMORIAL DAY"), flagPage(t, mode)],
  ];
}

/** Card names: "clock", "count" (the countdown), and "day0".."day2" (the on-the-day cards). */
export const DAY_CARD_NAMES = ["day0", "day1", "day2"];

/** The pages of any card by name, at time t. */
export function cardPages(name: string, t: LocalTime, mode: Mode = "off"): TextPage[] {
  if (name === "clock") return clockPages(t);
  const day = DAY_CARD_NAMES.indexOf(name);
  return day >= 0 ? dayCards(t, mode)[day] : countPages(t);
}

/** The flag scene's two variants, by .anim name (renderer/scenes/flag.py). */
export const FLAG_HALF = "flag_half";
export const FLAG_FULL = "flag_full";

/**
 * One cycle of the show: scene, clock, scene, count, ... The first scene is the flag: the half-staff variant on the
 * morning of Memorial Day, the full-staff one otherwise; the other variant is skipped. On the day (or in holiday
 * mode) the count slots become the day cards in turn. `scenes` is SHOW.scenes (names in show order).
 */
export function playlist(scenes: readonly { name: string }[], t: LocalTime, mode: Mode = "off"): PlayStep[] {
  const skip = halfStaff(t, mode) ? FLAG_FULL : FLAG_HALF;
  const day = isMemorialDay(t, mode);
  const steps: PlayStep[] = [];
  let n = 0;
  let slot = 0;
  scenes.forEach((s, i) => {
    if (s.name === skip) return;
    steps.push({ kind: "scene", scene: i });
    if (n++ % 2 === 0) steps.push({ kind: "card", card: "clock" });
    else steps.push({ kind: "card", card: day ? DAY_CARD_NAMES[slot++ % DAY_CARD_NAMES.length] : "count" });
  });
  return steps;
}
