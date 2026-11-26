// Lunar New Year date logic: which part of the season the bar's date is in, which zodiac animal to show, the card
// texts and the playlist. Pure functions of the bar's local time, so tests/logic.test.mts can check them against
// real dates (docs/DECISIONS.md D6, D10, D11).

import { HOLIDAYS, ZODIAC, daysLabel, formatDate, nextOccurrence, pad2, zodiac, type LocalTime } from "./kit.ts";
import { SHOW } from "./generated/show.ts";

/** The festival lasts from New Year's Day through the Lantern Festival, the 15th day. */
export const SPAN_DAYS = 15;

export type Season =
  /** Before New Year's Day: `days` to go; `animal` is the upcoming year's. */
  | { kind: "countdown"; days: number; animal: string }
  /** New Year's Day (dayOf 1) through the Lantern Festival (dayOf 15). */
  | { kind: "festival"; dayOf: number; animal: string }
  /** Outside the kit's date table: no countdown, a generic greeting, and the animal of the year in progress. */
  | { kind: "unknown"; animal: string };

/**
 * The animal of the lunar year in progress, without a table: Lunar New Year always falls between Jan 21 and
 * Feb 20, so from Feb 21 it's this year's animal and before Jan 21 it's last year's. In between we can't know;
 * last year's is used until Feb 21 (D11).
 */
export function animalWithoutTable(t: LocalTime): string {
  const after = t.month > 2 || (t.month === 2 && t.day >= 21);
  return zodiac(after ? t.year : t.year - 1);
}

export function season(t: LocalTime): Season {
  const occ = nextOccurrence(t, HOLIDAYS.lunarNewYear, SPAN_DAYS);
  if (!occ) return { kind: "unknown", animal: animalWithoutTable(t) };
  const animal = zodiac(occ.year);
  if (occ.days > 0) return { kind: "countdown", days: occ.days, animal };
  return { kind: "festival", dayOf: occ.dayOf, animal };
}

// --- holiday mode (START) ------------------------------------------------------------------------------------

/** Holiday mode: the festival preview, showing `ZODIAC[animal]`; `shown` counts the animals stepped through. */
export interface Preview {
  start: number;
  shown: number;
}

/**
 * One START press. Off -> on with the real season's animal; on -> the next animal of the twelve; after all twelve
 * have been shown -> off (D10).
 */
export function pressStart(p: Preview | null, currentAnimal: string): Preview | null {
  if (!p) return { start: Math.max(0, ZODIAC.indexOf(currentAnimal)), shown: 0 };
  return p.shown + 1 >= ZODIAC.length ? null : { start: p.start, shown: p.shown + 1 };
}

export function previewAnimal(p: Preview): string {
  return ZODIAC[(p.start + p.shown) % ZODIAC.length];
}

/** The season the show plays: the real one, or the festival preview in holiday mode. */
export function effectiveSeason(t: LocalTime, p: Preview | null): Season {
  return p ? { kind: "festival", dayOf: 1, animal: previewAnimal(p) } : season(t);
}

// --- cards and playlist ---------------------------------------------------------------------------------------

export type Style = keyof typeof SHOW.styles;
export interface TextLine {
  style: Style;
  text: string;
}
export interface CardPage {
  ms: number;
  lines: TextLine[];
}

const T = SHOW.timing;

/** The "count" card: the countdown, the festival greetings, or the generic greeting outside the date table. */
export function countPages(s: Season): CardPage[] {
  if (s.kind === "countdown") {
    return [{ ms: T.count, lines: [{ style: "head", text: daysLabel(s.days) }, { style: "sub", text: "TO LUNAR NEW YEAR" }] }];
  }
  if (s.kind === "unknown") {
    return [{ ms: T.fallback, lines: [{ style: "top", text: "HAPPY" }, { style: "bot", text: "NEW YEAR" }] }];
  }
  const greeting: TextLine[] = s.dayOf === SPAN_DAYS
    ? [{ style: "top", text: "LANTERN" }, { style: "bot", text: "FESTIVAL" }]
    : [{ style: "top", text: "HAPPY" }, { style: "bot", text: "NEW YEAR" }];
  return [
    { ms: T.animal, lines: [{ style: "small", text: "YEAR OF THE" }, { style: "name", text: s.animal }] },
    { ms: T.greeting, lines: greeting },
    { ms: T.wish, lines: [{ style: "top", text: "GONG XI" }, { style: "bot", text: "FA CAI" }] },
  ];
}

/** The clock card: the 24-hour time, then the date. */
export const clockTime = (t: LocalTime) => pad2(t.hour) + ":" + pad2(t.minute);
export const clockDate = (t: LocalTime) => formatDate(t);

export type PlayStep = { kind: "scene"; scene: number } | { kind: "card"; card: "clock" | "count" };

/** Scene index of the zodiac scene for an animal ("GOAT" -> the index of zodiac_goat in SHOW.scenes). */
export function zodiacScene(animal: string): number {
  return sceneIndex("zodiac_" + animal.toLowerCase());
}

export function sceneIndex(name: string): number {
  const i = SHOW.scenes.findIndex((s) => s.name === name);
  if (i < 0) throw new Error(`no scene ${name}`);
  return i;
}

/** The playlist for one cycle: the countdown order before the holiday (and outside the table), else the festival. */
export function playlist(s: Season): PlayStep[] {
  const names: readonly string[] = s.kind === "festival" ? SHOW.playlists.festival : SHOW.playlists.countdown;
  return names.map((n): PlayStep => {
    if (n === "clock" || n === "count") return { kind: "card", card: n };
    if (n === "ZODIAC") return { kind: "scene", scene: zodiacScene(s.animal) };
    return { kind: "scene", scene: sceneIndex(n) };
  });
}
