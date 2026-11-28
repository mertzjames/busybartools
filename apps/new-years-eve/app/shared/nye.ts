// New Year's Eve: pure time logic (docs/DECISIONS.md D3-D7). No device calls, no JS Date local-time methods.
//
// Everything is a function of the bar's local wall-clock time (walltime.LocalTime). The app, the Node tests and
// the browser mockup all run this same file (build.py inlines it into mockup/index.html), so the simulator plays
// exactly the phases the bar will.
//
// Keep this file free of `import` lines other than single-line imports from the shared kit, and free of enums or
// namespaces: the mockup build strips the types and inlines it.

import { addSeconds, daysUntil, pad2, secondsToMidnight, secondsUntilDate, type LocalTime } from "./vendor/busybar/walltime.ts";

/** The final-minute screen takes over at T-60 s. */
export const FINAL_S = 60;
/** Huge single digits for the last 10 s (10 ... 1). */
export const FINAL10_S = 10;
/** HAPPY NEW YEAR over fireworks for the first minute of Jan 1. */
export const CELEBRATE_S = 60;
/** After the celebration, the "happy new year" card is used until 06:00 on Jan 1. */
export const AFTER_S = 6 * 3600;
/** A countdown card between scenes. */
export const CARD_MS = 6000;
/** A card shorter than this is not worth showing: go to the final minute instead. */
export const MIN_CARD_MS = 2000;
/** START jumps to T-15 s. */
export const DEMO_LEAD_S = 15;

/**
 * party      Dec 31, more than 60 s to midnight: scenes and countdown cards
 * final      Dec 31, T-60 ... T-11: the final-minute screen
 * final10    Dec 31, T-10 ... T-1: one huge digit per second
 * celebrate  Jan 1, the first 60 s: 0, a burst, then HAPPY NEW YEAR over fireworks
 * after      Jan 1, until 06:00: scenes and a clock card that says HAPPY <year>
 * off        any other time: scenes and a clock card with the days left to the new year
 */
export type Phase = "party" | "final" | "final10" | "celebrate" | "after" | "off";

export function phaseAt(t: LocalTime): Phase {
  const r = secondsToMidnight(t); // 1 ... 86400
  if (t.month === 12 && t.day === 31) {
    if (r <= FINAL10_S) return "final10";
    if (r <= FINAL_S) return "final";
    return "party";
  }
  if (t.month === 1 && t.day === 1) {
    const s = 86400 - r; // seconds since midnight
    if (s < CELEBRATE_S) return "celebrate";
    if (s < AFTER_S) return "after";
  }
  return "off";
}

/** Seconds since the last local midnight (0 at 00:00:00). */
export function secondsSinceMidnight(t: LocalTime): number {
  return 86400 - secondsToMidnight(t);
}

/**
 * The year the countdown is counting to, or the one being celebrated.
 * On Dec 31 it's the year of the date reached at midnight. On Jan 1 (celebrate, after) it's the year that just began.
 * Otherwise it's the next new year.
 */
export function newYear(t: LocalTime): number {
  const ph = phaseAt(t);
  if (ph === "celebrate" || ph === "after") return t.year;
  if (ph === "party" || ph === "final" || ph === "final10") return addSeconds(t, secondsToMidnight(t)).year;
  return t.year + 1;
}

/** "HH:MM:SS", or "MM:SS" in the last hour. */
export function countdownText(remaining: number): string {
  const r = Math.max(0, Math.floor(remaining));
  const h = Math.floor(r / 3600);
  const m = Math.floor((r % 3600) / 60);
  const s = r % 60;
  return h > 0 ? pad2(h) + ":" + pad2(m) + ":" + pad2(s) : pad2(m) + ":" + pad2(s);
}

/** The final-minute count: "1:05" before T-60 (when a scene wouldn't fit), then plain seconds "59" ... "11". */
export function finalText(remaining: number): string {
  return remaining >= 60 ? Math.floor(remaining / 60) + ":" + pad2(remaining % 60) : String(remaining);
}

/** Lit pixels of the final-minute progress bar (0 at T-60, full at T-10). */
export function finalBarPixels(remaining: number, width: number): number {
  const lit = Math.floor((width * (FINAL_S - remaining)) / (FINAL_S - FINAL10_S));
  return Math.max(0, Math.min(width, lit));
}

export function hhmm(t: LocalTime): string {
  return pad2(t.hour) + ":" + pad2(t.minute);
}

/** The card between scenes: a big line (clock font) and two small stacked lines. */
export interface CardText {
  main: string;
  top: string;
  bottom: string;
}

export function cardText(t: LocalTime): CardText {
  const ph = phaseAt(t);
  if (ph === "party" || ph === "final" || ph === "final10") {
    return { main: countdownText(secondsToMidnight(t)), top: "TO", bottom: String(newYear(t)) };
  }
  if (ph === "celebrate" || ph === "after") return { main: hhmm(t), top: "HAPPY", bottom: String(t.year) };
  const days = daysUntil(t, t.year + 1, 1, 1);
  return { main: hhmm(t), top: days === 1 ? "1 DAY" : days + " DAYS", bottom: "TO " + (t.year + 1) };
}

// --- the bar's clock, with the demo offset ------------------------------------------------------------------

/** At monotonic time `ms` (Date.now()), the bar's clock had just reached `local` (a second boundary). */
export interface Anchor {
  local: LocalTime;
  ms: number;
}

/** The app's notion of now: the bar time plus the demo offset, and how far into that second we are. */
export interface Now {
  t: LocalTime;
  /** Milliseconds since `t` began (0-999). */
  frac: number;
}

/** a - b in seconds (calendar arithmetic only; Date.UTC is offset-free). */
export function diffSeconds(a: LocalTime, b: LocalTime): number {
  const s = (t: LocalTime) => Date.UTC(t.year, t.month - 1, t.day, t.hour, t.minute, t.second) / 1000;
  return s(a) - s(b);
}

export function effectiveAt(anchor: Anchor, nowMs: number, offsetS: number): Now {
  const elapsed = Math.max(0, nowMs - anchor.ms);
  const whole = Math.floor(elapsed / 1000);
  return { t: addSeconds(anchor.local, whole + offsetS), frac: elapsed - whole * 1000 };
}

/**
 * Whether a card should re-measure the bar's second boundary (a ~1 s burst of small time requests): every 10 min,
 * and every 2 min in the last 15 min before midnight so the final seconds land on the bar's own ticks.
 */
export function needsEdgeSync(t: LocalTime, msSinceEdge: number): boolean {
  const ph = phaseAt(t);
  if ((ph === "party" || ph === "final") && secondsToMidnight(t) <= 900) return msSinceEdge > 120000;
  return msSinceEdge > 600000;
}

/**
 * Demo mode (START): the offset, in seconds, that moves the app's clock to T-15 s before the next new year.
 * The offset carries across the year boundary, so every phase sees a real Dec 31 / Jan 1 date. `real` is the bar's
 * time without any offset.
 */
export function demoOffset(real: LocalTime): number {
  return secondsUntilDate(real, real.year + 1, 1, 1) - DEMO_LEAD_S;
}

/** Demo mode ends by itself after the celebration: once the effective time leaves Dec 31 / the celebration. */
export function settleDemo(offsetS: number, effective: LocalTime): number {
  if (offsetS === 0) return 0;
  const ph = phaseAt(effective);
  return ph === "after" || ph === "off" ? 0 : offsetS;
}

// --- what to show next ----------------------------------------------------------------------------------------

export type StepKind = "scene" | "card" | "final" | "final10" | "celebrate";

export interface Step {
  kind: StepKind;
  /** Scene index (scenes only, else -1). */
  index: number;
  /** How long the step lasts. Time-locked steps end exactly on a second boundary of the bar clock. */
  ms: number;
}

/** Where the party loop is: the next scene to play, and whether a card is due first. */
export interface Cursor {
  next: number;
  cardDue: boolean;
}

/**
 * Picks the next step for effective time `t` (`frac` ms into that second).
 * Scenes never overrun midnight: in the party phase a scene only starts if it ends by T-60 s, and a card is cut
 * to end at T-60 s. Otherwise the final-minute screen starts straight away.
 */
export function planStep(t: LocalTime, frac: number, cursor: Cursor, sceneMs: readonly number[]): { step: Step; cursor: Cursor } {
  const ph = phaseAt(t);
  const r = secondsToMidnight(t);
  const toBoundary = (seconds: number) => Math.max(1, seconds * 1000 - frac);
  const n = sceneMs.length;
  // after the countdown and the celebration, the party picks up with a scene, not a card
  const held: Cursor = { next: cursor.next, cardDue: false };
  const final = { step: { kind: "final" as StepKind, index: -1, ms: toBoundary(r - FINAL10_S) }, cursor: held };

  if (ph === "final10") return { step: { kind: "final10", index: -1, ms: toBoundary(r) }, cursor: held };
  if (ph === "final") return final;
  if (ph === "celebrate") {
    return { step: { kind: "celebrate", index: -1, ms: toBoundary(CELEBRATE_S - secondsSinceMidnight(t)) }, cursor: held };
  }

  const nextIndex = ((cursor.next % n) + n) % n;
  if (ph === "party") {
    const left = r * 1000 - frac - FINAL_S * 1000; // ms until the final-minute screen
    if (cursor.cardDue) {
      const ms = Math.min(CARD_MS, left);
      if (ms < MIN_CARD_MS) return final;
      return { step: { kind: "card", index: -1, ms }, cursor: { next: nextIndex, cardDue: false } };
    }
    if (sceneMs[nextIndex] > left) return final;
  } else if (cursor.cardDue) {
    return { step: { kind: "card", index: -1, ms: CARD_MS }, cursor: { next: nextIndex, cardDue: false } };
  }
  return {
    step: { kind: "scene", index: nextIndex, ms: sceneMs[nextIndex] },
    cursor: { next: (nextIndex + 1) % n, cardDue: true },
  };
}

/** The celebration's timeline, by seconds since midnight. */
export interface CelebrateState {
  /** "burst" is a one-shot animation started at 00:00:00; "loop" is the fireworks backdrop. */
  stage: "burst" | "loop";
  /** "zero": the huge 0; "none": let the burst show; "greeting": HAPPY NEW YEAR + year; "year": the year, huge. */
  text: "zero" | "none" | "greeting" | "year";
}

export const BURST_S = 3;
export const CELEBRATE_TEXT_S = 4;

/** `startedAt` is the second the celebration step began (a burst only plays if it began at 00:00:00). */
export function celebrateState(s: number, startedAt: number): CelebrateState {
  const stage = startedAt === 0 && s < BURST_S ? "burst" : "loop";
  if (s < 1) return { stage, text: "zero" };
  if (s < BURST_S) return { stage, text: stage === "burst" ? "none" : "greeting" };
  return { stage, text: Math.floor((s - BURST_S) / CELEBRATE_TEXT_S) % 2 === 0 ? "greeting" : "year" };
}
