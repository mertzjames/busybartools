// Mother's Day: pre-rendered scenes play in turn with live-text cards between them: the clock, and a countdown
// to Mother's Day (on the day, HAPPY / MOTHER'S DAY and a few sweet words). Playback is the shared show runner
// (lib/ts/busybar).
//
// Buttons: OK = next step, encoder = next/previous step, START = holiday mode (preview the day's cards and playlist
// on any date; press again to go back), Back = quit.

import { device } from "@shared/device";
import { createShow, type Card, type LocalTime, type Step, type TextSpec } from "@shared/kit";
import { DAY_CARD_NAMES, cardPages, playlist, type Style } from "@shared/mothersday";
import manifest from "./appmeta/manifest.json";
import { FONTS, LAYOUT, SHOW } from "@shared/generated/show";

const SPECS = LAYOUT as unknown as Record<Style, TextSpec>;

/** A runner card whose every line is recomputed from the time it is drawn at (the minute rollover included). */
function card(name: string, backdrop: string): Card {
  return {
    path: backdrop,
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
  let fromCard = false;
  const cards: Record<string, Card> = {
    clock: card("clock", SHOW.backdrops.clock_bg),
    count: card("count", SHOW.backdrops.count_bg),
  };
  for (const name of DAY_CARD_NAMES) cards[name] = card(name, SHOW.backdrops.count_bg);

  const show = createShow({
    app: manifest.id,
    device,
    fonts: FONTS,
    scenes: SHOW.scenes,
    cards,
    steps: (t) => {
      const steps: Step[] = playlist(SHOW.scenes.length, t, holiday, fromCard);
      fromCard = false;
      return steps;
    },
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
      fromCard = true; // start the new cycle on a count card, so the change shows at once
      show.start();
    }
  });
}

main();
