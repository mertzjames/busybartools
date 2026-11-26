// Juneteenth card and playlist logic: pure functions of the bar's local time (docs/DECISIONS.md D8, D10).
//
// Shared by the app (main.ts), the mockup (renderer/build.py inlines this file, type-stripped, with the kit's
// walltime.ts and holidays.ts) and the tests (tests/logic.test.mts), so all three show the same words on the same
// dates. Card text is returned as styles + strings; main.ts maps each style to a TextSpec from the generated LAYOUT.

import { HOLIDAYS, daysLabel, nextOccurrence } from "../../../../lib/ts/busybar/holidays.ts";
import { formatDate, pad2, type LocalTime } from "../../../../lib/ts/busybar/walltime.ts";

/** Text styles, matching LAYOUT in renderer/scenes/text.py. */
export type Style = "time" | "date" | "head" | "sub" | "mid" | "top" | "bot";

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
export const DAY_PAGE_MS = 4500;

const page = (...lines: [string, Style][]): TextPage => ({
  ms: DAY_PAGE_MS,
  lines: lines.map(([text, style]) => ({ style, text })),
});

/**
 * The on-the-day cards, one per count slot in the playlist, taking turns (docs/DECISIONS.md D8):
 * JUNETEENTH, then FREEDOM DAY / JUNE 19; and HAPPY / JUNETEENTH, then CELEBRATE / FREEDOM.
 */
export const DAY_CARDS: TextPage[][] = [
  [page(["JUNETEENTH", "mid"]), page(["FREEDOM DAY", "head"], ["JUNE 19", "sub"])],
  [page(["HAPPY", "top"], ["JUNETEENTH", "bot"]), page(["CELEBRATE", "head"], ["FREEDOM", "sub"])],
];

/** Card names: "clock", "count" (the countdown), and "day0", "day1" (the on-the-day cards). */
export const DAY_CARD_NAMES = DAY_CARDS.map((_, i) => "day" + i);

/** Days from t's date to the next June 19 (the kit's HOLIDAYS.juneteenth): 0 on the day. */
export function daysToJuneteenth(t: LocalTime): number {
  const occ = nextOccurrence(t, HOLIDAYS.juneteenth);
  return occ ? occ.days : 0; // a fixed date always has one
}

/** True on June 19 itself, or any day in holiday mode (START). */
export function isJuneteenth(t: LocalTime, holiday: boolean): boolean {
  return holiday || daysToJuneteenth(t) === 0;
}

/** The clock card: the time, then the date. */
export function clockPages(t: LocalTime): TextPage[] {
  return [
    { ms: CLOCK_TIME_MS, lines: [{ style: "time", text: pad2(t.hour) + ":" + pad2(t.minute) }] },
    { ms: CLOCK_DATE_MS, lines: [{ style: "date", text: formatDate(t) }] },
  ];
}

/** The countdown card: "205 DAYS" / "TO JUNETEENTH" (after the day it counts to next year's). */
export function countPages(t: LocalTime): TextPage[] {
  return [{
    ms: COUNT_MS,
    lines: [{ style: "head", text: daysLabel(daysToJuneteenth(t)) }, { style: "sub", text: "TO JUNETEENTH" }],
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
 * One cycle of the show: scene, clock, scene, count, ... On June 19 (or in holiday mode) the count slots become the
 * day cards in turn. The scenes always play in order: the solemn opening first, then the celebration.
 */
export function playlist(scenes: number, t: LocalTime, holiday: boolean): PlayStep[] {
  const day = isJuneteenth(t, holiday);
  const steps: PlayStep[] = [];
  let slot = 0;
  for (let i = 0; i < scenes; i++) {
    steps.push({ kind: "scene", scene: i });
    if (i % 2 === 0) steps.push({ kind: "card", card: "clock" });
    else steps.push({ kind: "card", card: day ? DAY_CARD_NAMES[slot++ % DAY_CARD_NAMES.length] : "count" });
  }
  return steps;
}

/** The step START jumps to: the first count slot, so the switch to (or from) holiday mode shows at once. */
export function firstCountStep(scenes: number): number {
  return scenes > 1 ? 3 : 0;
}
