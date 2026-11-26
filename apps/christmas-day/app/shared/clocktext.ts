// Clock card text and drawing helpers for this app: re-exports the shared render kit (lib/ts/busybar).
// Files outside app/src/ are bundled into main.js, so the build still emits a single script (docs/DECISIONS.md D8).

export { textBitmap, textWidth } from "../../../../lib/ts/busybar/xpmtext.ts";
export type { Bitmap, Font, TextSpec } from "../../../../lib/ts/busybar/xpmtext.ts";
export { nextMinute, parseWallClock } from "../../../../lib/ts/busybar/walltime.ts";
export type { WallClock } from "../../../../lib/ts/busybar/walltime.ts";
export { createDrawQueue } from "../../../../lib/ts/busybar/drawqueue.ts";
export type { DrawQueue } from "../../../../lib/ts/busybar/drawqueue.ts";
