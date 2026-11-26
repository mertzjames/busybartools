// Tests for lib/ts/busybar/sun.ts and settings.ts. Run by lib/tests/check.sh under Node 24.
import assert from "node:assert/strict";
import { test } from "node:test";

import { hhmmFromMinutes, locationFromOffset, offsetMinutes, sunTimes, usDst } from "../ts/busybar/sun.ts";
import { enumValue, loadSettings, readGeolocation, type SettingsDevice } from "../ts/busybar/settings.ts";

const near = (actual: number | null, expected: string, tol: number, label: string) => {
  assert.ok(actual !== null, label);
  const [h, m] = expected.split(":").map(Number);
  assert.ok(Math.abs(actual - (h * 60 + m)) <= tol, `${label}: got ${hhmmFromMinutes(actual)}, expected ${expected}`);
};

test("UTC offsets from timestamps", () => {
  assert.equal(offsetMinutes("2026-12-04T16:59:00-05:00"), -300);
  assert.equal(offsetMinutes("2026-12-04T16:59:00+05:30"), 330);
  assert.equal(offsetMinutes("2026-12-04T16:59:00Z"), 0);
  assert.equal(offsetMinutes("2026-12-04T16:59:00"), null);
});

test("sunset at known places (published almanac times, within 3 minutes)", () => {
  near(sunTimes(2026, 12, 4, { lat: 40.7128, lon: -74.006 }, -300).sunset, "16:28", 3, "New York, Dec 4");
  near(sunTimes(2026, 12, 4, { lat: 41.8781, lon: -87.6298 }, -360).sunset, "16:19", 3, "Chicago, Dec 4");
  near(sunTimes(2026, 12, 4, { lat: 34.0522, lon: -118.2437 }, -480).sunset, "16:44", 3, "Los Angeles, Dec 4");
  near(sunTimes(2026, 6, 21, { lat: 40.7128, lon: -74.006 }, -240).sunset, "20:31", 3, "New York, Jun 21 (EDT)");
  near(sunTimes(2026, 6, 21, { lat: 40.7128, lon: -74.006 }, -240).sunrise, "05:25", 3, "New York sunrise, Jun 21");
  const polar = sunTimes(2026, 12, 21, { lat: 78, lon: 15 }, 60);
  assert.deepEqual(polar, { sunrise: null, sunset: null });
});

test("location estimated from the time zone lands within about half an hour", () => {
  const eastern = sunTimes(2026, 12, 4, locationFromOffset(-300), -300).sunset!;
  const central = sunTimes(2026, 12, 4, locationFromOffset(-360), -360).sunset!;
  const pacific = sunTimes(2026, 12, 4, locationFromOffset(-480), -480).sunset!;
  near(eastern, "16:28", 30, "Eastern estimate vs New York");
  near(central, "16:19", 30, "Central estimate vs Chicago");
  near(pacific, "16:44", 30, "Pacific estimate vs Los Angeles");
  // daylight time: the offset is an hour ahead, so the estimate must undo it
  assert.deepEqual(locationFromOffset(-240, true), locationFromOffset(-300, false));
  assert.equal(usDst(2026, 3, 7), false);
  assert.equal(usDst(2026, 3, 8), true); // second Sunday of March 2026
  assert.equal(usDst(2026, 10, 31), true);
  assert.equal(usDst(2026, 11, 1), false); // first Sunday of November 2026
  assert.equal(usDst(2026, 12, 4), false);
});

function device(doc: unknown, fail = false): SettingsDevice {
  return {
    async AppsSettingsGet() {
      if (fail) throw new Error("offline");
      return doc as { version: number; values: Record<string, unknown> };
    },
  };
}

test("loadSettings: stored values, wrong types, old versions and failures fall back to defaults", async () => {
  const defaults = { sundown: "auto", showFinale: true, minutes: 5, location: null as unknown };
  const stored = { version: 2, values: { sundown: "17:00", showFinale: "yes", minutes: 10, location: { mode: "fixed", name: "Home", lat: 40.7, lon: -74 } } };
  const s = await loadSettings(device(stored), "app", 2, defaults);
  assert.equal(s.sundown, "17:00");
  assert.equal(s.showFinale, true); // a string where a boolean belongs is ignored
  assert.equal(s.minutes, 10);
  assert.deepEqual(readGeolocation(s.location), { lat: 40.7, lon: -74, name: "Home" });
  assert.deepEqual(await loadSettings(device(stored), "app", 3, defaults), defaults); // schema version changed
  let reported = 0;
  assert.deepEqual(await loadSettings(device(null, true), "app", 2, defaults, () => reported++), defaults);
  assert.equal(reported, 1);
});

test("enum and geolocation readers", () => {
  assert.equal(enumValue("center", ["official", "center"] as const, "official"), "center");
  assert.equal(enumValue("bogus", ["official", "center"] as const, "official"), "official");
  assert.equal(readGeolocation({ mode: "auto", name: "Bar" }), null);
  assert.equal(readGeolocation({ mode: "fixed", name: "x", lat: 0, lon: 0 }), null);
  assert.equal(readGeolocation({ lat: 95, lon: 0 }), null);
  assert.deepEqual(readGeolocation({ mode: "auto", name: "Bar", lat: 41.9, lon: -87.6 }), { lat: 41.9, lon: -87.6, name: "Bar" });
});
