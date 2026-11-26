// Unit tests for the app's date logic and card texts (app/shared/halloween.ts), against real dates, plus one run of
// the real show runner with this app's cards, and a check that the mockup runs the very same logic. Run:
// node --experimental-strip-types --test tests/logic.test.mts (Node 24).

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { mock, test } from "node:test";

import { parseLocal, type LocalTime } from "../../../lib/ts/busybar/walltime.ts";
import { createShow, type Card, type ShowDevice } from "../../../lib/ts/busybar/showrunner.ts";
import {
  DAY_CARDS, DAY_CARD_NAMES, HW_COUNT_MS, HW_COUNT_SUB, cardPages, clockPages, countPages, isHalloween,
  nightsLabel, nightsToHalloween, playlist,
} from "../app/shared/halloween.ts";
import { FONTS, LAYOUT, SHOW } from "../app/shared/generated/show.ts";

const T = (iso: string): LocalTime => {
  const t = parseLocal(iso);
  assert.ok(t, iso);
  return t;
};
const texts = (pages: { lines: { text: string }[] }[]) => pages.map((p) => p.lines.map((l) => l.text));
const GREETING = ["HAPPY", "HALLOWEEN"];

test("Halloween dates: Oct 31 every year, counted in nights", () => {
  assert.equal(nightsToHalloween(T("2027-10-31T00:00:00-04:00")), 0); // Sun 31 Oct 2027
  assert.equal(nightsToHalloween(T("2027-10-31T23:59:59+09:00")), 0);
  assert.equal(nightsToHalloween(T("2028-10-31T18:00:00+00:00")), 0); // Tue 31 Oct 2028
  assert.equal(nightsToHalloween(T("2026-11-26T12:00:00-05:00")), 339);
  assert.equal(nightsToHalloween(T("2027-10-30T23:59:59-04:00")), 1); // the night before
  assert.equal(nightsToHalloween(T("2027-01-01T00:00:00-05:00")), 303);
  assert.equal(nightsToHalloween(T("2027-11-01T00:00:00-04:00")), 365); // the day after: 29 Feb 2028 in between
  assert.equal(nightsToHalloween(T("2028-11-01T08:00:00-04:00")), 364); // to 31 Oct 2029
  assert.equal(nightsToHalloween(T("2026-10-31T12:00:00-04:00")), 0); // Sat 31 Oct 2026
});

test("nightsLabel: one night, many nights", () => {
  assert.equal(nightsLabel(1), "1 NIGHT");
  assert.equal(nightsLabel(2), "2 NIGHTS");
  assert.equal(nightsLabel(339), "339 NIGHTS");
});

test("isHalloween: only on the day, or any day in holiday mode", () => {
  assert.equal(isHalloween(T("2027-10-31T00:00:00-04:00"), false), true);
  assert.equal(isHalloween(T("2027-10-30T23:59:00-04:00"), false), false);
  assert.equal(isHalloween(T("2027-11-01T00:00:00-04:00"), false), false);
  assert.equal(isHalloween(T("2026-11-26T12:00:00-05:00"), true), true);
});

test("countdown card before and after the day; the greeting on it", () => {
  assert.equal(HW_COUNT_SUB, "TO HALLOWEEN");
  assert.deepEqual(texts(countPages(T("2026-11-26T12:00:00-05:00"))), [["339 NIGHTS", HW_COUNT_SUB]]);
  assert.deepEqual(texts(countPages(T("2027-10-30T08:00:00-04:00"))), [["1 NIGHT", HW_COUNT_SUB]]);
  assert.deepEqual(texts(countPages(T("2027-10-29T08:00:00-04:00"))), [["2 NIGHTS", HW_COUNT_SUB]]);
  assert.deepEqual(texts(countPages(T("2027-11-01T08:00:00-04:00"))), [["365 NIGHTS", HW_COUNT_SUB]]);
  assert.deepEqual(texts(countPages(T("2027-10-31T20:00:00-04:00"))), [GREETING]);
  assert.deepEqual(countPages(T("2026-11-26T12:00:00-05:00"))[0].lines.map((l) => l.style), ["head", "sub"]);
  assert.equal(countPages(T("2026-11-26T12:00:00-05:00"))[0].ms, HW_COUNT_MS);
});

test("the on-the-day cards: the greeting, then a spooky-fun phrase", () => {
  assert.deepEqual(DAY_CARD_NAMES, ["day0", "day1", "day2", "day3"]);
  assert.deepEqual(DAY_CARDS.map(texts), [
    [GREETING, ["TRICK OR", "TREAT!"]],
    [GREETING, ["BOO!"]],
    [GREETING, ["SPOOKY", "SEASON"]],
    [GREETING, ["HAPPY", "HAUNTING"]],
  ]);
  for (const card of DAY_CARDS) assert.deepEqual(card[0].lines.map((l) => l.style), ["hi", "lo"]);
  assert.deepEqual(DAY_CARDS[1][1].lines.map((l) => l.style), ["boo"]);
  const day = T("2027-10-31T19:00:00-04:00");
  assert.deepEqual(texts(cardPages("day2", day)), [GREETING, ["SPOOKY", "SEASON"]]);
});

test("clock card: time, then date, from the bar's wall clock", () => {
  assert.deepEqual(texts(clockPages(T("2027-10-31T07:05:42-04:00"))), [["07:05"], ["SUN 31 OCT"]]);
  assert.deepEqual(texts(clockPages(T("2028-10-31T23:59:00+09:00"))), [["23:59"], ["TUE 31 OCT"]]);
  assert.deepEqual(texts(cardPages("clock", T("2026-11-26T18:05:00-05:00"))), [["18:05"], ["THU 26 NOV"]]);
});

test("playlist: scene, clock, scene, count; the day cards on the day and in holiday mode", () => {
  const n = SHOW.scenes.length;
  assert.equal(n, 8);
  const names = (steps: ReturnType<typeof playlist>) => steps.map((s) => (s.kind === "scene" ? s.scene : s.card));
  const before = playlist(n, T("2026-11-26T12:00:00-05:00"), false);
  assert.deepEqual(names(before),
    [0, "clock", 1, "count", 2, "clock", 3, "count", 4, "clock", 5, "count", 6, "clock", 7, "count"]);
  const onDay = playlist(n, T("2027-10-31T12:00:00-04:00"), false);
  assert.deepEqual(names(onDay),
    [0, "clock", 1, "day0", 2, "clock", 3, "day1", 4, "clock", 5, "day2", 6, "clock", 7, "day3"]);
  assert.deepEqual(playlist(n, T("2028-10-31T00:00:00-04:00"), false), onDay);
  assert.deepEqual(playlist(n, T("2026-11-26T12:00:00-05:00"), true), onDay); // holiday mode
  assert.deepEqual(playlist(n, T("2027-11-01T00:00:00-04:00"), false), before); // the day after
  assert.deepEqual(playlist(n, T("2027-10-30T23:59:00-04:00"), false), before); // the day before
  // START: the cycle is rotated to begin at the first count slot, same steps
  const rotated = playlist(n, T("2026-11-26T12:00:00-05:00"), true, true);
  assert.deepEqual(names(rotated),
    ["day0", 2, "clock", 3, "day1", 4, "clock", 5, "day2", 6, "clock", 7, "day3", 0, "clock", 1]);
  assert.deepEqual(names(playlist(n, T("2026-11-26T12:00:00-05:00"), false, true))[0], "count");
});

test("every text fits the display, fits between the backdrops' corner art, and has its glyphs", () => {
  const all: [string, string][] = [];
  for (const card of DAY_CARDS) for (const page of card) for (const l of page.lines) all.push([l.style, l.text]);
  // the longest countdowns: 365 nights the day after a Halloween that precedes a leap day
  all.push(["head", nightsLabel(365)], ["head", nightsLabel(1)], ["sub", HW_COUNT_SUB], ["date", "WED 28 SEP"],
    ["time", "23:59"], ["time", "00:00"]);
  const layout = LAYOUT as Record<string, { font: string }>;
  for (const [style, text] of all) {
    const font = FONTS[layout[style].font];
    let w = 0;
    for (const ch of text) {
      assert.ok(font.glyphs[ch], `${style}: ${JSON.stringify(ch)} missing from ${layout[style].font}`);
      w += font.glyphs[ch][0].length + font.gap;
    }
    w -= font.gap;
    // centered with a 1 px shadow, the text must stay inside columns 8..63 (scenes.text.TEXT_GAP)
    const x = Math.floor((72 - w) / 2);
    assert.ok(x >= 8 && x + w <= 63, `${text} (${w} px at x=${x}) collides with the corner art`);
  }
});

test("the mockup runs the app's own logic (same texts and playlists, every day of three years)", () => {
  const html = readFileSync(new URL("../mockup/index.html", import.meta.url), "utf8");
  const m = html.match(/const HW = \(\(\) => \{[\s\S]*?\n\}\)\(\);/);
  assert.ok(m, "mockup logic block");
  const HW = new Function(`${m[0]}; return HW;`)();
  for (let d = 0; d < 3 * 366; d++) {
    const ms = Date.UTC(2026, 9, 1) + d * 86400000;
    const dt = new Date(ms);
    const iso = `${dt.toISOString().slice(0, 10)}T21:30:00-04:00`;
    const t = T(iso);
    assert.equal(HW.nightsToHalloween(t), nightsToHalloween(t), iso);
    for (const name of ["clock", "count", ...DAY_CARD_NAMES]) {
      assert.deepEqual(HW.cardPages(name, t), cardPages(name, t), `${iso} ${name}`);
    }
    assert.deepEqual(HW.playlist(8, t, false), playlist(8, t, false), iso);
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
        return { timestamp: "2027-10-31T19:00:00-04:00" };
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
