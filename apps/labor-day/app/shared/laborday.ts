// Labor Day card and playlist logic: pure functions of the bar's local time (docs/DECISIONS.md D7, D8).
//
// Shared by the app (main.ts), the mockup (renderer/build.py inlines this file, type-stripped, with the kit's
// walltime.ts and holidays.ts) and the tests (tests/logic.test.mts), so all three show the same words on the same
// dates. Card text is returned as styles + strings; main.ts maps each style to a TextSpec from the generated LAYOUT.

import { HOLIDAYS, daysLabel, nextOccurrence } from "./vendor/busybar/holidays.ts";
import { formatDate, pad2, type LocalTime } from "./vendor/busybar/walltime.ts";

/** Text styles, matching LAYOUT in renderer/scenes/text.py. */
export type Style = "time" | "date" | "head" | "sub";

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
export const PHRASE_MS = 4000;

/** The holiday's name on the cards (two big lines fit: "TO LABOR DAY" is 67 px). */
export const HOLIDAY_NAME = "LABOR DAY";

const page = (ms: number, head: string, sub: string): TextPage => ({
  ms,
  lines: [{ style: "head", text: head }, { style: "sub", text: sub }],
});
const greeting = page(GREETING_MS, "HAPPY", HOLIDAY_NAME);

/**
 * The on-the-day cards, one per count slot in the playlist: the greeting, then a short phrase. A thank-you to
 * workers first, then the day off and the end of summer (docs/DECISIONS.md D2, D7).
 */
export const DAY_CARDS: TextPage[][] = [
  [greeting, page(PHRASE_MS, "THANK YOU", "WORKERS")],
  [greeting, page(PHRASE_MS, "ENJOY", "THE DAY")],
  [greeting, page(PHRASE_MS, "SO LONG", "SUMMER")],
];

/** Card names: "clock", "count" (the countdown), and "day0".."day2" (the on-the-day cards). */
export const DAY_CARD_NAMES = DAY_CARDS.map((_, i) => "day" + i);

/** Days from t's date to the next Labor Day (first Monday of September): 0 on the day. */
export function daysToLaborDay(t: LocalTime): number {
  const occ = nextOccurrence(t, HOLIDAYS.laborDay);
  return occ ? occ.days : 0; // the rule always has a date
}

/** True on Labor Day itself, or any day in holiday mode (START). */
export function isLaborDay(t: LocalTime, holiday: boolean): boolean {
  return holiday || daysToLaborDay(t) === 0;
}

/** The clock card: the time, then the date. */
export function clockPages(t: LocalTime): TextPage[] {
  return [
    { ms: CLOCK_TIME_MS, lines: [{ style: "time", text: pad2(t.hour) + ":" + pad2(t.minute) }] },
    { ms: CLOCK_DATE_MS, lines: [{ style: "date", text: formatDate(t) }] },
  ];
}

/** The countdown card: "284 DAYS" / "TO LABOR DAY" (after the day it counts to next year's). */
export function countPages(t: LocalTime): TextPage[] {
  return [page(COUNT_MS, daysLabel(daysToLaborDay(t)), "TO " + HOLIDAY_NAME)];
}

/** The pages of any card by name, at time t. */
export function cardPages(name: string, t: LocalTime): TextPage[] {
  if (name === "clock") return clockPages(t);
  const day = DAY_CARD_NAMES.indexOf(name);
  return day >= 0 ? DAY_CARDS[day] : countPages(t);
}

/**
 * One cycle of the show: scene, clock, scene, count, ... On Labor Day (or in holiday mode) the count slots become
 * the day cards in turn. `fromCard` starts the cycle at the first count slot, so pressing START shows the effect at
 * once (the cycle is rotated, not shortened).
 */
export function playlist(scenes: number, t: LocalTime, holiday: boolean, fromCard = false): PlayStep[] {
  const day = isLaborDay(t, holiday);
  const steps: PlayStep[] = [];
  let slot = 0;
  for (let i = 0; i < scenes; i++) {
    steps.push({ kind: "scene", scene: i });
    if (i % 2 === 0) steps.push({ kind: "card", card: "clock" });
    else steps.push({ kind: "card", card: day ? DAY_CARD_NAMES[slot++ % DAY_CARD_NAMES.length] : "count" });
  }
  if (!fromCard) return steps;
  const first = steps.findIndex((s) => s.kind === "card" && s.card !== "clock");
  return first < 0 ? steps : steps.slice(first).concat(steps.slice(0, first));
}
