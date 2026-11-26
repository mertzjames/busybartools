// Unit tests for the app's date logic and card texts (app/shared/presidents.ts), against real Presidents' Day dates,
// plus one run of the real show runner with this app's cards. Run: node --experimental-strip-types --test
// tests/logic.test.mts (Node 24).

import assert from "node:assert/strict";
import { mock, test } from "node:test";

import { parseLocal, type LocalTime } from "../../../lib/ts/busybar/walltime.ts";
import { createShow, type Card, type ShowDevice } from "../../../lib/ts/busybar/showrunner.ts";
import {
  COUNT_MS, DAY_CARDS, DAY_CARD_NAMES, GREETING_MS, HOLIDAY_NAME, cardPages, clockPages, countPages,
  daysToPresidentsDay, isPresidentsDay, playlist,
} from "../app/shared/presidents.ts";
import { FONTS, LAYOUT, SHOW } from "../app/shared/generated/show.ts";

const T = (iso: string): LocalTime => {
  const t = parseLocal(iso);
  assert.ok(t, iso);
  return t;
};
const texts = (pages: { lines: { text: string }[] }[]) => pages.map((p) => p.lines.map((l) => l.text));

test("Presidents' Day dates: third Monday of February", () => {
  assert.equal(daysToPresidentsDay(T("2027-02-15T09:00:00-05:00")), 0); // Mon 15 Feb 2027
  assert.equal(daysToPresidentsDay(T("2028-02-21T23:59:59-05:00")), 0); // Mon 21 Feb 2028
  assert.equal(daysToPresidentsDay(T("2029-02-19T00:00:00+00:00")), 0); // Mon 19 Feb 2029
  assert.equal(daysToPresidentsDay(T("2026-11-26T12:00:00-05:00")), 81);
  assert.equal(daysToPresidentsDay(T("2027-02-14T23:59:59-05:00")), 1);
  assert.equal(daysToPresidentsDay(T("2027-02-16T00:00:00-05:00")), 370); // the day after: to 21 Feb 2028
  assert.equal(daysToPresidentsDay(T("2027-12-31T20:00:00-05:00")), 52);
  assert.equal(daysToPresidentsDay(T("2028-02-22T08:00:00-05:00")), 363); // to 19 Feb 2029 (2028 is a leap year)
  assert.equal(daysToPresidentsDay(T("2027-02-22T08:00:00-05:00")), 364); // Washington's birthday is not the day
});

test("isPresidentsDay: only on the day, or any day in holiday mode", () => {
  assert.equal(isPresidentsDay(T("2027-02-15T00:00:00-05:00"), false), true);
  assert.equal(isPresidentsDay(T("2027-02-14T23:59:00-05:00"), false), false);
  assert.equal(isPresidentsDay(T("2027-02-16T00:00:00-05:00"), false), false);
  assert.equal(isPresidentsDay(T("2028-02-21T12:00:00-05:00"), false), true);
  assert.equal(isPresidentsDay(T("2026-11-26T12:00:00-05:00"), true), true);
});

test("countdown card before and after the day", () => {
  assert.equal(HOLIDAY_NAME, "PRESIDENTS' DAY");
  assert.deepEqual(texts(countPages(T("2026-11-26T12:00:00-05:00"))), [["81 DAYS", "TO PRESIDENTS' DAY"]]);
  assert.deepEqual(texts(countPages(T("2027-02-14T08:00:00-05:00"))), [["1 DAY", "TO PRESIDENTS' DAY"]]);
  assert.deepEqual(texts(countPages(T("2027-02-16T08:00:00-05:00"))), [["370 DAYS", "TO PRESIDENTS' DAY"]]);
  assert.deepEqual(texts(countPages(T("2028-02-20T08:00:00-05:00"))), [["1 DAY", "TO PRESIDENTS' DAY"]]);
  assert.deepEqual(countPages(T("2026-11-26T12:00:00-05:00"))[0].lines.map((l) => l.style), ["head", "sub"]);
  assert.equal(countPages(T("2026-11-26T12:00:00-05:00"))[0].ms, COUNT_MS);
});

test("the on-the-day cards: HAPPY / PRESIDENTS' DAY, then a word", () => {
  assert.deepEqual(DAY_CARD_NAMES, ["day0", "day1", "day2"]);
  assert.deepEqual(DAY_CARDS.map(texts), [
    [["HAPPY", "PRESIDENTS' DAY"], ["LIBERTY"]],
    [["HAPPY", "PRESIDENTS' DAY"], ["UNION"]],
    [["HAPPY", "PRESIDENTS' DAY"], ["FREEDOM"]],
  ]);
  assert.equal(DAY_CARDS[0][0].ms, GREETING_MS);
  assert.deepEqual(DAY_CARDS[0][0].lines.map((l) => l.style), ["head", "sub"]);
  const day = T("2027-02-15T10:00:00-05:00");
  assert.deepEqual(texts(cardPages("day1", day)), [["HAPPY", "PRESIDENTS' DAY"], ["UNION"]]);
  // the count card itself still counts on the day (it is only used off the day)
  assert.deepEqual(texts(cardPages("count", day)), [["0 DAYS", "TO PRESIDENTS' DAY"]]);
});

test("clock card: time, then date, from the bar's wall clock", () => {
  assert.deepEqual(texts(clockPages(T("2027-02-15T07:05:42-05:00"))), [["07:05"], ["MON 15 FEB"]]);
  assert.deepEqual(texts(clockPages(T("2028-02-21T23:59:00+09:00"))), [["23:59"], ["MON 21 FEB"]]);
  assert.deepEqual(texts(cardPages("clock", T("2026-11-26T18:05:00-05:00"))), [["18:05"], ["THU 26 NOV"]]);
});

test("playlist: scene, clock, scene, count; the day cards on the day and in holiday mode", () => {
  const n = SHOW.scenes.length;
  assert.equal(n, 7);
  const names = (steps: ReturnType<typeof playlist>) => steps.map((s) => (s.kind === "scene" ? s.scene : s.card));
  const before = playlist(n, T("2026-11-26T12:00:00-05:00"), false);
  assert.deepEqual(names(before),
    [0, "clock", 1, "count", 2, "clock", 3, "count", 4, "clock", 5, "count", 6, "clock"]);
  const onDay = playlist(n, T("2027-02-15T12:00:00-05:00"), false);
  assert.deepEqual(names(onDay), [0, "clock", 1, "day0", 2, "clock", 3, "day1", 4, "clock", 5, "day2", 6, "clock"]);
  assert.deepEqual(playlist(n, T("2028-02-21T12:00:00-05:00"), false), onDay);
  assert.deepEqual(playlist(n, T("2026-11-26T12:00:00-05:00"), true), onDay); // holiday mode
  assert.deepEqual(playlist(n, T("2027-02-16T12:00:00-05:00"), false), before); // the day after
  assert.deepEqual(playlist(n, T("2027-02-14T12:00:00-05:00"), false), before); // the day before
  // START: the cycle is rotated to begin at the first count slot, same steps
  const rotated = playlist(n, T("2026-11-26T12:00:00-05:00"), true, true);
  assert.deepEqual(names(rotated),
    ["day0", 2, "clock", 3, "day1", 4, "clock", 5, "day2", 6, "clock", 0, "clock", 1]);
  assert.deepEqual(names(playlist(n, T("2026-11-26T12:00:00-05:00"), false, true))[0], "count");
});

test("every text fits the display and uses only glyphs the fonts have", () => {
  const all: [string, string][] = [];
  for (const card of DAY_CARDS) for (const page of card) for (const l of page.lines) all.push([l.style, l.text]);
  for (const iso of ["2026-11-26T12:00:00-05:00", "2027-02-14T12:00:00-05:00", "2027-02-16T12:00:00-05:00"]) {
    for (const name of ["clock", "count"]) for (const page of cardPages(name, T(iso))) {
      for (const l of page.lines) all.push([l.style, l.text]);
    }
  }
  all.push(["head", "370 DAYS"], ["head", "1 DAY"], ["date", "WED 28 SEP"], ["time", "23:59"]);
  const layout = LAYOUT as Record<string, { font: string }>;
  for (const [style, text] of all) {
    const font = FONTS[layout[style].font];
    let w = 0;
    for (const ch of text) {
      assert.ok(font.glyphs[ch], `${style}: ${JSON.stringify(ch)} missing from ${layout[style].font}`);
      w += font.glyphs[ch][0].length + font.gap;
    }
    assert.ok(w - font.gap + 1 <= 72, `${text} is ${w - font.gap} px wide`);
  }
});

test("show runner: this app's day cards play their pages over the count backdrop", async () => {
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
        return { timestamp: "2027-02-15T10:00:00-05:00" };
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
    const cards: Record<string, Card> = { clock: card("clock", SHOW.backdrops.clock_bg) };
    for (const n of ["count", ...DAY_CARD_NAMES]) cards[n] = card(n, SHOW.backdrops.count_bg);
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
    assert.equal(log[0], `anim ${SHOW.backdrops.count_bg}`);
    assert.ok(log.includes("text text0 34"), "the first page fades in");
    show.stop();
  } finally {
    mock.timers.reset();
  }
});
