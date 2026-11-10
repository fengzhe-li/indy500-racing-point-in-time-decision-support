import { describe, expect, it } from "vitest";
import data from "../data/historical-attempts-v1.json";
import { validateHistoricalData, toObservedSeries } from "../adapters/historical";
import { completedLaps, distanceAtTime, historicalComparison, lapBoundaries, timeAtDistance } from "./replay";
if (!validateHistoricalData(data)) throw new Error("Fixture invalid");
const a = data.rows[0], b = data.rows[1];
describe("historical numerical and availability boundaries", () => {
  it("uses recorded timing, not rounded speed inversion", () => {
    const series = toObservedSeries(a);
    expect(series.points[1].elapsedTimeS).toBe(a.lapTimesS[0]);
    expect(series.points[4].elapsedTimeS).toBeCloseTo(a.totalSeconds, 9);
    expect(a.lapTimesS[0]).not.toBe(9000 / a.lapSpeedsMph[0]);
    expect(distanceAtTime(series.points, 10)).toBeNull();
    expect(timeAtDistance(series.points, 100)).toBeNull();
  });
  it("rejects cross-session boundaries and compares only shared laps", () => {
    expect(() => historicalComparison(a, { ...b, sessionId: "other" })).toThrow();
    const comparison = historicalComparison(a, { ...b, lapTimesS: b.lapTimesS.slice(0, 3) });
    expect(comparison.count).toBe(3);
    expect(comparison.deltaAt(4)).toBeNull();
    expect(() => comparison.seekTime(4)).toThrow();
    expect(comparison.deltaAt(1.5)).toBeNull();
  });
  it("completes laps independently and holds each marker at its last known boundary", () => {
    const a = lapBoundaries([10, 12, 14, 16]), b = lapBoundaries([11, 13, 15, 17]);
    expect(completedLaps(a, 10.5)).toBe(1); expect(completedLaps(b, 10.5)).toBe(0);
    expect(completedLaps(a, 51.9)).toBe(3); expect(completedLaps(a, 52)).toBe(4);
    expect(completedLaps(b, 52)).toBe(3); expect(completedLaps(b, 100)).toBe(4);
  });
  it("supports linear sample interpolation but rejects invalid axes and extrapolation", () => {
    const points = [{ distanceM: 0, elapsedTimeS: 0 }, { distanceM: 100, elapsedTimeS: 10 }, { distanceM: 300, elapsedTimeS: 30 }];
    expect(timeAtDistance(points, 150)).toBe(15); expect(distanceAtTime(points, 15)).toBe(150);
    expect(timeAtDistance(points, 301)).toBeNull(); expect(distanceAtTime(points, -1)).toBeNull();
    expect(timeAtDistance([points[1], points[0]], 50)).toBeNull();
    expect(timeAtDistance([points[0], points[0]], 0)).toBeNull();
    expect(timeAtDistance(points, NaN)).toBeNull();
    expect(() => lapBoundaries([10, NaN])).toThrow();
  });
  it("validates unknown order but rejects duplicates, partial and inconsistent timing", () => {
    expect(data.rows.filter(r => r.year === 2024)).toHaveLength(31);
    expect(data.rows.filter(r => r.year === 2024 && r.attempt === null)).toHaveLength(28);
    expect(data.rows).toHaveLength(196);
    for (const value of [null, [], {}, { ...data, schemaVersion: "9.0.0" }, { ...data, rows: [...data.rows.slice(1), data.rows[1]] }]) {
      expect(validateHistoricalData(value)).toBe(false);
    }
    const changed = structuredClone(data);
    changed.rows[0].lapTimesS[0] += 1;
    expect(validateHistoricalData(changed)).toBe(false);
    changed.rows[0] = { ...a, lapTimesS: a.lapTimesS.slice(1) };
    expect(validateHistoricalData(changed)).toBe(false);
  });
});
