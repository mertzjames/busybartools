// Kwanzaa: the day's kinara, then harvest, unity cup, drums, kente and karamu scenes, with clock and count cards
// between them. Playback is the shared show runner (lib/ts/busybar/showrunner.ts); this file is configuration.
//
// The date logic lives in app/shared/kwanzaa.ts (unit-tested): during Kwanzaa (Dec 26 - Jan 1) the kinara shows
// the day's candles and the count card shows HABARI GANI? and the day's principle; otherwise the candles wait and
// the card counts down to Dec 26.
//
// Buttons: OK = next step, encoder = next/previous step, Back = quit.
// START = holiday mode (docs/DECISIONS.md D7): each press previews the next day of Kwanzaa (1..7), then back to
// the real date.

import { device } from "@shared/device";
import { createShow, formatDate, pad2, type Card, type Font, type LocalTime, type TextSpec } from "@shared/kit";
import { countPages, cycleSteps, kwanzaaDay, nextPreview } from "@shared/kwanzaa";
import { FONTS, SHOW } from "@shared/generated/show";
import manifest from "./appmeta/manifest.json";

const STYLES = SHOW.styles as Record<string, TextSpec>;

let preview = 0; // holiday mode: 0 = off, else the day of Kwanzaa being previewed

function today(t: LocalTime) {
  return preview ? { day: preview, days: 0 } : kwanzaaDay(t);
}

const CLOCK: Card = {
  path: SHOW.card.path,
  pages: () => [
    { ms: SHOW.timing.time, lines: [{ spec: STYLES.time, text: (t) => `${pad2(t.hour)}:${pad2(t.minute)}` }] },
    { ms: SHOW.timing.date, lines: [{ spec: STYLES.date, text: (t) => formatDate(t) }] },
  ],
};

const COUNT: Card = {
  path: SHOW.card.path,
  pages: (t0) => {
    const { day, days } = today(t0);
    return countPages(day, days).map((p) => ({
      ms: p.ms,
      lines: p.lines.map((l) => ({ spec: STYLES[l.style], text: () => l.text })),
    }));
  },
};

function main(): void {
  const show = createShow({
    app: manifest.id,
    device,
    fonts: FONTS as Record<string, Font>,
    scenes: SHOW.scenes,
    cards: { clock: CLOCK, count: COUNT },
    steps: (t) => cycleSteps(today(t).day),
  });
  show.start();

  const unbind = listen("input", (event) => {
    const r = show.input(event);
    if (r === "quit") {
      setTimeout(unbind, 0); // the listener is the last handle: unbind after this callback returns
      return;
    }
    if (r === "ignored" && event.key === "start" && event.action === "short") {
      preview = nextPreview(preview);
      show.start(); // a new cycle: re-picks the playlist from the top
    }
  });
}

main();
