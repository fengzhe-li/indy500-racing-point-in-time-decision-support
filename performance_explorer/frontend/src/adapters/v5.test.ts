import { describe, expect, it } from "vitest";
import baseline from "../test/fixtures/v5-baseline.json";
import lowGrip from "../test/fixtures/v5-low-grip.json";
import { compareV5, parseV5Replay, V5Adapter, v5AtTime, v5TimeAtDistance } from "./v5";
import { V6Adapter } from "./simulation";
const adapter = new V5Adapter();

describe("published V5 contract (actual simulated exports, never official results)", () => {
  it("accepts both published exports and keeps independent scenario provenance", () => {
    const a = adapter.adapt(baseline), b = adapter.adapt(lowGrip);
    expect(a.label).toContain("SIMULATED");
    expect(a.dataKind).toBe("simulated_quasi_steady");
    expect(a.scenario.vehicle).not.toEqual(b.scenario.vehicle);
    expect(a.availability.unavailable).toContain("throttle");
    expect(a.simulation).not.toBe(baseline);
    expect(a.provenance.notes.join(" ")).toContain("not surveyed GPS");
  });
  it.each([
    ["unknown version", (r: typeof baseline) => { r.schema_version = "v5-replay-2"; }],
    ["wrong units", (r: typeof baseline) => { r.units.speed = "mph"; }],
    ["nonfinite input", (r: typeof baseline) => { r.vehicle.mass_kg = NaN; }],
    ["missing provenance", (r: typeof baseline) => { r.provenance = {} as typeof r.provenance; }],
    ["missing node", (r: typeof baseline) => { r.speed_mps.pop(); }],
    ["wrong cell length", (r: typeof baseline) => { r.mode.pop(); }],
    ["invalid mode", (r: typeof baseline) => { r.mode[0] = "throttle"; }],
    ["reversed distance", (r: typeof baseline) => { r.distance_m[2] = 0; }],
    ["incorrect elapsed integral", (r: typeof baseline) => { r.elapsed_s[10] += .001; }],
    ["incorrect acceleration", (r: typeof baseline) => { r.acceleration_mps2[10] += .1; }],
    ["incorrect position", (r: typeof baseline) => { r.xy_m[10][0] += 1; }],
    ["incorrect segment time", (r: typeof baseline) => { r.segments[0].time_s += .01; }],
    ["incorrect segment boundary", (r: typeof baseline) => { r.segments[1].start_m += 1; }],
    ["incorrect total", (r: typeof baseline) => { r.lap_time_s += .1; }],
    ["missing config", (r: typeof baseline) => { r.environment = {} as typeof r.environment; }],
  ])("rejects %s", (_, change) => { const r = structuredClone(baseline); change(r); expect(() => parseV5Replay(r)).toThrow(); });
  it("rejects missing, extra and structurally malformed fields", () => {
    for (const value of [null, [], {}, { ...baseline, unexpected: 1 }, { ...baseline, segments: [null] }, { ...baseline, xy_m: [] }]) {
      expect(() => parseV5Replay(value)).toThrow();
    }
  });
  it("uses exact cell kinematics and reciprocal time/distance at interior points", () => {
    const r = parseV5Replay(lowGrip);
    r.elapsed_s.slice(0, -1).forEach((t, i) => {
      const mid = (t + r.elapsed_s[i + 1]) / 2;
      const sample = v5AtTime(r, mid), dt = mid - t;
      expect(sample.distanceM).toBeCloseTo(r.distance_m[i] + r.speed_mps[i] * dt + .5 * r.acceleration_mps2[i] * dt ** 2, 8);
      expect(v5TimeAtDistance(r, sample.distanceM)).toBeCloseTo(mid, 8);
    });
  });
  it("clamps each car at its own completion without wrapping to start", () => {
    const a = adapter.adapt(baseline), b = adapter.adapt(lowGrip), comparison = compareV5(a, b);
    const middle = (a.simulation.lap_time_s + b.simulation.lap_time_s) / 2;
    const state = comparison.atTime(middle);
    expect(state.a.complete).toBe(true); expect(state.b.complete).toBe(false);
    expect(state.a.distanceM).toBe(a.simulation.track_length_m);
    expect(state.b.distanceM).toBeLessThan(b.simulation.track_length_m);
    const finish = comparison.atTime(comparison.durationS + 50);
    expect(finish.a.complete && finish.b.complete).toBe(true);
    expect(comparison.atTime(-2).a.distanceM).toBe(0);
    expect(() => comparison.atTime(NaN)).toThrow();
  });
  it("keeps cumulative and incremental deltas separate and conserves total advantage", () => {
    const a = adapter.adapt(baseline), b = adapter.adapt(lowGrip), result = compareV5(a, b);
    expect(result.runningDelta[0].deltaS).toBe(0);
    const total = b.simulation.lap_time_s - a.simulation.lap_time_s;
    expect(result.runningDelta[result.runningDelta.length - 1].deltaS).toBeCloseTo(total, 9);
    expect(result.regions.reduce((sum, r) => sum + r.incrementalDeltaS, 0)).toBeCloseTo(total, 9);
    expect(result.regions.every(r => ["A", "B", "tie"].includes(r.winner))).toBe(true);
    expect(compareV5(b, a).runningDelta.slice(-1)[0].deltaS).toBeCloseTo(-total, 9);
    expect(compareV5(a, a).regions.every(r => r.winner === "tie")).toBe(true);
    expect(result.speedComparison).toHaveLength(result.runningDelta.length);
  });
  it("rejects unaligned origins, lengths and geometry", () => {
    const a = adapter.adapt(baseline), b = adapter.adapt(lowGrip);
    b.simulation.origin = "Official timing line";
    expect(() => compareV5(a, b)).toThrow(/Incompatible/);
    b.simulation.origin = a.simulation.origin;
    b.simulation.segments[0].radius_m! += 1;
    expect(() => compareV5(a, b)).toThrow(/Incompatible/);
  });
  it("leaves unfinished V6 explicitly disconnected", () => {
    expect(() => new V6Adapter().adapt({})).toThrow(/awaits a published/);
  });
});
