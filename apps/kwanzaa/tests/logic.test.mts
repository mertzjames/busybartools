// Logic tests for Kwanzaa (run by tests/check.sh under Node 24):
//   node --experimental-strip-types --test tests/logic.test.mts
//
// app/shared/kwanzaa.ts against real dates (the day index across the new year, the count, the card texts and the
// playlist), the holiday-mode cycle, and the app's configuration driven through the real show runner.
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { mock, test } from "node:test";

import {
  DEFAULT_ORDER, ORDERS, SETTINGS_VERSION, countPages, cycleSteps, kwanzaaDay, loadOrder, nextPreview, type Order,
  type PageText,
} from "../app/shared/kwanzaa.ts";
import {
  createShow, parseLocal, textWidth, type Font, type LocalTime, type SettingsDevice, type ShowDevice,
} from "../app/shared/kit.ts";
import { FONTS, SHOW } from "../app/shared/generated/show.ts";

const t = (iso: string): LocalTime => {
  const v = parseLocal(iso);
  assert.ok(v, iso);
  return v;
};
const texts = (pages: PageText[]) => pages.map((p) => p.lines.map((l) => `${l.text}|${l.style}`).join(" / "));

test("day of Kwanzaa across the new year", () => {
  assert.deepEqual(kwanzaaDay(t("2026-12-25T23:59:59-05:00")), { day: 0, days: 1 });
  assert.deepEqual(kwanzaaDay(t("2026-12-26T00:00:00-05:00")), { day: 1, days: 0 });
  assert.deepEqual(kwanzaaDay(t("2026-12-27T12:00:00+09:00")), { day: 2, days: 0 });
  assert.deepEqual(kwanzaaDay(t("2026-12-31T20:00:00+00:00")), { day: 6, days: 0 });
  assert.deepEqual(kwanzaaDay(t("2027-01-01T00:00:00+00:00")), { day: 7, days: 0 });
  assert.deepEqual(kwanzaaDay(t("2027-01-01T23:59:59+00:00")), { day: 7, days: 0 });
  assert.deepEqual(kwanzaaDay(t("2027-01-02T00:00:00+00:00")), { day: 0, days: 358 });
  assert.deepEqual(kwanzaaDay(t("2026-11-26T09:00:00+00:00")), { day: 0, days: 30 });
  assert.deepEqual(kwanzaaDay(t("2027-12-25T09:00:00+00:00")), { day: 0, days: 1 });
  assert.deepEqual(kwanzaaDay(t("2028-01-02T09:00:00+00:00")), { day: 0, days: 359 }); // 2028 is a leap year
  assert.deepEqual(kwanzaaDay(t("2028-12-31T09:00:00+00:00")), { day: 6, days: 0 });
});

test("count card before Kwanzaa", () => {
  assert.deepEqual(texts(countPages(0, 30)), ["30 DAYS|head / TO KWANZAA|sub", "KWANZAA|head / DEC 26 - JAN 1|sub"]);
  assert.deepEqual(texts(countPages(0, 1))[0], "1 DAY|head / TO KWANZAA|sub");
  assert.deepEqual(texts(countPages(0, 358))[0], "358 DAYS|head / TO KWANZAA|sub");
});

test("count card during Kwanzaa: the greeting, then the day's principle", () => {
  const greet = "HABARI GANI?|head / WHAT'S THE NEWS?|sub";
  assert.deepEqual(texts(countPages(1, 0)), [greet, "UMOJA|head / UNITY|sub", "KWANZAA|head / DAY 1 OF 7|sub"]);
  assert.deepEqual(texts(countPages(2, 0)), [greet, "KUJICHAGULIA|head / SELF-DETERMINATION|sub",
    "KWANZAA|head / DAY 2 OF 7|sub"]);
  assert.deepEqual(texts(countPages(3, 0)), [greet, "UJIMA|head / COLLECTIVE WORK|sub",
    "UJIMA|head / AND RESPONSIBILITY|sub", "KWANZAA|head / DAY 3 OF 7|sub"]);
  assert.deepEqual(texts(countPages(4, 0)), [greet, "UJAMAA|head / COOPERATIVE|sub", "UJAMAA|head / ECONOMICS|sub",
    "KWANZAA|head / DAY 4 OF 7|sub"]);
  assert.deepEqual(texts(countPages(5, 0)), [greet, "NIA|head / PURPOSE|sub", "KWANZAA|head / DAY 5 OF 7|sub"]);
  assert.deepEqual(texts(countPages(6, 0)), [greet, "KUUMBA|head / CREATIVITY|sub",
    "KARAMU|head / DAY 6: THE FEAST|sub"]);
  assert.deepEqual(texts(countPages(7, 0)), [greet, "IMANI|head / FAITH|sub", "KWANZAA|head / DAY 7 OF 7|sub"]);
});

test("every card text fits the display and uses only glyphs the fonts have", () => {
  const all: PageText[] = [...countPages(0, 1), ...countPages(0, 365)];
  for (let d = 1; d <= 7; d++) all.push(...countPages(d, 0));
  const styles = SHOW.styles as Record<string, { font: string }>;
  for (const p of all) {
    for (const l of p.lines) {
      const font = (FONTS as Record<string, Font>)[styles[l.style].font];
      for (const ch of l.text.toUpperCase()) assert.ok(font.glyphs[ch], `${l.style} ${l.text}: no glyph ${ch}`);
      assert.ok(textWidth(l.text, font) + 1 <= 72, `${l.text} is too wide`);
    }
  }
  assert.ok(textWidth("WED 30 DEC", (FONTS as Record<string, Font>).big) + 1 <= 72);
});

// The kinara variant each day shows, per lighting order. The unlit kinara and day 1 are shared by both orders.
const KINARA_NAMES: Record<Order, string[]> = {
  official: [0, 1, 2, 3, 4, 5, 6, 7].map((d) => `kinara_${d}`),
  center_out: ["kinara_0", "kinara_1", ...[2, 3, 4, 5, 6, 7].map((d) => `kinara_center_${d}`)],
};

test("playlist: the day's kinara (in each lighting order) first, then scenes with cards between", () => {
  assert.deepEqual([...SHOW.orders], [...ORDERS]);
  for (const order of ORDERS) {
    for (let day = 0; day <= 7; day++) {
      const steps = cycleSteps(day, order);
      const names = steps.map((s) => (s.kind === "scene" ? SHOW.scenes[s.scene].name : s.card));
      assert.deepEqual(names, [KINARA_NAMES[order][day], "clock", "harvest", "count", "unity_cup", "clock", "drums",
        "count", "kente", "clock", "karamu", "count"], `${order} day ${day}`);
    }
  }
  assert.deepEqual(cycleSteps(3), cycleSteps(3, "official")); // the default order
  const app = new URL("../app/src/", import.meta.url);
  for (const s of SHOW.scenes) assert.ok(existsSync(new URL(s.path, app)), s.path);
  assert.ok(existsSync(new URL(SHOW.card.path, app)));
});

test("settings.json declares the candle order the app reads", () => {
  const doc = JSON.parse(readFileSync(new URL("../app/src/appmeta/settings.json", import.meta.url), "utf8"));
  assert.equal(doc.format_version, 1);
  assert.equal(doc.version, SETTINGS_VERSION);
  const f = doc.fields.lighting_order;
  assert.equal(f.type, "enum");
  assert.equal(f.default, DEFAULT_ORDER);
  assert.equal(SHOW.default_order, DEFAULT_ORDER);
  assert.deepEqual(f.options.map((o: { value: string }) => o.value), [...ORDERS]);
  for (const o of f.options) assert.ok(o.label.length > 0 && o.label.length <= 20, o.label);
});

test("the candle order setting: stored values, and every failure falls back to the default", async () => {
  const dev = (doc: unknown, fail = false): SettingsDevice => ({
    async AppsSettingsGet() {
      if (fail) throw new Error("offline");
      return doc as { version: number; values: Record<string, unknown> };
    },
  });
  const quiet = () => {};
  assert.equal(await loadOrder(dev({ version: 1, values: { lighting_order: "center_out" } }), "a", quiet), "center_out");
  assert.equal(await loadOrder(dev({ version: 1, values: { lighting_order: "official" } }), "a", quiet), "official");
  assert.equal(await loadOrder(dev(null, true), "a", quiet), "official"); // request fails
  assert.equal(await loadOrder(dev({ version: 2, values: { lighting_order: "center_out" } }), "a", quiet), "official");
  assert.equal(await loadOrder(dev({ version: 1, values: { lighting_order: "sideways" } }), "a", quiet), "official");
  assert.equal(await loadOrder(dev({ version: 1, values: { lighting_order: 2 } }), "a", quiet), "official");
  assert.equal(await loadOrder(dev({ version: 1, values: {} }), "a", quiet), "official");
  assert.equal(await loadOrder(dev({ version: 1 }), "a", quiet), "official");
  assert.equal(await loadOrder(dev(undefined), "a", quiet), "official");
});

test("holiday mode cycles off -> day 1 .. day 7 -> off", () => {
  const seen = [0];
  for (let i = 0; i < 8; i++) seen.push(nextPreview(seen[seen.length - 1]));
  assert.deepEqual(seen, [0, 1, 2, 3, 4, 5, 6, 7, 0]);
});

// --- the app's configuration through the real runner --------------------------------------------------------

async function flush(ms: number) {
  for (let i = 0; i < 20; i++) await Promise.resolve();
  mock.timers.tick(ms);
  for (let i = 0; i < 20; i++) await Promise.resolve();
}

test("runner: Dec 31 plays kinara_6, then the clock card", async () => {
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    const log: string[] = [];
    const device: ShowDevice = {
      async DisplayDraw(p) {
        for (const e of p.elements) log.push(e.type === "animation" ? `anim ${e.path}` : `text ${e.id}`);
      },
      async DisplayClear() {},
      async TimeGet() {
        return { timestamp: "2026-12-31T18:05:00-05:00" };
      },
    };
    const show = createShow({
      app: "test", device, fonts: FONTS as Record<string, Font>, scenes: SHOW.scenes, report: (e) => { throw e; },
      cards: { clock: { path: SHOW.card.path, pages: () => [{ ms: 1000, lines: [] }] }, count: { path: SHOW.card.path, pages: () => [] } },
      steps: (u) => cycleSteps(kwanzaaDay(u).day),
    });
    show.start();
    await flush(0);
    assert.deepEqual(log.splice(0), ["anim animations/kinara_6.anim"]);
    await flush(SHOW.scenes[SHOW.kinara.official[6]].ms);
    await flush(0);
    assert.deepEqual(log.splice(0), ["anim animations/card_bg.anim"]);
    show.stop();
  } finally {
    mock.timers.reset();
  }
});
