// Logic tests for Lunar New Year (run by tests/check.sh under Node 24):
//   node --experimental-strip-types --test tests/logic.test.mts
//
// 1. app/shared/lny.ts against real dates: the season, the zodiac animal, the card texts, the playlists, holiday
//    mode and the fallback outside the kit's date table.
// 2. The mockup's JavaScript mirror (the <logic> block in mockup/template.html) agrees with the app every day.
// 3. Generated data: every playlist scene and .anim exists; every card text fits and uses glyphs the fonts have.
// 4. The show runner plays this app's configuration: the festival opens with the year's zodiac scene.
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { mock, test } from "node:test";

import {
  DEFAULT_GREETING, GREETINGS, SETTINGS_VERSION, animalWithoutTable, countPages, effectiveSeason, playlist, pressStart,
  previewAnimal, season, zodiacScene, type Greeting, type Preview, type Season,
} from "../app/shared/lny.ts";
import {
  ZODIAC, createShow, enumValue, loadSettings, parseLocal, textWidth, type Font, type LocalTime, type ShowDevice,
} from "../app/shared/kit.ts";
import { FONTS, SHOW } from "../app/shared/generated/show.ts";

const APP = new URL("..", import.meta.url);

const t = (iso: string): LocalTime => {
  const v = parseLocal(iso);
  assert.ok(v, iso);
  return v;
};
const at = (date: string) => season(t(`${date}T12:00:00+00:00`));
const texts = (s: Season, g?: Greeting) => countPages(s, g).map((p) => p.lines.map((l) => l.text).join(" / "));

test("countdown: the upcoming animal, even in January before the new year", () => {
  assert.deepEqual(at("2026-11-26"), { kind: "countdown", days: 72, animal: "GOAT" });
  assert.deepEqual(at("2027-01-15"), { kind: "countdown", days: 22, animal: "GOAT" });
  assert.deepEqual(at("2027-02-05"), { kind: "countdown", days: 1, animal: "GOAT" });
  assert.deepEqual(at("2026-01-10"), { kind: "countdown", days: 38, animal: "HORSE" });
  assert.deepEqual(at("2028-01-25"), { kind: "countdown", days: 1, animal: "MONKEY" });
});

test("festival: New Year's Day through the Lantern Festival (day 15), then the next countdown", () => {
  assert.deepEqual(at("2027-02-06"), { kind: "festival", dayOf: 1, animal: "GOAT" });
  assert.deepEqual(season(t("2027-02-06T00:00:00+00:00")), { kind: "festival", dayOf: 1, animal: "GOAT" });
  assert.deepEqual(at("2027-02-10"), { kind: "festival", dayOf: 5, animal: "GOAT" });
  assert.deepEqual(season(t("2027-02-20T23:59:59+00:00")), { kind: "festival", dayOf: 15, animal: "GOAT" });
  assert.deepEqual(season(t("2027-02-21T00:00:00+00:00")), { kind: "countdown", days: 339, animal: "MONKEY" });
  assert.deepEqual(at("2026-02-17"), { kind: "festival", dayOf: 1, animal: "HORSE" });
  assert.deepEqual(at("2028-02-09"), { kind: "festival", dayOf: 15, animal: "MONKEY" }); // Jan 26 + 14
});

test("outside the date table: no countdown, the animal of the year in progress", () => {
  assert.deepEqual(at("2036-03-01"), { kind: "unknown", animal: "DRAGON" });
  assert.deepEqual(at("2037-01-10"), { kind: "unknown", animal: "DRAGON" });
  assert.deepEqual(at("2037-02-20"), { kind: "unknown", animal: "DRAGON" });
  assert.deepEqual(at("2037-02-21"), { kind: "unknown", animal: "SNAKE" });
  assert.deepEqual(at("2037-12-31"), { kind: "unknown", animal: "SNAKE" });
  assert.equal(animalWithoutTable(t("2027-03-01T00:00:00+00:00")), "GOAT");
  assert.deepEqual(at("2036-02-11"), { kind: "festival", dayOf: 15, animal: "DRAGON" }); // last day in the table
});

test("card texts", () => {
  assert.deepEqual(texts(at("2026-11-26")), ["72 DAYS / TO LUNAR NEW YEAR"]);
  assert.deepEqual(texts(at("2027-02-05")), ["1 DAY / TO LUNAR NEW YEAR"]);
  assert.deepEqual(texts(at("2027-02-06")), ["YEAR OF THE / GOAT", "HAPPY / NEW YEAR", "GONG XI / FA CAI"]);
  assert.deepEqual(texts(at("2027-02-20")), ["YEAR OF THE / GOAT", "LANTERN / FESTIVAL", "GONG XI / FA CAI"]);
  assert.deepEqual(texts(at("2037-06-01")), ["HAPPY / NEW YEAR"]);
  assert.deepEqual(countPages(at("2026-11-26")).map((p) => p.lines.map((l) => l.style)), [["head", "sub"]]);
  assert.deepEqual(countPages(at("2027-02-06")).map((p) => p.ms), [4500, 3500, 3000]);
});

test("the greeting setting picks the wish page", () => {
  const ny = at("2027-02-06");
  const wish = (g: Greeting) => texts(ny, g).slice(2);
  assert.deepEqual(wish("mandarin"), ["GONG XI / FA CAI"]);
  assert.deepEqual(wish("cantonese"), ["GUNG HEI / FAT CHOI"]);
  assert.deepEqual(wish("vietnamese"), ["CHUC MUNG / NAM MOI"]);
  assert.deepEqual(wish("korean"), ["SAEHAE BOK / MANI BADEUSEYO"]);
  assert.deepEqual(countPages(ny, "korean")[2].lines.map((l) => l.style), ["head", "sub"]);
  assert.deepEqual(texts(ny, "none"), ["YEAR OF THE / GOAT", "HAPPY / NEW YEAR"]);
  assert.deepEqual(texts(at("2027-02-20"), "none"), ["YEAR OF THE / GOAT", "LANTERN / FESTIVAL"]);
  // the countdown and the fallback don't change with the setting
  for (const g of GREETINGS) {
    assert.deepEqual(texts(at("2026-11-26"), g), ["72 DAYS / TO LUNAR NEW YEAR"]);
    assert.deepEqual(texts(at("2037-06-01"), g), ["HAPPY / NEW YEAR"]);
  }
});

test("settings.json matches the app, and bad or missing settings fall back to Mandarin", async () => {
  const doc = JSON.parse(readFileSync(new URL("app/src/appmeta/settings.json", APP), "utf8"));
  assert.equal(doc.format_version, 1);
  assert.equal(doc.version, SETTINGS_VERSION);
  const field = doc.fields.greeting;
  assert.equal(field.type, "enum");
  assert.equal(field.default, DEFAULT_GREETING);
  assert.deepEqual(field.options.map((o: { value: string }) => o.value), [...GREETINGS]);
  const read = async (get: () => Promise<{ version: number; values: Record<string, unknown> }>) => {
    const s = await loadSettings({ AppsSettingsGet: get }, "x", SETTINGS_VERSION, { greeting: DEFAULT_GREETING as string });
    return enumValue(s.greeting, GREETINGS, DEFAULT_GREETING);
  };
  assert.equal(await read(async () => ({ version: 1, values: { greeting: "korean" } })), "korean");
  assert.equal(await read(async () => ({ version: 1, values: { greeting: "none" } })), "none");
  assert.equal(await read(async () => ({ version: 1, values: { greeting: "klingon" } })), "mandarin");
  assert.equal(await read(async () => ({ version: 1, values: { greeting: 3 } })), "mandarin");
  assert.equal(await read(async () => ({ version: 1, values: {} })), "mandarin");
  assert.equal(await read(async () => ({ version: 2, values: { greeting: "korean" } })), "mandarin"); // old version
  assert.equal(await read(async () => { throw new Error("offline"); }), "mandarin");
});

test("playlists: the zodiac scene of the season's animal; the festival opens with it; finale only then", () => {
  const goat = zodiacScene("GOAT");
  assert.equal(SHOW.scenes[goat].name, "zodiac_goat");
  const before = playlist(at("2027-01-15"));
  const during = playlist(at("2027-02-06"));
  const unknown = playlist(at("2037-06-01"));
  assert.deepEqual(during[0], { kind: "scene", scene: goat });
  assert.deepEqual(during[1], { kind: "card", card: "count" });
  assert.ok(before.some((s) => s.kind === "scene" && s.scene === goat));
  assert.ok(unknown.some((s) => s.kind === "scene" && s.scene === zodiacScene("SNAKE"))); // Jun 2037
  const names = (steps: typeof before) =>
    steps.filter((s) => s.kind === "scene").map((s) => SHOW.scenes[(s as { scene: number }).scene].name);
  const cards = (steps: typeof before) => steps.filter((s) => s.kind === "card").map((s) => (s as { card: string }).card);
  // the festival: every scene once, the finale included, cards alternating clock and count
  assert.equal(during.length, 16);
  assert.equal(new Set(names(during)).size, 8);
  assert.ok(names(during).includes("finale"));
  assert.deepEqual(cards(during), ["count", "clock", "count", "clock", "count", "clock", "count", "clock"]);
  // before the holiday (and outside the table): no finale, and a count card after the zodiac scene
  for (const steps of [before, unknown]) {
    assert.equal(steps.length, 14);
    assert.equal(new Set(names(steps)).size, 7);
    assert.ok(!names(steps).includes("finale"));
    assert.deepEqual(cards(steps), ["clock", "count", "clock", "count", "clock", "count", "count"]);
    for (let i = 0; i < steps.length; i++) assert.notEqual(steps[i].kind, steps[(i + 1) % steps.length].kind);
  }
  for (const steps of [before, during, unknown]) {
    assert.equal(names(steps).filter((n) => n.startsWith("zodiac_")).length, 1);
  }
  // holiday mode plays the festival playlist, finale included, on any date
  const p = pressStart(null, "GOAT");
  assert.ok(names(playlist(effectiveSeason(t("2026-11-26T12:00:00+00:00"), p))).includes("finale"));
});

test("holiday mode: START steps through all twelve animals from the season's, then exits", () => {
  let p: Preview | null = null;
  const seen: string[] = [];
  for (let i = 0; i < 12; i++) {
    p = pressStart(p, "GOAT");
    assert.ok(p);
    seen.push(previewAnimal(p));
    const s = effectiveSeason(t("2026-11-26T12:00:00+00:00"), p);
    assert.deepEqual(s, { kind: "festival", dayOf: 1, animal: seen[i] });
  }
  assert.deepEqual(seen, ["GOAT", "MONKEY", "ROOSTER", "DOG", "PIG", "RAT", "OX", "TIGER", "RABBIT", "DRAGON",
    "SNAKE", "HORSE"]);
  p = pressStart(p, "GOAT");
  assert.equal(p, null);
  assert.equal(effectiveSeason(t("2026-11-26T12:00:00+00:00"), p).kind, "countdown");
  assert.equal(previewAnimal(pressStart(null, "")!), "RAT"); // before the first time read: start at the top
});

// --- the mockup's mirror of this logic ---------------------------------------------------------------------------

function mockupLogic() {
  const html = readFileSync(new URL("mockup/template.html", APP), "utf8");
  const m = /\/\/ <logic>([\s\S]*?)\/\/ <\/logic>/.exec(html);
  assert.ok(m, "mockup/template.html has a <logic> block");
  const make = new Function("SHOW", m[1] + "\nreturn { season, countPages, playlist, pressStart, previewAnimal };");
  return make(SHOW) as {
    season: (t: LocalTime) => Season;
    countPages: (s: Season, g: Greeting) => { ms: number; lines: { style: string; text: string }[] }[];
    playlist: (s: Season) => unknown[];
    pressStart: (p: Preview | null, a: string) => Preview | null;
    previewAnimal: (p: Preview) => string;
  };
}

test("the mockup's logic mirrors the app for every day, 2024 through 2038", () => {
  const js = mockupLogic();
  let d = Date.UTC(2024, 0, 1);
  const end = Date.UTC(2038, 11, 31);
  for (; d <= end; d += 86400000) {
    const u = new Date(d);
    const lt: LocalTime = { year: u.getUTCFullYear(), month: u.getUTCMonth() + 1, day: u.getUTCDate(), hour: 9, minute: 30, second: 0 };
    const s = season(lt);
    assert.deepEqual(js.season(lt), s, JSON.stringify(lt));
    for (const g of GREETINGS) assert.deepEqual(js.countPages(s, g), countPages(s, g));
    assert.deepEqual(js.playlist(s), playlist(s));
  }
  let a: Preview | null = null;
  let b: Preview | null = null;
  for (let i = 0; i < 14; i++) {
    a = pressStart(a, "DOG");
    b = js.pressStart(b, "DOG");
    assert.deepEqual(b, a);
  }
});

// --- generated data -------------------------------------------------------------------------------------------

test("every scene and the card backdrop exist; every card text fits and has its glyphs", () => {
  for (const s of SHOW.scenes) assert.ok(existsSync(new URL(`app/src/${s.path}`, APP)), s.path);
  assert.ok(existsSync(new URL(`app/src/${SHOW.card.path}`, APP)));
  assert.deepEqual(SHOW.zodiac, ZODIAC.map((z) => "zodiac_" + z.toLowerCase()));
  const seasons: Season[] = [];
  for (let days = 1; days <= 400; days++) seasons.push({ kind: "countdown", days, animal: "GOAT" });
  for (const animal of ZODIAC) for (const dayOf of [1, 15]) seasons.push({ kind: "festival", dayOf, animal });
  seasons.push({ kind: "unknown", animal: "RAT" });
  for (const s of seasons) {
    for (const page of GREETINGS.flatMap((g) => countPages(s, g))) {
      for (const l of page.lines) {
        const spec = SHOW.styles[l.style];
        const font = FONTS[spec.font] as Font;
        for (const ch of l.text) assert.ok(ch === " " || font.glyphs[ch], `${spec.font} lacks ${ch} (${l.text})`);
        assert.ok(textWidth(l.text, font) + 1 <= 72, `${l.text} fits`);
      }
    }
  }
});

// --- the show runner with this app's configuration -----------------------------------------------------------

test("the show runner opens the festival with the year's zodiac scene, then the greeting card", async () => {
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    const log: string[] = [];
    const device: ShowDevice = {
      async DisplayDraw(p) {
        for (const e of p.elements) log.push(e.type === "animation" ? `anim ${e.path}` : `text ${e.id}`);
      },
      async DisplayClear() {},
      async TimeGet() {
        return { timestamp: "2027-02-06T08:00:00-05:00" };
      },
    };
    const show = createShow({
      app: "test", device, fonts: FONTS, scenes: SHOW.scenes, report: (e) => { throw e; },
      cards: {
        clock: { path: SHOW.card.path, pages: () => [] },
        count: {
          path: SHOW.card.path,
          pages: (u) => countPages(season(u)).map((p) => ({
            ms: p.ms, lines: p.lines.map((l) => ({ spec: SHOW.styles[l.style], text: () => l.text })),
          })),
        },
      },
      steps: (u) => playlist(season(u)),
    });
    const flush = async (ms: number) => {
      for (let i = 0; i < 20; i++) await Promise.resolve();
      mock.timers.tick(ms);
      for (let i = 0; i < 20; i++) await Promise.resolve();
    };
    show.start();
    await flush(0);
    assert.deepEqual(log.splice(0), ["anim animations/zodiac_goat.anim"]);
    await flush(6000);
    await flush(0);
    await flush(0);
    assert.deepEqual(log.splice(0).slice(0, 3), ["anim animations/card_bg.anim", "text text0", "text text1"]);
    show.stop();
  } finally {
    mock.timers.reset();
  }
});
