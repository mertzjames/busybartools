// App settings (shared render kit).
//
// A BUSY app can ship `app/src/appmeta/settings.json` (fields of type enum, boolean, integer, string, color, time,
// geolocation, group). The firmware shows them under Apps → <app> → Setup on the bar (enum, boolean and integer can be
// edited there; the others only in the bar's web interface) and the app reads them with `AppsSettingsGet` when it
// starts. Changes apply the next time the app starts.
//
//   const s = await loadSettings(device, manifest.id, SETTINGS_VERSION, { sundown: "auto", location: null });
//
// loadSettings never throws: a failed request, an old settings version or a value of the wrong type falls back to the
// default, so the show always runs.

import type { GeoPoint } from "./sun.ts";

export interface SettingsDevice {
  AppsSettingsGet(params: { app_id: string }): Promise<{ version: number; values: { [key: string]: unknown } }>;
}

/**
 * Reads the app's settings. Each key of `defaults` takes the stored value when it has the default's type (for a
 * default of null, any stored value is passed through for a parser such as readGeolocation); otherwise the default.
 */
export async function loadSettings<T extends Record<string, unknown>>(
  device: SettingsDevice, appId: string, version: number, defaults: T, report?: (err: unknown) => void,
): Promise<T> {
  const out = { ...defaults };
  try {
    const doc = await device.AppsSettingsGet({ app_id: appId });
    if (!doc || doc.version !== version || typeof doc.values !== "object" || doc.values === null) return out;
    for (const key of Object.keys(defaults) as (keyof T & string)[]) {
      const v = doc.values[key];
      const d = defaults[key];
      if (v === undefined) continue;
      if (d === null || typeof v === typeof d) out[key] = v as T[typeof key];
    }
  } catch (err) {
    if (report) report(err);
  }
  return out;
}

/** An enum setting's value if it is one of `options`, else `fallback`. */
export function enumValue<O extends string>(v: unknown, options: readonly O[], fallback: O): O {
  return typeof v === "string" && (options as readonly string[]).includes(v) ? (v as O) : fallback;
}

/**
 * A geolocation setting's coordinates, when it has them. The firmware's value is `{ mode, name, lat?, lon? }`:
 * "fixed" always carries lat/lon; "auto" may or may not, depending on whether the bar knows where it is.
 */
export function readGeolocation(v: unknown): (GeoPoint & { name?: string }) | null {
  if (!v || typeof v !== "object") return null;
  const o = v as { lat?: unknown; lon?: unknown; name?: unknown };
  if (typeof o.lat !== "number" || typeof o.lon !== "number") return null;
  if (!isFinite(o.lat) || !isFinite(o.lon) || Math.abs(o.lat) > 90 || Math.abs(o.lon) > 180) return null;
  if (o.lat === 0 && o.lon === 0) return null; // "unset" placeholders
  return { lat: o.lat, lon: o.lon, name: typeof o.name === "string" ? o.name : undefined };
}
