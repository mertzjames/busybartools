// Halloween card and playlist logic: pure functions of the bar's local time (docs/DECISIONS.md D8, D9).
//
// Shared by the app (main.ts), the mockup (renderer/build.py inlines this file, type-stripped, with the kit's
// walltime.ts and holidays.ts) and the tests (tests/logic.test.mts), so all three show the same words on the same
// dates. Card text is returned as styles + strings; main.ts maps each style to a TextSpec from the generated LAYOUT.
//
// Names here share one scope with walltime.ts and holidays.ts in the mockup, so app-level constants carry an HW_
// prefix (a repeated top-level name would be a SyntaxError there).

import { HOLIDAYS, nextOccurrence } from "./vendor/busybar/holidays.ts";
import { formatDate, pad2, type LocalTime } from "./vendor/busybar/walltime.ts";

/** Text styles, matching LAYOUT in renderer/scenes/text.py. */
export type Style = "time" | "date" | "head" | "sub" | "hi" | "lo" | "boo";

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

export const HW_CLOCK_TIME_MS = 4500;
export const HW_CLOCK_DATE_MS = 3500;
export const HW_COUNT_MS = 6000;
export const HW_GREETING_MS = 5000;
export const HW_PHRASE_MS = 3500;

/** The countdown's second line (tiny font). */
export const HW_COUNT_SUB = "TO HALLOWEEN";

/** "1 NIGHT" / "30 NIGHTS": Halloween is a night, so the countdown counts nights (D7). */
export function nightsLabel(n: number): string {
  return n + (n === 1 ? " NIGHT" : " NIGHTS");
}

const greeting: TextPage = {
  ms: HW_GREETING_MS,
  lines: [{ style: "hi", text: "HAPPY" }, { style: "lo", text: "HALLOWEEN" }],
};
const two = (a: string, b: string): TextPage => ({
  ms: HW_PHRASE_MS,
  lines: [{ style: "hi", text: a }, { style: "lo", text: b }],
});
const one = (text: string): TextPage => ({ ms: HW_PHRASE_MS, lines: [{ style: "boo", text }] });

/**
 * The on-the-day cards, one per count slot in the playlist: the greeting, then a spooky-fun phrase (D2). Every
 * big line fits between the count backdrop's corner art (56 px, shadow included; the tests check it).
 */
export const DAY_CARDS: TextPage[][] = [
  [greeting, two("TRICK OR", "TREAT!")],
  [greeting, one("BOO!")],
  [greeting, two("SPOOKY", "SEASON")],
  [greeting, two("HAPPY", "HAUNTING")],
];

/** Card names: "clock", "count" (the countdown), and "day0".."day3" (the on-the-day cards). */
export const DAY_CARD_NAMES = DAY_CARDS.map((_, i) => "day" + i);

/** Nights (days) from t's date to the next Halloween (Oct 31): 0 on the day. */
export function nightsToHalloween(t: LocalTime): number {
  const occ = nextOccurrence(t, HOLIDAYS.halloween);
  return occ ? occ.days : 0; // a fixed date always has an occurrence
}

/** True on Halloween itself, or any day in holiday mode (START). */
export function isHalloween(t: LocalTime, holiday: boolean): boolean {
  return holiday || nightsToHalloween(t) === 0;
}

/** The clock card: the time, then the date. */
export function clockPages(t: LocalTime): TextPage[] {
  return [
    { ms: HW_CLOCK_TIME_MS, lines: [{ style: "time", text: pad2(t.hour) + ":" + pad2(t.minute) }] },
    { ms: HW_CLOCK_DATE_MS, lines: [{ style: "date", text: formatDate(t) }] },
  ];
}

/**
 * The countdown card: "30 NIGHTS" / "TO HALLOWEEN" ("1 NIGHT" the night before; after the day it counts to next
 * year's). On the day itself (where the playlist shows the day cards instead) it is the greeting.
 */
export function countPages(t: LocalTime): TextPage[] {
  const n = nightsToHalloween(t);
  if (n === 0) return [greeting];
  return [{ ms: HW_COUNT_MS, lines: [{ style: "head", text: nightsLabel(n) }, { style: "sub", text: HW_COUNT_SUB }] }];
}

/** The pages of any card by name, at time t. */
export function cardPages(name: string, t: LocalTime): TextPage[] {
  if (name === "clock") return clockPages(t);
  const day = DAY_CARD_NAMES.indexOf(name);
  return day >= 0 ? DAY_CARDS[day] : countPages(t);
}

/**
 * One cycle of the show: scene, clock, scene, count, ... On Halloween (or in holiday mode) the count slots become
 * the day cards in turn. `fromCard` starts the cycle at the first count slot, so pressing START shows the effect at
 * once (the cycle is rotated, not shortened).
 */
export function playlist(scenes: number, t: LocalTime, holiday: boolean, fromCard = false): PlayStep[] {
  const day = isHalloween(t, holiday);
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
