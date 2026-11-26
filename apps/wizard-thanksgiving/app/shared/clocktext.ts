// Clock card text for this app: re-exports the shared render kit (lib/ts/busybar), docs/DECISIONS.md D10, D15.
// Files outside app/src/ are bundled into main.js, so the build still emits a single script.

export { textBitmap, textWidth } from "../../../../lib/ts/busybar/xpmtext.ts";
export type { Bitmap, Font, TextSpec } from "../../../../lib/ts/busybar/xpmtext.ts";
export { nextMinute, parseWallClock } from "../../../../lib/ts/busybar/walltime.ts";
export type { WallClock } from "../../../../lib/ts/busybar/walltime.ts";
