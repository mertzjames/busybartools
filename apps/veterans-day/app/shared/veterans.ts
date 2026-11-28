// Veterans Day dates, card texts, the 11:00 moment and the playlist: pure functions of the bar's local time
// (docs/DECISIONS.md D5, D6, D7, D9).
//
// Shared by the app (main.ts), the mockup (renderer/build.py inlines this file, type-stripped, with the kit's
// walltime.ts and holidays.ts) and the tests (tests/logic.test.mts), so all three show the same words on the same
// dates. Card text is returned as styles + strings; main.ts maps each style to a TextSpec from LAYOUT.
// Top-level names are prefixed or app-specific: the mockup pastes the kit files and this one into one scope.

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
 * Holiday mode (START): "off" follows the calendar; "day" previews Veterans Day on any date; "moment" previews the
 * 11:00 moment (the moment card opens every cycle, then the day's playlist). Each press moves to the next mode:
 * off, day, moment, off (D9).
 */
export type Mode = "off" | "day" | "moment";

export const MODES: readonly Mode[] = ["off", "day", "moment"];

export function nextMode(mode: Mode): Mode {
  return MODES[(MODES.indexOf(mode) + 1) % MODES.length];
}

/** The armistice took effect at the 11th hour of the 11th day of the 11th month: 11:00 local on Nov 11 (D6). */
export const VET_MOMENT_HOUR = 11;
/** The timer that starts the moment fires this long after 11:00:00, so a slightly early timer still lands inside. */
export const VET_MOMENT_DELAY_MS = 2000;
/** A timer is armed only when 11:00 is closer than this (cycles re-arm it, so it never runs for hours). */
export const VET_MOMENT_ARM_MS = 10 * 60 * 1000;

export const CLOCK_TIME_MS = 4500;
export const CLOCK_DATE_MS = 3500;
export const COUNT_MS = 6000;
export const WORD_MS = 4000;
export const PAIR_MS = 5000;
export const MOMENT_PAGE_MS = 5000;

const word = (text: string): TextPage => ({ ms: WORD_MS, lines: [{ style: "word", text }] });
const pair = (upper: string, lower: string): TextPage =>
  ({ ms: PAIR_MS, lines: [{ style: "upper", text: upper }, { style: "lower", text: lower }] });

/** Days from t's date to the next Veterans Day (Nov 11): 0 on the day. */
export function daysToVeteransDay(t: LocalTime): number {
  const occ = nextOccurrence(t, HOLIDAYS.veteransDay);
  return occ ? occ.days : 0; // a fixed date always has an occurrence
}

/** True on Veterans Day itself, or any day in holiday mode. */
export function isVeteransDay(t: LocalTime, mode: Mode = "off"): boolean {
  return mode !== "off" || daysToVeteransDay(t) === 0;
}

/**
 * The 11:00 moment: true from 11:00:00 to 11:00:59 on Nov 11 by the bar's wall clock (10:59 and 11:01 are outside),
 * or always in "moment" mode.
 */
export function inMoment(t: LocalTime, mode: Mode = "off"): boolean {
  if (mode === "moment") return true;
  return daysToVeteransDay(t) === 0 && t.hour === VET_MOMENT_HOUR && t.minute === 0;
}

/**
 * Milliseconds until the app should start a new cycle for the moment (11:00:00 plus VET_MOMENT_DELAY_MS), or null
 * when that is not today, already past, or further away than VET_MOMENT_ARM_MS.
 */
export function msToMoment(t: LocalTime): number | null {
  if (daysToVeteransDay(t) !== 0) return null;
  const s = (VET_MOMENT_HOUR * 3600) - (t.hour * 3600 + t.minute * 60 + t.second);
  if (s <= 0) return null;
  const ms = s * 1000 + VET_MOMENT_DELAY_MS;
  return ms <= VET_MOMENT_ARM_MS ? ms : null;
}

/** The clock card: the time, then the date. */
export function clockPages(t: LocalTime): TextPage[] {
  return [
    { ms: CLOCK_TIME_MS, lines: [{ style: "time", text: pad2(t.hour) + ":" + pad2(t.minute) }] },
    { ms: CLOCK_DATE_MS, lines: [{ style: "date", text: formatDate(t) }] },
  ];
}

/** The countdown card: "350 DAYS" / "TO VETERANS DAY" (after the day it counts to next year's). */
export function countPages(t: LocalTime): TextPage[] {
  return [{
    ms: COUNT_MS,
    lines: [{ style: "head", text: daysLabel(daysToVeteransDay(t)) }, { style: "sub", text: "TO VETERANS DAY" }],
  }];
}

/** The on-the-day cards, one per count slot in the playlist: VETERANS DAY, then a few words of thanks (D7). */
export function dayCards(): TextPage[][] {
  return [
    [word("VETERANS DAY"), pair("THANK YOU", "VETERANS")],
    [word("VETERANS DAY"), pair("HONOR ALL", "WHO SERVED")],
    [word("VETERANS DAY"),
      { ms: PAIR_MS, lines: [{ style: "head", text: "THANK YOU" }, { style: "sub", text: "FOR YOUR SERVICE" }] }],
  ];
}

/** The 11:00 moment card: the 11th hour, day and month, the armistice of 1918, and thanks (D6). */
export function momentPages(): TextPage[] {
  const ms = MOMENT_PAGE_MS;
  return [
    { ms, lines: [{ style: "word", text: "11TH HOUR" }] },
    { ms, lines: [{ style: "upper", text: "11TH DAY" }, { style: "lower", text: "11TH MONTH" }] },
    { ms, lines: [{ style: "head", text: "ARMISTICE" }, { style: "sub", text: "NOV 11 1918" }] },
    { ms, lines: [{ style: "upper", text: "THANK YOU" }, { style: "lower", text: "VETERANS" }] },
  ];
}

/** Card names: "clock", "count" (the countdown), "day0".."day2" (the on-the-day cards) and "moment" (11:00). */
export const DAY_CARD_NAMES = ["day0", "day1", "day2"];
export const MOMENT_CARD = "moment";

/** The pages of any card by name, at time t. */
export function cardPages(name: string, t: LocalTime): TextPage[] {
  if (name === "clock") return clockPages(t);
  if (name === MOMENT_CARD) return momentPages();
  const day = DAY_CARD_NAMES.indexOf(name);
  return day >= 0 ? dayCards()[day] : countPages(t);
}

/**
 * One cycle of the show: scene, clock, scene, count, ... On the day (or in holiday mode) the count slots become the
 * day cards in turn. A cycle that starts during the 11:00 moment opens with the moment card (D6). `scenes` is
 * SHOW.scenes (names in show order).
 */
export function playlist(scenes: readonly { name: string }[], t: LocalTime, mode: Mode = "off"): PlayStep[] {
  const day = isVeteransDay(t, mode);
  const steps: PlayStep[] = inMoment(t, mode) ? [{ kind: "card", card: MOMENT_CARD }] : [];
  let slot = 0;
  scenes.forEach((_, i) => {
    steps.push({ kind: "scene", scene: i });
    if (i % 2 === 0) steps.push({ kind: "card", card: "clock" });
    else steps.push({ kind: "card", card: day ? DAY_CARD_NAMES[slot++ % DAY_CARD_NAMES.length] : "count" });
  });
  return steps;
}
