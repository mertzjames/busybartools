// One-request-in-flight draw queue (shared render kit).
//
// Every draw is an HTTP request the bar's web server handles one at a time. Queue work by "slot": a newer job
// for the same slot replaces an unsent one (e.g. three opacity steps of a fade collapse to the latest), and
// jobs for different slots run in order. One failed request is reported and never stops the queue.
//
//   const q = createDrawQueue((err) => console.error(`${APP}: ${err}`));
//   q.send("stage", () => device.DisplayDraw({ application_name: APP, priority: 50, elements: [...] }));
//   q.stop();   // on quit: drop pending work

export interface DrawQueue {
  send(slot: string, run: () => Promise<unknown>): void;
  stop(): void;
  readonly pending: number;
}

export function createDrawQueue(report: (err: unknown) => void): DrawQueue {
  let busy = false;
  let stopped = false;
  const queue: { slot: string; run: () => Promise<unknown> }[] = [];

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

  return {
    send(slot, run) {
      if (stopped) return;
      const existing = queue.findIndex((q) => q.slot === slot);
      if (existing >= 0) queue.splice(existing, 1);
      queue.push({ slot, run });
      void pump();
    },
    stop() {
      stopped = true;
      queue.length = 0;
    },
    get pending() {
      return queue.length;
    },
  };
}
