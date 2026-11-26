// Tests for lib/ts/busybar/holidays.ts and showrunner.ts. Run by lib/tests/check.sh under Node 24.
import assert from "node:assert/strict";
import { mock, test } from "node:test";

import {
  HOLIDAYS, daysLabel, easter, hanukkahFirstNight, lunarNewYear, nextOccurrence, nthWeekday, shiftDate, zodiac,
} from "../ts/busybar/holidays.ts";
import { createShow, type ShowDevice } from "../ts/busybar/showrunner.ts";
import { parseLocal, type LocalTime } from "../ts/busybar/walltime.ts";

const t = (iso: string): LocalTime => {
  const v = parseLocal(iso);
  assert.ok(v, iso);
  return v;
};

test("nth weekday rules (published US federal holiday dates)", () => {
  assert.deepEqual(HOLIDAYS.mlkDay(2027), [1, 18]);
  assert.deepEqual(HOLIDAYS.presidentsDay(2027), [2, 15]);
  assert.deepEqual(HOLIDAYS.mothersDay(2027), [5, 9]);
  assert.deepEqual(HOLIDAYS.memorialDay(2027), [5, 31]);
  assert.deepEqual(HOLIDAYS.memorialDay(2026), [5, 25]);
  assert.deepEqual(HOLIDAYS.fathersDay(2027), [6, 20]);
  assert.deepEqual(HOLIDAYS.laborDay(2027), [9, 6]);
  assert.deepEqual(HOLIDAYS.thanksgiving(2026), [11, 26]);
  assert.deepEqual(HOLIDAYS.thanksgiving(2027), [11, 25]);
  assert.equal(nthWeekday(2026, 2, 0, -1), 22); // last Sunday of Feb 2026
});

test("Easter (Western)", () => {
  assert.deepEqual(easter(2024), [3, 31]);
  assert.deepEqual(easter(2025), [4, 20]);
  assert.deepEqual(easter(2026), [4, 5]);
  assert.deepEqual(easter(2027), [3, 28]);
  assert.deepEqual(easter(2028), [4, 16]);
  assert.deepEqual(easter(2038), [4, 25]); // latest possible date
});

test("Hanukkah: first candle evenings", () => {
  assert.deepEqual(hanukkahFirstNight(2023), [12, 7]);
  assert.deepEqual(hanukkahFirstNight(2024), [12, 25]);
  assert.deepEqual(hanukkahFirstNight(2025), [12, 14]);
  assert.deepEqual(hanukkahFirstNight(2026), [12, 4]);
  assert.deepEqual(hanukkahFirstNight(2027), [12, 24]);
  assert.deepEqual(hanukkahFirstNight(2028), [12, 12]);
  assert.deepEqual(hanukkahFirstNight(2032), [11, 27]); // the early "Thanksgivukkah"-adjacent year
});

test("Lunar New Year and zodiac", () => {
  assert.deepEqual(lunarNewYear(2027), [2, 6]);
  assert.equal(lunarNewYear(1999), null);
  assert.equal(zodiac(2026), "HORSE");
  assert.equal(zodiac(2027), "GOAT");
  assert.equal(zodiac(2032), "RAT");
});

test("nextOccurrence: before, on, during a span, after, across the year", () => {
  const v = nextOccurrence(t("2027-02-01T10:00:00+00:00"), HOLIDAYS.valentinesDay)!;
  assert.deepEqual(v, { year: 2027, month: 2, day: 14, days: 13, dayOf: 0 });
  assert.equal(nextOccurrence(t("2027-02-14T23:59:00+00:00"), HOLIDAYS.valentinesDay)!.days, 0);
  assert.deepEqual(nextOccurrence(t("2027-02-15T00:00:00+00:00"), HOLIDAYS.valentinesDay)!.year, 2028);
  const k = nextOccurrence(t("2027-01-01T12:00:00+00:00"), HOLIDAYS.kwanzaa, 7)!;
  assert.deepEqual(k, { year: 2026, month: 12, day: 26, days: -6, dayOf: 7 });
  assert.equal(nextOccurrence(t("2027-01-02T00:00:00+00:00"), HOLIDAYS.kwanzaa, 7)!.days, 358);
  const h = nextOccurrence(t("2026-12-06T20:00:00+00:00"), HOLIDAYS.hanukkah, 9)!;
  assert.equal(h.dayOf, 3);
  assert.equal(nextOccurrence(t("2036-03-01T00:00:00+00:00"), HOLIDAYS.lunarNewYear), null);
  assert.deepEqual(shiftDate(2026, 12, 30, 3), [2027, 1, 2]);
  assert.equal(daysLabel(1), "1 DAY");
  assert.equal(daysLabel(18), "18 DAYS");
});

// --- show runner ---------------------------------------------------------------------------------------------

function fakeDevice(iso: () => string) {
  const log: string[] = [];
  const device: ShowDevice = {
    async DisplayDraw(p) {
      for (const e of p.elements) {
        log.push(e.type === "animation" ? `anim ${e.path} loop=${e.loop}` : `text ${e.id} op=${e.opacity}`);
      }
    },
    async DisplayClear(p) {
      log.push(`clear ${p.element_ids ? p.element_ids.join(",") : "all"}`);
    },
    async TimeGet() {
      return { timestamp: iso() };
    },
  };
  return { device, log };
}

const FONT = { height: 1, gap: 1, glyphs: Object.fromEntries("0123456789: ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").map((c) => [c, ["#"]])) };
const SPEC = { font: "f", y: 0, top: [255, 255, 255], bottom: [255, 255, 255], shadow: [0, 0, 0] };

async function flush(ms: number) {
  for (let i = 0; i < 20; i++) await Promise.resolve();
  mock.timers.tick(ms);
  for (let i = 0; i < 20; i++) await Promise.resolve();
}

test("show runner: scene, card pages, minute rollover, playlist re-pick, quit", async () => {
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    let clock = "2026-12-04T16:59:58-05:00";
    const { device, log } = fakeDevice(() => clock);
    let cycles = 0;
    const show = createShow({
      app: "test", device, fonts: { f: FONT }, report: (e) => { throw e; },
      scenes: [{ path: "animations/a.anim", ms: 1000 }, { path: "animations/b.anim", ms: 1000 }],
      cards: {
        clock: {
          path: "animations/bg.anim",
          pages: () => [
            { ms: 4000, lines: [{ spec: SPEC, text: (u) => `${u.hour}:${u.minute}` }] },
            { ms: 2000, lines: [{ spec: SPEC, text: () => "A" }, { spec: SPEC, text: () => "B" }] },
          ],
        },
      },
      steps: (u) => {
        cycles++;
        return u.hour >= 17
          ? [{ kind: "scene", scene: 1 }]
          : [{ kind: "scene", scene: 0 }, { kind: "card", card: "clock" }];
      },
    });
    show.start();
    await flush(0);
    assert.equal(cycles, 1);
    assert.deepEqual(log.splice(0), ["anim animations/a.anim loop=false"]);
    await flush(1000); // scene done -> card
    await flush(0);
    await flush(0);
    assert.deepEqual(log.splice(0), ["anim animations/bg.anim loop=true", "text text0 op=34"]);
    await flush(150);
    await flush(150);
    assert.deepEqual(log.splice(0), ["text text0 op=67", "text text0 op=100"]);
    await flush(1700); // 16:59:58 + 2 s: the minute rolls over during page 1 -> redraw, no fade
    assert.deepEqual(log.splice(0), ["text text0 op=100"]);
    await flush(2000); // page 2: two lines
    await flush(0);
    assert.deepEqual(log.splice(0).filter((l) => l.endsWith("op=34")), ["text text0 op=34", "text text1 op=34"]);
    clock = "2026-12-04T17:00:05-05:00";
    await flush(2000); // card done -> new cycle picks the evening playlist
    await flush(0);
    await flush(0);
    assert.equal(cycles, 2);
    assert.deepEqual(show.steps, [{ kind: "scene", scene: 1 }]);
    assert.ok(log.includes("anim animations/b.anim loop=false"));
    assert.ok(log.includes("clear text0,text1"), log.join(" | "));
    log.splice(0);
    assert.equal(show.input({ key: "start", action: "short" }), "ignored");
    assert.equal(show.input({ key: "back", action: "short" }), "quit");
    await flush(0);
    assert.deepEqual(log, ["clear all"]);
  } finally {
    mock.timers.reset();
  }
});
