// Father's Day card and playlist logic: pure functions of the bar's local time (docs/DECISIONS.md D7, D8).
//
// Shared by the app (main.ts), the mockup (renderer/build.py inlines this file, type-stripped, with the kit's
// walltime.ts and holidays.ts) and the tests (tests/logic.test.mts), so all three show the same words on the same
// dates. Card text is returned as styles + strings; main.ts maps each style to a TextSpec from the generated LAYOUT.

import { HOLIDAYS, daysLabel, nextOccurrence } from "./vendor/busybar/holidays.ts";
import { formatDate, pad2, type LocalTime } from "./vendor/busybar/walltime.ts";

/** Text styles, matching LAYOUT in renderer/scenes/text.py. */
export type Style = "time" | "date" | "head" | "sub" | "top" | "bot" | "word";

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
export const GREETING_MS = 5000;
export const PHRASE_MS = 4000;

/** The holiday's name on the cards: `big` on the day's greeting, `tiny` under the countdown. */
export const HOLIDAY_NAME = "FATHER'S DAY";

const greeting: TextPage = {
  ms: GREETING_MS,
  lines: [{ style: "top", text: "HAPPY" }, { style: "bot", text: HOLIDAY_NAME }],
};
const two = (top: string, bot: string): TextPage => ({
  ms: PHRASE_MS,
  lines: [{ style: "top", text: top }, { style: "bot", text: bot }],
});
const word = (text: string): TextPage => ({ ms: PHRASE_MS, lines: [{ style: "word", text }] });

/**
 * The on-the-day cards, one per count slot in the playlist: the greeting, then a short phrase. Warm and simple, with
 * one gentle fishing pun (docs/DECISIONS.md D2, D7). `BEST DAD EVER` is too wide for one line of `big`, so it
 * takes two.
 */
export const DAY_CARDS: TextPage[][] = [
  [greeting, two("BEST DAD", "EVER")],
  [greeting, word("THANKS DAD")],
  [greeting, two("REEL COOL", "DAD")],
];

/** Card names: "clock", "count" (the countdown), and "day0".."day2" (the on-the-day cards). */
export const DAY_CARD_NAMES = DAY_CARDS.map((_, i) => "day" + i);

/** Days from t's date to the next Father's Day (third Sunday of June): 0 on the day. */
export function daysToFathersDay(t: LocalTime): number {
  const occ = nextOccurrence(t, HOLIDAYS.fathersDay);
  return occ ? occ.days : 0; // the rule always has a date
}

/** True on Father's Day itself, or any day in holiday mode (START). */
export function isFathersDay(t: LocalTime, holiday: boolean): boolean {
  return holiday || daysToFathersDay(t) === 0;
}

/** The clock card: the time, then the date. */
export function clockPages(t: LocalTime): TextPage[] {
  return [
    { ms: CLOCK_TIME_MS, lines: [{ style: "time", text: pad2(t.hour) + ":" + pad2(t.minute) }] },
    { ms: CLOCK_DATE_MS, lines: [{ style: "date", text: formatDate(t) }] },
  ];
}

/** The countdown card: "206 DAYS" / "TO FATHER'S DAY" (after the day it counts to next year's). */
export function countPages(t: LocalTime): TextPage[] {
  return [{
    ms: COUNT_MS,
    lines: [{ style: "head", text: daysLabel(daysToFathersDay(t)) }, { style: "sub", text: "TO " + HOLIDAY_NAME }],
  }];
}

/** The pages of any card by name, at time t. */
export function cardPages(name: string, t: LocalTime): TextPage[] {
  if (name === "clock") return clockPages(t);
  const day = DAY_CARD_NAMES.indexOf(name);
  return day >= 0 ? DAY_CARDS[day] : countPages(t);
}

/**
 * One cycle of the show: scene, clock, scene, count, ... On Father's Day (or in holiday mode) the count slots
 * become the day cards in turn. `fromCard` starts the cycle at the first count slot, so pressing START shows the
 * effect at once (the cycle is rotated, not shortened).
 */
export function playlist(scenes: number, t: LocalTime, holiday: boolean, fromCard = false): PlayStep[] {
  const day = isFathersDay(t, holiday);
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
