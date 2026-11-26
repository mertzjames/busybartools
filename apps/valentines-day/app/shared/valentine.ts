// Valentine's Day card and playlist logic: pure functions of the bar's local time (docs/DECISIONS.md D8, D9).
//
// Shared by the app (main.ts), the mockup (renderer/build.py inlines this file, type-stripped, with the kit's
// walltime.ts and holidays.ts) and the tests (tests/logic.test.mts), so all three show the same words on the same
// dates. Card text is returned as styles + strings; main.ts maps each style to a TextSpec from the generated LAYOUT.

import { HOLIDAYS, daysLabel, nextOccurrence } from "../../../../lib/ts/busybar/holidays.ts";
import { formatDate, pad2, type LocalTime } from "../../../../lib/ts/busybar/walltime.ts";

/** Text styles, matching LAYOUT in renderer/scenes/text.py. */
export type Style = "time" | "date" | "head" | "sub" | "candy";

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
export const CANDY_MS = 3000;

/** The countdown's second line ("TO VALENTINE'S DAY" fits the tiny font with 3 px to spare; D7). */
export const COUNT_SUB = "TO VALENTINE'S DAY";

const greeting: TextPage = {
  ms: GREETING_MS,
  lines: [{ style: "head", text: "HAPPY" }, { style: "sub", text: "VALENTINE'S DAY" }],
};
const candy = (text: string): TextPage => ({ ms: CANDY_MS, lines: [{ style: "candy", text }] });

/**
 * The on-the-day cards, one per count slot in the playlist: the greeting, then two candy-heart phrases. Short,
 * generic and sweet (docs/DECISIONS.md D2); each fits between the backdrop's two candy hearts (48 px).
 */
export const DAY_CARDS: TextPage[][] = [
  [greeting, candy("BE MINE"), candy("XOXO")],
  [greeting, candy("HUG ME"), candy("LOVE YOU")],
  [greeting, candy("BE TRUE"), candy("SO SWEET")],
];

/** Card names: "clock", "count" (the countdown), and "day0".."day2" (the on-the-day cards). */
export const DAY_CARD_NAMES = DAY_CARDS.map((_, i) => "day" + i);

/** Days from t's date to the next Valentine's Day (Feb 14): 0 on the day. */
export function daysToValentines(t: LocalTime): number {
  const occ = nextOccurrence(t, HOLIDAYS.valentinesDay);
  return occ ? occ.days : 0; // a fixed date always has an occurrence
}

/** True on Valentine's Day itself, or any day in holiday mode (START). */
export function isValentinesDay(t: LocalTime, holiday: boolean): boolean {
  return holiday || daysToValentines(t) === 0;
}

/** The clock card: the time, then the date. */
export function clockPages(t: LocalTime): TextPage[] {
  return [
    { ms: CLOCK_TIME_MS, lines: [{ style: "time", text: pad2(t.hour) + ":" + pad2(t.minute) }] },
    { ms: CLOCK_DATE_MS, lines: [{ style: "date", text: formatDate(t) }] },
  ];
}

/** The countdown card: "80 DAYS" / "TO VALENTINE'S DAY" (after the day it counts to next year's). */
export function countPages(t: LocalTime): TextPage[] {
  return [{
    ms: COUNT_MS,
    lines: [{ style: "head", text: daysLabel(daysToValentines(t)) }, { style: "sub", text: COUNT_SUB }],
  }];
}

/** The pages of any card by name, at time t. */
export function cardPages(name: string, t: LocalTime): TextPage[] {
  if (name === "clock") return clockPages(t);
  const day = DAY_CARD_NAMES.indexOf(name);
  return day >= 0 ? DAY_CARDS[day] : countPages(t);
}

/**
 * One cycle of the show: scene, clock, scene, count, ... On Valentine's Day (or in holiday mode) the count slots
 * become the day cards in turn. `fromCard` starts the cycle at the first count slot, so pressing START shows the
 * effect at once (the cycle is rotated, not shortened).
 */
export function playlist(scenes: number, t: LocalTime, holiday: boolean, fromCard = false): PlayStep[] {
  const day = isValentinesDay(t, holiday);
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
