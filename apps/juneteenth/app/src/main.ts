// Juneteenth: a show that opens solemn and becomes joyful, the way the day is observed. Pre-rendered scenes play
// in turn (dawn over Galveston Bay, the news arriving, the Juneteenth flag, a cookout, red foods, music, fireworks)
// with live-text cards between them: the clock, and a countdown to June 19 (on the day, JUNETEENTH and
// FREEDOM DAY). Playback is the shared show runner (lib/ts/busybar).
//
// Buttons: OK = next step, encoder = next/previous step, START = holiday mode (preview the day's cards and playlist
// on any date; press again to go back), Back = quit.

import { device } from "@shared/device";
import { createShow, type Card, type LocalTime, type Step, type TextSpec } from "@shared/kit";
import { DAY_CARD_NAMES, cardBackdrop, cardPages, firstCountStep, playlist, type Style } from "@shared/juneteenth";
import manifest from "./appmeta/manifest.json";
import { FONTS, LAYOUT, SHOW } from "@shared/generated/show";

const SPECS = LAYOUT as unknown as Record<Style, TextSpec>;

/** A runner card whose every line is recomputed from the time it is drawn at (the minute rollover included). */
function card(name: string): Card {
  return {
    path: SHOW.backdrops[cardBackdrop(name)],
    pages: (t0) => cardPages(name, t0).map((page, p) => ({
      ms: page.ms,
      lines: page.lines.map((line, k) => ({
        spec: SPECS[line.style],
        text: (t: LocalTime) => cardPages(name, t)[p]?.lines[k]?.text ?? "",
      })),
    })),
  };
}

function main(): void {
  let holiday = false;
  const cards: Record<string, Card> = { clock: card("clock"), count: card("count") };
  for (const name of DAY_CARD_NAMES) cards[name] = card(name);

  const show = createShow({
    app: manifest.id,
    device,
    fonts: FONTS,
    scenes: SHOW.scenes,
    cards,
    steps: (t): Step[] => playlist(SHOW.scenes.length, t, holiday),
  });
  show.start();

  const unbind = listen("input", (event) => {
    const r = show.input(event);
    if (r === "quit") {
      setTimeout(unbind, 0); // never unbind inside the handler itself
      return;
    }
    if (r === "ignored" && event.key === "start" && event.action === "short") {
      holiday = !holiday;
      show.start(firstCountStep(SHOW.scenes.length)); // a new cycle, starting on a count card so the change shows
    }
  });
}

main();
