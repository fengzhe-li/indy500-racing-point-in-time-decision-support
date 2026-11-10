import { compareV6, v6AtTime, type V6Series, type V6Sample, V6Adapter } from "./adapters/v6";

export type V6Replay = V6Series & {
  name: string;
  metadata: Record<string, unknown> & { track: V6Series["track"] };
  metrics: {
    status: V6Series["status"];
    elapsed_sim_s: number;
    lap_time_s: number | null;
    reason: string;
  };
  events: V6Series["events"];
};

const adapter = new V6Adapter();

/** Keep the Explorer view on the already audited schema-2 adapter contract. */
export function decodeV6(value: unknown): V6Replay {
  const series = adapter.adapt(value);
  const raw = value as Record<string, unknown>;
  return {
    ...series,
    name: raw.name as string,
    metadata: raw.metadata as V6Replay["metadata"],
    metrics: raw.metrics as V6Replay["metrics"],
    events: series.events,
  };
}

export function compatibleV6(a: V6Replay, b: V6Replay): boolean {
  try {
    compareV6(a, b);
    return true;
  } catch {
    return false;
  }
}

export function sampleV6(run: V6Series, time: number): V6Sample {
  return v6AtTime(run, time).sample;
}

export function nextV6Time(time: number, elapsedS: number, rate: number, endS: number): number {
  if (![time, elapsedS, rate, endS].every(Number.isFinite) || elapsedS < 0 || rate <= 0 || endS < 0) {
    throw new Error("Invalid V6 replay clock");
  }
  return Math.min(endS, Math.max(0, time + elapsedS * rate));
}
