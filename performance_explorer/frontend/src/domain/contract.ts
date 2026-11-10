export type DataMode = "historical" | "v5-quasi-steady" | "v6-dynamic";
export type DataKind = "observed_official_timing_summary" | "simulated_quasi_steady" | "simulated_dynamic_telemetry";
export type AxisKind = "lap_boundary" | "distance_m" | "elapsed_time_s";
export type GeometryClass = "oval_four_turn" | "unknown";

export interface Provenance { provider: string; dataset: string; sourceFiles: string[]; retrievedAt?: string; notes: string[] }
export interface SignalAvailability { available: string[]; unavailable: string[]; granularity: "lap" | "section" | "sample"; sampleCount: number }
export interface ComparisonSeriesV1 {
  schemaVersion: "1.0.0"; mode: DataMode; dataKind: DataKind; label: string;
  provenance: Provenance; units: Record<string, string>; geometry: GeometryClass;
  axes: { primary: AxisKind; secondary?: AxisKind };
  availability: SignalAvailability;
  points: Array<{ distanceM?: number; elapsedTimeS: number; speedMph?: number; lap?: number; sectionId?: string }>;
}
export interface HistoricalAttempt {
  year: number; sessionId: string; attemptId: string; carNumber: string; driver: string; team: string;
  attempt: number; averageSpeedMph: number; lapSpeedsMph: number[]; source: string;
}
export interface HistoricalDataV1 { schemaVersion: "1.0.0"; dataset: string; dataKind: "observed_official_timing_summary"; sourceFile: string; recordCount: number; rows: HistoricalAttempt[] }

// Integration boundary: future branches implement a provider against this stable contract.
// No unfinished V5/V6 source module is imported here.
export interface SimulationAdapter { readonly mode: "v5-quasi-steady" | "v6-dynamic"; adapt(payload: unknown): ComparisonSeriesV1 }
