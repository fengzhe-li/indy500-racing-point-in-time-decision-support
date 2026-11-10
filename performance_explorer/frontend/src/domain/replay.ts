import type { ComparisonSeriesV1, HistoricalAttempt } from "./contract";

// Explicit piecewise-linear interpolation helper for validated distance samples.
// Historical lap boundaries intentionally have no distanceM and return null.
function interpolate(points: ComparisonSeriesV1["points"], value: number, axis: "distanceM" | "elapsedTimeS"): number | null {
  const other = axis === "distanceM" ? "elapsedTimeS" : "distanceM";
  if (!Number.isFinite(value) || points.length < 2 || points.some((p, i) =>
    !Number.isFinite(p.distanceM) || !Number.isFinite(p.elapsedTimeS) ||
    (i > 0 && (p.distanceM! <= points[i - 1].distanceM! || p.elapsedTimeS <= points[i - 1].elapsedTimeS)))) return null;
  if (value < points[0][axis]! || value > points[points.length - 1][axis]!) return null;
  for (let i = 1; i < points.length; i++) if (value <= points[i][axis]!) {
    const a = points[i - 1], b = points[i], f = (value - a[axis]!) / (b[axis]! - a[axis]!);
    return a[other]! + f * (b[other]! - a[other]!);
  }
  return null;
}
export const timeAtDistance = (p: ComparisonSeriesV1["points"], d: number) => interpolate(p, d, "distanceM");
export const distanceAtTime = (p: ComparisonSeriesV1["points"], t: number) => interpolate(p, t, "elapsedTimeS");
export interface ReplayState { playing: boolean; elapsedS: number; durationS: number; speed: number }
export function tickReplay(s: ReplayState, dt: number): ReplayState {
  if (!s.playing || !Number.isFinite(dt) || dt < 0) return s;
  const elapsedS = Math.min(s.durationS, s.elapsedS + dt * s.speed);
  return { ...s, elapsedS, playing: elapsedS < s.durationS };
}
export const runningDelta = (aSeconds: number, bSeconds: number) => bSeconds - aSeconds;
export const segmentDelta = (aStart: number, aEnd: number, bStart: number, bEnd: number) => (bEnd - bStart) - (aEnd - aStart);
export function lapBoundaries(times: number[]) {
  if (!times.length || times.some(t => !Number.isFinite(t) || t <= 0)) throw new Error("Invalid lap durations");
  return times.reduce<number[]>((result, t) => [...result, result[result.length - 1] + t], [0]);
}
export function completedLaps(boundaries: number[], time: number) {
  return Math.max(0, boundaries.filter(t => t <= time + 1e-9).length - 1);
}
export function historicalComparison(a: HistoricalAttempt, b: HistoricalAttempt) {
  if (a.sessionId !== b.sessionId) throw new Error("Historical sessions are not comparable");
  const aTimes = lapBoundaries(a.lapTimesS), bTimes = lapBoundaries(b.lapTimesS);
  const count = Math.min(a.lapTimesS.length, b.lapTimesS.length);
  return { aTimes, bTimes, count, duration: Math.max(aTimes[aTimes.length - 1], bTimes[bTimes.length - 1]),
    // Seek to the instant both cars have reached the selected boundary.
    seekTime: (lap: number) => {
      if (!Number.isInteger(lap) || lap < 0 || lap > count) throw new Error("Unavailable lap boundary");
      return Math.max(aTimes[lap], bTimes[lap]);
    },
    deltaAt: (lap: number): number | null => Number.isInteger(lap) && lap >= 0 && lap <= count ? runningDelta(aTimes[lap], bTimes[lap]) : null,
  };
}
