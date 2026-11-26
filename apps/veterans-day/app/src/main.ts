// Veterans Day: a tribute. Pre-rendered scenes play in turn with live-text cards between them: the clock, and a
// countdown to Veterans Day (on the day, VETERANS DAY and a few words of thanks). At 11:00 on Nov 11, the 11th hour
// of the 11th day of the 11th month, a quiet card marks the armistice, then the show resumes (D6). Playback is the
// shared show runner (lib/ts/busybar).
//
// Buttons: OK = next step, encoder = next/previous step, Back = quit, START = holiday mode: the first press previews
// Veterans Day, the second previews the 11:00 moment, the third goes back to the calendar (D9).

import { device } from "@shared/device";
import { createShow, type Card, type LocalTime, type TextSpec } from "@shared/kit";
import {
  DAY_CARD_NAMES, MOMENT_CARD, cardPages, msToMoment, nextMode, playlist, type Mode, type Style,
} from "@shared/veterans";
import manifest from "./appmeta/manifest.json";
import { FONTS, LAYOUT, SHOW } from "@shared/generated/show";

const SPECS = LAYOUT as unknown as Record<Style, TextSpec>;

function main(): void {
  let mode: Mode = "off";
  let momentTimer: ReturnType<typeof setTimeout> | undefined;

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

  const cards: Record<string, Card> = {
    clock: card("clock", SHOW.backdrops.clock_bg),
    count: card("count", SHOW.backdrops.count_bg),
    [MOMENT_CARD]: card(MOMENT_CARD, SHOW.backdrops.moment_bg),
  };
  for (const name of DAY_CARD_NAMES) cards[name] = card(name, SHOW.backdrops.count_bg);

  function clearMoment(): void {
    if (momentTimer !== undefined) clearTimeout(momentTimer);
    momentTimer = undefined;
  }

  // Every cycle re-arms one timer when 11:00 on Nov 11 is less than 10 minutes away. When it fires, a new cycle
  // starts; its playlist (picked at 11:00:02 by the bar's clock) opens with the moment card (D6).
  function armMoment(t: LocalTime): void {
    clearMoment();
    const ms = msToMoment(t);
    if (ms === null) return;
    momentTimer = setTimeout(() => {
      momentTimer = undefined;
      show.start();
    }, ms);
  }

  const show = createShow({
    app: manifest.id,
    device,
    fonts: FONTS,
    scenes: SHOW.scenes,
    cards,
    steps: (t) => {
      armMoment(t);
      return playlist(SHOW.scenes, t, mode);
    },
  });
  show.start();

  const unbind = listen("input", (event) => {
    const r = show.input(event);
    if (r === "quit") {
      clearMoment();
      setTimeout(unbind, 0); // never unbind inside the handler itself
      return;
    }
    if (r === "ignored" && event.key === "start" && event.action === "short") {
      mode = nextMode(mode);
      show.start(); // a new cycle from the top, so the change shows at once
    }
  });
}

main();
