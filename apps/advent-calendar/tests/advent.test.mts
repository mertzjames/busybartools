// Logic tests for the Advent Calendar (run by tests/check.sh under Node 24):
//   node --experimental-strip-types --test tests/advent.test.mts
//
// 1. app/shared/advent.ts: seasons, countdown text, the show sequence, browsing.
// 2. The mockup's JavaScript mirror (mockup/template.html, the <logic> block) agrees with the app for every day of
//    several years, and draws text pixel-identical to the app's xpmtext bitmaps.
// 3. Generated data: 25 days, every animation exists, every live text uses only glyphs the fonts have and fits.
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { test } from "node:test";

import {
  browse, cardLines, cycleSteps, dateLabel, msUntilCardChange, openedDays, season, type Line,
} from "../app/shared/advent.ts";
import { addSeconds, parseLocal, textBitmap, type Font, type LocalTime } from "../app/shared/kit.ts";
import { FONTS, SHOW } from "../app/shared/generated/show.ts";

const APP = new URL("..", import.meta.url);

const t = (iso: string): LocalTime => {
  const v = parseLocal(iso);
  assert.ok(v, iso);
  return v;
};
const texts = (lines: Line[]) => lines.map((l) => `${l.text}|${l.style}`);

test("seasons follow the bar's local date", () => {
  assert.equal(season(t("2026-11-30T23:59:59+00:00")), "pre");
  assert.equal(season(t("2026-12-01T00:00:00+00:00")), "advent");
  assert.equal(season(t("2026-12-23T23:59:59+00:00")), "advent");
  assert.equal(season(t("2026-12-24T00:00:00+00:00")), "eve");
  assert.equal(season(t("2026-12-25T12:00:00+00:00")), "christmas");
  assert.equal(season(t("2026-12-26T00:00:00+00:00")), "post");
  assert.equal(season(t("2026-12-31T23:59:59+00:00")), "post");
  assert.equal(season(t("2027-01-01T00:00:00+00:00")), "pre");
  assert.equal(openedDays(t("2026-11-15T08:00:00+00:00")), 0);
  assert.equal(openedDays(t("2026-12-07T08:00:00+00:00")), 7);
  assert.equal(openedDays(t("2026-12-29T08:00:00+00:00")), 25);
});

test("countdown card text", () => {
  assert.deepEqual(texts(cardLines(t("2026-12-07T10:00:00+00:00"))), ["18 DAYS|head", "TO CHRISTMAS|sub"]);
  assert.deepEqual(texts(cardLines(t("2026-12-01T00:00:00+00:00"))), ["24 DAYS|head", "TO CHRISTMAS|sub"]);
  assert.deepEqual(texts(cardLines(t("2026-12-23T23:00:00+00:00"))), ["2 DAYS|head", "TO CHRISTMAS|sub"]);
  assert.deepEqual(texts(cardLines(t("2026-11-30T12:00:00+00:00"))), ["1 DAY|head", "TO ADVENT|sub"]);
  assert.deepEqual(texts(cardLines(t("2026-11-20T12:00:00+00:00"))), ["11 DAYS|head", "TO ADVENT|sub"]);
  assert.deepEqual(texts(cardLines(t("2027-01-01T12:00:00+00:00"))), ["334 DAYS|head", "TO ADVENT|sub"]);
  assert.deepEqual(texts(cardLines(t("2028-01-01T12:00:00+00:00"))), ["335 DAYS|head", "TO ADVENT|sub"]); // leap
  assert.deepEqual(texts(cardLines(t("2026-12-25T07:00:00+00:00"))), ["MERRY|top", "CHRISTMAS|bot"]);
  assert.deepEqual(texts(cardLines(t("2026-12-27T07:00:00+00:00"))), ["SEE YOU|top", "NEXT YEAR!|bot"]);
});

test("Christmas Eve counts hours and minutes to midnight, rounding up", () => {
  const eve = (hms: string) => cardLines(t(`2026-12-24T${hms}+00:00`))[0].text;
  assert.equal(eve("17:18:00"), "06:42");
  assert.equal(eve("17:18:30"), "06:42");
  assert.equal(eve("17:18:59"), "06:42");
  assert.equal(eve("17:19:00"), "06:41");
  assert.equal(eve("23:59:30"), "00:01");
  assert.equal(eve("00:00:00"), "24:00");
  assert.equal(cardLines(t("2026-12-24T12:00:00+00:00"))[1].text, "TO GO");
});

test("the card knows when its text changes", () => {
  assert.equal(msUntilCardChange(t("2026-12-24T17:18:42+00:00")), 18000);
  assert.equal(msUntilCardChange(t("2026-12-07T23:59:58+00:00")), 2000);
  assert.equal(msUntilCardChange(t("2026-12-07T12:00:00+00:00")), 12 * 3600 * 1000);
  // the redraw the app schedules shows the next minute's text
  const now = t("2026-12-24T17:18:42+00:00");
  const later = addSeconds(now, msUntilCardChange(now) / 1000);
  assert.equal(cardLines(later)[0].text, "06:41");
});

test("the show sequence", () => {
  assert.deepEqual(cycleSteps(t("2026-12-07T10:00:00+00:00"), null),
    [{ kind: "door", day: 7 }, { kind: "scene", day: 7 }, { kind: "card" }]);
  assert.deepEqual(cycleSteps(t("2026-12-25T10:00:00+00:00"), null),
    [{ kind: "door", day: 25 }, { kind: "scene", day: 25 }, { kind: "card" }]);
  assert.deepEqual(cycleSteps(t("2026-11-10T10:00:00+00:00"), null), [{ kind: "scene", day: 0 }, { kind: "card" }]);
  assert.deepEqual(cycleSteps(t("2026-12-30T10:00:00+00:00"), null), [{ kind: "scene", day: 25 }, { kind: "card" }]);
  assert.deepEqual(cycleSteps(t("2026-12-07T10:00:00+00:00"), 3),
    [{ kind: "door", day: 3 }, { kind: "scene", day: 3 }, { kind: "card" }]);
  assert.equal(dateLabel(7), "DEC 7");
});

test("the encoder browses opened days only", () => {
  const dec7 = t("2026-12-07T10:00:00+00:00");
  assert.equal(browse(dec7, null, -1), 6);
  assert.equal(browse(dec7, 6, 1), null);       // back on today: follow it again
  assert.equal(browse(dec7, null, 1), null);    // no peeking at tomorrow
  assert.equal(browse(dec7, 1, -1), 1);         // clamped at the first door
  assert.equal(browse(t("2026-11-07T10:00:00+00:00"), null, 1), null);
  const dec28 = t("2026-12-28T10:00:00+00:00");
  assert.equal(browse(dec28, null, 1), null);
  assert.equal(browse(dec28, null, -1), 24);
  assert.equal(browse(dec28, 24, 1), 25);
  assert.equal(browse(dec28, 25, 1), 25);
});

// ---------- the mockup mirror ----------

type Mirror = {
  season: typeof season; openedDays: typeof openedDays; dateLabel: typeof dateLabel; cardLines: typeof cardLines;
  msUntilCardChange: typeof msUntilCardChange; cycleSteps: typeof cycleSteps; browse: typeof browse;
  drawText: (buf: Uint8ClampedArray, w: number, h: number, text: string, spec: unknown, font: Font, a: number) => void;
};

function mirror(): Mirror {
  const html = readFileSync(new URL("mockup/template.html", APP), "utf8");
  const start = html.indexOf("const LOGIC = (() => {");
  const end = html.indexOf("/* </logic> */");
  assert.ok(start > 0 && end > start, "mockup/template.html must keep its <logic> block");
  return new Function(html.slice(start, end) + "\nreturn LOGIC;")() as Mirror;
}

function* everyDay(year: number) {
  for (let d = Date.UTC(year, 0, 1); d < Date.UTC(year + 1, 0, 1); d += 86400000) {
    const x = new Date(d);
    for (const [h, m, s] of [[0, 0, 0], [9, 30, 15], [17, 18, 42], [23, 59, 59]]) {
      yield { year, month: x.getUTCMonth() + 1, day: x.getUTCDate(), hour: h, minute: m, second: s } as LocalTime;
    }
  }
}

test("the mockup's logic matches the app for every day of 2026-2028", () => {
  const js = mirror();
  for (const year of [2026, 2027, 2028]) {
    for (const now of everyDay(year)) {
      const at = JSON.stringify(now);
      assert.equal(js.season(now), season(now), at);
      assert.equal(js.openedDays(now), openedDays(now), at);
      assert.deepEqual(js.cardLines(now), cardLines(now), at);
      assert.equal(js.msUntilCardChange(now), msUntilCardChange(now), at);
      for (const view of [null, 1, 12, 24, 25]) {
        assert.deepEqual(js.cycleSteps(now, view), cycleSteps(now, view), at);
        for (const delta of [-1, 1]) assert.equal(js.browse(now, view, delta), browse(now, view, delta), at);
      }
    }
  }
  for (let d = 1; d <= 25; d++) assert.equal(js.dateLabel(d), dateLabel(d));
});

function bitmapPixels(line: Line): Map<string, string> {
  const spec = SHOW.styles[line.style];
  const b = textBitmap(line.text, FONTS[spec.font] as Font, spec);
  const rows = b.data.split("\n");
  const [w, h, n] = rows[1].split(" ").map(Number);
  const pal = new Map<string, string>();
  for (const ln of rows.slice(2, 2 + n)) {
    const [ch, , val] = ln.split(" ");
    if (val !== "none") pal.set(ch, val.toUpperCase());
  }
  const out = new Map<string, string>();
  rows.slice(2 + n, 2 + n + h).forEach((r, y) => {
    for (let x = 0; x < w; x++) {
      const c = pal.get(r[x]);
      if (c) out.set(`${b.x + x},${b.y + y}`, c);
    }
  });
  return out;
}

function mockupPixels(js: Mirror, line: Line): Map<string, string> {
  const spec = SHOW.styles[line.style];
  const buf = new Uint8ClampedArray(72 * 16 * 4);
  js.drawText(buf, 72, 16, line.text, spec, FONTS[spec.font] as Font, 1);
  const out = new Map<string, string>();
  const hex = (v: number) => v.toString(16).toUpperCase().padStart(2, "0");
  for (let i = 0; i < 72 * 16; i++) {
    if (buf[i * 4] || buf[i * 4 + 1] || buf[i * 4 + 2]) {
      out.set(`${i % 72},${Math.floor(i / 72)}`, "#" + hex(buf[i * 4]) + hex(buf[i * 4 + 1]) + hex(buf[i * 4 + 2]));
    }
  }
  return out;
}

test("the mockup draws live text pixel-identical to the app", () => {
  const js = mirror();
  const samples: Line[] = [
    { text: "DEC 7", style: "date" }, { text: "DEC 25", style: "date" }, { text: "18 DAYS", style: "head" },
    { text: "06:42", style: "head" }, { text: "TO CHRISTMAS", style: "sub" }, { text: "TO GO", style: "sub" },
    { text: "MERRY", style: "top" }, { text: "NEXT YEAR!", style: "bot" },
  ];
  for (const line of samples) assert.deepEqual(mockupPixels(js, line), bitmapPixels(line), line.text);
});

// ---------- generated data ----------

test("25 days, each with its animation", () => {
  assert.equal(SHOW.days.length, 25);
  SHOW.days.forEach((d, i) => {
    assert.equal(d.day, i + 1);
    assert.ok(d.ms >= 7000 && d.ms <= 10000, `${d.name}: ${d.ms} ms`);
  });
  for (const a of [...SHOW.days, SHOW.door, SHOW.winter, SHOW.card]) {
    assert.ok(existsSync(new URL(`app/src/${a.path}`, APP)), a.path);
  }
});

test("every live text uses known glyphs and fits the display", () => {
  const lines: Line[] = [];
  for (let d = 1; d <= 25; d++) lines.push({ text: dateLabel(d), style: "date" });
  for (const year of [2026, 2027, 2028]) for (const now of everyDay(year)) lines.push(...cardLines(now));
  for (let s = 0; s < 86400; s += 60) {
    lines.push(...cardLines({ year: 2026, month: 12, day: 24, hour: Math.floor(s / 3600), minute: (s / 60) % 60, second: 0 }));
  }
  const seen = new Set<string>();
  for (const line of lines) {
    const key = line.text + "|" + line.style;
    if (seen.has(key)) continue;
    seen.add(key);
    const spec = SHOW.styles[line.style];
    const font = FONTS[spec.font] as Font;
    for (const ch of line.text) assert.ok(font.glyphs[ch], `${spec.font} has no ${JSON.stringify(ch)} (${line.text})`);
    const b = textBitmap(line.text, font, spec);
    assert.ok(b.x >= 0 && b.x + b.width <= 72 && b.y + b.height <= 16, `${line.text} does not fit`);
    assert.ok(Number(b.data.split("\n")[1].split(" ")[2]) <= 32, `${line.text}: over 32 colors`);
  }
});
