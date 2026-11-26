// Logic tests for Hanukkah (run by tests/check.sh under Node 24):
//   node --experimental-strip-types --test tests/logic.test.mts
//
// 1. app/shared/hanukkah.ts: tonight's candle count at the 17:00 boundaries, the card texts, the playlist and
//    holiday mode, against the real 2026 and 2027 dates.
// 2. The mockup's JavaScript mirror (mockup/template.html, the <logic> block) agrees with the app.
// 3. Generated data: every playlist scene and card exists, and every card text fits and uses glyphs the fonts have.
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { test } from "node:test";

import { candles, countPages, nextPreview, playlist, season, type Entry } from "../app/shared/hanukkah.ts";
import { parseLocal, textWidth, type Font, type LocalTime } from "../app/shared/kit.ts";
import { FONTS, SHOW } from "../app/shared/generated/show.ts";

const APP = new URL("..", import.meta.url);

const t = (iso: string): LocalTime => {
  const v = parseLocal(iso);
  assert.ok(v, iso);
  return v;
};
const at = (local: string) => t(local + ":00-05:00");

test("candle count follows 17:00 sundown (Hanukkah 2026: first candle the evening of Dec 4)", () => {
  assert.equal(candles(at("2026-12-03T23:59")), 0);
  assert.equal(candles(at("2026-12-04T00:00")), 0);
  assert.equal(candles(at("2026-12-04T16:59")), 0);
  assert.equal(candles(at("2026-12-04T17:00")), 1);
  assert.equal(candles(at("2026-12-05T10:00")), 1);
  assert.equal(candles(at("2026-12-05T16:59")), 1);
  assert.equal(candles(at("2026-12-05T17:00")), 2);
  assert.equal(candles(at("2026-12-07T18:30")), 4);
  assert.equal(candles(at("2026-12-11T16:59")), 7);
  assert.equal(candles(at("2026-12-11T17:00")), 8);
  assert.equal(candles(at("2026-12-12T09:00")), 8);
  assert.equal(candles(at("2026-12-12T17:00")), 8);
  assert.equal(candles(at("2026-12-12T23:00")), 8);
  assert.equal(candles(at("2026-12-12T23:59")), 8);
  assert.equal(candles(at("2026-12-13T00:00")), 0);
  assert.equal(candles(at("2026-12-13T18:00")), 0);
  // the offset never matters: only the bar's wall clock
  assert.equal(candles(t("2026-12-04T17:00:00+09:00")), 1);
  assert.equal(candles(t("2026-12-04T16:59:59-10:00")), 0);
});

test("2027 crosses into the new year: first candle the evening of Dec 24, last day Jan 1", () => {
  assert.equal(candles(at("2027-12-24T16:59")), 0);
  assert.equal(candles(at("2027-12-24T17:00")), 1);
  assert.equal(candles(at("2027-12-31T17:00")), 8);
  assert.equal(candles(at("2028-01-01T22:00")), 8);
  assert.equal(candles(at("2028-01-02T00:00")), 0);
});

const pages = (iso: string, preview = 0) => countPages(at(iso), preview);

test("count card texts: before, the day before, the first evening, during, after", () => {
  assert.deepEqual(pages("2026-11-26T12:00"), [["8 DAYS", "TO HANUKKAH"]]);
  assert.deepEqual(pages("2026-11-16T12:00"), [["18 DAYS", "TO HANUKKAH"]]);
  assert.deepEqual(pages("2026-12-02T23:59"), [["2 DAYS", "TO HANUKKAH"]]);
  assert.deepEqual(pages("2026-12-03T00:00"), [["TOMORROW", "HANUKKAH BEGINS"]]);
  assert.deepEqual(pages("2026-12-04T16:59"), [["TONIGHT", "HANUKKAH BEGINS"]]);
  assert.deepEqual(pages("2026-12-04T17:00"), [["NIGHT 1", "HAPPY HANUKKAH"], ["NIGHT 1", "CHAG SAMEACH"]]);
  assert.deepEqual(pages("2026-12-06T20:00"), [["NIGHT 3", "HAPPY HANUKKAH"], ["NIGHT 3", "CHAG SAMEACH"]]);
  assert.deepEqual(pages("2026-12-12T23:00"), [["NIGHT 8", "HAPPY HANUKKAH"], ["NIGHT 8", "CHAG SAMEACH"]]);
  // after: the count to Hanukkah 2027 (Dec 24)
  assert.deepEqual(pages("2026-12-13T00:00"), [["376 DAYS", "TO HANUKKAH"]]);
  assert.deepEqual(pages("2027-12-22T09:00"), [["2 DAYS", "TO HANUKKAH"]]);
  assert.equal(season(at("2026-11-26T12:00"), 0), "before");
  assert.equal(season(at("2026-12-03T12:00"), 0), "tomorrow");
  assert.equal(season(at("2026-12-04T12:00"), 0), "tonight");
  assert.equal(season(at("2026-12-08T12:00"), 0), "during");
});

const names = (entries: Entry[]) => entries.map((e) => (e.kind === "scene" ? e.name : `[${e.card}]`));

test("playlist: tonight's menorah and window; the finale only while candles are lit", () => {
  assert.deepEqual(names(playlist(at("2026-11-26T12:00"), 0)), [
    "[count]", "menorah_0", "[clock]", "dreidel", "[count]", "latkes", "[clock]", "sufganiyot", "[count]", "gelt",
    "[clock]", "window_0", "[clock]",
  ]);
  assert.deepEqual(names(playlist(at("2026-12-06T20:00"), 0)), [
    "[count]", "menorah_3", "[clock]", "dreidel", "[count]", "latkes", "[clock]", "sufganiyot", "[count]", "gelt",
    "[clock]", "window_3", "[count]", "finale", "[clock]",
  ]);
  assert.ok(names(playlist(at("2026-12-04T16:59"), 0)).includes("menorah_0"));
  assert.ok(names(playlist(at("2026-12-04T17:00"), 0)).includes("menorah_1"));
  assert.ok(names(playlist(at("2026-12-12T23:00"), 0)).includes("window_8"));
});

test("holiday mode: START previews nights 1..8, then follows the date again", () => {
  const seq = [0];
  for (let i = 0; i < 9; i++) seq.push(nextPreview(seq[seq.length - 1]));
  assert.deepEqual(seq, [0, 1, 2, 3, 4, 5, 6, 7, 8, 0]);
  const summer = at("2027-07-01T10:00");
  assert.deepEqual(countPages(summer, 5), [["NIGHT 5", "HAPPY HANUKKAH"], ["NIGHT 5", "CHAG SAMEACH"]]);
  assert.ok(names(playlist(summer, 5)).includes("menorah_5"));
  assert.ok(names(playlist(summer, 5)).includes("finale"));
  assert.ok(!names(playlist(summer, 0)).includes("finale"));
});

// ---------- the mockup mirror ----------

type Mirror = {
  candles: typeof candles; countPages: typeof countPages; playlist: typeof playlist; nextPreview: typeof nextPreview;
};

function mirror(): Mirror {
  const html = readFileSync(new URL("mockup/template.html", APP), "utf8");
  const start = html.indexOf("const LOGIC = (() => {");
  const end = html.indexOf("/* </logic> */");
  assert.ok(start > 0 && end > start, "mockup/template.html must keep its <logic> block");
  return new Function(html.slice(start, end) + "\nreturn LOGIC;")() as Mirror;
}

test("the mockup's logic matches the app on every day of 2026-2032", () => {
  const js = mirror();
  for (let d = Date.UTC(2026, 0, 1); d < Date.UTC(2033, 0, 1); d += 86400000) {
    const x = new Date(d);
    for (const [hour, minute] of [[0, 0], [16, 59], [17, 0], [23, 59]]) {
      const now: LocalTime = { year: x.getUTCFullYear(), month: x.getUTCMonth() + 1, day: x.getUTCDate(), hour,
        minute, second: 0 };
      const where = JSON.stringify(now);
      assert.equal(js.candles(now), candles(now), where);
      assert.deepEqual(js.countPages(now, 0), countPages(now, 0), where);
      assert.deepEqual(js.playlist(now, 0), playlist(now, 0), where);
    }
  }
  for (let p = 0; p <= 8; p++) {
    assert.equal(js.nextPreview(p), nextPreview(p));
    assert.deepEqual(js.countPages(at("2027-03-01T12:00"), p), countPages(at("2027-03-01T12:00"), p));
    assert.deepEqual(js.playlist(at("2027-03-01T12:00"), p), playlist(at("2027-03-01T12:00"), p));
  }
});

// ---------- generated data ----------

test("every playlist entry exists, and every card text fits the display", () => {
  const sceneNames = new Set(SHOW.scenes.map((s) => s.name));
  for (let n = 0; n <= 8; n++) {
    for (const e of playlist(at("2027-03-01T12:00"), n)) {
      if (e.kind === "scene") assert.ok(sceneNames.has(e.name), e.name);
      else assert.ok(e.card in SHOW.cards, e.card);
    }
  }
  const paths = [...SHOW.scenes.map((s) => s.path), ...Object.values(SHOW.cards)];
  for (const p of paths) assert.ok(existsSync(new URL("app/src/" + p, APP)), p);

  const texts: [string, keyof typeof SHOW.layout][] = [];
  for (const d of [1, 9, 99, 383]) texts.push([d === 1 ? "1 DAY" : `${d} DAYS`, "head"]);
  for (const [head, sub] of [["TOMORROW", "HANUKKAH BEGINS"], ["TONIGHT", "HANUKKAH BEGINS"], ["NIGHT 8", "HAPPY HANUKKAH"],
    ["NIGHT 8", "CHAG SAMEACH"], ["", "TO HANUKKAH"]]) {
    if (head) texts.push([head, "head"]);
    texts.push([sub, "sub"]);
  }
  texts.push(["23:59", "time"], ["WED 30 DEC", "date"]);
  for (const [text, style] of texts) {
    const spec = SHOW.layout[style] as { font: string };
    const font = FONTS[spec.font] as Font;
    for (const ch of text) assert.ok(font.glyphs[ch], `${style} font lacks ${JSON.stringify(ch)}`);
    assert.ok(textWidth(text, font) + 1 <= 72, `${text} is too wide`);
  }
});
