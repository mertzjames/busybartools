// Kwanzaa date logic and card texts: pure functions of the bar's local time, unit-tested in tests/logic.test.mts.
//
// Kwanzaa runs seven days, Dec 26 - Jan 1, so it crosses the new year; the kit's nextOccurrence handles that.
// Day 1 = Dec 26 (Umoja) ... day 7 = Jan 1 (Imani). Outside Kwanzaa, day = 0 and the count is to the next Dec 26.

import { HOLIDAYS, daysLabel, nextOccurrence, type LocalTime, type Step } from "./kit.ts";
import { SHOW } from "./generated/show.ts";

export interface KwanzaaDay {
  /** 1..7 during Kwanzaa, 0 before it (or after it: the count is then to next year's). */
  day: number;
  /** Days until the next Dec 26 (0 during Kwanzaa). */
  days: number;
}

export function kwanzaaDay(t: LocalTime): KwanzaaDay {
  const occ = nextOccurrence(t, HOLIDAYS.kwanzaa, 7);
  if (!occ) return { day: 0, days: 0 }; // unreachable: the rule is a fixed date
  return occ.dayOf > 0 ? { day: occ.dayOf, days: 0 } : { day: 0, days: occ.days };
}

export type Style = "head" | "sub" | "time" | "date";
export interface PageText {
  ms: number;
  lines: { style: Style; text: string }[];
}

/**
 * The "count" card. Before Kwanzaa: "18 DAYS" / "TO KWANZAA", then "KWANZAA" / "DEC 26 - JAN 1". During it: the
 * greeting "HABARI GANI?" ("What's the news?"), then its traditional answer, the day's principle (Swahili over the
 * English, with a second page when the English needs two lines), then the day ("KARAMU" on day 6, Dec 31).
 * Mirrors count_pages in renderer/scenes/text.py.
 */
export function countPages(day: number, days: number): PageText[] {
  const T = SHOW.timing;
  if (!day) {
    return [
      { ms: T.count, lines: [{ style: "head", text: daysLabel(days) }, { style: "sub", text: "TO KWANZAA" }] },
      { ms: T.dates, lines: [{ style: "head", text: "KWANZAA" }, { style: "sub", text: "DEC 26 - JAN 1" }] },
    ];
  }
  const p = SHOW.principles[day - 1];
  const pages: PageText[] = [
    { ms: T.greet, lines: [{ style: "head", text: SHOW.greeting[0] }, { style: "sub", text: SHOW.greeting[1] }] },
    { ms: T.principle, lines: [{ style: "head", text: p.word }, { style: "sub", text: p.english[0] }] },
  ];
  for (const line of p.english.slice(1)) {
    pages.push({ ms: T.principle2, lines: [{ style: "head", text: p.word }, { style: "sub", text: line }] });
  }
  pages.push(day === 6
    ? { ms: T.day, lines: [{ style: "head", text: "KARAMU" }, { style: "sub", text: "DAY 6: THE FEAST" }] }
    : { ms: T.day, lines: [{ style: "head", text: "KWANZAA" }, { style: "sub", text: `DAY ${day} OF 7` }] });
  return pages;
}

/**
 * One cycle of the show: the day's kinara (scene index = day; 0 = unlit), then the other scenes, with cards
 * alternating clock, count, clock, ... between them, and a count card to close.
 */
export function cycleSteps(day: number): Step[] {
  const steps: Step[] = [{ kind: "scene", scene: day }];
  const others = SHOW.scenes.length - SHOW.kinara;
  for (let i = 0; i < others; i++) {
    steps.push({ kind: "card", card: i % 2 === 0 ? "clock" : "count" });
    steps.push({ kind: "scene", scene: SHOW.kinara + i });
  }
  steps.push({ kind: "card", card: others % 2 === 0 ? "clock" : "count" });
  return steps;
}

/** Holiday mode (START): off (0) -> day 1 -> ... -> day 7 -> off. */
export function nextPreview(preview: number): number {
  return preview >= 7 ? 0 : preview + 1;
}
