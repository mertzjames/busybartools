// Sunrise and sunset (shared render kit), for apps whose show follows the sun: Hanukkah candles at sundown,
// fireworks at dusk.
//
// The NOAA "general solar position" approximation, accurate to a minute or two at mid latitudes, which is far finer
// than an LED show needs. Times are minutes after local midnight in the bar's own UTC offset.
//
// Where is the bar? Prefer a location the user set (the app's `geolocation` setting, settings.ts). Without one,
// `locationFromOffset` estimates it from the UTC offset in the bar's timestamp: the time zone's meridian
// (15° per hour) at a mid-US latitude. That is usually within half an hour of the true sunset. Daylight saving moves
// the offset by an hour, so pass `dst: true` when the date is in daylight time (US: mid-March to early November).

import { weekday } from "./walltime.ts";

export interface GeoPoint {
  /** Degrees north (negative south). */
  lat: number;
  /** Degrees east (negative west). */
  lon: number;
}

export interface SunTimes {
  /** Minutes after local midnight, or null when the sun doesn't rise or set that day (polar day or night). */
  sunrise: number | null;
  sunset: number | null;
}

const RAD = Math.PI / 180;

/** The UTC offset of an ISO 8601 timestamp, in minutes ("…-05:00" → -300, "…Z" → 0); null if it has none. */
export function offsetMinutes(iso: string): number | null {
  if (/Z$/.test(iso)) return 0;
  const m = /([+-])(\d{2}):?(\d{2})$/.exec(iso);
  if (!m) return null;
  const v = Number(m[2]) * 60 + Number(m[3]);
  return m[1] === "-" ? -v : v;
}

/** Latitude used when only the time zone is known: about the population center of the contiguous US. */
export const DEFAULT_LATITUDE = 39;

/** An estimated location from a UTC offset: the zone's meridian at DEFAULT_LATITUDE. */
export function locationFromOffset(offset: number, dst = false): GeoPoint {
  const standard = offset - (dst ? 60 : 0);
  return { lat: DEFAULT_LATITUDE, lon: (standard / 60) * 15 };
}

/** US daylight saving time (second Sunday of March to first Sunday of November), by date. */
export function usDst(year: number, month: number, day: number): boolean {
  if (month < 3 || month > 11) return false;
  if (month > 3 && month < 11) return true;
  const firstSunday = 1 + ((7 - weekday(year, month, 1)) % 7);
  return month === 3 ? day >= firstSunday + 7 : day < firstSunday;
}

function dayOfYear(year: number, month: number, day: number): number {
  return Math.round((Date.UTC(year, month - 1, day) - Date.UTC(year, 0, 1)) / 86400000) + 1;
}

/** Sunrise and sunset on a date at a place, in minutes after local midnight for the given UTC offset. */
export function sunTimes(year: number, month: number, day: number, at: GeoPoint, offset: number): SunTimes {
  const leap = (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;
  const g = ((2 * Math.PI) / (leap ? 366 : 365)) * (dayOfYear(year, month, day) - 1);
  const eqtime = 229.18 * (0.000075 + 0.001868 * Math.cos(g) - 0.032077 * Math.sin(g)
    - 0.014615 * Math.cos(2 * g) - 0.040849 * Math.sin(2 * g));
  const decl = 0.006918 - 0.399912 * Math.cos(g) + 0.070257 * Math.sin(g) - 0.006758 * Math.cos(2 * g)
    + 0.000907 * Math.sin(2 * g) - 0.002697 * Math.cos(3 * g) + 0.00148 * Math.sin(3 * g);
  const lat = at.lat * RAD;
  const cosHa = Math.cos(90.833 * RAD) / (Math.cos(lat) * Math.cos(decl)) - Math.tan(lat) * Math.tan(decl);
  if (cosHa > 1 || cosHa < -1) return { sunrise: null, sunset: null };
  const ha = Math.acos(cosHa) / RAD;
  const local = (utc: number) => Math.round(((utc + offset) % 1440 + 1440) % 1440);
  return { sunrise: local(720 - 4 * (at.lon + ha) - eqtime), sunset: local(720 - 4 * (at.lon - ha) - eqtime) };
}

/** "16:28" from minutes after midnight. */
export function hhmmFromMinutes(m: number): string {
  const h = Math.floor(m / 60) % 24;
  const mm = m % 60;
  return (h < 10 ? "0" : "") + h + ":" + (mm < 10 ? "0" : "") + mm;
}
