// Unit tests for the app's date logic, card texts and the 11:00 moment (app/shared/veterans.ts), against real
// Veterans Day dates; the mockup's inlined copy of the same logic; and runs of the real show runner with this app's
// cards and moment timer. Run: node --experimental-strip-types --test tests/logic.test.mts (Node 24).

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { mock, test } from "node:test";

import { parseLocal, type LocalTime } from "../../../lib/ts/busybar/walltime.ts";
import { createShow, type Card, type ShowDevice } from "../../../lib/ts/busybar/showrunner.ts";
import * as V from "../app/shared/veterans.ts";
import { FONTS, LAYOUT, SHOW } from "../app/shared/generated/show.ts";

const T = (iso: string): LocalTime => {
  const t = parseLocal(iso);
  assert.ok(t, iso);
  return t;
};
const texts = (pages: { lines: { text: string }[] }[]) => pages.map((p) => p.lines.map((l) => l.text));
const names = (steps: V.PlayStep[]) =>
  steps.map((s) => (s.kind === "scene" ? SHOW.scenes[s.scene].name : s.card));

const BEFORE = ["main_street", "clock", "parade", "count", "salute", "clock", "poppies", "count", "thank_you",
  "clock", "finale", "count"];
const DAY = ["main_street", "clock", "parade", "day0", "salute", "clock", "poppies", "day1", "thank_you", "clock",
  "finale", "day2"];

test("Veterans Day dates: November 11 every year", () => {
  assert.equal(V.daysToVeteransDay(T("2026-11-11T09:00:00-05:00")), 0);
  assert.equal(V.daysToVeteransDay(T("2027-11-11T00:00:00-05:00")), 0); // a Thursday
  assert.equal(V.daysToVeteransDay(T("2028-11-11T23:59:59-05:00")), 0); // a Saturday: still Nov 11
  assert.equal(V.daysToVeteransDay(T("2026-11-26T12:00:00-05:00")), 350); // today: Thanksgiving 2026
  assert.equal(V.daysToVeteransDay(T("2027-11-10T23:59:59-05:00")), 1);
  assert.equal(V.daysToVeteransDay(T("2027-11-12T00:00:00-05:00")), 365); // to Nov 11 2028 (a leap year)
  assert.equal(V.daysToVeteransDay(T("2028-11-12T00:00:00-05:00")), 364);
  assert.equal(V.daysToVeteransDay(T("2027-01-01T08:00:00+09:00")), 314);
});

test("isVeteransDay: only on the day, or any day in holiday mode", () => {
  assert.equal(V.isVeteransDay(T("2027-11-11T00:00:00-05:00")), true);
  assert.equal(V.isVeteransDay(T("2027-11-10T23:59:00-05:00")), false);
  assert.equal(V.isVeteransDay(T("2027-11-12T00:00:00-05:00")), false);
  assert.equal(V.isVeteransDay(T("2026-11-26T12:00:00-05:00"), "day"), true);
  assert.equal(V.isVeteransDay(T("2026-11-26T12:00:00-05:00"), "moment"), true);
});

test("the 11:00 moment: 11:00:00 to 11:00:59 on Nov 11 only (10:59, 11:00, 11:01)", () => {
  assert.equal(V.inMoment(T("2027-11-11T10:59:00-05:00")), false);
  assert.equal(V.inMoment(T("2027-11-11T10:59:59-05:00")), false);
  assert.equal(V.inMoment(T("2027-11-11T11:00:00-05:00")), true);
  assert.equal(V.inMoment(T("2027-11-11T11:00:02-05:00")), true);
  assert.equal(V.inMoment(T("2027-11-11T11:00:59-05:00")), true);
  assert.equal(V.inMoment(T("2027-11-11T11:01:00-05:00")), false);
  assert.equal(V.inMoment(T("2027-11-11T23:00:00-05:00")), false); // 23:00 is not the 11th hour
  assert.equal(V.inMoment(T("2027-11-10T11:00:00-05:00")), false); // the day before
  assert.equal(V.inMoment(T("2027-10-11T11:00:00-04:00")), false); // the 11th of another month
  assert.equal(V.inMoment(T("2028-11-11T11:00:30+01:00")), true);
  // holiday mode: "moment" always, "day" only by the clock
  assert.equal(V.inMoment(T("2026-11-26T18:00:00-05:00"), "moment"), true);
  assert.equal(V.inMoment(T("2026-11-26T11:00:00-05:00"), "day"), false);
});

test("msToMoment: a timer for 11:00:02, armed only within 10 minutes, only on Nov 11", () => {
  assert.equal(V.msToMoment(T("2027-11-11T10:59:00-05:00")), 62000);
  assert.equal(V.msToMoment(T("2027-11-11T10:59:59-05:00")), 3000);
  assert.equal(V.msToMoment(T("2027-11-11T10:51:00-05:00")), 542000);
  assert.equal(V.msToMoment(T("2027-11-11T10:50:00-05:00")), null);
  assert.equal(V.msToMoment(T("2027-11-11T09:00:00-05:00")), null);
  assert.equal(V.msToMoment(T("2027-11-11T11:00:00-05:00")), null); // the cycle starting now shows it already
  assert.equal(V.msToMoment(T("2027-11-11T11:01:00-05:00")), null);
  assert.equal(V.msToMoment(T("2027-11-10T10:59:00-05:00")), null);
});

test("START cycles holiday mode: off, day, moment, off", () => {
  assert.equal(V.nextMode("off"), "day");
  assert.equal(V.nextMode("day"), "moment");
  assert.equal(V.nextMode("moment"), "off");
});

test("countdown card before and after the day", () => {
  assert.deepEqual(texts(V.countPages(T("2026-11-26T12:00:00-05:00"))), [["350 DAYS", "TO VETERANS DAY"]]);
  assert.deepEqual(texts(V.countPages(T("2027-11-10T08:00:00-05:00"))), [["1 DAY", "TO VETERANS DAY"]]);
  assert.deepEqual(texts(V.countPages(T("2027-11-12T08:00:00-05:00"))), [["365 DAYS", "TO VETERANS DAY"]]);
  assert.deepEqual(V.countPages(T("2026-11-26T12:00:00-05:00"))[0].lines.map((l) => l.style), ["head", "sub"]);
  assert.equal(V.countPages(T("2026-11-26T12:00:00-05:00"))[0].ms, V.COUNT_MS);
});

test("the on-the-day cards and the moment card", () => {
  assert.deepEqual(V.DAY_CARD_NAMES, ["day0", "day1", "day2"]);
  assert.deepEqual(V.dayCards().map(texts), [
    [["VETERANS DAY"], ["THANK YOU", "VETERANS"]],
    [["VETERANS DAY"], ["HONOR ALL", "WHO SERVED"]],
    [["VETERANS DAY"], ["THANK YOU", "FOR YOUR SERVICE"]],
  ]);
  assert.deepEqual(texts(V.momentPages()),
    [["11TH HOUR"], ["11TH DAY", "11TH MONTH"], ["ARMISTICE", "NOV 11 1918"], ["THANK YOU", "VETERANS"]]);
  assert.deepEqual(texts(V.cardPages(V.MOMENT_CARD, T("2027-11-11T11:00:05-05:00"))), texts(V.momentPages()));
  assert.equal(V.momentPages().reduce((a, p) => a + p.ms, 0), 20000);
  // no festive greeting anywhere: a tribute (D2)
  for (const card of [...V.dayCards(), V.momentPages()]) for (const p of card)
    for (const l of p.lines) assert.ok(!/HAPPY/.test(l.text), l.text);
});

test("clock card: time, then date, from the bar's wall clock", () => {
  assert.deepEqual(texts(V.clockPages(T("2027-11-11T07:05:42-05:00"))), [["07:05"], ["THU 11 NOV"]]);
  assert.deepEqual(texts(V.cardPages("clock", T("2028-11-11T23:59:00+09:00"))), [["23:59"], ["SAT 11 NOV"]]);
  assert.deepEqual(texts(V.cardPages("clock", T("2026-11-26T18:05:00-05:00"))), [["18:05"], ["THU 26 NOV"]]);
});

test("playlist: count before and after, day cards on the day, the moment card first at 11:00", () => {
  const sc = SHOW.scenes;
  assert.deepEqual(names(V.playlist(sc, T("2026-11-26T09:00:00-05:00"))), BEFORE);
  assert.deepEqual(names(V.playlist(sc, T("2027-11-10T11:00:00-05:00"))), BEFORE); // the day before, at 11:00
  assert.deepEqual(names(V.playlist(sc, T("2027-11-12T11:00:30-05:00"))), BEFORE); // the day after
  assert.deepEqual(names(V.playlist(sc, T("2027-11-11T08:00:00-05:00"))), DAY);
  assert.deepEqual(names(V.playlist(sc, T("2027-11-11T10:59:59-05:00"))), DAY);
  assert.deepEqual(names(V.playlist(sc, T("2027-11-11T11:00:00-05:00"))), ["moment", ...DAY]);
  assert.deepEqual(names(V.playlist(sc, T("2027-11-11T11:00:59-05:00"))), ["moment", ...DAY]);
  assert.deepEqual(names(V.playlist(sc, T("2027-11-11T11:01:00-05:00"))), DAY);
  // holiday mode on any date
  assert.deepEqual(names(V.playlist(sc, T("2026-11-26T20:00:00-05:00"), "day")), DAY);
  assert.deepEqual(names(V.playlist(sc, T("2026-11-26T20:00:00-05:00"), "moment")), ["moment", ...DAY]);
});

test("every text fits the display and uses only glyphs the fonts have", () => {
  const all: [string, string][] = [];
  for (const card of [...V.dayCards(), V.momentPages()])
    for (const page of card) for (const l of page.lines) all.push([l.style, l.text]);
  all.push(["head", "365 DAYS"], ["head", "1 DAY"], ["sub", "TO VETERANS DAY"], ["date", "SUN 20 JAN"],
    ["date", "WED 28 SEP"], ["time", "23:59"], ["time", "00:00"]);
  const layout = LAYOUT as Record<string, { font: string; y: number }>;
  for (const [style, text] of all) {
    const font = FONTS[layout[style].font];
    let w = 0;
    for (const ch of text) {
      assert.ok(font.glyphs[ch], `${style}: ${JSON.stringify(ch)} missing from ${layout[style].font}`);
      w += font.glyphs[ch][0].length + font.gap;
    }
    assert.ok(w - font.gap + 1 <= 72, `${text} is ${w - font.gap} px wide`);
    assert.ok(layout[style].y + font.height + 1 <= 16, `${style} fits vertically`);
  }
});

test("the mockup runs the same logic as the app, every day of 2027 and 2028, around 11:00", () => {
  const html = readFileSync(new URL("../mockup/index.html", import.meta.url), "utf8");
  const start = html.indexOf("const VET = (() => {");
  const end = html.indexOf("})();", start) + "})();".length;
  assert.ok(start > 0 && end > start, "mockup logic block");
  const VET = new Function(html.slice(start, end) + "\nreturn VET;")();
  for (const year of [2027, 2028]) {
    for (let d = 0; d < 366; d++) {
      const date = new Date(Date.UTC(year, 0, 1 + d));
      if (date.getUTCFullYear() !== year) break;
      const ymd = date.toISOString().slice(0, 10);
      for (const hms of ["10:59:59", "11:00:00", "11:01:00"]) {
        const t = T(`${ymd}T${hms}-05:00`);
        assert.deepEqual(VET.msToMoment(t), V.msToMoment(t), `msToMoment ${ymd} ${hms}`);
        for (const m of V.MODES) {
          assert.deepEqual(VET.playlist(SHOW.scenes, t, m), V.playlist(SHOW.scenes, t, m), `${ymd} ${hms} ${m}`);
        }
        for (const name of ["clock", "count", V.MOMENT_CARD, ...V.DAY_CARD_NAMES])
          assert.deepEqual(VET.cardPages(name, t), V.cardPages(name, t), `${name} ${ymd} ${hms}`);
      }
    }
  }
});

// --- the real show runner, wired the way main.ts wires it ------------------------------------------------------

function rig(clock: () => string) {
  const log: string[] = [];
  const device: ShowDevice = {
    async DisplayDraw(p) {
      for (const e of p.elements) log.push(e.type === "animation" ? `anim ${e.path}` : `text ${e.id} ${e.opacity}`);
    },
    async DisplayClear() {
      log.push("clear");
    },
    async TimeGet() {
      return { timestamp: clock() };
    },
  };
  const card = (name: string, path: string): Card => ({
    path,
    pages: (t0) => V.cardPages(name, t0).map((page, p) => ({
      ms: page.ms,
      lines: page.lines.map((line, k) => ({
        spec: (LAYOUT as any)[line.style],
        text: (t: LocalTime) => V.cardPages(name, t)[p]?.lines[k]?.text ?? "",
      })),
    })),
  });
  const cards: Record<string, Card> = {
    clock: card("clock", SHOW.backdrops.clock_bg),
    [V.MOMENT_CARD]: card(V.MOMENT_CARD, SHOW.backdrops.moment_bg),
  };
  for (const n of ["count", ...V.DAY_CARD_NAMES]) cards[n] = card(n, SHOW.backdrops.count_bg);
  let timer: ReturnType<typeof setTimeout> | undefined;
  const show = createShow({
    app: "test", device, fonts: FONTS, scenes: SHOW.scenes, cards, report: (e) => { throw e; },
    steps: (t) => {
      if (timer !== undefined) clearTimeout(timer);
      timer = undefined;
      const ms = V.msToMoment(t);
      if (ms !== null) timer = setTimeout(() => { timer = undefined; show.start(); }, ms);
      return V.playlist(SHOW.scenes, t);
    },
  });
  return { show, log };
}

const flush = async (ms: number) => {
  for (let i = 0; i < 20; i++) await Promise.resolve();
  mock.timers.tick(ms);
  for (let i = 0; i < 20; i++) await Promise.resolve();
};

test("show runner: at 10:59 the timer starts a new cycle at 11:00:02 that opens with the moment card", async () => {
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    let now = Date.UTC(2027, 10, 11, 10, 59, 0);
    const iso = () => new Date(now).toISOString().slice(0, 19) + "-05:00";
    const { show, log } = rig(iso);
    show.start();
    await flush(0);
    await flush(0);
    assert.equal(log[0], "anim animations/main_street.anim");
    assert.deepEqual(show.steps.map((s) => (s.kind === "card" ? s.card : "scene"))[0], "scene");
    // advance the bar's clock and the timers together, a second at a time, to 11:00:02
    for (let s = 0; s < 62; s++) {
      now += 1000;
      await flush(1000);
    }
    await flush(0);
    assert.deepEqual(show.steps[0], { kind: "card", card: V.MOMENT_CARD });
    assert.equal(show.index, 0);
    assert.ok(log.includes(`anim ${SHOW.backdrops.moment_bg}`), "the moment backdrop plays");
    show.stop();
  } finally {
    mock.timers.reset();
  }
});

test("show runner: a cycle starting at 11:01 has no moment card", async () => {
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    const { show, log } = rig(() => "2027-11-11T11:01:00-05:00");
    show.start();
    await flush(0);
    await flush(0);
    assert.equal(log[0], "anim animations/main_street.anim");
    assert.ok(!show.steps.some((s) => s.kind === "card" && s.card === V.MOMENT_CARD));
    show.stop();
  } finally {
    mock.timers.reset();
  }
});
