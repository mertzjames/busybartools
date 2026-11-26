// Hanukkah: a menorah that follows tonight's candle count, with dreidel, latkes, sufganiyot, gelt and window
// scenes, a clock card and a countdown (or greeting) card between them.
//
// Scenes are full-screen .anim files the firmware plays by itself; the shared show runner (lib/ts/busybar/
// showrunner.ts) plays them and draws the cards' live text, one request in flight at a time. What to play is
// picked from the bar's date at the start of every cycle by the pure functions in @shared/hanukkah.
//
// Buttons: OK = next step, encoder = next/previous step, Back = quit,
//          START = holiday mode: preview night 1, 2, ... 8 on any date, then back to following the date.

import { device } from "@shared/device";
import { countPages, nextPreview, playlist } from "@shared/hanukkah";
import { createShow, formatDate, pad2, type Card, type LocalTime, type Step } from "@shared/kit";
import { FONTS, SHOW } from "@shared/generated/show";
import manifest from "./appmeta/manifest.json";

const LAYOUT = SHOW.layout;
const INDEX: Record<string, number> = {};
SHOW.scenes.forEach((s, i) => {
  INDEX[s.name] = i;
});

let preview = 0; // holiday mode: 1-8 previews that night; 0 follows the bar's date

const clock: Card = {
  path: SHOW.cards.clock,
  pages: () => [
    { ms: LAYOUT.time_ms, lines: [{ spec: LAYOUT.time, text: (t: LocalTime) => pad2(t.hour) + ":" + pad2(t.minute) }] },
    { ms: LAYOUT.date_ms, lines: [{ spec: LAYOUT.date, text: formatDate }] },
  ],
};

const count: Card = {
  path: SHOW.cards.count,
  pages: (t) =>
    countPages(t, preview).map(([head, sub]) => ({
      ms: LAYOUT.count_ms,
      lines: [{ spec: LAYOUT.head, text: () => head }, { spec: LAYOUT.sub, text: () => sub }],
    })),
};

function steps(t: LocalTime): Step[] {
  const out: Step[] = [];
  for (const e of playlist(t, preview)) {
    if (e.kind === "card") out.push({ kind: "card", card: e.card });
    else if (e.name in INDEX) out.push({ kind: "scene", scene: INDEX[e.name] });
  }
  return out;
}

function main(): void {
  const show = createShow({
    app: manifest.id,
    device,
    fonts: FONTS,
    scenes: SHOW.scenes,
    cards: { clock, count },
    steps,
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
      preview = nextPreview(preview);
      show.start(); // a new cycle, picked for the previewed night
    }
  });
}

main();
