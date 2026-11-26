// Lunar New Year: festival scenes and the zodiac animal of the year, with a clock card and a countdown card
// between them. Playback is the shared show runner (lib/ts/busybar/showrunner.ts); this file is configuration.
//
// What plays depends on the bar's date (app/shared/lny.ts): before the new year, the countdown playlist and
// "N DAYS / TO LUNAR NEW YEAR"; from New Year's Day through the Lantern Festival (day 15), the festival playlist
// and "YEAR OF THE / GOAT", "HAPPY / NEW YEAR" and a wish in the language set under Apps -> Lunar New Year -> Setup
// ("GONG XI / FA CAI" by default; app/src/appmeta/settings.json, read once at start). The zodiac scene is the current
// or upcoming year's animal. Outside the kit's date table, a generic "HAPPY / NEW YEAR" and no countdown.
//
// Buttons: OK = next step, encoder = next/previous step, Back = quit. START = holiday mode: the festival
// playlist and cards on any date; each further press steps to the next zodiac animal, and after all twelve it
// returns to the real date (docs/DECISIONS.md D10).

import { device } from "@shared/device";
import { createShow, enumValue, loadSettings, type Card, type Line, type Page } from "@shared/kit";
import {
  DEFAULT_GREETING, GREETINGS, SETTINGS_VERSION, clockDate, clockTime, countPages, effectiveSeason, playlist, pressStart, season,
  type Greeting, type Preview, type TextLine,
} from "@shared/lny";
import { FONTS, SHOW } from "@shared/generated/show";
import manifest from "./appmeta/manifest.json";

const report = (err: unknown) => console.error(`${manifest.id}: ${err instanceof Error ? err.message : String(err)}`);

function line(l: TextLine): Line {
  return { spec: SHOW.styles[l.style], text: () => l.text };
}

function run(greeting: Greeting): void {
  let preview: Preview | null = null;
  let currentAnimal = ""; // the real season's animal, from the last playlist pick

  const clock: Card = {
    path: SHOW.card.path,
    pages: (): Page[] => [
      { ms: SHOW.timing.time, lines: [{ spec: SHOW.styles.time, text: clockTime }] },
      { ms: SHOW.timing.date, lines: [{ spec: SHOW.styles.date, text: clockDate }] },
    ],
  };
  const count: Card = {
    path: SHOW.card.path,
    pages: (t) => countPages(effectiveSeason(t, preview), greeting).map((p) => ({ ms: p.ms, lines: p.lines.map(line) })),
  };

  const show = createShow({
    app: manifest.id,
    device,
    fonts: FONTS,
    scenes: SHOW.scenes,
    cards: { clock, count },
    steps: (t) => {
      currentAnimal = season(t).animal;
      return playlist(effectiveSeason(t, preview));
    },
    report,
  });
  show.start();

  const unbind = listen("input", (event) => {
    const result = show.input(event);
    if (result === "quit") {
      // The listener is the last handle: unbind after this callback returns.
      setTimeout(unbind, 0);
      return;
    }
    if (result === "ignored" && event.key === "start" && event.action === "short") {
      preview = pressStart(preview, currentAnimal);
      show.start(); // re-picks the playlist from the top, so the change shows at once
    }
  });
}

function main(): void {
  // Settings first (one request), then the show. loadSettings never throws: on any failure it returns the defaults.
  void loadSettings(device, manifest.id, SETTINGS_VERSION, { greeting: DEFAULT_GREETING as string }, report)
    .then((s) => run(enumValue(s.greeting, GREETINGS, DEFAULT_GREETING)));
}

main();
