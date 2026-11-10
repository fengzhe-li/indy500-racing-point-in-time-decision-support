import { useState } from "react";
import type { V5Series } from "./adapters/v5";

// Bounds and supported fields from the published V5 API (8879c30).
export const scenarioFields = [
  ["vehicle", "mass_kg", "Mass (kg)", 600, 1100],
  ["vehicle", "cd_a_m2", "Drag area (m²)", .6, 1.6],
  ["vehicle", "cl_a_m2", "Downforce area (m²)", .5, 2.5],
  ["vehicle", "tire_mu", "Tire friction coefficient", 1.1, 2.2],
  ["vehicle", "power_w", "Power (W)", 400000, 1100000],
  ["environment", "air_temperature_c", "Air temperature (°C)", 5, 45],
  ["environment", "track_temperature_c", "Track temperature (°C)", 15, 65],
] as const;
export type ScenarioRequest = { vehicle: Record<string, number>; environment: Record<string, number> };
export function V5ScenarioForm({ side, series, busy, submit }: {
  side: string; series: V5Series; busy: boolean; submit: (request?: ScenarioRequest) => void;
}) {
  const [draft, setDraft] = useState<Record<string, string>>(() => Object.fromEntries(scenarioFields.map(([group, key]) => [key, String(series.scenario[group][key] ?? "")])));
  return <form className="scenario-form" aria-label={`Car ${side} scenario`} onSubmit={e => {
    e.preventDefault();
    const request: ScenarioRequest = { vehicle: {}, environment: {} };
    for (const [group, key, , min, max] of scenarioFields) {
      const value = Number(draft[key]);
      if (!draft[key] || !Number.isFinite(value) || value < min || value > max) return;
      request[group][key] = value;
    }
    submit(request);
  }}>
    <div className="scenario-fields">{scenarioFields.map(([, key, label, min, max]) => <label key={key}>{label}<input aria-label={`Car ${side} ${label}`} type="number" required step="any" min={min} max={max} value={draft[key]} onChange={e => setDraft(s => ({ ...s, [key]: e.target.value }))} /></label>)}</div>
    <div className="scenario-actions"><button type="submit">{busy ? `Recompute Car ${side} again` : `Recompute Car ${side}`}</button><button type="button" onClick={() => submit()}>Load API baseline {side}</button></div>
    <p className="limitation">Draft inputs apply on recompute. Other parameters use the service baseline, even for imported runs. Applied inputs and output provenance are shown below. Blank or out-of-range values require correction.</p>
  </form>;
}

export async function requestV5(request: ScenarioRequest | undefined, signal: AbortSignal): Promise<unknown> {
  const response = await fetch(request ? "/api/v5/simulate" : "/api/v5/baseline", {
    method: request ? "POST" : "GET", signal,
    ...(request ? { headers: { "Content-Type": "application/json" }, body: JSON.stringify(request) } : {}),
  });
  if (!response.ok) {
    let message = `V5 service HTTP ${response.status}`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message += `: ${body.detail}`;
      else if (Array.isArray(body.detail)) message += `: ${body.detail.map((d: { msg?: string }) => d.msg ?? "Invalid input").join("; ")}`;
    } catch { /* Proxy errors can be plain text. */ }
    throw new Error(message);
  }
  return response.json();
}
