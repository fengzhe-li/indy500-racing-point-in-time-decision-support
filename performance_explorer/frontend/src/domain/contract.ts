export type DataMode = "historical" | "v5-quasi-steady" | "v6-dynamic";
export type DataKind = "observed_official_timing_summary" | "simulated_quasi_steady" | "simulated_dynamic_telemetry";
export type AxisKind = "lap_boundary" | "distance_m" | "elapsed_time_s";
export type GeometryClass = "oval_four_turn" | "assumed_oval" | "unknown";
export interface Provenance {
  provider: string; dataset: string; sourceFiles: string[]; retrievedAt?: string; notes: string[];
}
export interface SignalAvailability {
  available: string[]; unavailable: string[];
  granularity: "lap" | "section" | "sample"; sampleCount: number;
}
export interface ComparisonSeriesV1 {
  schemaVersion: "1.0.0"; mode: DataMode; dataKind: DataKind; label: string;
  provenance: Provenance; units: Record<string, string>; geometry: GeometryClass;
  axes: { primary: AxisKind; secondary?: AxisKind }; availability: SignalAvailability;
  points: Array<{ distanceM?: number; elapsedTimeS: number; speedMph?: number; lap?: number; sectionId?: string }>;
}
export interface HistoricalAttempt {
  year: number; sessionId: string; attemptId: string; carNumber: string; driver: string; team: string;
  attempt: number | null; attemptOrderQuality: string; resultStatus: "VALID_RETAINED";
  sourceLocator: string; sourceIds: string[]; averageSpeedMph: number; totalSeconds: number;
  lapTimesS: number[]; lapSpeedsMph: number[];
  timingBasis: "official_recorded_lap_duration"; lapSpeedBasis: "derived_from_recorded_lap_time"; source: string;
}
export interface HistoricalDataV1 {
  schemaVersion: "1.1.0"; dataset: string; dataKind: "observed_official_timing_summary";
  sourceFile: string; recordCount: number; rows: HistoricalAttempt[];
  sourceHashes: Record<string, string>;
  sources: Array<{source_id: string; source_uri: string; content_hash: string; evidence_quality: string}>;
}
export interface SimulationAdapter {
  readonly mode: "v5-quasi-steady" | "v6-dynamic";
  adapt(payload: unknown): ComparisonSeriesV1;
}
