// Tests for the shared TypeScript kit (lib/ts/busybar). Run by lib/tests/check.sh under Node 24:
//   node --experimental-strip-types --test lib/tests/ts_kit.test.mts
import assert from "node:assert/strict";
import { test } from "node:test";

import {
  addSeconds, daysUntil, formatDate, nextMinute, parseLocal, parseWallClock, secondsToMidnight, secondsUntilDate,
  weekday,
} from "../ts/busybar/walltime.ts";
import { textBitmap, textWidth, type Font } from "../ts/busybar/xpmtext.ts";
import { createDrawQueue } from "../ts/busybar/drawqueue.ts";

const t = (iso: string) => {
  const v = parseLocal(iso);
  assert.ok(v, iso);
  return v;
};

test("parseLocal reads wall-clock fields and ignores the offset", () => {
  assert.deepEqual(t("2026-12-31T23:59:50-05:00"), { year: 2026, month: 12, day: 31, hour: 23, minute: 59, second: 50 });
  assert.equal(parseLocal("not a time"), null);
});

test("calendar helpers", () => {
  assert.equal(weekday(2026, 12, 25), 5); // Friday
  assert.equal(formatDate(t("2026-11-26T08:00:00+00:00")), "THU 26 NOV");
  assert.equal(daysUntil(t("2026-12-01T10:00:00+00:00"), 2026, 12, 25), 24);
  assert.equal(daysUntil(t("2026-12-25T00:00:00+00:00"), 2026, 12, 25), 0);
  assert.equal(daysUntil(t("2026-12-26T00:00:00+00:00"), 2026, 12, 25), -1);
  assert.equal(daysUntil(t("2026-11-30T23:00:00+00:00"), 2027, 1, 1), 32);
});

test("midnight and date countdowns", () => {
  assert.equal(secondsToMidnight(t("2026-12-31T23:59:50+00:00")), 10);
  assert.equal(secondsToMidnight(t("2026-12-31T00:00:00+00:00")), 86400);
  assert.equal(secondsUntilDate(t("2026-12-31T23:59:50+00:00"), 2027, 1, 1), 10);
  assert.equal(secondsUntilDate(t("2026-12-24T18:00:00+00:00"), 2026, 12, 25), 6 * 3600);
  assert.ok(secondsUntilDate(t("2027-01-01T00:00:05+00:00"), 2027, 1, 1) < 0);
});

test("addSeconds carries across the year boundary", () => {
  assert.deepEqual(addSeconds(t("2026-12-31T23:59:55+00:00"), 10),
    { year: 2027, month: 1, day: 1, hour: 0, minute: 0, second: 5 });
});

test("wall clock compatibility (Wizarding Thanksgiving)", () => {
  assert.deepEqual(parseWallClock("2026-11-26T18:05:42-05:00"), { hhmm: "18:05", date: "THU 26 NOV", msToNextMinute: 18000 });
  assert.equal(nextMinute("23:59"), "00:00");
});

test("xpm text: size, palette limit, centering", () => {
  const font: Font = { height: 3, gap: 1, glyphs: { A: [".#.", "#.#", "#.#"], " ": ["..", "..", ".."] } };
  assert.equal(textWidth("A A", font), 3 + 1 + 2 + 1 + 3);
  const bmp = textBitmap("A", font, { font: "x", y: 2, top: [255, 0, 0], bottom: [0, 0, 255], shadow: [10, 10, 10] });
  const lines = bmp.data.split("\n");
  assert.equal(lines[0], "! XPM2");
  assert.equal(lines[1], "4 4 5 1"); // width+1, height+1, none + shadow + 3 gradient rows
  assert.equal(bmp.x, Math.floor((72 - 3) / 2));
  assert.equal(textBitmap("A", font, { font: "x", y: 0, top: [0, 0, 0], bottom: [0, 0, 0], shadow: [0, 0, 0] }, 5).x, 5);
});

test("draw queue: one in flight, newer job replaces unsent job in the same slot", async () => {
  const ran: string[] = [];
  const errors: unknown[] = [];
  const q = createDrawQueue((e) => errors.push(e));
  let release!: () => void;
  q.send("a", () => new Promise<void>((r) => { ran.push("a1"); release = r; }));
  q.send("b", async () => { ran.push("b1"); });
  q.send("b", async () => { ran.push("b2"); throw new Error("boom"); });
  assert.equal(q.pending, 1);
  release();
  await new Promise((r) => setTimeout(r, 10));
  assert.deepEqual(ran, ["a1", "b2"]);
  assert.equal(errors.length, 1);
});
