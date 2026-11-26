// Unit tests for the app's date logic and card texts (app/shared/july4.ts), against real dates and times, plus runs
// of the real show runner with this app's cards and a check that the mockup runs the same logic. Run:
// node --experimental-strip-types --test tests/logic.test.mts (Node 24).

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { mock, test } from "node:test";

import { addSeconds, parseLocal, type LocalTime } from "../../../lib/ts/busybar/walltime.ts";
import { createShow, type Card, type ShowDevice, type ShowElement, type Step } from "../../../lib/ts/busybar/showrunner.ts";
import { textBitmap, type TextSpec } from "../../../lib/ts/busybar/xpmtext.ts";
import {
  COUNT_MS, DAY_CARD, DUSK_HOUR, FIREWORKS_MS, GREETING_MS, cardPages, clockPages, countPages, dayPages,
  daysToJuly4, demoShift, demoTime, fireworksIn, isJuly4, playlist, secondsBetween, secondsToDusk,
} from "../app/shared/july4.ts";
import { FONTS, LAYOUT, SHOW } from "../app/shared/generated/show.ts";

const T = (iso: string): LocalTime => {
  const t = parseLocal(iso);
  assert.ok(t, iso);
  return t;
};
const texts = (pages: { lines: { text: string }[] }[]) => pages.map((p) => p.lines.map((l) => l.text));
const SPECS = LAYOUT as unknown as Record<string, TextSpec>;

test("July 4 dates: the count to the next Fourth", () => {
  assert.equal(daysToJuly4(T("2026-11-26T12:00:00-07:00")), 220);
  assert.equal(daysToJuly4(T("2027-07-03T23:59:59-04:00")), 1);
  assert.equal(daysToJuly4(T("2027-07-04T00:00:00-04:00")), 0);
  assert.equal(daysToJuly4(T("2027-07-04T23:59:59-04:00")), 0);
  assert.equal(daysToJuly4(T("2027-07-05T00:00:00-04:00")), 365); // to 4 Jul 2028, across 29 Feb
  assert.equal(daysToJuly4(T("2028-07-05T08:00:00+00:00")), 364);
  assert.equal(daysToJuly4(T("2027-12-31T20:00:00-05:00")), 186);
  assert.equal(daysToJuly4(T("2028-01-01T00:00:00-05:00")), 185);
  assert.equal(daysToJuly4(T("2030-07-04T12:00:00+09:00")), 0);
});

test("isJuly4: only on the day, or any day in holiday mode", () => {
  assert.equal(isJuly4(T("2027-07-04T00:00:00-04:00"), false), true);
  assert.equal(isJuly4(T("2027-07-03T23:59:00-04:00"), false), false);
  assert.equal(isJuly4(T("2027-07-05T00:00:00-04:00"), false), false);
  assert.equal(isJuly4(T("2026-11-26T12:00:00-07:00"), true), true);
});

test("the fireworks countdown: hours and minutes to 21:00, rounded up", () => {
  assert.equal(DUSK_HOUR, 21);
  assert.equal(fireworksIn(T("2027-07-04T00:00:00-04:00")), "21:00");
  assert.equal(fireworksIn(T("2027-07-04T08:30:00-04:00")), "12:30");
  assert.equal(fireworksIn(T("2027-07-04T18:45:00-04:00")), "02:15");
  assert.equal(fireworksIn(T("2027-07-04T19:59:30-04:00")), "01:01");
  assert.equal(fireworksIn(T("2027-07-04T20:00:00-04:00")), "01:00");
  assert.equal(fireworksIn(T("2027-07-04T20:58:00-04:00")), "00:02");
  assert.equal(fireworksIn(T("2027-07-04T20:59:00-04:00")), "00:01");
  assert.equal(fireworksIn(T("2027-07-04T20:59:59-04:00")), "00:01");
  assert.equal(fireworksIn(T("2027-07-04T21:00:00-04:00")), null);
  assert.equal(fireworksIn(T("2027-07-04T21:00:01-04:00")), null);
  assert.equal(fireworksIn(T("2027-07-04T23:59:59-04:00")), null);
  assert.equal(secondsToDusk(T("2027-07-04T20:59:00-04:00")), 60);
  assert.equal(secondsToDusk(T("2027-07-04T21:00:00-04:00")), 0);
});

test("the day card at 20:59, at 21:00 and after", () => {
  const greeting = ["HAPPY", "4TH OF JULY"];
  assert.deepEqual(texts(dayPages(T("2027-07-04T20:59:00-04:00"))), [greeting, ["FIREWORKS IN", "00:01"]]);
  assert.deepEqual(texts(dayPages(T("2027-07-04T21:00:00-04:00"))), [greeting, ["ENJOY THE", "FIREWORKS!"]]);
  assert.deepEqual(texts(dayPages(T("2027-07-04T22:30:00-04:00"))), [greeting, ["ENJOY THE", "FIREWORKS!"]]);
  assert.deepEqual(texts(dayPages(T("2027-07-04T09:10:00-04:00"))), [greeting, ["FIREWORKS IN", "11:50"]]);
  const pages = dayPages(T("2027-07-04T12:00:00-04:00"));
  assert.deepEqual(pages.map((p) => p.ms), [GREETING_MS, FIREWORKS_MS]);
  assert.deepEqual(pages.map((p) => p.lines.map((l) => l.style)), [["head", "sub"], ["lead", "num"]]);
  assert.deepEqual(dayPages(T("2027-07-04T21:30:00-04:00"))[1].lines.map((l) => l.style), ["lead", "num"]);
  assert.deepEqual(texts(cardPages(DAY_CARD, T("2027-07-04T20:59:00-04:00"))),
    texts(dayPages(T("2027-07-04T20:59:00-04:00"))));
});

test("countdown card before, on and after the day", () => {
  assert.deepEqual(texts(countPages(T("2026-11-26T12:00:00-07:00"))), [["220 DAYS", "TO JULY 4TH"]]);
  assert.deepEqual(texts(countPages(T("2027-07-03T08:00:00-04:00"))), [["1 DAY", "TO JULY 4TH"]]);
  assert.deepEqual(texts(countPages(T("2027-07-05T08:00:00-04:00"))), [["365 DAYS", "TO JULY 4TH"]]);
  assert.deepEqual(texts(countPages(T("2028-07-05T08:00:00-04:00"))), [["364 DAYS", "TO JULY 4TH"]]);
  // the count card itself still counts on the day (on the day the playlist uses the day card instead)
  assert.deepEqual(texts(cardPages("count", T("2027-07-04T10:00:00-04:00"))), [["0 DAYS", "TO JULY 4TH"]]);
  assert.deepEqual(countPages(T("2026-11-26T12:00:00-07:00"))[0].lines.map((l) => l.style), ["head", "sub"]);
  assert.equal(countPages(T("2026-11-26T12:00:00-07:00"))[0].ms, COUNT_MS);
});

test("clock card: time, then date, from the bar's wall clock", () => {
  assert.deepEqual(texts(clockPages(T("2027-07-04T07:05:42-04:00"))), [["07:05"], ["SUN 4 JUL"]]);
  assert.deepEqual(texts(clockPages(T("2028-07-04T23:59:00+09:00"))), [["23:59"], ["TUE 4 JUL"]]);
  assert.deepEqual(texts(cardPages("clock", T("2026-11-26T18:05:00-07:00"))), [["18:05"], ["THU 26 NOV"]]);
});

const names = (steps: ReturnType<typeof playlist>) => steps.map((s) => (s.kind === "scene" ? s.scene : s.card));

test("playlist: scene, clock, scene, count; the day card on the day and in holiday mode", () => {
  const n = SHOW.scenes.length;
  assert.equal(n, 7);
  const before = playlist(n, T("2026-11-26T12:00:00-07:00"), false);
  assert.deepEqual(names(before), [0, "clock", 1, "count", 2, "clock", 3, "count", 4, "clock", 5, "count", 6, "clock"]);
  const onDay = playlist(n, T("2027-07-04T12:00:00-04:00"), false);
  assert.deepEqual(names(onDay), [0, "clock", 1, "day", 2, "clock", 3, "day", 4, "clock", 5, "day", 6, "clock"]);
  assert.deepEqual(playlist(n, T("2027-07-04T22:00:00-04:00"), false), onDay); // after dusk too
  assert.deepEqual(playlist(n, T("2026-11-26T12:00:00-07:00"), true), onDay); // holiday mode
  assert.deepEqual(playlist(n, T("2027-07-05T00:00:00-04:00"), false), before); // the day after
  assert.deepEqual(playlist(n, T("2027-07-03T23:59:00-04:00"), false), before); // the day before
  // START: the cycle is rotated to begin at the first count slot, same steps
  assert.deepEqual(names(playlist(n, T("2026-11-26T12:00:00-07:00"), true, true)),
    ["day", 2, "clock", 3, "day", 4, "clock", 5, "day", 6, "clock", 0, "clock", 1]);
  assert.equal(names(playlist(n, T("2026-11-26T12:00:00-07:00"), false, true))[0], "count");
  // demo: the day card after every scene, starting on it
  assert.deepEqual(names(playlist(n, T("2027-07-04T20:58:00-04:00"), true, true, true)),
    ["day", 1, "day", 2, "day", 3, "day", 4, "day", 5, "day", 6, "day", 0]);
});

test("demo mode: the Fourth at 20:58, keeping the bar's seconds, then the count runs out", () => {
  const anchor = T("2026-11-26T14:23:17-07:00");
  const shift = demoShift(anchor);
  assert.equal(Math.abs(shift % 60), 0, "a whole number of minutes, so minute rollovers stay on the bar's");
  const at = (s: number) => demoTime(addSeconds(anchor, s), shift);
  assert.deepEqual(at(0), { year: 2026, month: 7, day: 4, hour: 20, minute: 58, second: 17 });
  assert.ok(isJuly4(at(0), false));
  assert.equal(fireworksIn(at(0)), "00:02");
  assert.equal(fireworksIn(at(43)), "00:01"); // the bar's next minute rollover
  assert.equal(fireworksIn(at(102)), "00:01");
  assert.equal(fireworksIn(at(103)), null); // 21:00:00
  assert.equal(secondsBetween(anchor, at(0)), shift);
  // the shifted clock rolls over exactly when the bar's does
  for (const s of [0, 30, 42, 43, 100, 3600]) assert.equal(addSeconds(anchor, s).second, at(s).second);
  // a demo begun on July 4 itself, or late in the year
  assert.deepEqual(demoTime(T("2027-07-04T22:10:05-04:00"), demoShift(T("2027-07-04T22:10:05-04:00"))),
    { year: 2027, month: 7, day: 4, hour: 20, minute: 58, second: 5 });
  assert.equal(fireworksIn(demoTime(T("2027-12-31T23:59:59-05:00"), demoShift(T("2027-12-31T23:59:59-05:00")))),
    "00:02");
});

test("every text fits the display and uses only glyphs the fonts have", () => {
  const all = new Map<string, [string, string]>();
  const add = (t: LocalTime, name: string) => {
    for (const page of cardPages(name, t)) for (const l of page.lines) all.set(l.style + "|" + l.text, [l.style, l.text]);
  };
  // every minute of the Fourth (the countdown's every value), and every day of two years
  let t = T("2027-07-04T00:00:00-04:00");
  for (let m = 0; m < 24 * 60; m++, t = addSeconds(t, 60)) add(t, DAY_CARD);
  t = T("2027-01-01T12:00:00-05:00");
  for (let d = 0; d < 731; d++, t = addSeconds(t, 86400)) for (const name of ["clock", "count"]) add(t, name);
  for (const s of ["23:59", "00:00"]) all.set("time|" + s, ["time", s]);
  assert.ok(all.has("head|365 DAYS") && all.has("num|21:00") && all.has("num|00:01") && all.has("num|FIREWORKS!"));
  const layout = LAYOUT as Record<string, { font: string }>;
  for (const [style, text] of all.values()) {
    const font = FONTS[layout[style].font];
    let w = 0;
    for (const ch of text) {
      assert.ok(font.glyphs[ch], `${style}: ${JSON.stringify(ch)} missing from ${layout[style].font}`);
      w += font.glyphs[ch][0].length + font.gap;
    }
    assert.ok(w - font.gap + 1 <= 72, `${text} is ${w - font.gap} px wide`);
  }
});

// --- the real show runner -----------------------------------------------------------------------------------

function cardsFor(view: (t: LocalTime) => LocalTime = (t) => t): Record<string, Card> {
  const card = (name: string, path: string): Card => ({
    path,
    pages: (t0) => cardPages(name, view(t0)).map((page, p) => ({
      ms: page.ms,
      lines: page.lines.map((line, k) => ({
        spec: SPECS[line.style],
        text: (t: LocalTime) => cardPages(name, view(t))[p]?.lines[k]?.text ?? "",
      })),
    })),
  });
  return { clock: card("clock", SHOW.backdrops.clock_bg), count: card("count", SHOW.backdrops.count_bg),
    day: card("day", SHOW.backdrops.count_bg) };
}

async function runShow(timestamp: string, steps: (t: LocalTime) => Step[], ms: number,
  view?: (t: LocalTime) => LocalTime): Promise<ShowElement[]> {
  mock.timers.enable({ apis: ["setTimeout"] });
  const drawn: ShowElement[] = [];
  try {
    const device: ShowDevice = {
      async DisplayDraw(p) { drawn.push(...p.elements); },
      async DisplayClear() {},
      async TimeGet() { return { timestamp }; },
    };
    const show = createShow({ app: "test", device, fonts: FONTS, scenes: SHOW.scenes, cards: cardsFor(view),
      report: (e) => { throw e; }, steps });
    const flush = async (step: number) => {
      for (let i = 0; i < 20; i++) await Promise.resolve();
      mock.timers.tick(step);
      for (let i = 0; i < 20; i++) await Promise.resolve();
    };
    show.start();
    await flush(0);
    await flush(0);
    for (let at = 0; at < ms; at += 50) await flush(50);
    show.stop();
  } finally {
    mock.timers.reset();
  }
  return drawn;
}

const bitmap = (text: string, style: string) => textBitmap(text, FONTS[SPECS[style].font] as any, SPECS[style]).data;
const shows = (drawn: ShowElement[], text: string, style: string) =>
  drawn.some((e) => e.type === "xpmbitmap" && e.data === bitmap(text, style) && e.opacity === 100);

test("show runner: at 20:59:55 the day card counts 00:01, then turns to ENJOY THE FIREWORKS! at 21:00", async () => {
  const drawn = await runShow("2027-07-04T20:59:55-04:00", () => [{ kind: "card", card: DAY_CARD }], 9000);
  assert.equal(drawn[0].type === "animation" && drawn[0].path, SHOW.backdrops.count_bg);
  assert.ok(shows(drawn, "HAPPY", "head") && shows(drawn, "4TH OF JULY", "sub"), "the greeting page");
  assert.ok(shows(drawn, "FIREWORKS IN", "lead") && shows(drawn, "00:01", "num"), "the countdown page at 20:59:59");
  assert.ok(shows(drawn, "ENJOY THE", "lead") && shows(drawn, "FIREWORKS!", "num"), "redrawn at the 21:00 rollover");
});

test("show runner: demo mode's shifted clock counts down on the bar's own minute rollovers", async () => {
  const anchor = T("2026-11-26T14:23:56-07:00");
  const shift = demoShift(anchor);
  const view = (t: LocalTime) => demoTime(t, shift);
  const drawn = await runShow("2026-11-26T14:23:56-07:00",
    (t) => playlist(SHOW.scenes.length, view(t), true, true, true), 9000, view);
  assert.ok(shows(drawn, "FIREWORKS IN", "lead"));
  assert.ok(shows(drawn, "00:02", "num") || shows(drawn, "00:01", "num"));
  assert.ok(shows(drawn, "00:01", "num"), "20:58 -> 20:59 at the bar's rollover");
});

// --- the mockup runs the same logic --------------------------------------------------------------------------

test("mockup: its inlined logic matches the app's for every day of four years", () => {
  const html = readFileSync(new URL("../mockup/index.html", import.meta.url), "utf8");
  const m = /const J4 = \(\(\) => \{[\s\S]*?\n\}\)\(\);/.exec(html);
  assert.ok(m, "the mockup inlines the app's logic as J4");
  const J4 = new Function(m[0] + "\nreturn J4;")();
  let t = T("2026-01-01T00:00:00-05:00");
  for (let d = 0; d < 4 * 366; d++, t = addSeconds(t, 86400 + 37 * 60)) {
    for (const name of ["clock", "count", "day"]) assert.deepEqual(J4.cardPages(name, t), cardPages(name, t));
    for (const holiday of [false, true]) {
      assert.deepEqual(J4.playlist(7, t, holiday, false, false), playlist(7, t, holiday, false, false));
    }
    assert.equal(J4.demoShift(t), demoShift(t));
  }
});
