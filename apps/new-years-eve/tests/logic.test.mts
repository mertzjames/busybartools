// Unit tests for the app's pure logic: phases, year, countdown text, the demo offset, the planner (never overrunning
// midnight) and the live screens. Run: node --experimental-strip-types --test tests/logic.test.mts (Node 24).

import { test } from "node:test";
import assert from "node:assert/strict";

import { addSeconds, parseLocal, type LocalTime } from "../../../lib/ts/busybar/walltime.ts";
import {
  CARD_MS, CELEBRATE_S, FINAL_S, cardText, celebrateState, countdownText, demoOffset, diffSeconds, effectiveAt,
  finalBarPixels, finalText, needsEdgeSync, newYear, phaseAt, planStep, settleDemo,
  type Anchor, type Cursor, type Step,
} from "../app/shared/nye.ts";
import { composeBitmap, odometerLayers, overlayAt, screenAt, type Fonts, type Layout, type Overlay } from "../app/shared/screens.ts";
import { FONTS, LAYOUT, SHOW } from "../app/shared/generated/show.ts";

const L = LAYOUT as unknown as Layout;
const F = FONTS as unknown as Fonts;
const SCENE_MS = SHOW.scenes.map((s) => s.ms);
const T = (iso: string): LocalTime => {
  const t = parseLocal(iso);
  assert.ok(t, iso);
  return t;
};
const iso = (t: LocalTime) =>
  `${t.year}-${String(t.month).padStart(2, "0")}-${String(t.day).padStart(2, "0")}T` +
  `${String(t.hour).padStart(2, "0")}:${String(t.minute).padStart(2, "0")}:${String(t.second).padStart(2, "0")}`;

// ---------------------------------------------------------------------------------------------------------------
test("phases around midnight and the year boundary", () => {
  const cases: [string, string][] = [
    ["2026-12-31T00:00:00", "party"],
    ["2026-12-31T23:58:59", "party"],     // T-61
    ["2026-12-31T23:59:00", "final"],     // T-60
    ["2026-12-31T23:59:49", "final"],     // T-11
    ["2026-12-31T23:59:50", "final10"],   // T-10
    ["2026-12-31T23:59:59", "final10"],   // T-1
    ["2027-01-01T00:00:00", "celebrate"], // 0
    ["2027-01-01T00:00:59", "celebrate"],
    ["2027-01-01T00:01:00", "after"],
    ["2027-01-01T05:59:59", "after"],
    ["2027-01-01T06:00:00", "off"],
    ["2026-12-30T23:59:59", "off"],
    ["2026-11-25T20:15:00", "off"],
    ["2028-12-31T23:59:55", "final10"],   // a leap year's Dec 31
  ];
  for (const [when, phase] of cases) assert.equal(phaseAt(T(when)), phase, when);
});

test("the new year comes from the bar's date", () => {
  assert.equal(newYear(T("2026-12-31T21:00:00")), 2027);
  assert.equal(newYear(T("2026-12-31T23:59:59")), 2027);
  assert.equal(newYear(T("2027-01-01T00:00:00")), 2027);
  assert.equal(newYear(T("2027-01-01T03:00:00")), 2027);
  assert.equal(newYear(T("2027-01-01T07:00:00")), 2028);
  assert.equal(newYear(T("2026-11-25T20:15:00")), 2027);
  assert.equal(newYear(T("2099-12-31T23:00:00")), 2100);
});

test("countdown and final-minute text", () => {
  assert.equal(countdownText(86400), "24:00:00");
  assert.equal(countdownText(86399), "23:59:59");
  assert.equal(countdownText(3600), "01:00:00");
  assert.equal(countdownText(3599), "59:59");
  assert.equal(countdownText(61), "01:01");
  assert.equal(countdownText(0), "00:00");
  assert.equal(finalText(75), "1:15");
  assert.equal(finalText(60), "1:00");
  assert.equal(finalText(59), "59");
  assert.equal(finalText(11), "11");
  assert.equal(finalBarPixels(90, 72), 0);
  assert.equal(finalBarPixels(60, 72), 0);
  assert.equal(finalBarPixels(35, 72), 36);
  assert.equal(finalBarPixels(11, 72), 70);
  assert.equal(finalBarPixels(10, 72), 72);
});

test("card text in every phase", () => {
  assert.deepEqual(cardText(T("2026-12-31T21:45:12")), { main: "02:14:48", top: "TO", bottom: "2027" });
  assert.deepEqual(cardText(T("2026-12-31T23:42:05")), { main: "17:55", top: "TO", bottom: "2027" });
  assert.deepEqual(cardText(T("2026-12-31T23:58:59")), { main: "01:01", top: "TO", bottom: "2027" });
  assert.deepEqual(cardText(T("2027-01-01T00:42:00")), { main: "00:42", top: "HAPPY", bottom: "2027" });
  assert.deepEqual(cardText(T("2026-11-25T20:15:00")), { main: "20:15", top: "37 DAYS", bottom: "TO 2027" });
  assert.deepEqual(cardText(T("2027-01-01T07:00:00")), { main: "07:00", top: "365 DAYS", bottom: "TO 2028" });
  assert.deepEqual(cardText(T("2027-12-30T10:00:00")), { main: "10:00", top: "2 DAYS", bottom: "TO 2028" });
});

test("the app clock: anchor + elapsed ms + demo offset, carrying across the year", () => {
  const anchor: Anchor = { local: T("2026-12-31T23:59:58"), ms: 1000 };
  const n = effectiveAt(anchor, 3500, 0);
  assert.equal(iso(n.t), "2027-01-01T00:00:00");
  assert.equal(n.frac, 500);
  assert.equal(iso(effectiveAt(anchor, 1999, 0).t), "2026-12-31T23:59:58");
  assert.equal(iso(effectiveAt(anchor, 1000, -60).t), "2026-12-31T23:58:58");
  assert.equal(diffSeconds(T("2027-01-01T00:00:01"), T("2026-12-31T23:59:59")), 2);
});

// ---------------------------------------------------------------------------------------------------------------
test("demo mode jumps to T-15 s before the next new year, from any date", () => {
  for (const real of ["2026-11-25T20:15:00", "2026-12-31T23:59:50", "2026-12-31T12:00:00", "2027-01-01T00:00:10",
    "2028-02-29T09:30:00", "2026-01-01T00:00:00"]) {
    const t = T(real);
    const eff = addSeconds(t, demoOffset(t));
    const expectYear = t.year + 1;
    assert.equal(iso(eff), `${expectYear - 1}-12-31T23:59:45`, real);
    assert.equal(phaseAt(eff), "final", real);
    assert.equal(newYear(eff), expectYear, real);
  }
});

test("demo mode stays on through the countdown and celebration, then ends by itself", () => {
  const off = 12345;
  assert.equal(settleDemo(off, T("2026-12-31T23:59:45")), off);
  assert.equal(settleDemo(off, T("2026-12-31T23:59:55")), off);
  assert.equal(settleDemo(off, T("2027-01-01T00:00:30")), off);
  assert.equal(settleDemo(off, T("2027-01-01T00:01:00")), 0);
  assert.equal(settleDemo(0, T("2026-12-31T23:59:45")), 0);
});

// ---------------------------------------------------------------------------------------------------------------
// A simulated run of the app's planner: the same loop main.ts runs, on a fake millisecond clock.
interface Played { step: Step; start: LocalTime; startFrac: number; endMs: number; startMs: number }

function simulate(startIso: string, startFrac: number, untilMs: number, cursor: Cursor = { next: 0, cardDue: false },
  offset = 0, events: { atMs: number; demo?: boolean; skip?: boolean }[] = []): Played[] {
  const anchor: Anchor = { local: T(startIso), ms: -startFrac };
  let ms = 0;
  let off = offset;
  const out: Played[] = [];
  let guard = 0;
  while (ms < untilMs && guard++ < 10000) {
    let n = effectiveAt(anchor, ms, off);
    const settled = settleDemo(off, n.t);
    if (settled !== off) {
      off = settled;
      n = effectiveAt(anchor, ms, off);
    }
    const r = planStep(n.t, n.frac, cursor, SCENE_MS);
    cursor = r.cursor;
    let end = ms + r.step.ms;
    const ev = events.find((e) => e.atMs >= ms && e.atMs < end);
    out.push({ step: r.step, start: n.t, startFrac: n.frac, startMs: ms, endMs: end });
    if (ev) {
      if (ev.demo) off = demoOffset(effectiveAt(anchor, ev.atMs, 0).t);
      end = ev.atMs;
      out[out.length - 1].endMs = end;
      events = events.filter((e) => e !== ev);
    }
    ms = end;
  }
  return out;
}

/** ms from the simulated start to the bar's midnight at the end of `day`. */
function msToMidnight(startIso: string, startFrac: number): number {
  const t = T(startIso);
  return (86400 - (t.hour * 3600 + t.minute * 60 + t.second)) * 1000 - startFrac;
}

test("scenes and cards never overrun T-60 s; the countdown lands exactly on the bar's seconds", () => {
  const starts: string[] = [];
  for (let s = 0; s < 1500; s += 37) starts.push(iso(addSeconds(T("2026-12-31T23:35:00"), s)));
  for (const start of starts) {
    for (const frac of [0, 1, 499, 999]) {
      for (const cardDue of [false, true]) {
        const mid = msToMidnight(start, frac);
        const run = simulate(start, frac, mid + 90000, { next: 3, cardDue });
        for (const p of run) {
          if (p.endMs > mid) break;
          if (p.step.kind === "scene" || p.step.kind === "card") {
            assert.ok(p.endMs <= mid - FINAL_S * 1000, `${start}+${frac}: ${p.step.kind} ends ${mid - p.endMs} ms before midnight`);
          }
        }
        const finalIdx = run.findIndex((p) => p.step.kind === "final");
        assert.ok(finalIdx >= 0, `${start}: no final step`);
        const f = run[finalIdx];
        assert.equal(f.endMs, mid - 10000, `${start}+${frac}: final ends at T-10`);
        assert.ok(mid - f.startMs <= Math.max(...SCENE_MS) + FINAL_S * 1000 + 1000, "final starts no earlier than needed");
        const f10 = run[finalIdx + 1];
        assert.equal(f10.step.kind, "final10");
        assert.equal(f10.endMs, mid);
        const cel = run[finalIdx + 2];
        assert.equal(cel.step.kind, "celebrate");
        assert.equal(cel.endMs, mid + CELEBRATE_S * 1000);
        assert.equal(run[finalIdx + 3].step.kind, "scene", "the party carries on after the celebration");
      }
    }
  }
});

test("a scene that wouldn't finish before T-60 s goes straight to the final minute", () => {
  // 23:58:00 is T-120: a 14 s scene fits (ends T-106). At T-70 nothing fits.
  let r = planStep(T("2026-12-31T23:58:00"), 0, { next: 0, cardDue: false }, [14000]);
  assert.equal(r.step.kind, "scene");
  r = planStep(T("2026-12-31T23:58:50"), 250, { next: 0, cardDue: false }, [14000]);
  assert.deepEqual(r.step, { kind: "final", index: -1, ms: 60000 - 250 });
  // a card is cut to end at T-60 ...
  r = planStep(T("2026-12-31T23:58:56"), 500, { next: 0, cardDue: true }, [14000]);
  assert.deepEqual(r.step, { kind: "card", index: -1, ms: 3500 });
  // ... unless less than 2 s would be left
  r = planStep(T("2026-12-31T23:58:58"), 500, { next: 0, cardDue: true }, [14000]);
  assert.equal(r.step.kind, "final");
  // a full card when there's room
  r = planStep(T("2026-12-31T22:00:00"), 0, { next: 0, cardDue: true }, [14000]);
  assert.deepEqual(r.step, { kind: "card", index: -1, ms: CARD_MS });
});

test("scenes and cards alternate through the playlist, in every phase", () => {
  const run = simulate("2026-11-25T20:00:00", 0, 400000);
  const kinds = run.map((p) => p.step.kind);
  for (let i = 0; i < kinds.length; i++) assert.equal(kinds[i], i % 2 === 0 ? "scene" : "card");
  const order = run.filter((p) => p.step.kind === "scene").map((p) => p.step.index);
  assert.deepEqual(order.slice(0, SCENE_MS.length + 2), [...SCENE_MS.keys(), 0, 1]);
});

test("a full evening: party, final minute, final ten, celebration, after", () => {
  const mid = msToMidnight("2026-12-31T23:40:00", 0);
  const run = simulate("2026-12-31T23:40:00", 0, mid + 10 * 60000);
  const seq = run.map((p) => phaseAt(p.start));
  const firstFinal = run.findIndex((p) => p.step.kind === "final");
  assert.ok(seq.slice(0, firstFinal).every((ph) => ph === "party"));
  assert.deepEqual(run.slice(firstFinal, firstFinal + 3).map((p) => p.step.kind), ["final", "final10", "celebrate"]);
  assert.ok(seq.slice(firstFinal + 3).every((ph) => ph === "after"));
  assert.equal(iso(run[firstFinal + 2].start), "2027-01-01T00:00:00");
});

test("START in November plays the countdown and celebration, then returns to real time", () => {
  const run = simulate("2026-11-25T20:15:00", 300, 200000, { next: 0, cardDue: false }, 0, [{ atMs: 5000, demo: true }]);
  const afterDemo = run.filter((p) => p.startMs >= 5000);
  assert.deepEqual(afterDemo.slice(0, 3).map((p) => p.step.kind), ["final", "final10", "celebrate"]);
  assert.equal(iso(afterDemo[0].start), "2026-12-31T23:59:45");
  assert.equal(afterDemo[0].endMs - afterDemo[0].startMs, 5000 - 300);
  assert.equal(iso(afterDemo[2].start), "2027-01-01T00:00:00");
  // back to the real date (Nov 25, about 20:16:20) once the celebration is over
  const back = afterDemo[3];
  assert.equal(back.step.kind, "scene");
  assert.equal(phaseAt(back.start), "off");
  assert.equal(iso(back.start), "2026-11-25T20:16:20");
});

test("celebration timeline", () => {
  assert.deepEqual(celebrateState(0, 0), { stage: "burst", text: "zero" });
  assert.deepEqual(celebrateState(1, 0), { stage: "burst", text: "none" });
  assert.deepEqual(celebrateState(2, 0), { stage: "burst", text: "none" });
  assert.deepEqual(celebrateState(3, 0), { stage: "loop", text: "greeting" });
  assert.deepEqual(celebrateState(7, 0), { stage: "loop", text: "year" });
  assert.deepEqual(celebrateState(11, 0), { stage: "loop", text: "greeting" });
  // started late (app launched at 00:00:20): no burst
  assert.deepEqual(celebrateState(20, 20), { stage: "loop", text: "greeting" });
  assert.deepEqual(celebrateState(23, 20), { stage: "loop", text: "year" });
  assert.deepEqual(celebrateState(1, 1), { stage: "loop", text: "greeting" });
});

test("edge re-sync gets more frequent near midnight", () => {
  assert.equal(needsEdgeSync(T("2026-11-25T20:00:00"), 300000), false);
  assert.equal(needsEdgeSync(T("2026-11-25T20:00:00"), 700000), true);
  assert.equal(needsEdgeSync(T("2026-12-31T23:50:00"), 150000), true);
  assert.equal(needsEdgeSync(T("2026-12-31T23:50:00"), 60000), false);
});

// ---------------------------------------------------------------------------------------------------------------
function checkBitmap(b: ReturnType<typeof composeBitmap>, label: string): void {
  assert.ok(b, label);
  const lines = b.data.split("\n");
  assert.equal(lines[0], "! XPM2");
  const [w, h, n, cpp] = lines[1].split(" ").map(Number);
  assert.equal(cpp, 1);
  assert.ok(n <= 32, `${label}: ${n} colors`);
  assert.equal(w, b.width);
  assert.equal(h, b.height);
  assert.ok(b.x >= 0 && b.y >= 0 && b.x + w <= 72 && b.y + h <= 16, `${label}: fits 72x16`);
  assert.equal(lines.length, 2 + n + h);
  for (const row of lines.slice(2 + n)) assert.equal(row.length, w);
}

test("every live screen fits the display and the 32-color limit", () => {
  const start = T("2026-12-31T23:57:30");
  for (let s = 0; s < 300; s++) {
    const t = addSeconds(start, s);
    const ph = phaseAt(t);
    const kind = ph === "party" ? "card" : ph === "after" ? "card" : ph;
    const sc = screenAt(kind as Step["kind"], t, 0, L, F);
    checkBitmap(composeBitmap(sc.layers, F) ?? { data: "! XPM2\n1 1 1 1\n. c none\n.", width: 1, height: 1, x: 0, y: 0 }, iso(t));
  }
  for (const when of ["2026-12-31T00:00:00", "2026-12-31T13:33:38", "2026-11-25T20:15:00", "2027-01-01T07:00:00"]) {
    checkBitmap(composeBitmap(screenAt("card", T(when), 0, L, F).layers, F), when);
  }
});

test("live screens pick the right backdrop", () => {
  assert.equal(screenAt("final", T("2026-12-31T23:59:29"), 0, L, F).stage, "final");
  assert.equal(screenAt("final", T("2026-12-31T23:59:30"), 0, L, F).stage, "final_fast");
  assert.equal(screenAt("final", T("2026-12-31T23:58:50"), 0, L, F).stage, "final"); // pre-roll
  assert.equal(screenAt("final", T("2026-12-31T23:59:50"), 0, L, F).stage, "final10"); // late tick
  assert.equal(screenAt("final10", T("2026-12-31T23:59:55"), 0, L, F).stage, "final10");
  assert.deepEqual(screenAt("celebrate", T("2027-01-01T00:00:00"), 0, L, F).stage, "burst");
  assert.deepEqual(screenAt("celebrate", T("2027-01-01T00:00:05"), 0, L, F).stage, "fireworks");
  assert.equal(screenAt("celebrate", T("2027-01-01T00:01:00"), 0, L, F).stage, "card"); // late tick
  assert.equal(screenAt("card", T("2026-12-31T23:59:30"), 0, L, F).stage, "card");
});

test("final ten shows one digit per second, and 0 at midnight", () => {
  for (let r = 10; r >= 1; r--) {
    const t = addSeconds(T("2027-01-01T00:00:00"), -r);
    const layers = screenAt("final10", t, 0, L, F).layers;
    assert.equal(layers.length, 1);
    assert.equal((layers[0] as { text: string }).text, String(r));
  }
  const zero = screenAt("celebrate", T("2027-01-01T00:00:00"), 0, L, F).layers;
  assert.equal((zero[0] as { text: string }).text, "0");
  for (const d of "0123456789") assert.ok(F.huge.glyphs[d], `huge ${d}`);
});

test("odometer rolls only the digits that change", () => {
  const a = odometerLayers(2026, 2027, 0, L, F).map((l) => (l as { text: string }).text).join("");
  const b = odometerLayers(2026, 2027, 1, L, F).map((l) => (l as { text: string }).text).join("");
  const mid = odometerLayers(2029, 2030, 0.5, L, F).map((l) => (l as { text: string }).text).join("");
  assert.equal(a, "2026");
  assert.equal(b, "2027");
  assert.equal(mid, "202390"); // "2", "0" stay; "2"->"3" and "9"->"0" are both mid-roll
  const scene = SHOW.scenes.find((s) => "overlay" in s) as unknown as { overlay: Overlay };
  assert.equal(overlayAt(scene.overlay, 0, T("2026-12-31T22:00:00"), L, F), null);
  assert.ok(overlayAt(scene.overlay, 900, T("2026-12-31T22:00:00"), L, F));
});
