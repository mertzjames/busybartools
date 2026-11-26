// St. Patrick's Day card and playlist logic: pure functions of the bar's local time (docs/DECISIONS.md D8, D9).
//
// Shared by the app (main.ts), the mockup (renderer/build.py inlines this file, type-stripped, with the kit's
// walltime.ts and holidays.ts) and the tests (tests/logic.test.mts), so all three show the same words on the same
// dates. Card text is returned as styles + strings; main.ts maps each style to a TextSpec from the generated LAYOUT.

import { HOLIDAYS, daysLabel, nextOccurrence } from "../../../../lib/ts/busybar/holidays.ts";
import { formatDate, pad2, type LocalTime } from "../../../../lib/ts/busybar/walltime.ts";

/** Text styles, matching LAYOUT in renderer/scenes/text.py. */
export type Style = "time" | "date" | "head" | "sub" | "word" | "top" | "bottom";

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
export const HAPPY_MS = 2500;
export const NAME_MS = 4000;
export const GREETING_MS = 4000;

/** Two big lines, one above the other: the name of the day, or the greeting. */
const pair = (ms: number, top: string, bottom: string): TextPage => ({
  ms, lines: [{ style: "top", text: top }, { style: "bottom", text: bottom }],
});

/**
 * The on-the-day cards, one per count slot in the playlist (they take turns): HAPPY, then ST. PATRICK'S / DAY; and
 * the greeting ERIN GO / BRAGH ("Ireland forever"), then HAPPY / ST. PATRICK'S DAY. Nothing drink-centric
 * (docs/DECISIONS.md D2, D8).
 */
export const DAY_CARDS: TextPage[][] = [
  [{ ms: HAPPY_MS, lines: [{ style: "word", text: "HAPPY" }] }, pair(NAME_MS, "ST. PATRICK'S", "DAY")],
  [pair(GREETING_MS, "ERIN GO", "BRAGH"),
    { ms: NAME_MS, lines: [{ style: "head", text: "HAPPY" }, { style: "sub", text: "ST. PATRICK'S DAY" }] }],
];

/** Card names: "clock", "count" (the countdown), and "day0", "day1" (the on-the-day cards). */
export const DAY_CARD_NAMES = DAY_CARDS.map((_, i) => "day" + i);

/** Days from t's date to the next St. Patrick's Day (March 17): 0 on the day. */
export function daysToStPatricks(t: LocalTime): number {
  const occ = nextOccurrence(t, HOLIDAYS.stPatricksDay);
  return occ ? occ.days : 0; // a fixed date: the rule always has one
}

/** True on St. Patrick's Day itself, or any day in holiday mode (START). */
export function isStPatricksDay(t: LocalTime, holiday: boolean): boolean {
  return holiday || daysToStPatricks(t) === 0;
}

/** The clock card: the time, then the date. */
export function clockPages(t: LocalTime): TextPage[] {
  return [
    { ms: CLOCK_TIME_MS, lines: [{ style: "time", text: pad2(t.hour) + ":" + pad2(t.minute) }] },
    { ms: CLOCK_DATE_MS, lines: [{ style: "date", text: formatDate(t) }] },
  ];
}

/** The countdown card: "111 DAYS" / "TO ST. PATRICK'S" (after the day it counts to next year's). */
export function countPages(t: LocalTime): TextPage[] {
  return [{
    ms: COUNT_MS,
    lines: [{ style: "head", text: daysLabel(daysToStPatricks(t)) }, { style: "sub", text: "TO ST. PATRICK'S" }],
  }];
}

/** The pages of any card by name, at time t. */
export function cardPages(name: string, t: LocalTime): TextPage[] {
  if (name === "clock") return clockPages(t);
  const day = DAY_CARD_NAMES.indexOf(name);
  return day >= 0 ? DAY_CARDS[day] : countPages(t);
}

/**
 * One cycle of the show: scene, clock, scene, count, ... On St. Patrick's Day (or in holiday mode) the count slots
 * become the day cards in turn. `fromCard` starts the cycle at the first count slot, so pressing START shows the
 * effect at once (the cycle is rotated, not shortened).
 */
export function playlist(scenes: number, t: LocalTime, holiday: boolean, fromCard = false): PlayStep[] {
  const day = isStPatricksDay(t, holiday);
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
