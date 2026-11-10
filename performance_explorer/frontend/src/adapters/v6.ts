import type { ComparisonSeriesV1, SimulationAdapter } from "../domain/contract";

const flags = ["steering_saturated", "throttle_saturated", "brake_saturated", "tire_saturated", "off_track"];
const held = new Set([...flags, "steering_command_rad", "throttle_command", "brake_command", "track_distance_m", "target_speed_m_s"]);
const core = ["sim_time_s", "x_m", "y_m", "heading_rad", "speed_m_s", "off_track"];
const optional = ["progress_m", "track_distance_m", "steering_command_rad", "throttle_command", "brake_command", "yaw_rate_rad_s", "path_error_m"];
const known = new Set([...core, ...optional, ...flags, "u_m_s", "v_m_s", "lateral_accel_m_s2", "longitudinal_accel_m_s2", "target_speed_m_s"]);
export type V6Sample = Record<string, number | boolean>;
type Track = { kind: string; coordinates: string; provenance: string; length_m: number; straight_length_m: number; radius_m: number; width_m: number; banking_rad: number };
export interface V6Series extends ComparisonSeriesV1 {
  mode: "v6-dynamic";
  track: Track; samples: V6Sample[]; durationS: number;
  status: "completed" | "off_track" | "unstable" | "numerical_error" | "timeout";
  reason: string; events: Array<{ type: string; sim_time_s: number; x_m: number; y_m: number; progress_m: number; reason: string }>;
  metadata: Record<string, unknown>;
}
function check(value: unknown, message: string): asserts value { if (!value) throw new Error(`Invalid V6 schema 2: ${message}`); }
function object(value: unknown): asserts value is Record<string, unknown> { check(value && typeof value === "object" && !Array.isArray(value), "expected object"); }
const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const near = (a: number, b: number) => Math.abs(a - b) <= 1e-8;
const n = (s: V6Sample, key: string) => s[key] as number;
export class V6Adapter implements SimulationAdapter {
  readonly mode = "v6-dynamic" as const;
  adapt(payload: unknown): V6Series {
    object(payload);
    check(payload.schema_version === 2 && payload.label === "SIMULATED", "unsupported schema or label");
    check(typeof payload.name === "string" && payload.name.length > 0, "missing name");
    const metadata = payload.metadata; object(metadata);
    check(metadata.units === "SI" && metadata.label === "SIMULATED", "SI simulated metadata required");
    check(metadata.model_version === "v6.1-audited-bicycle" && typeof metadata.parameter_provenance === "string", "unsupported model coordinate semantics or missing provenance");
    const track = metadata.track; object(track);
    check(track.kind === "approximate_stadium" && track.coordinates === "local Cartesian x east, y north; metres; CCW radians", "unsupported geometry or coordinates");
    for (const key of ["length_m", "straight_length_m", "radius_m", "width_m"]) check(finite(track[key]) && track[key] > 0, `invalid track ${key}`);
    check(finite(track.banking_rad) && typeof track.provenance === "string", "missing track evidence");
    check(near(track.length_m as number, 2 * (track.straight_length_m as number) + 2 * Math.PI * (track.radius_m as number)), "inconsistent stadium length");
    const fields = payload.fields;
    check(Array.isArray(fields) && fields.every(f => typeof f === "string") && new Set(fields).size === fields.length && core.every(f => fields.includes(f)), "missing or duplicate core fields");
    check(Array.isArray(payload.rows) && payload.rows.length > 0, "empty rows");
    const samples: V6Sample[] = payload.rows.map(row => {
      check(Array.isArray(row) && row.length === fields.length, "row width");
      const result: V6Sample = {};
      fields.forEach((field, i) => {
        check(flags.includes(field) ? typeof row[i] === "boolean" : finite(row[i]), `invalid ${field}`);
        if (known.has(field)) result[field] = row[i]; // Unknown numeric channels are not given invented units/semantics.
      });
      return result;
    });
    samples.forEach((s, i) => {
      check(n(s, "sim_time_s") >= 0 && (i === 0 ? n(s, "sim_time_s") === 0 : n(s, "sim_time_s") > n(samples[i - 1], "sim_time_s")), "timestamps");
      check(n(s, "speed_m_s") >= 0, "negative speed");
      for (const key of ["throttle_command", "brake_command"]) if (key in s) check(n(s, key) >= 0 && n(s, key) <= 1, `invalid ${key}`);
    });
    const sampling = payload.sampling; object(sampling);
    check(sampling.source === "actual V6 samples" && sampling.replay_sample_count === samples.length &&
      Number.isInteger(sampling.full_sample_count) && (sampling.full_sample_count as number) >= samples.length &&
      finite(sampling.min_interval_s) && sampling.min_interval_s >= 0, "invalid sampling provenance or counts");
    const metrics = payload.metrics; object(metrics);
    const durationS = n(samples[samples.length - 1], "sim_time_s");
    check(finite(metrics.elapsed_sim_s) && near(metrics.elapsed_sim_s, durationS), "terminal time mismatch");
    check(["completed", "off_track", "unstable", "numerical_error", "timeout"].includes(String(metrics.status)) && typeof metrics.reason === "string", "unknown terminal status");
    const complete = metrics.status === "completed";
    check(metrics.completed_lap === complete && (complete ? finite(metrics.lap_time_s) && near(metrics.lap_time_s, durationS) : metrics.lap_time_s === null), "completion mismatch");
    check(metrics.off_track === (metrics.status === "off_track") && samples[samples.length - 1].off_track === metrics.off_track, "terminal boundary flag mismatch");
    check(Array.isArray(payload.events) && payload.events.length > 0, "missing terminal event");
    const events = payload.events.map(e => {
      object(e); check(typeof e.type === "string" && typeof e.reason === "string" && [e.sim_time_s, e.x_m, e.y_m, e.progress_m].every(finite), "event fields");
      check((e.sim_time_s as number) >= 0 && (e.sim_time_s as number) <= durationS + 1e-8, "event outside recording");
      return { ...e } as V6Series["events"][number];
    });
    const terminal = events[events.length - 1], last = samples[samples.length - 1];
    check(terminal.type === metrics.status && near(terminal.sim_time_s, durationS) && near(terminal.x_m, n(last, "x_m")) && near(terminal.y_m, n(last, "y_m")) && (!("progress_m" in last) || near(terminal.progress_m, n(last, "progress_m"))), "terminal event mismatch");
    const sim = metadata.simulation;
    const laps = sim && typeof sim === "object" && !Array.isArray(sim) && Number.isInteger((sim as Record<string, unknown>).max_laps) && ((sim as Record<string, unknown>).max_laps as number) >= 1 ? (sim as Record<string, unknown>).max_laps as number : 1;
    check(!complete || (terminal.progress_m >= laps * (track.length_m as number) - 1e-6 && (!("progress_m" in last) || n(last, "progress_m") >= laps * (track.length_m as number) - 1e-6)), "completed run did not reach lap distance");
    return {
      schemaVersion: "1.0.0", mode: this.mode, dataKind: "simulated_dynamic_telemetry", label: `SIMULATED · V6 · ${payload.name}`,
      geometry: "assumed_oval", axes: { primary: "elapsed_time_s", ...(fields.includes("progress_m") ? { secondary: "distance_m" as const } : {}) },
      units: { time: "s", distance: "m", speed: "mph", position: "m", heading: "rad", steering: "rad", yawRate: "rad/s", trackingError: "m", throttle: "dimensionless", braking: "dimensionless" },
      availability: { available: fields.filter(f => known.has(f)), unavailable: optional.filter(f => !fields.includes(f)), granularity: "sample", sampleCount: samples.length },
      provenance: { provider: "V6 published schema-2 replay", dataset: payload.name, sourceFiles: [], notes: [String(track.provenance), String(metadata.parameter_provenance), "Actual reduced simulation samples; interpolation is display-only, held commands/flags, unwrapped heading. Full-resolution extrema may be absent.", `Ignored unknown channels: ${fields.filter(f => !known.has(f)).join(", ") || "none"}`] },
      points: samples.map(s => ({ elapsedTimeS: n(s, "sim_time_s"), ...(s.progress_m === undefined ? {} : { distanceM: n(s, "progress_m") }), speedMph: n(s, "speed_m_s") / .44704 })),
      track: { ...track } as Track, samples, durationS, status: metrics.status as V6Series["status"], reason: metrics.reason, events, metadata: structuredClone(metadata),
    };
  }
}
export function v6AtTime(run: V6Series, time: number) {
  check(finite(time), "nonfinite seek");
  const t = Math.max(0, Math.min(run.durationS, time)), samples = run.samples;
  let lo = 0, hi = samples.length - 1;
  while (lo < hi) { const mid = Math.ceil((lo + hi) / 2); if (n(samples[mid], "sim_time_s") <= t) lo = mid; else hi = mid - 1; }
  const a = samples[lo], b = samples[Math.min(lo + 1, samples.length - 1)], result = { ...a };
  const dt = n(b, "sim_time_s") - n(a, "sim_time_s");
  if (dt > 0) for (const key of Object.keys(a)) if (!held.has(key)) result[key] = n(a, key) + (n(b, key) - n(a, key)) * (t - n(a, "sim_time_s")) / dt;
  return { sample: result, terminal: t === run.durationS, complete: t === run.durationS && run.status === "completed", status: t === run.durationS ? run.status : "in_progress" };
}
/** Distance comparisons require a strictly advancing, common reference origin.
 * Failure truncates the valid interval; there is never a projected lap finish. */
export function compareV6(a: V6Series, b: V6Series) {
  const key = (r: V6Series) => JSON.stringify([r.track.kind, r.track.coordinates, r.track.length_m, r.track.straight_length_m, r.track.radius_m, r.track.width_m, r.track.banking_rad]);
  if (a.mode !== "v6-dynamic" || b.mode !== "v6-dynamic" || key(a) !== key(b)) throw new Error("Incompatible V6 geometry");
  const coordinateConsistent = (r: V6Series) => r.samples.every(s => {
    if (!finite(s.progress_m) || !finite(s.track_distance_m)) return false;
    const wrapped = ((s.progress_m % r.track.length_m) + r.track.length_m) % r.track.length_m;
    const error = Math.abs(wrapped - s.track_distance_m);
    return Math.min(error, Math.abs(error - r.track.length_m)) < 1e-6;
  });
  const advancing = (r: V6Series) => coordinateConsistent(r) && r.samples.length > 1 && r.samples[0].progress_m === 0 && r.samples[0].track_distance_m === 0 && r.samples.every((s, i) => finite(s.progress_m) && (i === 0 || n(s, "progress_m") > n(r.samples[i - 1], "progress_m")));
  const distanceAvailable = advancing(a) && advancing(b);
  const endM = distanceAvailable ? Math.min(n(a.samples[a.samples.length - 1], "progress_m"), n(b.samples[b.samples.length - 1], "progress_m"), a.track.length_m) : null;
  const arrival = (r: V6Series, d: number) => {
    let lo = 0, hi = r.samples.length - 1;
    while (lo + 1 < hi) { const mid = (lo + hi) >> 1; if (n(r.samples[mid], "progress_m") <= d) lo = mid; else hi = mid; }
    const x = r.samples[lo], y = r.samples[hi];
    return n(x, "sim_time_s") + (n(y, "sim_time_s") - n(x, "sim_time_s")) * (d - n(x, "progress_m")) / (n(y, "progress_m") - n(x, "progress_m"));
  };
  const deltaAt = (d: number) => {
    if (endM === null || !finite(d) || d < 0 || d > endM) throw new Error("Unavailable or outside common V6 progress interval");
    return arrival(b, d) - arrival(a, d);
  };
  return { label: "SIMULATED", durationS: Math.max(a.durationS, b.durationS), distanceAvailable, commonEndM: endM,
    limitations: "Reduced display samples; linear progress interpolation. Only common recorded coverage, no inferred finish for failed runs.",
    atTime: (t: number) => ({ a: v6AtTime(a, t), b: v6AtTime(b, t) }), deltaAt,
    interval: (startM: number, finishM: number) => { if (finishM <= startM) throw new Error("Invalid interval"); return { startM, endM: finishM, incrementalDeltaS: deltaAt(finishM) - deltaAt(startM), cumulativeDeltaS: deltaAt(finishM) }; },
  };
}
