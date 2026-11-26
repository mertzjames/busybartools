// Wizard Thanksgiving: plays the pre-rendered scenes in order, with a clock/date card after each one.
//
// Scenes are full-screen .anim files the firmware plays by itself (docs/DECISIONS.md D2), so the app
// only sends one draw per scene plus a handful for each clock card. One request is in flight at a time.
//
// Buttons: OK = skip to the next step, encoder = next/previous step, Back = quit.

import { device } from "@shared/device";
import { nextMinute, parseWallClock, textBitmap, type Font, type TextSpec } from "@shared/clocktext";
import manifest from "./appmeta/manifest.json";
import { FONTS, SHOW } from "@shared/generated/show";

const APP = manifest.id;
const PRIORITY = 50;
const FADE_STEPS = [34, 67, 100];
const FADE_STEP_MS = 150;

type Step = { kind: "scene"; i: number } | { kind: "clock" };
type Element = Parameters<typeof device.DisplayDraw>[0]["elements"][number];

const STEPS: Step[] = [];
for (let i = 0; i < SHOW.scenes.length; i++) {
  STEPS.push({ kind: "scene", i });
  STEPS.push({ kind: "clock" });
}

const report = (err: unknown) => console.error(`${APP}: ${err instanceof Error ? err.message : String(err)}`);

function main(): void {
  let stepIndex = 0;
  let stopped = false;
  let token = 0; // bumps on every step change so stale timers and responses do nothing
  let timers: ReturnType<typeof setTimeout>[] = [];
  let textOnScreen = false;

  // --- one request at a time; a newer draw for the same slot replaces an unsent one ---
  let busy = false;
  const queue: { slot: string; run: () => Promise<unknown> }[] = [];
  function send(slot: string, run: () => Promise<unknown>): void {
    const existing = queue.findIndex((q) => q.slot === slot);
    if (existing >= 0) queue.splice(existing, 1);
    queue.push({ slot, run });
    void pump();
  }
  async function pump(): Promise<void> {
    if (busy) return;
    busy = true;
    while (queue.length && !stopped) {
      const job = queue.shift()!;
      try {
        await job.run();
      } catch (err) {
        report(err);
      }
    }
    busy = false;
  }
  const draw = (slot: string, elements: Element[]) =>
    send(slot, () => device.DisplayDraw({ application_name: APP, priority: PRIORITY, elements }));

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

  function stage(path: string, loop: boolean): Element {
    return { id: "stage", type: "animation", path, x: 0, y: 0, loop, z_index: 1 };
  }

  function showText(text: string, fontName: string, spec: TextSpec): void {
    const bmp = textBitmap(text, FONTS[fontName] as Font, spec);
    FADE_STEPS.forEach((opacity, k) => {
      later(k * FADE_STEP_MS, () => {
        draw("text", [{
          id: "text", type: "xpmbitmap", data: bmp.data, x: bmp.x, y: bmp.y, opacity, z_index: 2,
        } as Element]);
      });
    });
    textOnScreen = true;
  }

  function playScene(i: number): void {
    const scene = SHOW.scenes[i];
    draw("stage", [stage(scene.path, false)]);
    if (textOnScreen) {
      send("clear-text", () => device.DisplayClear({ application_name: APP, element_ids: ["text"] }));
      textOnScreen = false;
    }
    later(scene.ms, advance);
  }

  function playClock(): void {
    const clock = SHOW.clock;
    const mine = token;
    draw("stage", [stage(clock.path, true)]);
    send("time", async () => {
      const info = await device.TimeGet();
      if (mine !== token || stopped) return;
      const wall = parseWallClock(info.timestamp);
      if (!wall) throw new Error(`unexpected timestamp ${info.timestamp}`);
      showText(wall.hhmm, clock.time.font, clock.time);
      // minute rolls over while the time is showing: update it in place
      if (wall.msToNextMinute < clock.time_ms) {
        later(wall.msToNextMinute, () => showText(nextMinute(wall.hhmm), clock.time.font, clock.time));
      }
      later(clock.time_ms, () => showText(wall.date, clock.date.font, clock.date));
    });
    later(clock.time_ms + clock.date_ms, advance);
  }

  function go(index: number): void {
    token++;
    clearTimers();
    stepIndex = (index + STEPS.length) % STEPS.length;
    const step = STEPS[stepIndex];
    if (step.kind === "scene") playScene(step.i);
    else playClock();
  }
  function advance(): void {
    go(stepIndex + 1);
  }

  go(0);

  const unbind = listen("input", (event) => {
    if (stopped) return;
    if (event.key === "encoder") {
      go(stepIndex + event.delta);
      return;
    }
    if (event.action !== "short") return;
    if (event.key === "ok") {
      advance();
      return;
    }
    if (event.key !== "back") return;

    stopped = true;
    token++;
    clearTimers();
    queue.length = 0;
    void device.DisplayClear({ application_name: APP }).catch(report);
    // The listener is the last handle: unbind after this callback returns.
    setTimeout(unbind, 0);
  });
}

main();
