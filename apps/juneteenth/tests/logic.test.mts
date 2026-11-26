// Unit tests for the app's date logic and card texts (app/shared/juneteenth.ts), against real dates, plus one run of
// the real show runner with this app's cards (holiday mode via START), and a check that the mockup's inlined logic
// gives the same answers as the app's TypeScript on every day of several years. Run: node
// --experimental-strip-types --test tests/logic.test.mts (Node 24).

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { mock, test } from "node:test";

import { parseLocal, type LocalTime } from "../../../lib/ts/busybar/walltime.ts";
import { createShow, type Card, type ShowDevice } from "../../../lib/ts/busybar/showrunner.ts";
import {
  COUNT_MS, DAY_CARDS, DAY_CARD_NAMES, cardBackdrop, cardPages, clockPages, countPages, daysToJuneteenth,
  firstCountStep, isJuneteenth, playlist,
} from "../app/shared/juneteenth.ts";
import { FONTS, LAYOUT, SHOW } from "../app/shared/generated/show.ts";

const T = (iso: string): LocalTime => {
  const t = parseLocal(iso);
  assert.ok(t, iso);
  return t;
};
const texts = (pages: { lines: { text: string }[] }[]) => pages.map((p) => p.lines.map((l) => l.text));
const names = (steps: ReturnType<typeof playlist>) => steps.map((s) => (s.kind === "scene" ? s.scene : s.card));

test("dates: June 19 every year, counted on the bar's wall clock", () => {
  assert.equal(daysToJuneteenth(T("2027-06-19T00:00:00-05:00")), 0);
  assert.equal(daysToJuneteenth(T("2027-06-19T23:59:59-05:00")), 0);
  assert.equal(daysToJuneteenth(T("2028-06-19T12:00:00+09:00")), 0);
  assert.equal(daysToJuneteenth(T("2026-11-26T12:00:00-05:00")), 205); // the day this app was built
  assert.equal(daysToJuneteenth(T("2027-06-18T23:59:59-05:00")), 1);
  assert.equal(daysToJuneteenth(T("2027-06-20T00:00:00-05:00")), 365); // the day after: to June 19, 2028 (leap)
  assert.equal(daysToJuneteenth(T("2028-06-20T00:00:00-05:00")), 364); // to June 19, 2029
  assert.equal(daysToJuneteenth(T("2027-01-01T00:00:00-06:00")), 169);
  assert.equal(daysToJuneteenth(T("2027-12-31T23:00:00-06:00")), 171); // across the new year (2028 is a leap year)
  assert.equal(daysToJuneteenth(T("2028-02-29T08:00:00-06:00")), 111);
});

test("isJuneteenth: only on the day, or any day in holiday mode", () => {
  assert.equal(isJuneteenth(T("2027-06-19T00:00:00-05:00"), false), true);
  assert.equal(isJuneteenth(T("2027-06-18T23:59:00-05:00"), false), false);
  assert.equal(isJuneteenth(T("2027-06-20T00:00:00-05:00"), false), false);
  assert.equal(isJuneteenth(T("2026-11-26T12:00:00-05:00"), true), true);
});

test("countdown card before and after the day", () => {
  assert.deepEqual(texts(countPages(T("2026-11-26T12:00:00-05:00"))), [["205 DAYS", "TO JUNETEENTH"]]);
  assert.deepEqual(texts(countPages(T("2027-06-18T08:00:00-05:00"))), [["1 DAY", "TO JUNETEENTH"]]);
  assert.deepEqual(texts(countPages(T("2027-06-20T08:00:00-05:00"))), [["365 DAYS", "TO JUNETEENTH"]]);
  assert.deepEqual(texts(countPages(T("2028-07-04T08:00:00-05:00"))), [["350 DAYS", "TO JUNETEENTH"]]);
  assert.deepEqual(countPages(T("2026-11-26T12:00:00-05:00"))[0].lines.map((l) => l.style), ["head", "sub"]);
  assert.equal(countPages(T("2026-11-26T12:00:00-05:00"))[0].ms, COUNT_MS);
});

test("the on-the-day cards: JUNETEENTH, FREEDOM DAY / JUNE 19; HAPPY / JUNETEENTH, CELEBRATE / FREEDOM", () => {
  assert.deepEqual(DAY_CARD_NAMES, ["day0", "day1"]);
  assert.deepEqual(DAY_CARDS.map(texts), [
    [["JUNETEENTH"], ["FREEDOM DAY", "JUNE 19"]],
    [["HAPPY", "JUNETEENTH"], ["CELEBRATE", "FREEDOM"]],
  ]);
  assert.deepEqual(DAY_CARDS[0][0].lines.map((l) => l.style), ["mid"]);
  assert.deepEqual(DAY_CARDS[1][0].lines.map((l) => l.style), ["top", "bot"]);
  const day = T("2027-06-19T10:00:00-05:00");
  assert.deepEqual(texts(cardPages("day1", day)), [["HAPPY", "JUNETEENTH"], ["CELEBRATE", "FREEDOM"]]);
  // the day cards say the same thing on every date (they are only used on the day or in holiday mode)
  assert.deepEqual(cardPages("day0", T("2026-11-26T10:00:00-05:00")), cardPages("day0", day));
  assert.equal(cardBackdrop("day0"), "day_bg");
  assert.equal(cardBackdrop("count"), "count_bg");
  assert.equal(cardBackdrop("clock"), "clock_bg");
});

test("clock card: time, then date, from the bar's wall clock", () => {
  assert.deepEqual(texts(clockPages(T("2027-06-19T07:05:42-05:00"))), [["07:05"], ["SAT 19 JUN"]]);
  assert.deepEqual(texts(clockPages(T("2028-06-19T23:59:00+09:00"))), [["23:59"], ["MON 19 JUN"]]);
  assert.deepEqual(texts(cardPages("clock", T("2026-11-26T18:05:00-05:00"))), [["18:05"], ["THU 26 NOV"]]);
});

test("playlist: scene, clock, scene, count; the day cards before, on and after the day, and in holiday mode", () => {
  const n = SHOW.scenes.length;
  assert.equal(n, 7);
  const before = playlist(n, T("2026-11-26T12:00:00-05:00"), false);
  assert.deepEqual(names(before), [0, "clock", 1, "count", 2, "clock", 3, "count", 4, "clock", 5, "count", 6, "clock"]);
  const onDay = playlist(n, T("2027-06-19T12:00:00-05:00"), false);
  assert.deepEqual(names(onDay), [0, "clock", 1, "day0", 2, "clock", 3, "day1", 4, "clock", 5, "day0", 6, "clock"]);
  assert.deepEqual(playlist(n, T("2028-06-19T12:00:00-05:00"), false), onDay);
  assert.deepEqual(playlist(n, T("2026-11-26T12:00:00-05:00"), true), onDay); // holiday mode
  assert.deepEqual(playlist(n, T("2027-06-20T12:00:00-05:00"), false), before); // the day after
  assert.deepEqual(playlist(n, T("2027-06-18T23:59:00-05:00"), false), before); // the day before
  // the scenes always open solemn: dawn, then the news
  assert.deepEqual(SHOW.scenes.slice(0, 2).map((s) => s.name), ["dawn", "news"]);
  assert.equal(SHOW.scenes[n - 1].name, "finale");
  // START jumps to the first count slot, whatever the date
  assert.deepEqual(names(before)[firstCountStep(n)], "count");
  assert.deepEqual(names(onDay)[firstCountStep(n)], "day0");
});

test("every text fits the display and uses only glyphs the fonts have", () => {
  const all: [string, string][] = [];
  for (const card of DAY_CARDS) for (const page of card) for (const l of page.lines) all.push([l.style, l.text]);
  // a fixed date: the longest countdown is 365 days (the day after June 19, before a leap day)
  all.push(["head", "365 DAYS"], ["head", "1 DAY"], ["sub", "TO JUNETEENTH"], ["date", "WED 28 SEP"], ["time", "23:59"]);
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
  let most = 0;
  for (let y = 2026; y <= 2040; y++) {
    for (let d = 0; d < 366; d++) {
      const date = new Date(Date.UTC(y, 0, 1 + d));
      if (date.getUTCFullYear() !== y) continue;
      most = Math.max(most, daysToJuneteenth(T(date.toISOString().slice(0, 10) + "T12:00:00+00:00")));
    }
  }
  assert.equal(most, 365, `longest countdown ${most}`);
});

test("the mockup runs the same logic as the app on every day of 2026-2030", () => {
  const html = readFileSync(new URL("../mockup/index.html", import.meta.url), "utf8");
  const start = html.indexOf("const JUNETEENTH = (() => {");
  const end = html.indexOf("})();", start);
  assert.ok(start > 0 && end > start, "the mockup inlines the app's logic");
  const M = new Function(html.slice(start, end + 5) + "\nreturn JUNETEENTH;")();
  for (let y = 2026; y <= 2030; y++) {
    for (let d = 0; d < 366; d++) {
      const date = new Date(Date.UTC(y, 0, 1 + d));
      if (date.getUTCFullYear() !== y) continue;
      const t = T(date.toISOString().slice(0, 10) + "T09:30:00-05:00");
      assert.equal(M.daysToJuneteenth(t), daysToJuneteenth(t));
      for (const name of ["clock", "count", ...DAY_CARD_NAMES]) {
        assert.deepEqual(M.cardPages(name, t), cardPages(name, t));
      }
      assert.deepEqual(M.playlist(7, t, false), playlist(7, t, false));
      assert.deepEqual(M.playlist(7, t, true), playlist(7, t, true));
    }
  }
  assert.equal(M.firstCountStep(7), firstCountStep(7));
});

test("show runner: START (holiday mode) restarts on a day card over the holiday backdrop", async () => {
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
        return { timestamp: "2026-11-26T10:00:00-05:00" };
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
    let holiday = false;
    const show = createShow({
      app: "test", device, fonts: FONTS, scenes: SHOW.scenes, cards, report: (e) => { throw e; },
      steps: (t) => playlist(SHOW.scenes.length, t, holiday),
    });
    const flush = async (ms: number) => {
      for (let i = 0; i < 20; i++) await Promise.resolve();
      mock.timers.tick(ms);
      for (let i = 0; i < 20; i++) await Promise.resolve();
    };
    show.start();
    await flush(0);
    assert.deepEqual(show.steps[firstCountStep(SHOW.scenes.length)], { kind: "card", card: "count" });
    assert.equal(log[0], `anim ${SHOW.scenes[0].path}`);
    // START, as main.ts handles it
    assert.equal(show.input({ key: "start", action: "short" }), "ignored");
    holiday = true;
    log.length = 0;
    show.start(firstCountStep(SHOW.scenes.length));
    await flush(0);
    await flush(0);
    assert.equal(show.index, firstCountStep(SHOW.scenes.length));
    assert.deepEqual(show.steps[show.index], { kind: "card", card: "day0" });
    assert.ok(log.includes(`anim ${SHOW.backdrops.day_bg}`), log.join("\n"));
    assert.ok(log.includes("text text0 34"), "the greeting fades in");
    show.stop();
  } finally {
    mock.timers.reset();
  }
});
