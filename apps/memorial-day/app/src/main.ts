// Memorial Day: a quiet tribute. Pre-rendered scenes play in turn with live-text cards between them: the clock, and
// a countdown to Memorial Day (on the day, MEMORIAL DAY and a few words). The flag scene follows the custom: at
// half-staff until noon on Memorial Day, then full staff. Playback is the shared show runner (lib/ts/busybar).
//
// Buttons: OK = next step, encoder = next/previous step, Back = quit, START = holiday mode: each press previews
// the morning of Memorial Day (half-staff), then the afternoon (full staff), then goes back to the calendar.

import { device } from "@shared/device";
import { createShow, type Card, type LocalTime, type TextSpec } from "@shared/kit";
import { DAY_CARD_NAMES, cardPages, nextMode, playlist, type Mode, type Style } from "@shared/memorial";
import manifest from "./appmeta/manifest.json";
import { FONTS, LAYOUT, SHOW } from "@shared/generated/show";

const SPECS = LAYOUT as unknown as Record<Style, TextSpec>;

function main(): void {
  let mode: Mode = "off";

  /** A runner card whose every line is recomputed from the time it is drawn at (the minute rollover included). */
  function card(name: string, backdrop: string): Card {
    return {
      path: backdrop,
      pages: (t0) => cardPages(name, t0, mode).map((page, p) => ({
        ms: page.ms,
        lines: page.lines.map((line, k) => ({
          spec: SPECS[line.style],
          text: (t: LocalTime) => cardPages(name, t, mode)[p]?.lines[k]?.text ?? "",
        })),
      })),
    };
  }

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
    steps: (t) => playlist(SHOW.scenes, t, mode),
  });
  show.start();

  const unbind = listen("input", (event) => {
    const r = show.input(event);
    if (r === "quit") {
      setTimeout(unbind, 0); // never unbind inside the handler itself
      return;
    }
    if (r === "ignored" && event.key === "start" && event.action === "short") {
      mode = nextMode(mode);
      show.start(); // a new cycle from the flag scene, so the change shows at once
    }
  });
}

main();
