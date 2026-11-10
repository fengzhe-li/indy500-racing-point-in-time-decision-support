import { describe, expect, it } from "vitest";
import baseline from "../test/fixtures/v6-baseline.json";
import conservative from "../test/fixtures/v6-conservative.json";
import failed from "../test/fixtures/v6-delay_0.6s.json";
import zero from "../test/fixtures/v6-offset_+8m.json";
import { compareV6, V6Adapter, v6AtTime } from "./v6";
const adapter = new V6Adapter();
const copy = () => structuredClone(baseline);
describe("published V6 schema 2 consumer", () => {
  it.each([baseline, conservative, failed, zero])("accepts real $name export and records provenance", fixture => {
    const run = adapter.adapt(fixture);
    expect(run.label).toContain("SIMULATED");
    expect(run.provenance.notes.join(" ")).toContain("not official IMS GPS");
    expect(run.durationS).toBe(fixture.metrics.elapsed_sim_s);
  });
  it("interpolates actual position/unwrapped heading and holds controls/flags", () => {
    const run = adapter.adapt(baseline), a = run.samples[0], b = run.samples[1];
    const result = v6AtTime(run, Number(b.sim_time_s) / 2);
    expect(result.sample.x_m).toBeCloseTo((Number(a.x_m) + Number(b.x_m)) / 2, 10);
    expect(result.sample.throttle_command).toBe(a.throttle_command);
    expect(result.sample.off_track).toBe(a.off_track);
    run.samples[0].heading_rad = 6.2; run.samples[1].heading_rad = 6.4;
    expect(v6AtTime(run, Number(b.sim_time_s) / 2).sample.heading_rad).toBeCloseTo(6.3, 12);
    expect(() => v6AtTime(run, NaN)).toThrow();
  });
  it("clamps failed runs at actual terminal event without completing a lap", () => {
    const run = adapter.adapt(failed), state = v6AtTime(run, 10000);
    expect(state).toMatchObject({ terminal: true, complete: false, status: "off_track" });
    expect(state.sample.sim_time_s).toBe(failed.metrics.elapsed_sim_s);
    expect(state.sample.x_m).toBe(failed.events[0].x_m);
    expect(state.sample.off_track).toBe(true);
    expect(v6AtTime(adapter.adapt(zero), 4)).toMatchObject({ terminal: true, complete: false });
    expect(v6AtTime(adapter.adapt(baseline), 10000).complete).toBe(true);
  });
  it("synchronizes distinct terminal times and restricts deltas to common recorded coverage", () => {
    const comparison = compareV6(adapter.adapt(baseline), adapter.adapt(failed));
    expect(comparison.atTime(30).a.terminal).toBe(false);
    expect(comparison.atTime(30).b.status).toBe("off_track");
    expect(comparison.commonEndM).toBeCloseTo(failed.events[0].progress_m, 8);
    expect(() => comparison.deltaAt(2000)).toThrow();
    const c = compareV6(adapter.adapt(baseline), adapter.adapt(conservative));
    expect(c.deltaAt(1000)).toBeGreaterThan(0);
    expect(c.interval(0, 1000).incrementalDeltaS + c.interval(1000, 2000).incrementalDeltaS).toBeCloseTo(c.deltaAt(2000), 12);
  });
  it("keeps optional missing channels absent and ignores unknown numeric signals", () => {
    const data = copy(), i = data.fields.indexOf("throttle_command");
    data.fields.splice(i, 1); data.rows.forEach(row => row.splice(i, 1));
    data.fields.push("unknown_signal"); data.rows.forEach(row => row.push(123));
    const run = adapter.adapt(data);
    expect(run.availability.unavailable).toContain("throttle_command");
    expect(run.samples[0].throttle_command).toBeUndefined();
    expect(run.samples[0].unknown_signal).toBeUndefined();
    expect(run.provenance.notes.join()).toContain("Ignored unknown channels: unknown_signal");
  });
  it("makes missing or nonmonotonic progress unavailable, with no fake distance axis", () => {
    const data = copy(), i = data.fields.indexOf("progress_m");
    data.fields.splice(i, 1); data.rows.forEach(row => row.splice(i, 1));
    const run = adapter.adapt(data);
    expect(run.points[0].distanceM).toBeUndefined();
    expect(compareV6(run, adapter.adapt(baseline)).distanceAvailable).toBe(false);
    const normal = adapter.adapt(baseline); normal.samples[1].progress_m = -1;
    expect(compareV6(normal, normal).distanceAvailable).toBe(false);
    const c = compareV6(adapter.adapt(zero), adapter.adapt(baseline));
    expect(() => c.deltaAt(0)).toThrow();
  });
  it.each([
    (x: ReturnType<typeof copy>) => { x.schema_version = 3; },
    (x: ReturnType<typeof copy>) => { x.label = "OBSERVED"; },
    (x: ReturnType<typeof copy>) => { x.rows[1][0] = 0; },
    (x: ReturnType<typeof copy>) => { x.rows[1][1] = NaN; },
    (x: ReturnType<typeof copy>) => { x.events[0].sim_time_s += 1; },
    (x: ReturnType<typeof copy>) => { x.events[0].type = "off_track"; },
    (x: ReturnType<typeof copy>) => { x.events[0].x_m += 1; },
    (x: ReturnType<typeof copy>) => { x.metrics.completed_lap = false; },
    (x: ReturnType<typeof copy>) => { x.metadata.units = "imperial"; },
    (x: ReturnType<typeof copy>) => { x.metadata.track.coordinates = "another origin"; },
    (x: ReturnType<typeof copy>) => { x.fields[1] = x.fields[0]; },
    (x: ReturnType<typeof copy>) => { x.sampling.replay_sample_count += 1; },
    (x: ReturnType<typeof copy>) => { x.metadata.model_version = "unreviewed-model"; },
  ])("rejects invalid export %#", mutate => { const data = copy(); mutate(data); expect(() => adapter.adapt(data)).toThrow(/Invalid V6/); });
  it("disables distance deltas when wrapped/unwrapped coordinates disagree", () => {
    const a = adapter.adapt(baseline); a.samples[1].track_distance_m = 100;
    expect(compareV6(a, adapter.adapt(conservative)).distanceAvailable).toBe(false);
  });
  it("rejects incompatible geometry and never compares V5 vs V6", () => {
    const a = adapter.adapt(baseline), b = adapter.adapt(conservative); b.track.width_m += 1;
    expect(() => compareV6(a, b)).toThrow(/Incompatible/);
    b.mode = "v5-quasi-steady" as typeof b.mode;
    expect(() => compareV6(a, b)).toThrow(/Incompatible/);
  });
});
