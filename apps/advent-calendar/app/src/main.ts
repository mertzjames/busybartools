// Advent Calendar: every pass opens today's door, plays today's vignette, then shows a live countdown card.
//
// Vignettes are full-screen .anim files the firmware plays by itself, so the app sends one draw per scene plus a
// few xpmbitmap text draws per card (docs/DECISIONS.md D3, D4). The bar's /api/time decides the day and the
// countdown; what to show is computed by the pure functions in @shared/advent.
//
// Buttons: encoder = browse the days already opened, OK = back to today, Back = quit.

import { device } from "@shared/device";
import { browse, cardLines, cycleSteps, dateLabel, msUntilCardChange, type Line, type Step } from "@shared/advent";
import { addSeconds, createDrawQueue, parseLocal, textBitmap, type Font, type LocalTime } from "@shared/kit";
import { FONTS, SHOW } from "@shared/generated/show";
import manifest from "./appmeta/manifest.json";

const APP = manifest.id;
const PRIORITY = 50;
const FADE_STEPS = [34, 67, 100];
const FADE_STEP_MS = 150;
const TEXT_IDS = ["t0", "t1"];

type Element = Parameters<typeof device.DisplayDraw>[0]["elements"][number];

const report = (err: unknown) => console.error(`${APP}: ${err instanceof Error ? err.message : String(err)}`);

function main(): void {
  let stopped = false;
  let token = 0; // bumps on every restart, so stale timers and responses do nothing
  let timers: ReturnType<typeof setTimeout>[] = [];
  let textOnScreen = false;
  let view: number | null = null; // browsed day, or null to follow today
  let now: LocalTime | null = null; // the last time read from the bar

  const queue = createDrawQueue(report);
  const draw = (slot: string, elements: Element[]) =>
    queue.send(slot, () => device.DisplayDraw({ application_name: APP, priority: PRIORITY, elements }));

  function later(ms: number, fn: () => void): void {
    const mine = token;
    timers.push(
      setTimeout(() => {
        if (mine === token && !stopped) fn();
      }, ms),
    );
  }
  function clearTimers(): void {
    for (const t of timers) clearTimeout(t);
    timers = [];
  }

  /** Reads the bar's local time, then runs `fn` with it unless the show moved on meanwhile. */
  function withTime(fn: (t: LocalTime) => void): void {
    const mine = token;
    queue.send("time", async () => {
      const info = await device.TimeGet();
      if (mine !== token || stopped) return;
      const t = parseLocal(info.timestamp);
      if (!t) throw new Error(`unexpected timestamp ${info.timestamp}`);
      now = t;
      fn(t);
    });
  }

  function stage(path: string, loop: boolean): void {
    draw("stage", [{ id: "stage", type: "animation", path, x: 0, y: 0, loop, z_index: 1 }]);
  }

  function clearText(): void {
    if (!textOnScreen) return;
    queue.send("clear-text", () => device.DisplayClear({ application_name: APP, element_ids: TEXT_IDS }));
    textOnScreen = false;
  }

  /** Draws up to two lines of live text, fading in with three opacity steps. */
  function showLines(lines: Line[], fade: boolean): void {
    const bitmaps = lines.map((line) => {
      const spec = SHOW.styles[line.style];
      return textBitmap(line.text, FONTS[spec.font] as Font, spec);
    });
    const steps = fade ? FADE_STEPS : [100];
    steps.forEach((opacity, k) => {
      later(k * FADE_STEP_MS, () => {
        draw("text", bitmaps.map((b, i) => ({
          id: TEXT_IDS[i], type: "xpmbitmap", data: b.data, x: b.x, y: b.y, opacity, z_index: 2,
        }) as Element));
      });
    });
    textOnScreen = true;
  }

  function playStep(steps: Step[], i: number): void {
    if (i >= steps.length) {
      cycle();
      return;
    }
    const step = steps[i];
    const next = () => playStep(steps, i + 1);
    if (step.kind === "door") {
      clearText();
      stage(SHOW.door.path, false);
      later(SHOW.door.text_ms, () => showLines([{ text: dateLabel(step.day), style: "date" }], true));
      later(SHOW.door.ms, next);
    } else if (step.kind === "scene") {
      const scene = step.day === 0 ? SHOW.winter : SHOW.days[step.day - 1];
      stage(scene.path, false);
      clearText();
      later(scene.ms, next);
    } else {
      stage(SHOW.card.path, true);
      withTime((t) => {
        showLines(cardLines(t), true);
        // the countdown ticks over while the card is up (a minute on Christmas Eve): redraw it in place
        const change = msUntilCardChange(t);
        if (change < SHOW.card.ms) later(change, () => showLines(cardLines(addSeconds(t, change / 1000)), false));
      });
      later(SHOW.card.ms, next);
    }
  }

  /** One pass of the show, planned from a fresh reading of the bar's clock. */
  function cycle(): void {
    withTime((t) => playStep(cycleSteps(t, view), 0));
  }

  function restart(): void {
    token++;
    clearTimers();
    cycle();
  }

  restart();

  const unbind = listen("input", (event) => {
    if (stopped) return;
    if (event.key === "encoder") {
      if (!now) return;
      const next = browse(now, view, event.delta);
      if (next === view) return;
      view = next;
      restart();
      return;
    }
    if (event.action !== "short") return;
    if (event.key === "ok") {
      view = null;
      restart();
      return;
    }
    if (event.key !== "back") return;

    stopped = true;
    token++;
    clearTimers();
    queue.stop();
    void device.DisplayClear({ application_name: APP }).catch(report);
    // The listener is the last handle: unbind after this callback returns.
    setTimeout(unbind, 0);
  });
}

main();
