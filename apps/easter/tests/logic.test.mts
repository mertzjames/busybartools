// Unit tests for the app's date logic and card texts (app/shared/easter.ts), against real Easter dates, plus one run
// of the real show runner with this app's cards, and a check that the mockup's inlined logic gives the same answers
// as the app's TypeScript on every day of several years. Run: node --experimental-strip-types --test
// tests/logic.test.mts (Node 24).

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { mock, test } from "node:test";

import { parseLocal, type LocalTime } from "../../../lib/ts/busybar/walltime.ts";
import { createShow, type Card, type ShowDevice } from "../../../lib/ts/busybar/showrunner.ts";
import {
  COUNT_MS, DAY_CARDS, DAY_CARD_NAMES, cardBackdrop, cardPages, clockPages, countPages, daysToEaster, isEaster,
  playlist,
} from "../app/shared/easter.ts";
import { FONTS, LAYOUT, SHOW } from "../app/shared/generated/show.ts";

const T = (iso: string): LocalTime => {
  const t = parseLocal(iso);
  assert.ok(t, iso);
  return t;
};
const texts = (pages: { lines: { text: string }[] }[]) => pages.map((p) => p.lines.map((l) => l.text));
const HAPPY = ["HAPPY", "EASTER"];

test("Easter dates: Western Easter Sunday from the kit's computus", () => {
  assert.equal(daysToEaster(T("2027-03-28T09:00:00-04:00")), 0); // Sun 28 Mar 2027
  assert.equal(daysToEaster(T("2028-04-16T23:59:59-04:00")), 0); // Sun 16 Apr 2028
  assert.equal(daysToEaster(T("2029-04-01T00:00:00+00:00")), 0); // Sun 1 Apr 2029
  assert.equal(daysToEaster(T("2026-11-26T12:00:00-05:00")), 122);
  assert.equal(daysToEaster(T("2027-03-27T23:59:59-04:00")), 1);
  assert.equal(daysToEaster(T("2027-03-29T00:00:00-04:00")), 384); // the day after: next year's (16 Apr 2028)
  assert.equal(daysToEaster(T("2027-12-31T20:00:00-05:00")), 107);
  assert.equal(daysToEaster(T("2028-04-17T08:00:00-04:00")), 349); // to 1 Apr 2029
  assert.equal(daysToEaster(T("2026-04-05T12:00:00-04:00")), 0); // Sun 5 Apr 2026
  assert.equal(daysToEaster(T("2026-04-06T12:00:00-04:00")), 356); // the rollover to 28 Mar 2027
});

test("isEaster: only on the day, or any day in holiday mode", () => {
  assert.equal(isEaster(T("2027-03-28T00:00:00-04:00"), false), true);
  assert.equal(isEaster(T("2027-03-27T23:59:00-04:00"), false), false);
  assert.equal(isEaster(T("2027-03-29T00:00:00-04:00"), false), false);
  assert.equal(isEaster(T("2026-11-26T12:00:00-05:00"), true), true);
});

test("countdown card before and after the day", () => {
  assert.deepEqual(texts(countPages(T("2026-11-26T12:00:00-05:00"))), [["122 DAYS", "TO EASTER"]]);
  assert.deepEqual(texts(countPages(T("2027-03-27T08:00:00-04:00"))), [["1 DAY", "TO EASTER"]]);
  assert.deepEqual(texts(countPages(T("2027-03-29T08:00:00-04:00"))), [["384 DAYS", "TO EASTER"]]);
  assert.deepEqual(texts(countPages(T("2028-04-17T08:00:00-04:00"))), [["349 DAYS", "TO EASTER"]]);
  assert.deepEqual(countPages(T("2026-11-26T12:00:00-05:00"))[0].lines.map((l) => l.style), ["head", "sub"]);
  assert.equal(countPages(T("2026-11-26T12:00:00-05:00"))[0].ms, COUNT_MS);
});

test("the on-the-day cards: HAPPY / EASTER, then an extra page", () => {
  assert.deepEqual(DAY_CARD_NAMES, ["day0", "day1", "day2"]);
  assert.deepEqual(DAY_CARDS.map(texts), [
    [HAPPY, ["EGG HUNT", "TIME!"]],
    [HAPPY, ["HOPPY", "EASTER!"]],
    [HAPPY, ["SPRING IS", "HERE!"]],
  ]);
  assert.deepEqual(DAY_CARDS[0][0].lines.map((l) => l.style), ["top", "bot"]);
  const day = T("2027-03-28T10:00:00-04:00");
  assert.deepEqual(texts(cardPages("day1", day)), [HAPPY, ["HOPPY", "EASTER!"]]);
  assert.equal(cardBackdrop("day2"), "day_bg");
  assert.equal(cardBackdrop("count"), "count_bg");
  assert.equal(cardBackdrop("clock"), "clock_bg");
});

test("clock card: time, then date, from the bar's wall clock", () => {
  assert.deepEqual(texts(clockPages(T("2027-03-28T07:05:42-04:00"))), [["07:05"], ["SUN 28 MAR"]]);
  assert.deepEqual(texts(clockPages(T("2028-04-16T23:59:00+09:00"))), [["23:59"], ["SUN 16 APR"]]);
  assert.deepEqual(texts(cardPages("clock", T("2026-11-26T18:05:00-05:00"))), [["18:05"], ["THU 26 NOV"]]);
});

test("playlist: scene, clock, scene, count; the day cards on the day and in holiday mode", () => {
  const n = SHOW.scenes.length;
  assert.equal(n, 7);
  const names = (steps: ReturnType<typeof playlist>) => steps.map((s) => (s.kind === "scene" ? s.scene : s.card));
  const before = playlist(n, T("2026-11-26T12:00:00-05:00"), false);
  assert.deepEqual(names(before), [0, "clock", 1, "count", 2, "clock", 3, "count", 4, "clock", 5, "count", 6, "clock"]);
  const onDay = playlist(n, T("2027-03-28T12:00:00-04:00"), false);
  assert.deepEqual(names(onDay), [0, "clock", 1, "day0", 2, "clock", 3, "day1", 4, "clock", 5, "day2", 6, "clock"]);
  assert.deepEqual(playlist(n, T("2028-04-16T12:00:00-04:00"), false), onDay);
  assert.deepEqual(playlist(n, T("2029-04-01T12:00:00-04:00"), false), onDay);
  assert.deepEqual(playlist(n, T("2026-11-26T12:00:00-05:00"), true), onDay); // holiday mode
  assert.deepEqual(playlist(n, T("2027-03-29T12:00:00-04:00"), false), before); // the day after
  // START: the cycle is rotated to begin at the first count slot, same steps
  const rotated = playlist(n, T("2026-11-26T12:00:00-05:00"), true, true);
  assert.deepEqual(names(rotated), ["day0", 2, "clock", 3, "day1", 4, "clock", 5, "day2", 6, "clock", 0, "clock", 1]);
  assert.deepEqual(names(playlist(n, T("2026-11-26T12:00:00-05:00"), false, true))[0], "count");
});

test("every text fits the display and uses only glyphs the fonts have", () => {
  const all: [string, string][] = [];
  for (const card of DAY_CARDS) for (const page of card) for (const l of page.lines) all.push([l.style, l.text]);
  // the longest countdown: a late Easter followed by an early one is under 400 days
  all.push(["head", "399 DAYS"], ["head", "1 DAY"], ["sub", "TO EASTER"], ["date", "WED 28 SEP"], ["time", "23:59"]);
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
  // and the countdown really stays under 400 days on every day of 2026-2040
  let most = 0;
  for (let y = 2026; y <= 2040; y++) {
    for (let d = 0; d < 366; d++) {
      const date = new Date(Date.UTC(y, 0, 1 + d));
      if (date.getUTCFullYear() !== y) continue;
      const iso = date.toISOString().slice(0, 10) + "T12:00:00+00:00";
      most = Math.max(most, daysToEaster(T(iso)));
    }
  }
  assert.ok(most < 400, `longest countdown ${most}`);
});

test("the mockup runs the same logic as the app on every day of 2026-2030", () => {
  const html = readFileSync(new URL("../mockup/index.html", import.meta.url), "utf8");
  const start = html.indexOf("const EASTER = (() => {");
  const end = html.indexOf("})();", start);
  assert.ok(start > 0 && end > start, "the mockup inlines the app's logic");
  const M = new Function(html.slice(start, end + 5) + "\nreturn EASTER;")();
  for (let y = 2026; y <= 2030; y++) {
    for (let d = 0; d < 366; d++) {
      const date = new Date(Date.UTC(y, 0, 1 + d));
      if (date.getUTCFullYear() !== y) continue;
      const t = T(date.toISOString().slice(0, 10) + "T09:30:00-04:00");
      assert.equal(M.daysToEaster(t), daysToEaster(t));
      for (const name of ["clock", "count", ...DAY_CARD_NAMES]) {
        assert.deepEqual(M.cardPages(name, t), cardPages(name, t));
      }
      assert.deepEqual(M.playlist(7, t, false), playlist(7, t, false));
    }
  }
});

test("show runner: this app's day cards play their pages over the holiday backdrop", async () => {
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
        return { timestamp: "2027-03-28T10:00:00-04:00" };
      },
    };
    const card = (name: string): Card => ({
      path: SHOW.backdrops[cardBackdrop(name)],
      pages: (t0) => cardPages(name, t0).map((page, p) => ({
        ms: page.ms,
        lines: page.lines.map((line, k) => ({
          spec: (LAYOUT as any)[line.style],
          text: (t: LocalTime) => cardPages(name, t)[p]?.lines[k]?.text ?? "",
        })),
      })),
    });
    const cards: Record<string, Card> = {};
    for (const n of ["clock", "count", ...DAY_CARD_NAMES]) cards[n] = card(n);
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
    assert.ok(log.includes("text text0 34") && log.includes("text text1 34"), "both lines fade in");
    show.stop();
  } finally {
    mock.timers.reset();
  }
});
