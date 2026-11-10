import type { ComparisonSeriesV1, HistoricalAttempt, HistoricalDataV1 } from "../domain/contract";
const positive = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v) && v > 0;
const object = (v: unknown): v is Record<string, unknown> => v !== null && typeof v === "object" && !Array.isArray(v);

export function validateHistoricalData(value: unknown): value is HistoricalDataV1 {
  if (!object(value) || value.schemaVersion !== "1.1.0" || value.dataKind !== "observed_official_timing_summary" ||
      typeof value.dataset !== "string" || typeof value.sourceFile !== "string" ||
      !object(value.sourceHashes) || !Array.isArray(value.sources) || !Array.isArray(value.rows) || value.recordCount !== value.rows.length) return false;
  const ids = new Set<string>();
  return value.rows.every(r => {
    if (!object(r) || typeof r.attemptId !== "string" || !r.attemptId || ids.has(r.attemptId)) return false;
    ids.add(r.attemptId);
    if (!Number.isInteger(r.year) || ![2020, 2021, 2022, 2023, 2024].includes(r.year as number) ||
        r.sessionId !== `INDY500_DAY1_${r.year}` || r.resultStatus !== "VALID_RETAINED" ||
        (r.attempt !== null && (!positive(r.attempt) || !Number.isInteger(r.attempt))) ||
        ![r.driver, r.carNumber, r.source, r.sourceLocator, r.attemptOrderQuality].every(s => typeof s === "string" && s.length > 0) ||
        !Array.isArray(r.sourceIds) || !r.sourceIds.length || !r.sourceIds.every(s => typeof s === "string") ||
        r.timingBasis !== "official_recorded_lap_duration" || r.lapSpeedBasis !== "derived_from_recorded_lap_time" ||
        !positive(r.averageSpeedMph) || !positive(r.totalSeconds) ||
        !Array.isArray(r.lapTimesS) || r.lapTimesS.length !== 4 || !r.lapTimesS.every(positive) ||
        !Array.isArray(r.lapSpeedsMph) || r.lapSpeedsMph.length !== 4 || !r.lapSpeedsMph.every(positive)) return false;
    const times = r.lapTimesS as number[], speeds = r.lapSpeedsMph as number[];
    return Math.abs(times.reduce((a, b) => a + b, 0) - r.totalSeconds) <= .0005 &&
      Math.abs(36000 / r.totalSeconds - r.averageSpeedMph) <= .001 &&
      times.every((t, i) => Math.abs(9000 / t - speeds[i]) <= .001);
  });
}
export function toObservedSeries(row: HistoricalAttempt): ComparisonSeriesV1 {
  let elapsedTimeS = 0;
  const points = [{ lap: 0, elapsedTimeS }];
  row.lapTimesS.forEach((duration, i) => { elapsedTimeS += duration; points.push({ lap: i + 1, elapsedTimeS }); });
  return {
    schemaVersion: "1.0.0", mode: "historical", dataKind: "observed_official_timing_summary",
    label: `OBSERVED · ${row.year} ${row.driver} · car ${row.carNumber}`,
    provenance: { provider: "Canonical official timing", dataset: "canonical/v1 retained attempts",
      sourceFiles: [row.source], notes: [
        "Lap durations are recorded official values. Elapsed boundaries sum these durations; no wall-clock timestamps are inferred.",
        "Lap speeds are rounded canonical derivations from recorded lap times; four-lap average speeds are official values.",
        "Section records exist in canonical data, but validated spatial boundary mapping is not exposed by this adapter.",
      ] },
    units: { speed: "mph", time: "s" }, geometry: "unknown", axes: { primary: "lap_boundary" },
    availability: { available: ["four_lap_average_speed_mph", "lap_time_seconds", "lap_average_speed_mph"],
      unavailable: ["gps", "continuous_position", "section_times", "steering", "throttle", "braking"], granularity: "lap", sampleCount: 4 }, points,
  };
}
