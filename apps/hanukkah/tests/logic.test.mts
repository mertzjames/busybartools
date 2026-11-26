// Logic tests for Hanukkah (run by tests/check.sh under Node 24):
//   node --experimental-strip-types --test tests/logic.test.mts
//
// 1. app/shared/hanukkah.ts: tonight's candle count at the candle-time boundaries (fixed hours, sunset at a
//    location, sunset estimated from the time zone, fallbacks), the card texts, the playlist and holiday mode,
//    against the real 2026 and 2027 dates.
// 2. The mockup's JavaScript mirror (mockup/template.html, the <logic> block) agrees with the app.
// 3. Generated data: every playlist scene and card exists, and every card text fits and uses glyphs the fonts have.
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { test } from "node:test";

import {
  DEFAULT_SKY, SETTINGS_DEFAULTS, SUNDOWN_OPTIONS, skyFromSettings, candles as candlesFor, countPages as pagesFor, nextPreview, playlist as playlistFor,
  season as seasonFor, sundownFor, type Entry, type Sky,
} from "../app/shared/hanukkah.ts";
import { parseLocal, textWidth, type Font, type LocalTime } from "../app/shared/kit.ts";
import { FONTS, SHOW } from "../app/shared/generated/show.ts";

const APP = new URL("..", import.meta.url);

const t = (iso: string): LocalTime => {
  const v = parseLocal(iso);
  assert.ok(v, iso);
  return v;
};
const at = (local: string) => t(local + ":00-05:00");

// The original fixed-17:00 rule, as the "17:00" setting gives it; most date tests use it.
const FIXED17: Sky = { sundown: "17:00", location: null, offset: -300 };
const NEW_YORK: Sky = { sundown: "sunset", location: { lat: 40.7128, lon: -74.006 }, offset: -300 };
const EASTERN: Sky = { sundown: "sunset", location: null, offset: -300 }; // no location: estimated from -05:00
const candles = (u: LocalTime, sky: Sky = FIXED17) => candlesFor(u, sky);
const countPages = (u: LocalTime, preview: number, sky: Sky = FIXED17) => pagesFor(u, preview, sky);
const playlist = (u: LocalTime, preview: number, sky: Sky = FIXED17) => playlistFor(u, preview, sky);
const season = (u: LocalTime, preview: number, sky: Sky = FIXED17) => seasonFor(u, preview, sky);

test("candle count with the fixed 17:00 candle time (Hanukkah 2026: first candle the evening of Dec 4)", () => {
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

test("candle time: sunset at the location setting (New York, Dec 2026)", () => {
  // the kit's NOAA approximation gives 16:30 on Dec 4 (almanac 16:28; the kit is tested to within 3 minutes)
  assert.equal(sundownFor(at("2026-12-04T12:00"), NEW_YORK), 16 * 60 + 30);
  assert.equal(candles(at("2026-12-04T16:29"), NEW_YORK), 0);
  assert.equal(candles(at("2026-12-04T16:30"), NEW_YORK), 1);
  assert.equal(candles(at("2026-12-05T16:28"), NEW_YORK), 1);
  assert.equal(candles(at("2026-12-05T16:29"), NEW_YORK), 2);
  assert.equal(candles(at("2026-12-11T16:29"), NEW_YORK), 8);
  assert.equal(candles(at("2026-12-12T23:00"), NEW_YORK), 8);
  assert.equal(candles(at("2026-12-13T18:00"), NEW_YORK), 0);
  assert.deepEqual(pagesFor(at("2026-12-04T15:00"), 0, NEW_YORK)[1], ["TONIGHT", "CANDLES AT 16:30"]);
});

test("candle time: no location, so sunset is estimated from the bar's UTC offset", () => {
  // -05:00 in December (standard time): 75 W at 39 N
  assert.equal(sundownFor(at("2026-12-04T12:00"), EASTERN), 16 * 60 + 38);
  assert.equal(candles(at("2026-12-04T16:37"), EASTERN), 0);
  assert.equal(candles(at("2026-12-04T16:38"), EASTERN), 1);
  // a zone's estimate sits on its own meridian, so every zone lands at the same local time
  assert.equal(sundownFor(at("2026-12-04T12:00"), { ...EASTERN, offset: -480 }), 16 * 60 + 38);
});

test("candle time: fixed settings override the sun, and fallbacks", () => {
  for (const opt of SUNDOWN_OPTIONS) {
    if (opt === "sunset") continue;
    const [h, m] = opt.split(":").map(Number);
    const sky: Sky = { sundown: opt, location: { lat: 40.7, lon: -74 }, offset: -300 };
    assert.equal(sundownFor(at("2026-12-04T12:00"), sky), h * 60 + m, opt);
    const before = `2026-12-04T${String(m ? h : h - 1).padStart(2, "0")}:${m ? "29" : "59"}`;
    assert.equal(candles(at(before), sky), 0, `${opt}: ${before}`);
    assert.equal(candles(at(`2026-12-04T${opt}`), sky), 1, opt);
  }
  // no settings and no offset in the timestamp: 17:00
  assert.equal(sundownFor(at("2026-12-04T12:00"), DEFAULT_SKY), 17 * 60);
  assert.equal(candles(at("2026-12-04T16:59"), DEFAULT_SKY), 0);
  assert.equal(candles(at("2026-12-04T17:00"), DEFAULT_SKY), 1);
  // a polar night has no sunset: 17:00
  assert.equal(sundownFor(at("2026-12-04T12:00"), { sundown: "sunset", location: { lat: 78, lon: 15 }, offset: 60 }),
    17 * 60);
});

test("settings: what the bar stores becomes the candle-time rule, with fallbacks", () => {
  // defaults (no settings stored, or loadSettings fell back): sunset, estimated from the time zone
  assert.deepEqual(skyFromSettings(SETTINGS_DEFAULTS, -300), EASTERN);
  assert.deepEqual(skyFromSettings({ sundown: "17:30", location: { mode: "auto", name: "Bar location" } }, -300),
    { sundown: "17:30", location: null, offset: -300 });
  assert.deepEqual(skyFromSettings({ sundown: "bogus", location: { mode: "fixed", name: "Home", lat: 40.7128,
    lon: -74.006 } }, -300), { ...NEW_YORK, location: { lat: 40.7128, lon: -74.006, name: "Home" } });
  assert.deepEqual(skyFromSettings(SETTINGS_DEFAULTS, null), DEFAULT_SKY);
});

const pages = (iso: string, preview = 0) => countPages(at(iso), preview);

test("count card texts: before, the day before, the first evening, during, after", () => {
  assert.deepEqual(pages("2026-11-26T12:00"), [["8 DAYS", "TO HANUKKAH"]]);
  assert.deepEqual(pages("2026-11-16T12:00"), [["18 DAYS", "TO HANUKKAH"]]);
  assert.deepEqual(pages("2026-12-02T23:59"), [["2 DAYS", "TO HANUKKAH"]]);
  assert.deepEqual(pages("2026-12-03T00:00"), [["TOMORROW", "HANUKKAH BEGINS"]]);
  assert.deepEqual(pages("2026-12-04T16:59"), [["TONIGHT", "HANUKKAH BEGINS"], ["TONIGHT", "CANDLES AT 17:00"]]);
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
  candles: typeof candlesFor; countPages: typeof pagesFor; playlist: typeof playlistFor; nextPreview: typeof nextPreview;
  sundownFor: typeof sundownFor;
};

function mirror(): Mirror {
  const html = readFileSync(new URL("mockup/template.html", APP), "utf8");
  const start = html.indexOf("const LOGIC = (() => {");
  const end = html.indexOf("/* </logic> */");
  assert.ok(start > 0 && end > start, "mockup/template.html must keep its <logic> block");
  return new Function(html.slice(start, end) + "\nreturn LOGIC;")() as Mirror;
}

const SKIES: Sky[] = [FIXED17, NEW_YORK, EASTERN, DEFAULT_SKY, { sundown: "16:30", location: null, offset: 60 },
  { sundown: "sunset", location: { lat: -33.9, lon: 151.2 }, offset: 660 }];

test("the mockup's logic matches the app on every day of 2026-2032", () => {
  const js = mirror();
  for (let d = Date.UTC(2026, 0, 1); d < Date.UTC(2033, 0, 1); d += 86400000) {
    const x = new Date(d);
    const sky = SKIES[Math.floor(d / 86400000) % SKIES.length];
    for (const [hour, minute] of [[0, 0], [16, 29], [16, 30], [16, 59], [17, 0], [23, 59]]) {
      const now: LocalTime = { year: x.getUTCFullYear(), month: x.getUTCMonth() + 1, day: x.getUTCDate(), hour,
        minute, second: 0 };
      const where = JSON.stringify([now, sky]);
      assert.equal(js.sundownFor(now, sky), sundownFor(now, sky), where);
      assert.equal(js.candles(now, sky), candlesFor(now, sky), where);
      assert.deepEqual(js.countPages(now, 0, sky), pagesFor(now, 0, sky), where);
      assert.deepEqual(js.playlist(now, 0, sky), playlistFor(now, 0, sky), where);
    }
  }
  for (let p = 0; p <= 8; p++) {
    assert.equal(js.nextPreview(p), nextPreview(p));
    assert.deepEqual(js.countPages(at("2027-03-01T12:00"), p, EASTERN), countPages(at("2027-03-01T12:00"), p, EASTERN));
    assert.deepEqual(js.playlist(at("2027-03-01T12:00"), p, EASTERN), playlist(at("2027-03-01T12:00"), p, EASTERN));
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
  for (const [head, sub] of [["TOMORROW", "HANUKKAH BEGINS"], ["TONIGHT", "HANUKKAH BEGINS"], ["", "CANDLES AT 18:00"], ["NIGHT 8", "HAPPY HANUKKAH"],
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
