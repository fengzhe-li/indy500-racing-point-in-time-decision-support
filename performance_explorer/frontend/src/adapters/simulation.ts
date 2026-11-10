import type { ComparisonSeriesV1, SimulationAdapter } from "../domain/contract";
// Versioned extension points only. Concrete V5/V6 payload schemas await their branch contracts.
export class V5Adapter implements SimulationAdapter { readonly mode="v5-quasi-steady" as const; adapt(_payload:unknown):ComparisonSeriesV1{throw new Error("V5 adapter awaits the published V5 contract (schema version and distance grid).")}}
export class V6Adapter implements SimulationAdapter { readonly mode="v6-dynamic" as const; adapt(_payload:unknown):ComparisonSeriesV1{throw new Error("V6 adapter awaits the published V6 telemetry contract (schema version and validated track-distance coordinate).")}}
