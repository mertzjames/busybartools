// Easter card and playlist logic: pure functions of the bar's local time (docs/DECISIONS.md D8, D9).
//
// Shared by the app (main.ts), the mockup (renderer/build.py inlines this file, type-stripped, with the kit's
// walltime.ts and holidays.ts) and the tests (tests/logic.test.mts), so all three show the same words on the same
// dates. Card text is returned as styles + strings; main.ts maps each style to a TextSpec from the generated LAYOUT.

import { HOLIDAYS, daysLabel, nextOccurrence } from "./vendor/busybar/holidays.ts";
import { formatDate, pad2, type LocalTime } from "./vendor/busybar/walltime.ts";

/** Text styles, matching LAYOUT in renderer/scenes/text.py. */
export type Style = "time" | "date" | "head" | "sub" | "top" | "bot";

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
export const HAPPY_MS = 4500;
export const EXTRA_MS = 4000;

const HAPPY: TextPage = { ms: HAPPY_MS, lines: [{ style: "top", text: "HAPPY" }, { style: "bot", text: "EASTER" }] };
const extra = (head: string, sub: string): TextPage => ({
  ms: EXTRA_MS,
  lines: [{ style: "head", text: head }, { style: "sub", text: sub }],
});

/**
 * The on-the-day cards, one per count slot in the playlist: HAPPY / EASTER, then a cheerful extra page
 * (docs/DECISIONS.md D8).
 */
export const DAY_CARDS: TextPage[][] = [
  [HAPPY, extra("EGG HUNT", "TIME!")],
  [HAPPY, extra("HOPPY", "EASTER!")],
  [HAPPY, extra("SPRING IS", "HERE!")],
];

/** Card names: "clock", "count" (the countdown), and "day0".."day2" (the on-the-day cards). */
export const DAY_CARD_NAMES = DAY_CARDS.map((_, i) => "day" + i);

/** Days from t's date to the next Western Easter Sunday (the kit's computus): 0 on the day. */
export function daysToEaster(t: LocalTime): number {
  const occ = nextOccurrence(t, HOLIDAYS.easter);
  return occ ? occ.days : 0; // the rule always has a date
}

/** True on Easter Sunday itself, or any day in holiday mode (START). */
export function isEaster(t: LocalTime, holiday: boolean): boolean {
  return holiday || daysToEaster(t) === 0;
}

/** The clock card: the time, then the date. */
export function clockPages(t: LocalTime): TextPage[] {
  return [
    { ms: CLOCK_TIME_MS, lines: [{ style: "time", text: pad2(t.hour) + ":" + pad2(t.minute) }] },
    { ms: CLOCK_DATE_MS, lines: [{ style: "date", text: formatDate(t) }] },
  ];
}

/** The countdown card: "122 DAYS" / "TO EASTER" (after the day it counts to next year's). */
export function countPages(t: LocalTime): TextPage[] {
  return [{
    ms: COUNT_MS,
    lines: [{ style: "head", text: daysLabel(daysToEaster(t)) }, { style: "sub", text: "TO EASTER" }],
  }];
}

/** The pages of any card by name, at time t. */
export function cardPages(name: string, t: LocalTime): TextPage[] {
  if (name === "clock") return clockPages(t);
  const day = DAY_CARD_NAMES.indexOf(name);
  return day >= 0 ? DAY_CARDS[day] : countPages(t);
}

/** The backdrop for a card: the clock's, the countdown's, or the holiday's (the day cards). */
export function cardBackdrop(name: string): "clock_bg" | "count_bg" | "day_bg" {
  if (name === "clock") return "clock_bg";
  return DAY_CARD_NAMES.includes(name) ? "day_bg" : "count_bg";
}

/**
 * One cycle of the show: scene, clock, scene, count, ... On Easter (or in holiday mode) the count slots become the
 * day cards in turn. `fromCard` starts the cycle at the first count slot, so pressing START shows the effect at
 * once (the cycle is rotated, not shortened).
 */
export function playlist(scenes: number, t: LocalTime, holiday: boolean, fromCard = false): PlayStep[] {
  const day = isEaster(t, holiday);
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
