// Scene-and-card show runner (shared render kit).
//
// The playback loop every scene-based app had its own copy of: play full-screen .anim scenes (the firmware runs
// them by itself) and, between them, "cards": a looping backdrop .anim with live pixel-font text drawn from the
// bar's clock (the time, the date, a countdown, a greeting). One draw request is in flight at a time (drawqueue).
//
//   const show = createShow({ app: manifest.id, device, fonts: FONTS, scenes: SHOW.scenes, cards: { clock: CLOCK } });
//   show.start();
//   const unbind = listen("input", (e) => { if (show.input(e) === "quit") setTimeout(unbind, 0); });
//
// A card's pages are computed from the bar's time when the card starts; each line's text is recomputed at the start
// of its page and again whenever the minute rolls over during it (only changed lines are redrawn). `steps(t)` picks
// the playlist again at the start of every cycle, so a show can change with the date (Hanukkah's candles, a
// countdown that becomes a greeting on the day).
//
// Buttons: OK = next step, encoder = next/previous step, Back = quit (clears the display). Other keys are returned
// as "ignored" for the app to handle.

import { createDrawQueue } from "./drawqueue.ts";
import { addSeconds, parseLocal, type LocalTime } from "./walltime.ts";
import { textBitmap, type Font, type TextSpec } from "./xpmtext.ts";

/** The subset of the BusyBar client the runner uses (structural, so lib/ needs no npm dependency). */
export interface ShowDevice {
  DisplayDraw(params: { application_name: string; priority: number; elements: ShowElement[] }): Promise<unknown>;
  DisplayClear(params: { application_name: string; element_ids?: string[] }): Promise<unknown>;
  TimeGet(): Promise<{ timestamp: string }>;
}

/** The two draw elements the runner sends (a subset of the firmware's DisplayElement). */
export type ShowElement =
  | { id: string; type: "animation"; path: string; x: number; y: number; loop: boolean; z_index: number }
  | { id: string; type: "xpmbitmap"; data: string; x: number; y: number; opacity: number; z_index: number };

export interface ShowInput {
  readonly key: string;
  readonly action: string;
  readonly delta?: number;
}

export interface Scene {
  path: string;
  ms: number;
}

/** One line of live text. `x` overrides centering. Empty text draws nothing. */
export interface Line {
  spec: TextSpec;
  text: (t: LocalTime) => string;
  x?: number;
}

export interface Page {
  ms: number;
  lines: Line[];
}

export interface Card {
  /** Backdrop animation, looped while the card shows. */
  path: string;
  pages: (t: LocalTime) => Page[];
}

export type Step = { kind: "scene"; scene: number } | { kind: "card"; card: string };

export interface ShowOptions {
  app: string;
  device: ShowDevice;
  fonts: Record<string, Font>;
  scenes: readonly Scene[];
  cards: Record<string, Card>;
  /** The playlist for one cycle. Default: every scene in order, each followed by the "clock" card. */
  steps?: (t: LocalTime) => Step[];
  priority?: number;
  report?: (err: unknown) => void;
  /** Fade-in opacity steps for text and their spacing (ms). */
  fade?: readonly number[];
  fadeStepMs?: number;
}

export interface Show {
  start(): void;
  /** Handles a device input event: "quit" after Back (the app should unbind), "ignored" for keys it doesn't use. */
  input(event: ShowInput): "handled" | "ignored" | "quit";
  /** Jumps to step `index` of the current cycle. */
  go(index: number): void;
  stop(): void;
  readonly steps: readonly Step[];
  readonly index: number;
}

export function defaultSteps(scenes: number): Step[] {
  const out: Step[] = [];
  for (let i = 0; i < scenes; i++) out.push({ kind: "scene", scene: i }, { kind: "card", card: "clock" });
  return out;
}

const MAX_LINES = 4;

export function createShow(opts: ShowOptions): Show {
  const APP = opts.app;
  const priority = opts.priority ?? 50;
  const fade = opts.fade ?? [34, 67, 100];
  const fadeStepMs = opts.fadeStepMs ?? 150;
  const report = opts.report ?? ((err: unknown) => console.error(`${APP}: ${err instanceof Error ? err.message : String(err)}`));
  const pickSteps = opts.steps ?? (() => defaultSteps(opts.scenes.length));

  let steps: Step[] = defaultSteps(opts.scenes.length);
  let index = 0;
  let stopped = false;
  let token = 0; // bumps on every step change so stale timers and responses do nothing
  let timers: ReturnType<typeof setTimeout>[] = [];
  let drawn: string[] = []; // text element ids on screen
  const shown: string[] = []; // text per line slot, to skip redraws that change nothing

  const queue = createDrawQueue(report);
  const draw = (slot: string, elements: ShowElement[]) =>
    queue.send(slot, () => opts.device.DisplayDraw({ application_name: APP, priority, elements }));

  function later(ms: number, fn: () => void): void {
    const mine = token;
    timers.push(setTimeout(() => {
      if (mine === token && !stopped) fn();
    }, ms));
  }
  function clearTimers(): void {
    for (const t of timers) clearTimeout(t);
    timers = [];
  }

  async function now(): Promise<LocalTime> {
    const info = await opts.device.TimeGet();
    const t = parseLocal(info.timestamp);
    if (!t) throw new Error(`unexpected timestamp ${info.timestamp}`);
    return t;
  }

  function stage(path: string, loop: boolean): ShowElement {
    return { id: "stage", type: "animation", path, x: 0, y: 0, loop, z_index: 1 };
  }

  function clearIds(ids: string[]): void {
    const gone = drawn.filter((id) => ids.includes(id));
    if (!gone.length) return;
    drawn = drawn.filter((id) => !gone.includes(id));
    for (const id of gone) shown[Number(id.slice(4))] = "";
    // a unique slot per clear, so a later clear never replaces an unsent one
    queue.send("clear:" + gone.join(","), () => opts.device.DisplayClear({ application_name: APP, element_ids: gone }));
  }
  /** Clears text slots >= keep. */
  function clearText(keep: number): void {
    clearIds(drawn.filter((id) => Number(id.slice(4)) >= keep));
  }

  function drawLine(slot: number, line: Line, t: LocalTime, fadeIn: boolean): void {
    const text = line.text(t);
    const id = "text" + slot;
    if (!fadeIn && text === shown[slot]) return;
    shown[slot] = text;
    if (!text) {
      clearIds([id]);
      return;
    }
    const font = opts.fonts[line.spec.font];
    if (!font) throw new Error(`no font ${line.spec.font}`);
    const bmp = textBitmap(text, font, line.spec, line.x);
    const steps = fadeIn ? fade : [100];
    steps.forEach((opacity, k) => {
      later(k * fadeStepMs, () => draw(id, [{
        id, type: "xpmbitmap", data: bmp.data, x: bmp.x, y: bmp.y, opacity, z_index: 2 + slot,
      }]));
    });
    if (!drawn.includes(id)) drawn.push(id);
  }

  function playScene(i: number): void {
    const scene = opts.scenes[i];
    draw("stage", [stage(scene.path, false)]);
    clearText(0);
    later(scene.ms, advance);
  }

  function playCard(name: string): void {
    const card = opts.cards[name];
    if (!card) throw new Error(`no card ${name}`);
    const mine = token;
    draw("stage", [stage(card.path, true)]);
    clearText(0);
    queue.send("time", async () => {
      const t0 = await now();
      if (mine !== token || stopped) return;
      const pages = card.pages(t0);
      let at = 0;
      for (const page of pages) {
        const start = at;
        const lines = page.lines.slice(0, MAX_LINES);
        later(start, () => {
          clearText(lines.length);
          const t = addSeconds(t0, Math.floor(start / 1000));
          lines.forEach((line, k) => drawLine(k, line, t, true));
        });
        // minute rollovers during this page: recompute every line, redraw the ones that changed
        const msToMinute = (60 - t0.second) * 1000;
        for (let m = msToMinute; m < start + page.ms; m += 60000) {
          if (m <= start) continue;
          later(m, () => {
            const t = addSeconds(t0, Math.round(m / 1000));
            lines.forEach((line, k) => drawLine(k, line, t, false));
          });
        }
        at += page.ms;
      }
      later(Math.max(at, 1000), advance);
    });
  }

  function go(i: number): void {
    token++;
    clearTimers();
    index = ((i % steps.length) + steps.length) % steps.length;
    const step = steps[index];
    if (step.kind === "scene") playScene(step.scene);
    else playCard(step.card);
  }

  function advance(): void {
    if (index + 1 < steps.length) {
      go(index + 1);
      return;
    }
    newCycle();
  }

  // re-pick the playlist from the bar's date, then start it from the top
  function newCycle(): void {
    token++;
    clearTimers();
    const mine = token;
    queue.send("cycle", async () => {
      try {
        const t = await now();
        if (mine !== token || stopped) return;
        const next = pickSteps(t);
        if (next.length) steps = next;
      } catch (err) {
        report(err); // keep the previous playlist; never stop the show over one failed request
      }
      if (mine === token && !stopped) go(0);
    });
  }

  function stop(): void {
    if (stopped) return;
    stopped = true;
    token++;
    clearTimers();
    queue.stop();
    void opts.device.DisplayClear({ application_name: APP }).catch(report);
  }

  return {
    start: newCycle,
    go,
    stop,
    input(event: ShowInput) {
      if (stopped) return "ignored";
      if (event.key === "encoder") {
        go(index + (event.delta ?? 0));
        return "handled";
      }
      if (event.action !== "short") return "ignored";
      if (event.key === "ok") {
        advance();
        return "handled";
      }
      if (event.key === "back") {
        stop();
        return "quit";
      }
      return "ignored";
    },
    get steps() {
      return steps;
    },
    get index() {
      return index;
    },
  };
}
