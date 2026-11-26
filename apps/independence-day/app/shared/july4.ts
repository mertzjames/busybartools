// Independence Day card and playlist logic: pure functions of the bar's local time (docs/DECISIONS.md D6-D9).
//
// Shared by the app (main.ts), the mockup (renderer/build.py inlines this file, type-stripped, with the kit's
// walltime.ts and holidays.ts) and the tests (tests/logic.test.mts), so all three show the same words at the same
// times. Card text is returned as styles + strings; main.ts maps each style to a TextSpec from the generated LAYOUT.

import { HOLIDAYS, daysLabel, nextOccurrence } from "../../../../lib/ts/busybar/holidays.ts";
import { addSeconds, formatDate, pad2, type LocalTime } from "../../../../lib/ts/busybar/walltime.ts";

/** Text styles, matching LAYOUT in renderer/scenes/text.py. */
export type Style = "time" | "date" | "head" | "sub" | "lead" | "num";

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

export const CLOCK_TIME_MS = 4500;
export const CLOCK_DATE_MS = 3500;
export const COUNT_MS = 6000;
export const GREETING_MS = 4500;
export const FIREWORKS_MS = 5500;

/**
 * Dusk on the Fourth, when the fireworks start: 21:00 bar-local time (D7). A fixed hour for now; a settings option
 * or a sunset estimate can replace it later.
 */
export const DUSK_HOUR = 21;
export const DUSK_MINUTE = 0;

/** In demo mode (START twice) the cards show the Fourth at this time of day, so the last minutes can be reviewed. */
export const DEMO_HOUR = 20;
export const DEMO_MINUTE = 58;

/** The names of the two count-slot cards: "count" (the days before) and "day" (the Fourth itself). */
export const COUNT_CARD = "count";
export const DAY_CARD = "day";

/** Days from t's date to the next Fourth of July: 0 on the day, 364 or 365 the day after. */
export function daysToJuly4(t: LocalTime): number {
  const occ = nextOccurrence(t, HOLIDAYS.independenceDay);
  return occ ? occ.days : 0; // a fixed date always has an occurrence
}

/** True on July 4 itself, or any day in holiday mode (START). */
export function isJuly4(t: LocalTime, holiday: boolean): boolean {
  return holiday || daysToJuly4(t) === 0;
}

/** Seconds from t to dusk on t's own date; zero or negative once dusk has passed. */
export function secondsToDusk(t: LocalTime): number {
  return DUSK_HOUR * 3600 + DUSK_MINUTE * 60 - (t.hour * 3600 + t.minute * 60 + t.second);
}

/**
 * The fireworks countdown, "HH:MM" of hours and minutes until dusk, rounded up to the minute: "00:01" during the
 * last minute and "21:00" at midnight. Null once dusk has come. The runner redraws a card line each time the
 * minute rolls over (at second 0), so the count steps down exactly on the minute.
 */
export function fireworksIn(t: LocalTime): string | null {
  const s = secondsToDusk(t);
  if (s <= 0) return null;
  const m = Math.ceil(s / 60);
  return pad2(Math.floor(m / 60)) + ":" + pad2(m % 60);
}

/** The clock card: the time, then the date. */
export function clockPages(t: LocalTime): TextPage[] {
  return [
    { ms: CLOCK_TIME_MS, lines: [{ style: "time", text: pad2(t.hour) + ":" + pad2(t.minute) }] },
    { ms: CLOCK_DATE_MS, lines: [{ style: "date", text: formatDate(t) }] },
  ];
}

/** The countdown card: "221 DAYS" / "TO JULY 4TH" (after the day it counts to next year's). */
export function countPages(t: LocalTime): TextPage[] {
  return [{
    ms: COUNT_MS,
    lines: [{ style: "head", text: daysLabel(daysToJuly4(t)) }, { style: "sub", text: "TO JULY 4TH" }],
  }];
}

/**
 * The Fourth's own card, for any time of that day: HAPPY / 4TH OF JULY, then FIREWORKS IN / HH:MM until dusk, and
 * ENJOY THE / FIREWORKS! after it. Always two pages of two lines, so a minute rollover during the card (the runner
 * recomputes each line by page and line index) moves straight from "00:01" to the after-dusk words.
 */
export function dayPages(t: LocalTime): TextPage[] {
  const count = fireworksIn(t);
  return [
    { ms: GREETING_MS, lines: [{ style: "head", text: "HAPPY" }, { style: "sub", text: "4TH OF JULY" }] },
    {
      ms: FIREWORKS_MS,
      lines: count === null
        ? [{ style: "lead", text: "ENJOY THE" }, { style: "num", text: "FIREWORKS!" }]
        : [{ style: "lead", text: "FIREWORKS IN" }, { style: "num", text: count }],
    },
  ];
}

/** The pages of any card by name, at time t. */
export function cardPages(name: string, t: LocalTime): TextPage[] {
  if (name === "clock") return clockPages(t);
  if (name === DAY_CARD) return dayPages(t);
  return countPages(t);
}

/**
 * One cycle of the show: scene, clock, scene, count, ... On the Fourth (or in holiday mode) the count slots become
 * the day card. `dense` (demo mode) puts the day card after every scene, with no clock, so the fireworks countdown
 * comes round every 20 seconds or so. `fromCard` starts the cycle at the first count slot, so pressing START shows
 * the change at once (the cycle is rotated, not shortened).
 */
export function playlist(scenes: number, t: LocalTime, holiday: boolean, fromCard = false, dense = false): PlayStep[] {
  const day = isJuly4(t, holiday);
  const steps: PlayStep[] = [];
  for (let i = 0; i < scenes; i++) {
    steps.push({ kind: "scene", scene: i });
    if (dense) steps.push({ kind: "card", card: DAY_CARD });
    else if (i % 2 === 0) steps.push({ kind: "card", card: "clock" });
    else steps.push({ kind: "card", card: day ? DAY_CARD : COUNT_CARD });
  }
  if (!fromCard) return steps;
  const first = steps.findIndex((s) => s.kind === "card" && s.card !== "clock");
  return first < 0 ? steps : steps.slice(first).concat(steps.slice(0, first));
}

/** Seconds from a to b (both wall-clock times; offset-free calendar arithmetic). */
export function secondsBetween(a: LocalTime, b: LocalTime): number {
  const ms = (t: LocalTime) => Date.UTC(t.year, t.month - 1, t.day, t.hour, t.minute, t.second);
  return Math.round((ms(b) - ms(a)) / 1000);
}

/**
 * Demo mode: the shift, in whole minutes, that moves `anchor` (the bar's time when demo mode began) to July 4 of
 * its year at DEMO_HOUR:DEMO_MINUTE, keeping its seconds. Whole minutes keep the shifted clock's minute rollovers
 * on the bar's own, which is when the runner redraws card lines. Apply it with demoTime().
 */
export function demoShift(anchor: LocalTime): number {
  return secondsBetween(anchor, {
    year: anchor.year, month: 7, day: 4, hour: DEMO_HOUR, minute: DEMO_MINUTE, second: anchor.second,
  });
}

/** The time the cards show in demo mode. */
export function demoTime(t: LocalTime, shift: number): LocalTime {
  return addSeconds(t, shift);
}
