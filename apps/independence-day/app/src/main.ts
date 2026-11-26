// Independence Day: pre-rendered scenes play in turn with live-text cards between them: the clock, and a countdown
// to the Fourth of July (on the day, HAPPY / 4TH OF JULY and the hours and minutes until the fireworks at dusk).
// Playback is the shared show runner (lib/ts/busybar).
//
// Buttons: OK = next step, encoder = next/previous step, Back = quit, START = cycle the review modes:
//   normal -> holiday mode (the Fourth's cards and playlist on any date, at today's time of day)
//          -> demo (the Fourth at 20:58, so the fireworks countdown runs out in a minute or two) -> normal.

import { device } from "@shared/device";
import { createShow, type Card, type LocalTime, type Step, type TextSpec } from "@shared/kit";
import { COUNT_CARD, DAY_CARD, cardPages, demoShift, demoTime, playlist, type Style } from "@shared/july4";
import manifest from "./appmeta/manifest.json";
import { FONTS, LAYOUT, SHOW } from "@shared/generated/show";

const SPECS = LAYOUT as unknown as Record<Style, TextSpec>;

type Mode = "normal" | "holiday" | "demo";
const NEXT_MODE: Record<Mode, Mode> = { normal: "holiday", holiday: "demo", demo: "normal" };

function main(): void {
  let mode: Mode = "normal";
  let shift: number | null = null; // demo: seconds added to the bar's time (set at the first cycle of the demo)
  let fromCard = false;
  const view = (t: LocalTime): LocalTime => (mode === "demo" && shift !== null ? demoTime(t, shift) : t);

  /** A runner card whose every line is recomputed from the time it is drawn at (the minute rollover included). */
  const card = (name: string, backdrop: string): Card => ({
    path: backdrop,
    pages: (t0) => cardPages(name, view(t0)).map((page, p) => ({
      ms: page.ms,
      lines: page.lines.map((line, k) => ({
        spec: SPECS[line.style],
        text: (t: LocalTime) => cardPages(name, view(t))[p]?.lines[k]?.text ?? "",
      })),
    })),
  });

  const show = createShow({
    app: manifest.id,
    device,
    fonts: FONTS,
    scenes: SHOW.scenes,
    cards: {
      clock: card("clock", SHOW.backdrops.clock_bg),
      [COUNT_CARD]: card(COUNT_CARD, SHOW.backdrops.count_bg),
      [DAY_CARD]: card(DAY_CARD, SHOW.backdrops.count_bg),
    },
    steps: (t) => {
      if (mode === "demo" && shift === null) shift = demoShift(t);
      const steps: Step[] = playlist(SHOW.scenes.length, view(t), mode !== "normal", fromCard, mode === "demo");
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
      mode = NEXT_MODE[mode];
      shift = null;
      fromCard = true; // start the new cycle on a count card, so the change shows at once
      show.start();
    }
  });
}

main();
