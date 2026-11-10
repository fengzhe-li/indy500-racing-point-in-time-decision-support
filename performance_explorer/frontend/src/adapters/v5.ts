import type { ComparisonSeriesV1, SimulationAdapter } from "../domain/contract";
import schema from "../../../contracts/v5-replay-1/replay.schema.json";

export interface V5Segment {
  name: string; distance_m: number; radius_m: number | null; banking_deg: number;
  evidence_class: string; start_m: number; time_s: number; label_xy_m: [number, number];
}
export interface V5Replay {
  schema_version: "v5-replay-1"; units: Record<string, string>; provenance: Record<string, string>; origin: string;
  vehicle: Record<string, number>; environment: Record<string, number | null>;
  lap_time_s: number; track_length_m: number; average_speed_mph: number; segments: V5Segment[];
  distance_m: number[]; elapsed_s: number[]; speed_mps: number[]; speed_cap_mps: number[];
  acceleration_mps2: number[]; mode: Array<"acceleration" | "braking" | "corner_cap" | "steady_or_transition">;
  xy_m: [number, number][];
}
export interface V5Series extends ComparisonSeriesV1 {
  mode: "v5-quasi-steady";
  simulation: V5Replay;
  scenario: { vehicle: Record<string, number>; environment: Record<string, number | null> };
}
const number = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const positive = (v: unknown): v is number => number(v) && v > 0;
const object = (v: unknown): v is Record<string, unknown> => v !== null && typeof v === "object" && !Array.isArray(v);
const close = (a: number, b: number, tol = 1e-6) => Math.abs(a - b) <= tol;
const pair = (v: unknown) => Array.isArray(v) && v.length === 2 && v.every(number);
function requireCondition(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(`Invalid v5-replay-1: ${message}`);
}
/** Consumer validation of the pinned upstream schema, plus numerical invariants. */
export function parseV5Replay(payload: unknown): V5Replay {
  requireCondition(object(payload), "expected an object");
  requireCondition(payload.schema_version === "v5-replay-1", "unsupported schema version");
  const keys = Object.keys(schema.properties);
  requireCondition(keys.every(k => k in payload) && Object.keys(payload).every(k => keys.includes(k)), "missing or unknown fields");
  requireCondition(object(payload.units) && Object.values(payload.units).every(v => typeof v === "string") &&
    payload.units.distance === "m" && payload.units.time === "s" && payload.units.speed === "m/s" &&
    payload.units.acceleration === "m/s²" && payload.units.geometry === "m", "SI units required");
  requireCondition(object(payload.provenance) && Object.keys(payload.provenance).length > 0 &&
    Object.values(payload.provenance).every(v => typeof v === "string" && v.length > 0), "missing provenance");
  requireCondition(typeof payload.origin === "string" && payload.origin.length > 0, "missing coordinate origin");
  requireCondition(object(payload.vehicle) && Object.keys(payload.vehicle).length > 0 && Object.values(payload.vehicle).every(number), "vehicle configuration");
  requireCondition(object(payload.environment) && Object.keys(payload.environment).length > 0 && Object.values(payload.environment).every(v => v === null || number(v)), "environment configuration");
  requireCondition(positive(payload.lap_time_s) && positive(payload.track_length_m) && positive(payload.average_speed_mph), "invalid totals");
  const n = Array.isArray(payload.distance_m) ? payload.distance_m.length : 0;
  requireCondition(n >= 3, "at least two cells required");
  for (const key of ["distance_m", "elapsed_s", "speed_mps", "speed_cap_mps"]) {
    const values = payload[key];
    requireCondition(Array.isArray(values) && values.length === n && values.every(number), `invalid ${key}`);
  }
  requireCondition(Array.isArray(payload.acceleration_mps2) && payload.acceleration_mps2.length === n - 1 && payload.acceleration_mps2.every(number), "invalid acceleration cells");
  requireCondition(Array.isArray(payload.mode) && payload.mode.length === n - 1 && payload.mode.every(m => ["acceleration", "braking", "corner_cap", "steady_or_transition"].includes(m)), "invalid constraint modes");
  requireCondition(Array.isArray(payload.xy_m) && payload.xy_m.length === n && payload.xy_m.every(pair), "invalid geometry samples");
  const segmentKeys = Object.keys(schema.$defs.Segment.properties);
  requireCondition(Array.isArray(payload.segments) && payload.segments.length > 0 && payload.segments.every(s => object(s) &&
    segmentKeys.every(k => k in s) && Object.keys(s).every(k => segmentKeys.includes(k)) &&
    typeof s.name === "string" && s.name.length > 0 && typeof s.evidence_class === "string" && s.evidence_class.length > 0 &&
    positive(s.distance_m) && (s.radius_m === null || positive(s.radius_m)) && number(s.banking_deg) &&
    number(s.start_m) && positive(s.time_s) && pair(s.label_xy_m)), "invalid segments");
  const r = payload as unknown as V5Replay;
  requireCondition(close(r.distance_m[0], 0) && close(r.elapsed_s[0], 0) &&
    close(r.distance_m[n - 1], r.track_length_m) && close(r.elapsed_s[n - 1], r.lap_time_s) &&
    close(r.speed_mps[0], r.speed_mps[n - 1]), "invalid periodic boundaries");
  requireCondition(close(r.track_length_m / r.lap_time_s / .44704, r.average_speed_mph), "average-speed/time mismatch");
  r.speed_mps.forEach((v, i) => requireCondition(v > 0 && r.speed_cap_mps[i] > 0 && v <= r.speed_cap_mps[i] + 1e-6, "invalid speed/cap"));
  for (let i = 0; i < n - 1; i++) {
    const ds = r.distance_m[i + 1] - r.distance_m[i], dt = r.elapsed_s[i + 1] - r.elapsed_s[i];
    requireCondition(ds > 0 && dt > 0, "nonmonotonic axes");
    requireCondition(close(ds, (r.speed_mps[i] + r.speed_mps[i + 1]) * dt / 2) &&
      close(r.speed_mps[i + 1], r.speed_mps[i] + r.acceleration_mps2[i] * dt), "inconsistent kinematic integration");
  }
  let end = 0, segmentTime = 0;
  for (const s of r.segments) {
    requireCondition(close(s.start_m, end), "segment gaps or overlaps");
    end += s.distance_m; segmentTime += s.time_s;
    requireCondition(end <= r.track_length_m + 1e-6, "segment beyond track");
    requireCondition(close(v5TimeAtDistance(r, end) - v5TimeAtDistance(r, s.start_m), s.time_s), "segment time mismatch");
  }
  requireCondition(close(end, r.track_length_m) && close(segmentTime, r.lap_time_s), "incomplete segment coverage");
  r.distance_m.forEach((d, i) => {
    const [x, y] = v5PositionAtDistance(r, d);
    requireCondition(close(x, r.xy_m[i][0], 1e-5) && close(y, r.xy_m[i][1], 1e-5), "geometry samples disagree with segment path");
  });
  requireCondition(close(r.xy_m[0][0], r.xy_m[n - 1][0], 1e-5) && close(r.xy_m[0][1], r.xy_m[n - 1][1], 1e-5), "track not closed");
  return structuredClone(r);
}
function cell(values: number[], value: number) {
  let lo = 0, hi = values.length - 1;
  while (lo + 1 < hi) { const mid = (lo + hi) >> 1; if (values[mid] <= value) lo = mid; else hi = mid; }
  return Math.min(lo, values.length - 2);
}
function clamp(value: number, max: number) {
  if (!Number.isFinite(value)) throw new Error("Nonfinite interpolation query");
  return Math.max(0, Math.min(max, value));
}
/** Exact constant-acceleration reconstruction within each simulation cell. */
export function v5AtTime(r: V5Replay, time: number) {
  const t = clamp(time, r.lap_time_s), i = cell(r.elapsed_s, t), dt = t - r.elapsed_s[i];
  const acceleration = r.acceleration_mps2[i];
  const distanceM = t === r.lap_time_s ? r.track_length_m : r.distance_m[i] + r.speed_mps[i] * dt + .5 * acceleration * dt * dt;
  return { elapsedTimeS: t, distanceM, speedMps: r.speed_mps[i] + acceleration * dt,
    positionM: v5PositionAtDistance(r, distanceM), complete: t >= r.lap_time_s };
}
export function v5TimeAtDistance(r: V5Replay, distance: number) {
  const d = clamp(distance, r.track_length_m);
  if (d === r.track_length_m) return r.lap_time_s;
  const i = cell(r.distance_m, d), ds = d - r.distance_m[i];
  const speed = Math.sqrt(Math.max(0, r.speed_mps[i] ** 2 + 2 * r.acceleration_mps2[i] * ds));
  return r.elapsed_s[i] + 2 * ds / (r.speed_mps[i] + speed);
}
export function v5PositionAtDistance(r: V5Replay, distance: number): [number, number] {
  let remaining = clamp(distance, r.track_length_m), x = 0, y = 0, heading = 0;
  for (const segment of r.segments) {
    const ds = Math.min(remaining, segment.distance_m);
    if (segment.radius_m === null) { x += ds * Math.cos(heading); y += ds * Math.sin(heading); }
    else {
      const next = heading + ds / segment.radius_m;
      x += segment.radius_m * (Math.sin(next) - Math.sin(heading));
      y += segment.radius_m * (Math.cos(heading) - Math.cos(next)); heading = next;
    }
    remaining -= ds;
    if (remaining <= 1e-9) break;
  }
  return [x, y];
}
export class V5Adapter implements SimulationAdapter {
  readonly mode = "v5-quasi-steady" as const;
  adapt(payload: unknown): V5Series {
    const simulation = parseV5Replay(payload);
    return {
      schemaVersion: "1.0.0", mode: this.mode, dataKind: "simulated_quasi_steady", label: "SIMULATED · V5 quasi-steady",
      geometry: "assumed_oval", axes: { primary: "distance_m", secondary: "elapsed_time_s" },
      provenance: { provider: "V5 published replay export", dataset: simulation.schema_version, sourceFiles: [],
        notes: [simulation.origin, ...Object.entries(simulation.provenance).map(([k, v]) => `${k}: ${v}`), "Within-cell values use simulated constant-acceleration kinematics, not observed telemetry."] },
      units: { time: "s", distance: "m", speed: "mph" },
      availability: { available: ["elapsed_time", "distance", "speed", "assumed_position", "segment_time"],
        unavailable: ["observed_gps", "steering", "throttle", "braking", "yaw_rate", "tracking_error"], granularity: "sample", sampleCount: simulation.distance_m.length },
      points: simulation.distance_m.map((distanceM, i) => ({ distanceM, elapsedTimeS: simulation.elapsed_s[i], speedMph: simulation.speed_mps[i] / .44704 })),
      scenario: { vehicle: { ...simulation.vehicle }, environment: { ...simulation.environment } }, simulation,
    };
  }
}
function coordinateKey(r: V5Replay) {
  return JSON.stringify([r.origin, r.track_length_m, r.segments.map(s => [s.name, s.start_m, s.distance_m, s.radius_m, s.banking_deg])]);
}
export function compareV5(a: V5Series, b: V5Series) {
  const ar = a.simulation, br = b.simulation;
  if (coordinateKey(ar) !== coordinateKey(br)) throw new Error("Incompatible V5 track-distance coordinates or origins");
  const boundaries = [...new Set([...ar.distance_m, ...br.distance_m, ...ar.segments.map(s => s.start_m)])].sort((x, y) => x - y);
  const deltaAt = (distance: number) => {
    if (!Number.isFinite(distance) || distance < -1e-6 || distance > ar.track_length_m + 1e-6) throw new Error("Outside common comparison interval");
    return v5TimeAtDistance(br, distance) - v5TimeAtDistance(ar, distance);
  };
  return {
    label: "SIMULATED" as const, durationS: Math.max(ar.lap_time_s, br.lap_time_s),
    atTime: (time: number) => ({ a: v5AtTime(ar, time), b: v5AtTime(br, time) }),
    runningDelta: boundaries.map(distanceM => ({ distanceM, deltaS: deltaAt(distanceM) })),
    speedComparison: boundaries.map(distanceM => ({ distanceM,
      aMps: v5AtTime(ar, v5TimeAtDistance(ar, distanceM)).speedMps,
      bMps: v5AtTime(br, v5TimeAtDistance(br, distanceM)).speedMps })),
    regions: ar.segments.map(s => {
      const startM = s.start_m, endM = Math.min(ar.track_length_m, startM + s.distance_m);
      const incrementalDeltaS = deltaAt(endM) - deltaAt(startM);
      return { name: s.name, startM, endM, incrementalDeltaS, cumulativeDeltaS: deltaAt(endM),
        winner: Math.abs(incrementalDeltaS) < 1e-9 ? "tie" : incrementalDeltaS < 0 ? "B" : "A",
        evidence: "SIMULATED interval time over matched assumed track geometry; no causal attribution." };
    }),
  };
}
