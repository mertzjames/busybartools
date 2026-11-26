// Unit tests for the app's date logic, flag custom and card texts (app/shared/memorial.ts), against real Memorial Day
// dates; the mockup's inlined copy of the same logic; and one run of the real show runner with this app's cards.
// Run: node --experimental-strip-types --test tests/logic.test.mts (Node 24).

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { mock, test } from "node:test";

import { parseLocal, type LocalTime } from "../../../lib/ts/busybar/walltime.ts";
import { createShow, type Card, type ShowDevice } from "../../../lib/ts/busybar/showrunner.ts";
import * as M from "../app/shared/memorial.ts";
import { FONTS, LAYOUT, SHOW } from "../app/shared/generated/show.ts";

const T = (iso: string): LocalTime => {
  const t = parseLocal(iso);
  assert.ok(t, iso);
  return t;
};
const texts = (pages: { lines: { text: string }[] }[]) => pages.map((p) => p.lines.map((l) => l.text));
const names = (steps: M.PlayStep[]) =>
  steps.map((s) => (s.kind === "scene" ? SHOW.scenes[s.scene].name : s.card));

test("Memorial Day dates: the last Monday of May", () => {
  assert.equal(M.daysToMemorialDay(T("2027-05-31T09:00:00-04:00")), 0); // Mon 31 May 2027
  assert.equal(M.daysToMemorialDay(T("2028-05-29T23:59:59-04:00")), 0); // Mon 29 May 2028
  assert.equal(M.daysToMemorialDay(T("2026-05-25T00:00:00+00:00")), 0); // Mon 25 May 2026
  assert.equal(M.daysToMemorialDay(T("2029-05-28T12:00:00-07:00")), 0); // Mon 28 May 2029
  assert.equal(M.daysToMemorialDay(T("2026-11-26T12:00:00-05:00")), 186);
  assert.equal(M.daysToMemorialDay(T("2027-05-30T23:59:59-04:00")), 1);
  assert.equal(M.daysToMemorialDay(T("2027-06-01T00:00:00-04:00")), 363); // the day after: to 29 May 2028
  assert.equal(M.daysToMemorialDay(T("2027-12-31T20:00:00-05:00")), 150);
});

test("isMemorialDay: only on the day, or any day in holiday mode", () => {
  assert.equal(M.isMemorialDay(T("2027-05-31T00:00:00-04:00")), true);
  assert.equal(M.isMemorialDay(T("2027-05-30T23:59:00-04:00")), false);
  assert.equal(M.isMemorialDay(T("2027-06-01T00:00:00-04:00")), false);
  assert.equal(M.isMemorialDay(T("2026-11-26T12:00:00-05:00"), "morning"), true);
  assert.equal(M.isMemorialDay(T("2026-11-26T12:00:00-05:00"), "afternoon"), true);
});

test("the flag: half-staff until noon on Memorial Day, then full staff; full staff on other days", () => {
  assert.equal(M.halfStaff(T("2027-05-31T00:00:00-04:00")), true);
  assert.equal(M.halfStaff(T("2027-05-31T06:30:00-04:00")), true);
  assert.equal(M.halfStaff(T("2027-05-31T11:59:00-04:00")), true);
  assert.equal(M.halfStaff(T("2027-05-31T11:59:59-04:00")), true);
  assert.equal(M.halfStaff(T("2027-05-31T12:00:00-04:00")), false);
  assert.equal(M.halfStaff(T("2027-05-31T23:59:00-04:00")), false);
  assert.equal(M.halfStaff(T("2028-05-29T11:59:00-04:00")), true);
  assert.equal(M.halfStaff(T("2028-05-29T12:00:00-04:00")), false);
  assert.equal(M.halfStaff(T("2027-05-30T09:00:00-04:00")), false); // the day before
  assert.equal(M.halfStaff(T("2027-06-01T09:00:00-04:00")), false); // the day after
  assert.equal(M.halfStaff(T("2026-11-26T09:00:00-05:00")), false);
  // holiday mode forces the morning or the afternoon on any date and at any hour
  assert.equal(M.halfStaff(T("2026-11-26T18:00:00-05:00"), "morning"), true);
  assert.equal(M.halfStaff(T("2027-05-31T09:00:00-04:00"), "afternoon"), false);
});

test("START cycles holiday mode: off, morning, afternoon, off", () => {
  assert.equal(M.nextMode("off"), "morning");
  assert.equal(M.nextMode("morning"), "afternoon");
  assert.equal(M.nextMode("afternoon"), "off");
});

test("countdown card before and after the day", () => {
  assert.deepEqual(texts(M.countPages(T("2026-11-26T12:00:00-05:00"))), [["186 DAYS", "TO MEMORIAL DAY"]]);
  assert.deepEqual(texts(M.countPages(T("2027-05-30T08:00:00-04:00"))), [["1 DAY", "TO MEMORIAL DAY"]]);
  assert.deepEqual(texts(M.countPages(T("2027-06-01T08:00:00-04:00"))), [["363 DAYS", "TO MEMORIAL DAY"]]);
  assert.deepEqual(M.countPages(T("2026-11-26T12:00:00-05:00"))[0].lines.map((l) => l.style), ["head", "sub"]);
  assert.equal(M.countPages(T("2026-11-26T12:00:00-05:00"))[0].ms, M.COUNT_MS);
});

test("the on-the-day cards, morning and afternoon", () => {
  assert.deepEqual(M.DAY_CARD_NAMES, ["day0", "day1", "day2"]);
  const morning = T("2027-05-31T11:59:00-04:00");
  const noon = T("2027-05-31T12:00:00-04:00");
  assert.deepEqual(M.dayCards(morning).map(texts), [
    [["MEMORIAL DAY"], ["HONOR AND", "REMEMBER"]],
    [["MEMORIAL DAY"], ["WE REMEMBER"]],
    [["MEMORIAL DAY"], ["HALF-STAFF", "UNTIL NOON"]],
  ]);
  assert.deepEqual(texts(M.cardPages("day2", noon)), [["MEMORIAL DAY"], ["FULL STAFF", "RAISED AT NOON"]]);
  assert.deepEqual(texts(M.cardPages("day2", T("2026-11-26T20:00:00-05:00"), "morning")),
    [["MEMORIAL DAY"], ["HALF-STAFF", "UNTIL NOON"]]);
  assert.deepEqual(texts(M.cardPages("day2", T("2026-11-26T08:00:00-05:00"), "afternoon")),
    [["MEMORIAL DAY"], ["FULL STAFF", "RAISED AT NOON"]]);
  assert.deepEqual(M.dayCards(morning)[0][1].lines.map((l) => l.style), ["upper", "lower"]);
  // no festive greeting anywhere
  for (const m of M.MODES) for (const card of M.dayCards(morning, m)) for (const p of card)
    for (const l of p.lines) assert.ok(!/HAPPY/.test(l.text), l.text);
});

test("clock card: time, then date, from the bar's wall clock", () => {
  assert.deepEqual(texts(M.clockPages(T("2027-05-31T07:05:42-04:00"))), [["07:05"], ["MON 31 MAY"]]);
  assert.deepEqual(texts(M.cardPages("clock", T("2028-05-29T23:59:00+09:00"))), [["23:59"], ["MON 29 MAY"]]);
  assert.deepEqual(texts(M.cardPages("clock", T("2026-11-26T18:05:00-05:00"))), [["18:05"], ["THU 26 NOV"]]);
});

test("playlist: the flag variant follows the custom; the day cards on the day and in holiday mode", () => {
  const sc = SHOW.scenes;
  const before = names(M.playlist(sc, T("2026-11-26T09:00:00-05:00")));
  assert.deepEqual(before, ["flag_full", "clock", "services", "count", "poppies", "clock", "headstones", "count",
    "bugler", "clock", "flyover", "count", "tomb", "clock", "wall", "count"]);
  const morning = names(M.playlist(sc, T("2027-05-31T11:59:00-04:00")));
  // four count slots take the three day cards in turn, so the last (after the wall) is day0 again (D14)
  assert.deepEqual(morning, ["flag_half", "clock", "services", "day0", "poppies", "clock", "headstones", "day1",
    "bugler", "clock", "flyover", "day2", "tomb", "clock", "wall", "day0"]);
  const afternoon = names(M.playlist(sc, T("2027-05-31T12:00:00-04:00")));
  assert.deepEqual(afternoon, ["flag_full", ...morning.slice(1)]);
  assert.deepEqual(names(M.playlist(sc, T("2028-05-29T08:00:00-04:00"))), morning);
  assert.deepEqual(names(M.playlist(sc, T("2028-05-29T15:00:00-04:00"))), afternoon);
  assert.deepEqual(names(M.playlist(sc, T("2027-06-01T09:00:00-04:00"))), before); // the day after
  assert.deepEqual(names(M.playlist(sc, T("2027-05-30T09:00:00-04:00"))), before); // the day before
  // holiday mode on any date
  assert.deepEqual(names(M.playlist(sc, T("2026-11-26T20:00:00-05:00"), "morning")), morning);
  assert.deepEqual(names(M.playlist(sc, T("2026-11-26T08:00:00-05:00"), "afternoon")), afternoon);
});

test("every text fits the display and uses only glyphs the fonts have", () => {
  const all: [string, string][] = [];
  for (const m of M.MODES) for (const card of M.dayCards(T("2027-05-31T10:00:00-04:00"), m))
    for (const page of card) for (const l of page.lines) all.push([l.style, l.text]);
  all.push(["head", "365 DAYS"], ["head", "1 DAY"], ["sub", "TO MEMORIAL DAY"], ["date", "WED 28 SEP"],
    ["time", "23:59"], ["head", "FULL STAFF"], ["sub", "RAISED AT NOON"]);
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

test("the mockup runs the same logic as the app, every day of 2027 and 2028, at 11:59 and 12:00", () => {
  const html = readFileSync(new URL("../mockup/index.html", import.meta.url), "utf8");
  const start = html.indexOf("const MEM = (() => {");
  const end = html.indexOf("})();", start) + "})();".length;
  assert.ok(start > 0 && end > start, "mockup logic block");
  const MEM = new Function(html.slice(start, end) + "\nreturn MEM;")();
  for (const year of [2027, 2028]) {
    for (let d = 0; d < 366; d++) {
      const date = new Date(Date.UTC(year, 0, 1 + d));
      if (date.getUTCFullYear() !== year) break;
      const ymd = date.toISOString().slice(0, 10);
      for (const hm of ["11:59", "12:00"]) {
        const t = T(`${ymd}T${hm}:00-04:00`);
        for (const m of M.MODES) {
          assert.deepEqual(MEM.playlist(SHOW.scenes, t, m), M.playlist(SHOW.scenes, t, m), `${ymd} ${hm} ${m}`);
          for (const name of ["clock", "count", ...M.DAY_CARD_NAMES])
            assert.deepEqual(MEM.cardPages(name, t, m), M.cardPages(name, t, m), `${name} ${ymd} ${hm} ${m}`);
        }
      }
    }
  }
});

test("show runner: the morning playlist opens on the half-staff flag; the day cards play over the count backdrop",
  async () => {
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
          return { timestamp: "2027-05-31T10:00:00-04:00" };
        },
      };
      const card = (name: string, path: string): Card => ({
        path,
        pages: (t0) => M.cardPages(name, t0).map((page, p) => ({
          ms: page.ms,
          lines: page.lines.map((line, k) => ({
            spec: (LAYOUT as any)[line.style],
            text: (t: LocalTime) => M.cardPages(name, t)[p]?.lines[k]?.text ?? "",
          })),
        })),
      });
      const cards: Record<string, Card> = { clock: card("clock", SHOW.backdrops.clock_bg) };
      for (const n of ["count", ...M.DAY_CARD_NAMES]) cards[n] = card(n, SHOW.backdrops.count_bg);
      const show = createShow({
        app: "test", device, fonts: FONTS, scenes: SHOW.scenes, cards, report: (e) => { throw e; },
        steps: (t) => M.playlist(SHOW.scenes, t),
      });
      const flush = async (ms: number) => {
        for (let i = 0; i < 20; i++) await Promise.resolve();
        mock.timers.tick(ms);
        for (let i = 0; i < 20; i++) await Promise.resolve();
      };
      show.start();
      await flush(0);
      await flush(0);
      assert.equal(log[0], "anim animations/flag_half.anim");
      show.go(3); // the first count slot: day0
      await flush(0);
      await flush(0);
      assert.deepEqual(show.steps[3], { kind: "card", card: "day0" });
      assert.ok(log.includes(`anim ${SHOW.backdrops.count_bg}`));
      assert.ok(log.includes("text text0 34"), "the first page fades in");
      show.stop();
    } finally {
      mock.timers.reset();
    }
  });
