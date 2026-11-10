import type { ComparisonSeriesV1, SimulationAdapter } from "../domain/contract";
export { V5Adapter } from "./v5";
// Deliberately no import from unfinished V6 source and no fabricated channels.
export class V6Adapter implements SimulationAdapter {
  readonly mode = "v6-dynamic" as const;
  adapt(_payload: unknown): ComparisonSeriesV1 {
    throw new Error("V6 adapter awaits a published versioned export, units, validated track-distance coordinate and completion/failure semantics.");
  }
}
