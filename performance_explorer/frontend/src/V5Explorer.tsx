import { useEffect, useMemo, useRef, useState, type PointerEvent } from "react";
import { V5ScenarioForm, requestV5, type ScenarioRequest } from "./V5ScenarioForm";
import baseline from "./data/v5-baseline.json";
import lowGrip from "./data/v5-low-grip.json";
import source from "../../contracts/v5-replay-1/SOURCE.json";
import { compareV5, trackDominance, V5Adapter, v5PositionAtDistance, type V5Series, v5AtTime, v5TimeAtDistance } from "./adapters/v5";
import { tickReplay, type ReplayState } from "./domain/replay";

type Side = "A" | "B";
type Run = { id: string; name: string; series: V5Series; lineage: string };
const adapter = new V5Adapter();
const presets: Run[] = [
  { id: "baseline", name: "Accepted baseline", series: adapter.adapt(baseline), lineage: `V5 ${source.upstreamCommit} · SHA-256 ${source.files["frontend/src/data/v5-baseline.json"].sha256}` },
  { id: "low-grip", name: "Grip −25% scenario", series: adapter.adapt(lowGrip), lineage: `V5 ${source.upstreamCommit} · SHA-256 ${source.files["frontend/src/data/v5-low-grip.json"].sha256}` },
];
const format = (n: number, digits = 4) => n.toFixed(digits);
const signed = (n: number) => `${n > 0 ? "+" : ""}${format(n)}`;
const colors = { A: "#55d4de", B: "#ff9c50", tie: "#849298" };

/** Only consumes exported or API-returned simulations; no solver here. */
export function V5Explorer() {
  const [runs, setRuns] = useState<[Run, Run]>([presets[0], presets[1]]);
  const [imports, setImports] = useState<Partial<Record<Side, Run>>>({});
  const [errors, setErrors] = useState<Partial<Record<Side, string>>>({});
  const [loading, setLoading] = useState<Partial<Record<Side, boolean>>>({});
  const epochs = useRef({ A: 0, B: 0 });
  const requests = useRef<Partial<Record<Side, AbortController>>>({});
  useEffect(() => () => { epochs.current.A++; epochs.current.B++; requests.current.A?.abort(); requests.current.B?.abort(); }, []);
  const select = (side: Side, run: Run) => {
    epochs.current[side]++;
    requests.current[side]?.abort();
    setLoading(s => ({ ...s, [side]: false }));
    setErrors(s => ({ ...s, [side]: "" }));
    setRuns(s => side === "A" ? [run, s[1]] : [s[0], run]);
  };
  const importRun = async (side: Side, file?: File) => {
    if (!file) return;
    const epoch = ++epochs.current[side];
    requests.current[side]?.abort();
    setLoading(s => ({ ...s, [side]: true }));
    setErrors(s => ({ ...s, [side]: "" }));
    try {
      if (file.size > 10 * 1024 * 1024) throw new Error("Replay exceeds the 10 MiB import limit.");
      const content = await file.text();
      const series = adapter.adapt(JSON.parse(content));
      const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(content));
      const hash = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, "0")).join("");
      if (epoch !== epochs.current[side]) return;
      const run: Run = { id: `import-${side}-${epoch}`, name: file.name, series,
        lineage: `User-imported export · producer commit unverified · SHA-256 ${hash}` };
      setImports(s => ({ ...s, [side]: run }));
      setRuns(s => side === "A" ? [run, s[1]] : [s[0], run]);
    } catch (error) {
      if (epoch === epochs.current[side]) setErrors(s => ({ ...s, [side]: `${error instanceof Error ? error.message : "Import failed"} Last valid configuration retained.` }));
    } finally {
      if (epoch === epochs.current[side]) setLoading(s => ({ ...s, [side]: false }));
    }
  };
  const recompute = async (side: Side, request?: ScenarioRequest) => {
    const epoch = ++epochs.current[side];
    requests.current[side]?.abort();
    const controller = new AbortController(); requests.current[side] = controller;
    const timeout = window.setTimeout(() => controller.abort(), 30000);
    setLoading(s => ({ ...s, [side]: true })); setErrors(s => ({ ...s, [side]: "" }));
    try {
      const series = adapter.adapt(await requestV5(request, controller.signal));
      if (epoch !== epochs.current[side]) return;
      const run: Run = { id: `api-${side}-${epoch}`, name: request ? `API scenario ${side} · ${epoch}` : `API baseline ${side} · ${epoch}`, series,
        lineage: `Actual SIMULATED API output · ${request ? "POST /api/v5/simulate" : "GET /api/v5/baseline"} · runtime producer commit unverified · request ${JSON.stringify(request ?? {})}` };
      setImports(s => ({ ...s, [side]: run }));
      setRuns(s => side === "A" ? [run, s[1]] : [s[0], run]);
    } catch (error) {
      if (epoch === epochs.current[side]) setErrors(s => ({ ...s, [side]: `${controller.signal.aborted ? "V5 service timed out" : error instanceof Error ? error.message : "V5 request failed"}. Last valid configuration retained. Check the V5 service connection.` }));
    } finally {
      window.clearTimeout(timeout);
      if (epoch === epochs.current[side]) setLoading(s => ({ ...s, [side]: false }));
    }
  };
  const compatible = useMemo(() => {
    try { return { comparison: compareV5(runs[0].series, runs[1].series), error: "" }; }
    catch (error) { return { comparison: null, error: (error as Error).message }; }
  }, [runs]);
  return <div className="shell v5-explorer">
    <header><div className="brand"><span className="mark">500</span><div><h1>PERFORMANCE EXPLORER</h1><p>DUAL-CAR COMPARISON · V5</p></div></div><span className="pill">SIMULATED</span></header>
    <main><section className="intro"><div><div className="eyebrow">ENGINEERING WORKSPACE / V5</div><h2>Two configurations.<br /><em>One elapsed-time clock.</em></h2></div>
      <p>Actual V5 quasi-steady exports on an assumed oval. Generic vehicle scenarios; no individual-car prediction accuracy, GPS or control telemetry is implied.</p></section>
      <section className="panel controls"><div className="control-head"><h3>Independent simulated configurations</h3><span className="pill">v5-replay-1</span></div>
        <div className="v5-config-grid">{(["A", "B"] as Side[]).map((side, i) => {
          const options = [...presets, ...(imports[side] ? [imports[side]!] : [])];
          return <div key={side} className={`car-card ${i === 0 ? "cyan" : "orange"}`}>
            <label className="selector">CAR {side} · SIMULATED CONFIGURATION<select aria-label={`Car ${side} configuration`} value={runs[i].id} onChange={e => select(side, options.find(r => r.id === e.target.value)!)}>
              {options.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
            </select></label>
            <p>{format(runs[i].series.simulation.lap_time_s)} s · {format(runs[i].series.simulation.average_speed_mph, 3)} mph average</p>
            <V5ScenarioForm key={runs[i].id} side={side} series={runs[i].series} busy={!!loading[side]} submit={request => { void recompute(side, request); }} />
            <label className="import-control">Import Car {side} V5 replay JSON<input aria-label={`Import Car ${side} V5 replay JSON`} type="file" accept=".json,application/json" onChange={e => { void importRun(side, e.target.files?.[0]); e.target.value = ""; }} /></label>
            {loading[side] && <p role="status">Loading Car {side} · last valid run remains visible…</p>}
            {errors[side] && <p role="alert">{errors[side]}</p>}
            <details><summary>Inputs & provenance · Car {side}</summary><p className="lineage">{runs[i].lineage}</p>
              <p>{runs[i].series.simulation.origin}</p>
              <InputSnapshot series={runs[i].series} />
              {Object.entries(runs[i].series.simulation.provenance).map(([k, v]) => <p key={k}><b>{k}: </b>{v}</p>)}
            </details>
          </div>;
        })}</div>
        <p className="limitation">Choose either export independently, including identical runs, or import another V5 output. Recompute uses the existing V5 API and requires a connected V5 service. Bundled exports and local imports work without it. Historical timing and V6 channels remain separate. V5 has no demonstrated aggregate MAE improvement over the training-median baseline; these are engineering scenarios, not individual-car predictions.</p>
      </section>
      {compatible.comparison ? <SimulationComparison key={`${runs[0].id}/${runs[1].id}`} runs={runs} comparison={compatible.comparison} /> :
        <p role="alert" className="warning">{compatible.error}. Comparison and replay disabled. Select exports with matching origin, geometry and segment boundaries.</p>}
      <footer>SIMULATED · V5 quasi-steady model · Assumed path and vehicle inputs · No GPS, ECU, throttle, steering or brake-pressure data · No V6 dynamics</footer>
    </main>
  </div>;
}

const inputUnits: Record<string, string> = { mass_kg: "kg", cd_a_m2: "m²", cl_a_m2: "m²", power_w: "W", drive_force_max_n: "N", brake_force_max_n: "N", max_speed_mps: "m/s", air_temperature_c: "°C", track_temperature_c: "°C", pressure_pa: "Pa", reference_track_temperature_c: "°C", grip_per_track_temp_k: "K⁻¹", tire_mu: "dimensionless", rolling_resistance_coefficient: "dimensionless" };
function InputSnapshot({ series }: { series: V5Series }) {
  return <div className="input-snapshot">{Object.entries({ ...series.scenario.vehicle, ...series.scenario.environment }).map(([key, value]) =>
    <div key={key}><span>{key}</span><span>{value === null ? "unavailable / no correction" : `${value} ${inputUnits[key] ?? "(see V5 input definition)"}`}</span></div>)}</div>;
}

type Comparison = ReturnType<typeof compareV5>;
function SimulationComparison({ runs, comparison }: { runs: [Run, Run]; comparison: Comparison }) {
  const r = runs[0].series.simulation, length = r.track_length_m;
  const [play, setPlay] = useState<ReplayState>({ playing: false, elapsedS: 0, speed: 1, durationS: comparison.durationS });
  const [highlight, setHighlight] = useState<number | null>(null);
  const [inspection, setInspection] = useState<number | null>(null);
  useEffect(() => {
    if (!play.playing) return;
    let previous = performance.now();
    const timer = window.setInterval(() => {
      const now = performance.now(); const dt = (now - previous) / 1000; previous = now;
      setPlay(s => tickReplay(s, dt));
    }, 50);
    return () => window.clearInterval(timer);
  }, [play.playing]);
  const state = comparison.atTime(play.elapsedS), distance = state.a.distanceM;
  const currentRegion = r.segments.findIndex((s, i) => distance < s.start_m + s.distance_m || i === r.segments.length - 1);
  const inspectedRegion = inspection === null ? null : r.segments.findIndex((s, i) => inspection < s.start_m + s.distance_m || i === r.segments.length - 1);
  const active = highlight ?? inspectedRegion ?? currentRegion;
  const region = comparison.regions[active];
  const regionSum = (corners: boolean) => comparison.regions.reduce((sum, item, i) => sum + ((r.segments[i].radius_m !== null) === corners ? item.incrementalDeltaS : 0), 0);
  const delta = comparison.deltaAt(distance), dominance = trackDominance(comparison.regions);
  const seek = (t: number) => setPlay(s => ({ ...s, playing: false, elapsedS: Math.max(0, Math.min(comparison.durationS, t)) }));
  const seekDistance = (d: number) => { setHighlight(null); setInspection(null); seek(comparison.seekTimeAtDistance(d)); };
  // Uniform coordinate scaling preserves the assumed geometry's aspect ratio.
  const pathPoints = Array.from({ length: 401 }, (_, i) => v5PositionAtDistance(r, i * length / 400));
  const xs = pathPoints.map(p => p[0]), ys = pathPoints.map(p => p[1]);
  const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
  const scale = Math.min(560 / (maxX - minX), 230 / (maxY - minY));
  const project = ([x, y]: [number, number]) => [320 + (x - (minX + maxX) / 2) * scale, 145 - (y - (minY + maxY) / 2) * scale];
  const path = (start: number, end: number) => Array.from({ length: 51 }, (_, i) => project(v5PositionAtDistance(r, start + (end - start) * i / 50)).join(",")).join(" ");
  const lapDelta = runs[1].series.simulation.lap_time_s - r.lap_time_s;
  return <>
    <div className="grid">
      <section className="panel replay-panel"><div className="panel-title"><h3>Shared-clock replay</h3><span className="subtle">SIMULATED · ASSUMED GEOMETRY</span></div>
        <svg className="v5-track" viewBox="0 0 640 300" role="img" aria-label="Two simulated vehicles on the same assumed closed oval">
          {comparison.regions.map((region, i) => <polyline key={region.name} data-testid={`track-segment-${i}`} data-highlighted={active === i} points={path(region.startM, region.endM)} fill="none"
            stroke={colors[region.winner as keyof typeof colors]} strokeWidth={active === i ? 12 : 7} opacity={active === i ? 1 : .55}
            onPointerEnter={() => setHighlight(i)} onPointerLeave={() => setHighlight(null)} onClick={() => seekDistance(region.startM)}><title>{region.name}: {region.winner === "tie" ? "tie" : `Car ${region.winner} gains`} · B − A {signed(region.incrementalDeltaS)} s</title></polyline>)}
          {(["A", "B"] as Side[]).map(side => {
            const car = side === "A" ? state.a : state.b; const [x, y] = project(car.positionM);
            return <g key={side} data-testid={`sim-car-${side}`} data-distance={car.distanceM} data-complete={car.complete} transform={`translate(${x} ${y})`}>
              <circle r={side === "A" ? 12 : 7} fill={side === "B" ? colors.B : "#0c1318"} stroke={colors[side]} strokeWidth="3" />
              <text y={side === "A" ? -17 : 26} textAnchor="middle" fill={colors[side]} fontSize="14">{side}{car.complete ? " ✓" : ""}</text>
            </g>;
          })}
          {inspection !== null && <circle data-testid="track-inspection-point" cx={project(v5PositionAtDistance(r, inspection))[0]} cy={project(v5PositionAtDistance(r, inspection))[1]} r="5" fill="#fff"><title>Inspection point {format(inspection, 2)} m; not a third vehicle</title></circle>}
          <text x="320" y="130" textAnchor="middle" fill="#e6ecee" fontSize="16">ASSUMED CLOSED PATH</text>
          <text x="320" y="153" textAnchor="middle" fill="#aebbc0" fontSize="12">{format(length, 3)} m · same origin for both cars</text>
          <text x="320" y="175" textAnchor="middle" fill="#aebbc0" fontSize="12">{comparison.regions[active].name}</text>
        </svg>
        <div className="timeline"><label>Shared elapsed time (s)<input aria-label="Simulation timeline" type="range" min="0" max={comparison.durationS} step="any" value={play.elapsedS} onChange={e => seek(Number(e.target.value))} /></label>
          <div className="timeline-bottom"><span>{format(play.elapsedS)} s</span><span>Both complete at {format(comparison.durationS)} s</span></div></div>
        <div className="replay-controls"><button className="primary" aria-label={play.playing ? "Pause simulation" : "Play simulation"} onClick={() => setPlay(s => ({ ...s, elapsedS: s.elapsedS >= s.durationS ? 0 : s.elapsedS, playing: !s.playing }))}>{play.playing ? "Ⅱ PAUSE" : "▶ PLAY BOTH"}</button>
          <button onClick={() => { setHighlight(null); seek(0); }}>Restart simulation</button>
          <label className="speed-control">RATE<select aria-label="Simulation playback speed" value={play.speed} onChange={e => setPlay(s => ({ ...s, speed: Number(e.target.value) }))}>{[.5, 1, 2, 4, 10].map(v => <option key={v} value={v}>{v}×</option>)}</select></label></div>
        {(["A", "B"] as Side[]).map(side => { const car = side === "A" ? state.a : state.b; return <p key={side} data-testid={`sim-status-${side}`}>Car {side}: {format(car.distanceM, 2)} m · {format(car.speedMps, 2)} m/s · {car.complete ? "complete (marker clamped; speed is the simulated endpoint value)" : "in progress"}</p>; })}
        <p className="limitation">Each car follows its own simulated time–distance mapping. Completed markers stay at L, even though L and 0 share a drawing position. No wrapping or physical stopped-vehicle dynamics are inferred.</p>
      </section>
      <section className="panel delta-panel"><h3>Equal-distance time comparison · SIMULATED</h3>
        <div className="delta-readout"><strong className={delta < 0 ? "orange-text" : "cyan-text"}>{signed(delta)}<small> s</small></strong></div>
        <p data-testid="running-delta">B − A at {format(distance, 2)} m (Car A cursor). Positive: B takes longer. Negative: B takes less time.</p>
        <p>Full-lap B − A: <b>{signed(lapDelta)} s</b></p>
        <DistanceGraph label="Running delta graph" points={comparison.runningDelta.map(p => [p.distanceM, p.deltaS])} length={length} distance={distance} otherDistance={state.b.distanceM} seek={seekDistance} inspect={setInspection} inspection={inspection} unit="s · B − A" />
        <p className="limitation">Delta compares each run's arrival time at the same distance. It is not the time separation of the two markers at this instant. Graph seeking places Car A at the selected distance and places Car B using that same elapsed time.</p>
        <div className="insight"><p>At {format(distance, 2)} m, A takes {format(comparison.seekTimeAtDistance(distance))} s; B takes {format(comparison.seekTimeAtDistance(distance) + delta)} s. Difference: {signed(delta)} s.<small>Calculated with each export's constant-acceleration cells. Interval differences describe the simulated result; they do not establish a causal effect or real-car performance.</small></p></div>
      </section>
    </div>
    <section className="panel v5-speed-panel"><h3>Distance-aligned speed profiles · SIMULATED</h3>
      <DistanceGraph label="Speed profile graph" points={comparison.speedComparison.map(p => [p.distanceM, p.aMps])} second={comparison.speedComparison.map(p => [p.distanceM, p.bMps])} length={length} distance={distance} otherDistance={state.b.distanceM} seek={seekDistance} inspect={setInspection} inspection={inspection} unit="m/s" />
      {inspection !== null && <p role="status">Inspection at {format(inspection, 2)} m: A {format(v5SpeedAt(runs[0].series, inspection), 3)} m/s; B {format(v5SpeedAt(runs[1].series, inspection), 3)} m/s; arrival delta B − A {signed(comparison.deltaAt(inspection))} s. White point marks the inspected assumed track position.</p>}
      <p className="chart-legend"><span className="legend-a">● A speed / solid A cursor</span><span className="legend-b">● B speed / dashed B cursor</span></p>
      <p>At A's distance: speed B − A = {format(v5SpeedAt(runs[1].series, distance) - v5SpeedAt(runs[0].series, distance), 3)} m/s.</p>
      <p className="limitation">Profiles use a common distance grid, including both meshes. Click or drag either graph; arrow keys seek 25 m, Home/End seek 0/L. Calculations use exact cell kinematics; connecting graph samples are a drawing approximation.</p>
    </section>
    <section className="panel engineering-insights"><h3>Engineering comparison · SIMULATED</h3>
      <p>Car A: {runs[0].name} · Car B: {runs[1].name}</p>
      <p data-testid="region-insight">{region.name} [{format(region.startM, 2)}, {format(region.endM, 2)} m]: {region.winner === "tie" ? "Equal interval times" : `Car ${region.winner} gains ${format(Math.abs(region.incrementalDeltaS))} seconds`}. A: {format(region.aTimeS)} s; B: {format(region.bTimeS)} s.</p>
      <p>Cumulative B − A at this region's exit: {signed(region.cumulativeDeltaS)} s. Full lap [0, {format(length, 2)} m]: {signed(lapDelta)} s.</p>
      <p>Sum across corner regions: B − A {signed(regionSum(true))} s. Sum across straight regions: {signed(regionSum(false))} s. These signed contributions sum to the lap difference; offsets between regions can occur.</p>
      <p>Applied tire friction: A {runs[0].series.scenario.vehicle.tire_mu}, B {runs[1].series.scenario.vehicle.tire_mu} (dimensionless). Other inputs may also differ; inspect both applied snapshots.</p>
      <p className="limitation">Evidence: the two validated V5 exports, matched assumed segment boundaries and constant-acceleration cell arrival times. These are measured differences within the model outputs, not isolated causal effects or observed corner advantages. Hover a chart or region to inspect it; click or use keyboard controls to seek.</p>
    </section>
    <section className="panel v5-dominance"><h3>Track Dominance · SIMULATED segment-time advantage</h3>
      <p>{(["A", "B", "tie"] as const).map(side => <span key={side} style={{ color: colors[side], marginRight: 16 }}>{side === "tie" ? "Tied" : `Car ${side}`}: {format(dominance[side].percent, 1)}% ({format(dominance[side].distanceM, 1)} m) </span>)}</p>
      <p className="limitation">Length-weighted share of whole matched segments won by interval time. Ties use |B − A| &lt; 10⁻⁹ s. This is not pointwise speed dominance; it depends on the segment partition.</p>
      <div className="v5-segment-table"><div className="table-row table-head"><span>SEGMENT</span><span>A (s)</span><span>B (s)</span><span>B − A (s)</span><span>ADVANTAGE</span></div>
        {comparison.regions.map((region, i) => <button key={region.name} aria-label={`Inspect ${region.name}`} className={`table-row ${active === i ? "active-row" : ""}`} onMouseEnter={() => setHighlight(i)} onMouseLeave={() => setHighlight(null)} onFocus={() => setHighlight(i)} onBlur={() => setHighlight(null)} onClick={() => seekDistance(region.startM)}>
          <span>{region.name}</span><span>{format(region.aTimeS)}</span><span>{format(region.bTimeS)}</span><span>{signed(region.incrementalDeltaS)}</span><span style={{ color: colors[region.winner as keyof typeof colors] }}>{region.winner === "tie" ? "Tie" : `Car ${region.winner}`}</span>
        </button>)}</div>
      <p>Sum of incremental B − A: {signed(comparison.regions.reduce((sum, region) => sum + region.incrementalDeltaS, 0))} s = full-lap delta. Select a row to seek its entry; hover or focus to highlight its track segment.</p>
    </section>
  </>;
}

// Reuse the upstream kinematic inverse, never linear speed interpolation.
function v5SpeedAt(series: V5Series, distance: number) { return v5AtTime(series.simulation, v5TimeAtDistance(series.simulation, distance)).speedMps; }

function DistanceGraph({ label, points, second, length, distance, otherDistance, seek, inspect, inspection, unit }: {
  label: string; points: number[][]; second?: number[][]; length: number; distance: number; otherDistance: number; seek: (d: number) => void; inspect: (d: number | null) => void; inspection: number | null; unit: string;
}) {
  let lo = Infinity, hi = -Infinity;
  for (const [, v] of points) { if (v < lo) lo = v; if (v > hi) hi = v; }
  if (second) for (const [, v] of second) { if (v < lo) lo = v; if (v > hi) hi = v; }
  const padding = Math.max((hi - lo) * .12, .05);
  const x = (d: number) => 60 + 540 * d / length;
  const y = (v: number) => 175 - 145 * (v - lo + padding) / (hi - lo + 2 * padding);
  const line = (p: number[][]) => p.map(([d, v]) => `${x(d)},${y(v)}`).join(" ");
  const fromPointer = (e: PointerEvent<SVGSVGElement>, click = false) => {
    const rect = e.currentTarget.getBoundingClientRect();
    if (rect.width > 0) (click ? seek : inspect)(Math.max(0, Math.min(length, ((e.clientX - rect.left) * 640 / rect.width - 60) / 540 * length)));
  };
  return <svg className="v5-graph" viewBox="0 0 640 210" preserveAspectRatio="none" role="slider" tabIndex={0} aria-label={label} aria-valuemin={0} aria-valuemax={length} aria-valuenow={distance} aria-valuetext={`${format(distance, 2)} metres; Car A distance`}
    onPointerDown={e => { e.currentTarget.setPointerCapture?.(e.pointerId); fromPointer(e, true); }} onPointerMove={e => fromPointer(e, e.buttons === 1)} onPointerLeave={() => inspect(null)}
    onKeyDown={e => { const d = e.key === "Home" ? 0 : e.key === "End" ? length : ["ArrowRight", "ArrowUp"].includes(e.key) ? Math.min(length, distance + 25) : ["ArrowLeft", "ArrowDown"].includes(e.key) ? Math.max(0, distance - 25) : null; if (d !== null) { e.preventDefault(); seek(d); } }}>
    {inspection !== null && <line data-testid={`${label}-inspection`} x1={x(inspection)} x2={x(inspection)} y1="25" y2="178" stroke="#ffffff" strokeDasharray="2 3" />}
    {[lo, (lo + hi) / 2, hi].map((v, i) => <g key={i}><line x1="60" x2="600" y1={y(v)} y2={y(v)} stroke="#26343b" /><text className="graph-y-label" x="54" y={y(v) + 4} textAnchor="end" fill="#aebbc0" fontSize="11">{format(v, 2)}</text></g>)}
    <text x="60" y="15" fill="#aebbc0" fontSize="11">{unit}</text>
    <polyline points={line(points)} fill="none" stroke={colors.A} strokeWidth="2" />
    {second && <polyline points={line(second)} fill="none" stroke={colors.B} strokeWidth="2" />}
    <line data-testid={`${label}-cursor-A`} x1={x(distance)} x2={x(distance)} y1="22" y2="180" stroke={colors.A} />
    <line x1={x(otherDistance)} x2={x(otherDistance)} y1="22" y2="180" stroke={colors.B} strokeDasharray="5 4" />
    {[0, length / 2, length].map(d => <text key={d} x={x(d)} y="202" textAnchor={d === 0 ? "start" : d === length ? "end" : "middle"} fill="#aebbc0" fontSize="11">{format(d, 1)} m</text>)}
  </svg>;
}
