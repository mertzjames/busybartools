// New Year's Eve: party scenes and countdown cards until the final minute, a final-minute screen, huge digits for
// the last ten seconds, then fireworks and HAPPY NEW YEAR. Everything is timed by the bar's own local clock.
//
// The phase logic and the live screens are pure functions in app/shared/nye.ts and screens.ts (unit-tested, and run
// by the mockup too). This file only keeps the clock in sync, runs timers and sends draws, one request at a time.
//
// Buttons: OK = skip the current scene or card, START = demo (jump to 15 s before midnight), Back = quit.

import { device } from "@shared/device";
import { createDrawQueue, parseLocal, type LocalTime } from "@shared/kit";
import {
  demoOffset, diffSeconds, effectiveAt, needsEdgeSync, planStep, secondsSinceMidnight, settleDemo,
  type Anchor, type Cursor, type Now, type Step, type StepKind,
} from "@shared/nye";
import { composeBitmap, overlayAt, screenAt, type Fonts, type Layer, type Layout, type Overlay } from "@shared/screens";
import { FONTS, LAYOUT, SHOW } from "@shared/generated/show";
import manifest from "./appmeta/manifest.json";

const APP = manifest.id;
const PRIORITY = 50;
const L = LAYOUT as unknown as Layout;
const F = FONTS as Fonts;
const SCENE_MS: number[] = SHOW.scenes.map((s) => s.ms);
/** Ticks land this long after a second boundary, so the clock has surely moved on. */
const TICK_LATE_MS = 30;

type Element = Parameters<typeof device.DisplayDraw>[0]["elements"][number];

const report = (err: unknown) => console.error(`${APP}: ${err instanceof Error ? err.message : String(err)}`);
const sleep = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms));

function main(): void {
  const queue = createDrawQueue(report);
  let stopped = false;
  let token = 0; // bumps on every step change so stale timers do nothing
  let timers: ReturnType<typeof setTimeout>[] = [];
  let anchor: Anchor | null = null;
  let lastEdgeSync = 0;
  let current: StepKind = "card";
  let offset = 0; // demo offset in seconds
  let cursor: Cursor = { next: 0, cardDue: false };
  let shownStage = "";
  let shownText = "";

  function later(ms: number, fn: () => void): void {
    const mine = token;
    timers.push(setTimeout(() => {
      if (mine === token && !stopped) fn();
    }, Math.max(0, ms)));
  }
  function clearTimers(): void {
    for (const t of timers) clearTimeout(t);
    timers = [];
  }

  // --- drawing: one request in flight; a newer draw for the same slot replaces an unsent one ---
  function setStage(path: string, loop: boolean): void {
    shownStage = path;
    const el = { id: "stage", type: "animation", path, x: 0, y: 0, loop, z_index: 1 } as Element;
    queue.send("stage", () => device.DisplayDraw({ application_name: APP, priority: PRIORITY, elements: [el] }));
  }
  function setText(layers: Layer[] | null): void {
    const bmp = layers ? composeBitmap(layers, F) : null;
    const key = bmp ? `${bmp.x},${bmp.y},${bmp.data}` : "";
    if (key === shownText) return;
    shownText = key;
    if (!bmp) {
      queue.send("text", () => device.DisplayClear({ application_name: APP, element_ids: ["text"] }));
      return;
    }
    const el = { id: "text", type: "xpmbitmap", data: bmp.data, x: bmp.x, y: bmp.y, z_index: 2 } as Element;
    queue.send("text", () => device.DisplayDraw({ application_name: APP, priority: PRIORITY, elements: [el] }));
  }

  // --- the bar's clock ---
  async function readBar(): Promise<{ t: LocalTime; mid: number }> {
    const sent = Date.now();
    const info = await device.TimeGet();
    const t = parseLocal(info.timestamp);
    if (!t) throw new Error(`unexpected timestamp ${info.timestamp}`);
    return { t, mid: (sent + Date.now()) / 2 };
  }
  /** Polls /api/time until the second changes, to find where the bar's seconds begin. */
  async function syncEdge(): Promise<void> {
    let prev = await readBar();
    for (let i = 0; i < 30 && !stopped; i++) {
      await sleep(40);
      const cur = await readBar();
      if (diffSeconds(cur.t, prev.t) !== 0) {
        anchor = { local: cur.t, ms: Math.round((prev.mid + cur.mid) / 2) };
        lastEdgeSync = Date.now();
        return;
      }
      prev = cur;
    }
    anchor = { local: prev.t, ms: Math.round(prev.mid - 500) };
  }
  /** One cheap read; re-measure the edge only if the clock has drifted or jumped by more than a second. */
  async function checkSync(): Promise<void> {
    const cur = await readBar();
    const predicted = anchor ? effectiveAt(anchor, cur.mid, 0).t : null;
    const drifted = !predicted || Math.abs(diffSeconds(cur.t, predicted)) > 1;
    if (drifted || needsEdgeSync(effectiveAt(anchor!, cur.mid, offset).t, Date.now() - lastEdgeSync)) {
      await syncEdge();
    }
  }
  function now(): Now {
    return effectiveAt(anchor!, Date.now(), offset);
  }

  // --- steps ---
  function plan(): void {
    if (stopped || !anchor) return;
    token++;
    clearTimers();
    let n = now();
    const settled = settleDemo(offset, n.t);
    if (settled !== offset) {
      offset = settled;
      n = now();
    }
    const next = planStep(n.t, n.frac, cursor, SCENE_MS);
    cursor = next.cursor;
    current = next.step.kind;
    if (next.step.kind === "scene") playScene(next.step.index);
    else playLive(next.step, n);
    later(next.step.ms, plan);
  }

  function playScene(i: number): void {
    const scene = SHOW.scenes[i];
    setStage(scene.path, false);
    setText(null);
    const overlay = (scene as { overlay?: Overlay }).overlay;
    if (overlay) {
      for (const e of overlay.events) later(e[0], () => setText(overlayAt(overlay, e[0], now().t, L, F)));
    }
  }

  function playLive(step: Step, n: Now): void {
    const startedAt = secondsSinceMidnight(n.t);
    const tick = () => {
      const cur = now();
      const screen = screenAt(step.kind, cur.t, startedAt, L, F);
      const bg = SHOW.bg[screen.stage];
      if (bg.path !== shownStage) setStage(bg.path, screen.loop);
      setText(screen.layers);
      later(1000 - cur.frac + TICK_LATE_MS, tick);
    };
    tick();
    if (step.kind === "card") queue.send("sync", checkSync); // after the first tick, so the card shows at once
  }

  // Start: show the card backdrop at once, then find the bar's second boundary and begin.
  setStage(SHOW.bg.card.path, true);
  const start = () => queue.send("sync", async () => {
    try {
      await syncEdge();
    } catch (err) {
      report(err);
      if (!stopped) timers.push(setTimeout(start, 2000));
      return;
    }
    plan();
  });
  start();

  const unbind = listen("input", (event) => {
    if (stopped || event.key === "encoder" || event.action !== "short") return;
    if (event.key === "start" && anchor) {
      offset = demoOffset(effectiveAt(anchor, Date.now(), 0).t);
      plan();
      return;
    }
    if (event.key === "ok") {
      // only scenes and cards can be skipped; the countdown and the celebration follow the clock
      if (current === "scene" || current === "card") plan();
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
