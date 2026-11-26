// Unit tests for the app's date logic and card texts (app/shared/valentine.ts), against real dates, plus one run of
// the real show runner with this app's cards. Run: node --experimental-strip-types --test tests/logic.test.mts
// (Node 24).

import assert from "node:assert/strict";
import { mock, test } from "node:test";

import { parseLocal, type LocalTime } from "../../../lib/ts/busybar/walltime.ts";
import { createShow, type Card, type ShowDevice } from "../../../lib/ts/busybar/showrunner.ts";
import {
  COUNT_MS, COUNT_SUB, DAY_CARDS, DAY_CARD_NAMES, cardPages, clockPages, countPages, daysToValentines,
  isValentinesDay, playlist,
} from "../app/shared/valentine.ts";
import { FONTS, LAYOUT, SHOW } from "../app/shared/generated/show.ts";

const T = (iso: string): LocalTime => {
  const t = parseLocal(iso);
  assert.ok(t, iso);
  return t;
};
const texts = (pages: { lines: { text: string }[] }[]) => pages.map((p) => p.lines.map((l) => l.text));
const GREETING = ["HAPPY", "VALENTINE'S DAY"];

test("Valentine's Day dates: Feb 14 every year", () => {
  assert.equal(daysToValentines(T("2027-02-14T00:00:00-05:00")), 0); // Sun 14 Feb 2027
  assert.equal(daysToValentines(T("2027-02-14T23:59:59+09:00")), 0);
  assert.equal(daysToValentines(T("2028-02-14T12:00:00+00:00")), 0); // Mon 14 Feb 2028
  assert.equal(daysToValentines(T("2026-11-26T12:00:00-05:00")), 80);
  assert.equal(daysToValentines(T("2027-02-13T23:59:59-05:00")), 1);
  assert.equal(daysToValentines(T("2027-01-01T00:00:00-05:00")), 44);
  assert.equal(daysToValentines(T("2027-02-15T00:00:00-05:00")), 364); // the day after: to 14 Feb 2028
  assert.equal(daysToValentines(T("2028-02-15T08:00:00-05:00")), 365); // to 14 Feb 2029 (29 Feb 2028 in between)
  assert.equal(daysToValentines(T("2028-02-28T08:00:00-05:00")), 352);
});

test("isValentinesDay: only on the day, or any day in holiday mode", () => {
  assert.equal(isValentinesDay(T("2027-02-14T00:00:00-05:00"), false), true);
  assert.equal(isValentinesDay(T("2027-02-13T23:59:00-05:00"), false), false);
  assert.equal(isValentinesDay(T("2027-02-15T00:00:00-05:00"), false), false);
  assert.equal(isValentinesDay(T("2026-11-26T12:00:00-05:00"), true), true);
});

test("countdown card before and after the day", () => {
  assert.equal(COUNT_SUB, "TO VALENTINE'S DAY");
  assert.deepEqual(texts(countPages(T("2026-11-26T12:00:00-05:00"))), [["80 DAYS", COUNT_SUB]]);
  assert.deepEqual(texts(countPages(T("2027-02-13T08:00:00-05:00"))), [["1 DAY", COUNT_SUB]]);
  assert.deepEqual(texts(countPages(T("2027-02-15T08:00:00-05:00"))), [["364 DAYS", COUNT_SUB]]);
  assert.deepEqual(countPages(T("2026-11-26T12:00:00-05:00"))[0].lines.map((l) => l.style), ["head", "sub"]);
  assert.equal(countPages(T("2026-11-26T12:00:00-05:00"))[0].ms, COUNT_MS);
});

test("the on-the-day cards: the greeting, then candy-heart phrases", () => {
  assert.deepEqual(DAY_CARD_NAMES, ["day0", "day1", "day2"]);
  assert.deepEqual(DAY_CARDS.map(texts), [
    [GREETING, ["BE MINE"], ["XOXO"]],
    [GREETING, ["HUG ME"], ["LOVE YOU"]],
    [GREETING, ["BE TRUE"], ["SO SWEET"]],
  ]);
  for (const card of DAY_CARDS) {
    assert.deepEqual(card[0].lines.map((l) => l.style), ["head", "sub"]);
    for (const page of card.slice(1)) assert.deepEqual(page.lines.map((l) => l.style), ["candy"]);
  }
  const day = T("2027-02-14T10:00:00-05:00");
  assert.deepEqual(texts(cardPages("day1", day)), [GREETING, ["HUG ME"], ["LOVE YOU"]]);
});

test("clock card: time, then date, from the bar's wall clock", () => {
  assert.deepEqual(texts(clockPages(T("2027-02-14T07:05:42-05:00"))), [["07:05"], ["SUN 14 FEB"]]);
  assert.deepEqual(texts(clockPages(T("2028-02-14T23:59:00+09:00"))), [["23:59"], ["MON 14 FEB"]]);
  assert.deepEqual(texts(cardPages("clock", T("2026-11-26T18:05:00-05:00"))), [["18:05"], ["THU 26 NOV"]]);
});

test("playlist: scene, clock, scene, count; the day cards on the day and in holiday mode", () => {
  const n = SHOW.scenes.length;
  assert.equal(n, 7);
  const names = (steps: ReturnType<typeof playlist>) => steps.map((s) => (s.kind === "scene" ? s.scene : s.card));
  const before = playlist(n, T("2026-11-26T12:00:00-05:00"), false);
  assert.deepEqual(names(before), [0, "clock", 1, "count", 2, "clock", 3, "count", 4, "clock", 5, "count", 6, "clock"]);
  const onDay = playlist(n, T("2027-02-14T12:00:00-05:00"), false);
  assert.deepEqual(names(onDay), [0, "clock", 1, "day0", 2, "clock", 3, "day1", 4, "clock", 5, "day2", 6, "clock"]);
  assert.deepEqual(playlist(n, T("2028-02-14T00:00:00-05:00"), false), onDay);
  assert.deepEqual(playlist(n, T("2026-11-26T12:00:00-05:00"), true), onDay); // holiday mode
  assert.deepEqual(playlist(n, T("2027-02-15T00:00:00-05:00"), false), before); // the day after
  assert.deepEqual(playlist(n, T("2027-02-13T23:59:00-05:00"), false), before); // the day before
  // START: the cycle is rotated to begin at the first count slot, same steps
  const rotated = playlist(n, T("2026-11-26T12:00:00-05:00"), true, true);
  assert.deepEqual(names(rotated), ["day0", 2, "clock", 3, "day1", 4, "clock", 5, "day2", 6, "clock", 0, "clock", 1]);
  assert.deepEqual(names(playlist(n, T("2026-11-26T12:00:00-05:00"), false, true))[0], "count");
});

test("every text fits the display (candy phrases fit between the candy hearts) and has its glyphs", () => {
  const all: [string, string][] = [];
  for (const card of DAY_CARDS) for (const page of card) for (const l of page.lines) all.push([l.style, l.text]);
  all.push(["head", "365 DAYS"], ["head", "1 DAY"], ["sub", COUNT_SUB], ["date", "WED 28 SEP"], ["time", "23:59"]);
  const layout = LAYOUT as Record<string, { font: string }>;
  for (const [style, text] of all) {
    const font = FONTS[layout[style].font];
    let w = 0;
    for (const ch of text) {
      assert.ok(font.glyphs[ch], `${style}: ${JSON.stringify(ch)} missing from ${layout[style].font}`);
      w += font.glyphs[ch][0].length + font.gap;
    }
    w -= font.gap;
    assert.ok(w + 1 <= 72, `${text} is ${w} px wide`);
    // count_bg's candy hearts fill columns 1-9 and 62-70 in rows 1-9: big lines there must stay in 11..60
    if (style === "candy" || style === "head") assert.ok(w + 1 <= 48, `${text} (${w} px) collides with the candy hearts`);
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
        return { timestamp: "2027-02-14T10:00:00-05:00" };
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
    assert.ok(log.includes("text text1 34"), "the greeting has two lines");
    show.stop();
  } finally {
    mock.timers.reset();
  }
});
