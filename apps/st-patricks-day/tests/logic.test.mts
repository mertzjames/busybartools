// Unit tests for the app's date logic and card texts (app/shared/stpatricks.ts), against real dates, plus one run of
// the real show runner with this app's cards, and a check that the mockup's inlined copy of the logic agrees with
// the app on every day of several years. Run: node --experimental-strip-types --test tests/logic.test.mts (Node 24).

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { mock, test } from "node:test";

import { parseLocal, type LocalTime } from "../../../lib/ts/busybar/walltime.ts";
import { shiftDate } from "../../../lib/ts/busybar/holidays.ts";
import { createShow, type Card, type ShowDevice } from "../../../lib/ts/busybar/showrunner.ts";
import {
  COUNT_MS, DAY_CARDS, DAY_CARD_NAMES, cardPages, clockPages, countPages, daysToStPatricks, isStPatricksDay,
  playlist,
} from "../app/shared/stpatricks.ts";
import { FONTS, LAYOUT, SHOW } from "../app/shared/generated/show.ts";

const T = (iso: string): LocalTime => {
  const t = parseLocal(iso);
  assert.ok(t, iso);
  return t;
};
const texts = (pages: { lines: { text: string }[] }[]) => pages.map((p) => p.lines.map((l) => l.text));
const names = (steps: ReturnType<typeof playlist>) => steps.map((s) => (s.kind === "scene" ? s.scene : s.card));

test("St. Patrick's Day dates: March 17 every year", () => {
  assert.equal(daysToStPatricks(T("2027-03-17T00:00:00-04:00")), 0);
  assert.equal(daysToStPatricks(T("2027-03-17T23:59:59-04:00")), 0);
  assert.equal(daysToStPatricks(T("2028-03-17T12:00:00+01:00")), 0); // a leap year
  assert.equal(daysToStPatricks(T("2026-11-26T12:00:00-05:00")), 111);
  assert.equal(daysToStPatricks(T("2027-03-16T23:59:59-04:00")), 1);
  assert.equal(daysToStPatricks(T("2027-03-18T00:00:00-04:00")), 365); // to 17 Mar 2028, across Feb 29
  assert.equal(daysToStPatricks(T("2028-03-18T08:00:00-04:00")), 364); // to 17 Mar 2029
  assert.equal(daysToStPatricks(T("2027-12-31T20:00:00-05:00")), 77);
  assert.equal(daysToStPatricks(T("2028-01-01T00:00:00+09:00")), 76);
});

test("isStPatricksDay: only on the day, or any day in holiday mode", () => {
  assert.equal(isStPatricksDay(T("2027-03-17T00:00:00-04:00"), false), true);
  assert.equal(isStPatricksDay(T("2027-03-16T23:59:00-04:00"), false), false);
  assert.equal(isStPatricksDay(T("2027-03-18T00:00:00-04:00"), false), false);
  assert.equal(isStPatricksDay(T("2026-11-26T12:00:00-05:00"), true), true);
});

test("countdown card before and after the day", () => {
  assert.deepEqual(texts(countPages(T("2026-11-26T12:00:00-05:00"))), [["111 DAYS", "TO ST. PATRICK'S"]]);
  assert.deepEqual(texts(countPages(T("2027-03-16T08:00:00-04:00"))), [["1 DAY", "TO ST. PATRICK'S"]]);
  assert.deepEqual(texts(countPages(T("2027-03-18T08:00:00-04:00"))), [["365 DAYS", "TO ST. PATRICK'S"]]);
  assert.deepEqual(countPages(T("2026-11-26T12:00:00-05:00"))[0].lines.map((l) => l.style), ["head", "sub"]);
  assert.equal(countPages(T("2026-11-26T12:00:00-05:00"))[0].ms, COUNT_MS);
});

test("the on-the-day cards: HAPPY ST. PATRICK'S DAY and ERIN GO BRAGH, nothing drink-centric", () => {
  assert.deepEqual(DAY_CARD_NAMES, ["day0", "day1"]);
  assert.deepEqual(DAY_CARDS.map(texts), [
    [["HAPPY"], ["ST. PATRICK'S", "DAY"]],
    [["ERIN GO", "BRAGH"], ["HAPPY", "ST. PATRICK'S DAY"]],
  ]);
  const day = T("2027-03-17T10:00:00-04:00");
  assert.deepEqual(texts(cardPages("day1", day)), [["ERIN GO", "BRAGH"], ["HAPPY", "ST. PATRICK'S DAY"]]);
  for (const card of DAY_CARDS) for (const page of card) for (const l of page.lines) {
    assert.doesNotMatch(l.text, /SLAINTE|BEER|PINT|DRINK|CHEERS/);
  }
});

test("clock card: time, then date, from the bar's wall clock", () => {
  assert.deepEqual(texts(clockPages(T("2027-03-17T07:05:42-04:00"))), [["07:05"], ["WED 17 MAR"]]);
  assert.deepEqual(texts(clockPages(T("2028-03-17T23:59:00+09:00"))), [["23:59"], ["FRI 17 MAR"]]);
  assert.deepEqual(texts(cardPages("clock", T("2026-11-26T18:05:00-05:00"))), [["18:05"], ["THU 26 NOV"]]);
});

test("playlist: scene, clock, scene, count; the day cards on the day and in holiday mode", () => {
  const n = SHOW.scenes.length;
  assert.equal(n, 7);
  const before = playlist(n, T("2026-11-26T12:00:00-05:00"), false);
  assert.deepEqual(names(before), [0, "clock", 1, "count", 2, "clock", 3, "count", 4, "clock", 5, "count", 6, "clock"]);
  const onDay = playlist(n, T("2027-03-17T12:00:00-04:00"), false);
  assert.deepEqual(names(onDay), [0, "clock", 1, "day0", 2, "clock", 3, "day1", 4, "clock", 5, "day0", 6, "clock"]);
  assert.deepEqual(playlist(n, T("2028-03-17T12:00:00-04:00"), false), onDay);
  assert.deepEqual(playlist(n, T("2026-11-26T12:00:00-05:00"), true), onDay); // holiday mode
  assert.deepEqual(playlist(n, T("2027-03-18T12:00:00-04:00"), false), before); // the day after
  // START: the cycle is rotated to begin at the first count slot, same steps
  const rotated = playlist(n, T("2026-11-26T12:00:00-05:00"), true, true);
  assert.deepEqual(names(rotated), ["day0", 2, "clock", 3, "day1", 4, "clock", 5, "day0", 6, "clock", 0, "clock", 1]);
  assert.equal(names(playlist(n, T("2026-11-26T12:00:00-05:00"), false, true))[0], "count");
});

test("every text fits the display and uses only glyphs the fonts have", () => {
  const all: [string, string][] = [];
  for (const card of DAY_CARDS) for (const page of card) for (const l of page.lines) all.push([l.style, l.text]);
  all.push(["head", "365 DAYS"], ["head", "1 DAY"], ["sub", "TO ST. PATRICK'S"], ["date", "WED 28 SEP"],
    ["time", "23:59"]);
  const layout = LAYOUT as Record<string, { font: string; y: number }>;
  for (const [style, text] of all) {
    const font = FONTS[layout[style].font];
    let w = 0;
    for (const ch of text) {
      assert.ok(font.glyphs[ch], `${style}: ${JSON.stringify(ch)} missing from ${layout[style].font}`);
      w += font.glyphs[ch][0].length + font.gap;
    }
    assert.ok(w - font.gap + 1 <= 72, `${text} is ${w - font.gap} px wide`);
    assert.ok(layout[style].y + font.height + 1 <= 16, `${style} (with its shadow) fits the 16 rows`);
  }
});

test("the mockup runs the same card logic as the app, on every day of 2026-2029", () => {
  const html = readFileSync(new URL("../mockup/index.html", import.meta.url), "utf8");
  const m = html.match(/\/\*SPD_LOGIC_BEGIN\*\/([\s\S]*?)\/\*SPD_LOGIC_END\*\//);
  assert.ok(m, "the mockup has the inlined logic block");
  const SPD = new Function(`${m[1]}\nreturn SPD;`)();
  for (let i = 0; i < 4 * 366; i++) {
    const [y, mo, d] = shiftDate(2026, 1, 1, i);
    const t = T(`${y}-${String(mo).padStart(2, "0")}-${String(d).padStart(2, "0")}T09:30:00-05:00`);
    assert.equal(SPD.daysToStPatricks(t), daysToStPatricks(t));
    for (const name of ["clock", "count", ...DAY_CARD_NAMES]) {
      assert.deepEqual(SPD.cardPages(name, t), cardPages(name, t));
    }
    assert.deepEqual(SPD.playlist(7, t, false), playlist(7, t, false));
  }
});

test("show runner: this app's day cards play their pages over the day backdrop", async () => {
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    const log: string[] = [];
    const device: ShowDevice = {
      async DisplayDraw(p) {
        for (const e of p.elements) log.push(e.type === "animation" ? `anim ${e.path}` : `text ${e.id} ${e.opacity}`);
      },
      async DisplayClear() {
        log.push("clear");
      },
      async TimeGet() {
        return { timestamp: "2027-03-17T10:00:00-04:00" };
      },
    };
    const card = (name: string, path: string): Card => ({
      path,
      pages: (t0) => cardPages(name, t0).map((page, p) => ({
        ms: page.ms,
        lines: page.lines.map((line, k) => ({
          spec: (LAYOUT as any)[line.style],
          text: (t: LocalTime) => cardPages(name, t)[p]?.lines[k]?.text ?? "",
        })),
      })),
    });
    const cards: Record<string, Card> = {
      clock: card("clock", SHOW.backdrops.clock_bg), count: card("count", SHOW.backdrops.count_bg),
    };
    for (const n of DAY_CARD_NAMES) cards[n] = card(n, SHOW.backdrops.day_bg);
    const show = createShow({
      app: "test", device, fonts: FONTS, scenes: SHOW.scenes, cards, report: (e) => { throw e; },
      steps: (t) => playlist(SHOW.scenes.length, t, false, true),
    });
    const flush = async (ms: number) => {
      for (let i = 0; i < 20; i++) await Promise.resolve();
      mock.timers.tick(ms);
      for (let i = 0; i < 20; i++) await Promise.resolve();
    };
    show.start();
    await flush(0);
    await flush(0);
    assert.deepEqual(show.steps[0], { kind: "card", card: "day0" });
    assert.equal(log[0], `anim ${SHOW.backdrops.day_bg}`);
    assert.ok(log.includes("text text0 34"), "the first page fades in");
    await flush(3000); // page 2: two lines
    await flush(0);
    assert.ok(log.includes("text text1 34"), "the second page has two lines");
    show.stop();
  } finally {
    mock.timers.reset();
  }
});
