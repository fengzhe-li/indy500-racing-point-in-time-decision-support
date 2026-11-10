import { useEffect, useMemo, useRef, useState } from "react";
import { compareV6, V6Adapter, v6AtTime, type V6Series, type V6Sample } from "./adapters/v6";

type ReplayEntry = { name: string; file: string; status: string };
type ReplayIndex = { schema_version: 2; label: "SIMULATED"; runs: ReplayEntry[] };
const adapter = new V6Adapter();
const replayRoot = "/v6/replays/";
const colors = ["#55d4de", "#ff9c50"];
const units: Record<string, string> = {
  speed_m_s: "m/s", x_m: "m", y_m: "m", steering_command_rad: "rad", yaw_rate_rad_s: "rad/s",
  lateral_accel_m_s2: "m/s²", path_error_m: "m", throttle_command: "", brake_command: "",
};
const labels: Record<string, string> = {
  speed_m_s: "Speed", x_m: "X position", y_m: "Y position", steering_command_rad: "Steering",
  yaw_rate_rad_s: "Yaw rate", lateral_accel_m_s2: "Lateral acceleration", path_error_m: "Tracking error",
  throttle_command: "Throttle", brake_command: "Brake",
};
const number = (sample: V6Sample, field: string) => typeof sample[field] === "number" ? sample[field] as number : null;
const display = (sample: V6Sample, field: string) => {
  const value = number(sample, field);
  return value === null ? "Not exported" : `${value.toFixed(field === "steering_command_rad" || field === "yaw_rate_rad_s" ? 4 : 2)}${units[field] ? ` ${units[field]}` : ""}`;
};

async function fetchJson(url: string): Promise<unknown> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Replay request failed (${response.status})`);
  return response.json();
}
function validateIndex(value: unknown): ReplayIndex {
  if (!value || typeof value !== "object") throw new Error("Invalid V6 replay index");
  const index = value as ReplayIndex;
  if (index.schema_version !== 2 || index.label !== "SIMULATED" || !Array.isArray(index.runs) || !index.runs.length ||
      index.runs.some(run => typeof run.name !== "string" || typeof run.file !== "string" || !/^replays\/[\w.+-]+\.json$/.test(run.file))) {
    throw new Error("Invalid V6 replay index");
  }
  return index;
}

function PositionMap({ a, b, time }: { a: V6Series; b: V6Series; time: number }) {
  const [stateA, stateB] = [v6AtTime(a, time), v6AtTime(b, time)];
  const all = [...a.samples, ...b.samples];
  const xs = all.map(p => Number(p.x_m)), ys = all.map(p => Number(p.y_m));
  const bounds = xs.reduce((result, x, index) => ({
    minX: Math.min(result.minX, x), maxX: Math.max(result.maxX, x),
    minY: Math.min(result.minY, ys[index]), maxY: Math.max(result.maxY, ys[index]),
  }), { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity });
  const { minX, maxX, minY, maxY } = bounds;
  const padX = Math.max(15, (maxX - minX) * .04), padY = Math.max(15, (maxY - minY) * .08);
  const project = (x: number, y: number): [number, number] => [24 + (x - minX + padX) / (maxX - minX + padX * 2) * 752, 18 + (maxY + padY - y) / (maxY - minY + padY * 2) * 285];
  const line = (run: V6Series) => run.samples.map(p => project(Number(p.x_m), Number(p.y_m)).join(",")).join(" ");
  const vehicle = (run: V6Series, sample: V6Sample, side: number) => {
    const [x, y] = project(Number(sample.x_m), Number(sample.y_m));
    const heading = number(sample, "heading_rad") ?? 0;
    const terminalEvent = run.status === "off_track" ? run.events.find(e => e.type === "off_track") : undefined;
    const point = terminalEvent ? project(terminalEvent.x_m, terminalEvent.y_m) : null;
    return <g key={side} data-testid={`v6-marker-${side}`} data-time={sample.sim_time_s} data-x={sample.x_m} data-y={sample.y_m}>
      {point && <><circle cx={point[0]} cy={point[1]} r="9" fill="none" stroke="#ff6976" strokeWidth="2"/><text x={point[0] + 11} y={point[1] - 8} className="v6-event-label">OFF TRACK</text></>}
      <g transform={`translate(${x} ${y}) rotate(${-heading * 180 / Math.PI})`}><path d="M 11 0 L -7 -5 L -3 0 L -7 5 Z" fill={colors[side]} stroke="#091115" strokeWidth="2"/></g>
      <text x={x + 13} y={y - 10} fill={colors[side]} className="v6-car-label">CAR {side === 0 ? "A" : "B"}</text>
    </g>;
  };
  return <svg className="v6-map" viewBox="0 0 800 330" role="img" aria-label="Recorded V6 vehicle positions on the simulated course">
    <polyline points={line(a)} fill="none" stroke="#55d4de" strokeOpacity=".45" strokeWidth="1.5"/>
    <polyline points={line(b)} fill="none" stroke="#ff9c50" strokeOpacity=".45" strokeWidth="1.5"/>
    {vehicle(a, stateA.sample, 0)}{vehicle(b, stateB.sample, 1)}
    <text x="24" y="320" className="v6-map-note">RECORDED CARTESIAN POSITIONS · APPROXIMATE STADIUM · {a.track.length_m.toFixed(0)} m</text>
  </svg>;
}

function TelemetryCard({ run, sample, side, status }: { run: V6Series; sample: V6Sample; side: number; status: string }) {
  return <section className="panel v6-telemetry">
    <div className="panel-title"><h3 style={{ color: colors[side] }}>Car {side === 0 ? "A" : "B"} · {run.label.split(" · ").slice(-1)[0]}</h3><span className="subtle">{status.replace(/_/g, " ").toUpperCase()} · {run.durationS.toFixed(3)} S</span></div>
    <dl>{Object.entries(labels).map(([field, label]) => <div key={field}><dt>{label}</dt><dd>{display(sample, field)}</dd></div>)}</dl>
    <p className="limitation">{status === "in_progress" ? "Recorded replay in progress." : run.reason || (run.status === "completed" ? "Completed successfully." : "Terminal replay event.")}</p>
  </section>;
}

export function V6Explorer() {
  const [index, setIndex] = useState<ReplayIndex>();
  const [selected, setSelected] = useState<[string, string]>(["baseline", "delay_0.6s"]);
  const [runs, setRuns] = useState<[V6Series, V6Series]>();
  const [time, setTime] = useState(0), [playing, setPlaying] = useState(false), [rate, setRate] = useState(1);
  const [error, setError] = useState("");
  const generation = useRef(0);
  useEffect(() => { let live = true; fetchJson(`${replayRoot}index.json`).then(validateIndex).then(value => {
    if (live) { setIndex(value); setSelected(current => [value.runs.some(r => r.name === current[0]) ? current[0] : value.runs[0].name, value.runs.some(r => r.name === current[1]) ? current[1] : value.runs[Math.min(1, value.runs.length - 1)].name]); }
  }).catch(e => { if (live) setError(e instanceof Error ? e.message : "Unable to read V6 replay index"); });
    return () => { live = false; };
  }, []);
  const duration = Math.max(runs?.[0].durationS ?? 0, runs?.[1].durationS ?? 0);
  useEffect(() => {
    if (!index) return;
    const request = ++generation.current; let live = true;
    setPlaying(false); setError("");
    const load = async (name: string) => {
      const entry = index.runs.find(r => r.name === name);
      if (!entry) throw new Error(`Unknown V6 run: ${name}`);
      return adapter.adapt(await fetchJson(`${replayRoot}${entry.file}`));
    };
    Promise.all(selected.map(load)).then(pair => {
      const candidate: [V6Series, V6Series] = [pair[0], pair[1]];
      compareV6(candidate[0], candidate[1]);
      if (live && request === generation.current) { setRuns(candidate); setTime(0); }
    }).catch(e => {
      if (live && request === generation.current) setError(e instanceof Error ? e.message : "Unable to load V6 replays");
    });
    return () => { live = false; };
  }, [index, selected]);
  useEffect(() => {
    if (!playing || !runs) return;
    let previous = performance.now();
    const timer = window.setInterval(() => {
      const now = performance.now(), dt = Math.max(0, (now - previous) / 1000); previous = now;
      setTime(value => Math.min(duration, value + dt * rate));
    }, 50);
    return () => window.clearInterval(timer);
  }, [playing, rate, duration, runs]);
  useEffect(() => { if (playing && time >= duration) setPlaying(false); }, [playing, time, duration]);
  const comparison = useMemo(() => runs ? compareV6(runs[0], runs[1]) : undefined, [runs]);
  const states = comparison?.atTime(time);
  const change = (side: number, name: string) => setSelected(current => side === 0 ? [name, current[1]] : [current[0], name]);
  const restart = () => { setPlaying(false); setTime(0); };
  return <div className="shell v6-explorer">
    <header><div className="brand"><span className="mark">500</span><div><h1>PERFORMANCE EXPLORER</h1><p>DUAL-CAR COMPARISON · V6 VEHICLE DYNAMICS</p></div></div><span className="pill">SIMULATED — V6</span></header>
    <main>
      <section className="intro"><div><div className="eyebrow">ENGINEERING WORKSPACE / V6</div><h2>Replay the run.<br/><em>Follow the dynamics.</em></h2></div><p>Two authentic schema-2 V6 recordings on one elapsed-time clock. Each vehicle stops at its own recorded terminal event.</p></section>
      <div className="notice v6-notice">SIMULATED — V6 · Approximate stadium and illustrative vehicle model. V6 remains a separate simulation domain from V5 and historical timing; this view makes no cross-mode lap-time or Track Dominance comparisons.</div>
      <section className="panel v6-selectors"><label>CAR A<select aria-label="Car A V6 replay" value={selected[0]} disabled={!index} onChange={e => change(0, e.target.value)}>{(index?.runs ?? []).map(run => <option key={run.name} value={run.name}>{run.name} · {run.status}</option>)}</select></label><label>CAR B<select aria-label="Car B V6 replay" value={selected[1]} disabled={!index} onChange={e => change(1, e.target.value)}>{(index?.runs ?? []).map(run => <option key={run.name} value={run.name}>{run.name} · {run.status}</option>)}</select></label><span>Same validated V6 coordinate system and stadium geometry required.</span></section>
      {error && <p className="warning" role="alert">V6 replay unavailable: {error}</p>}
      {!runs && !error && <p role="status">Loading authentic V6 schema-2 replays…</p>}
      {runs && states && <>
        <section className="panel v6-replay-panel"><div className="panel-title"><h3>Recorded vehicle paths</h3><span className="subtle">SHARED TIME · {time.toFixed(3)} / {duration.toFixed(3)} S</span></div>
          <PositionMap a={runs[0]} b={runs[1]} time={time}/>
          <div className="v6-legend"><span style={{ color: colors[0] }}>● CAR A · {runs[0].status.replace(/_/g, " ").toUpperCase()}</span><span style={{ color: colors[1] }}>● CAR B · {runs[1].status.replace(/_/g, " ").toUpperCase()}</span><span>○ OFF-TRACK TERMINAL EVENT</span></div>
          <div className="replay-controls"><button className="primary" aria-label={playing ? "Pause V6 replay" : "Play V6 replay"} onClick={() => { if (time >= duration) setTime(0); setPlaying(p => !p); }}>{playing ? "Ⅱ PAUSE" : "▶ PLAY BOTH"}</button><button aria-label="Restart V6 replay" onClick={restart}>↺ RESTART</button><label className="speed-control">SPEED<select aria-label="V6 playback speed" value={rate} onChange={e => setRate(Number(e.target.value))}>{[.25, .5, 1, 2, 5, 10].map(v => <option key={v} value={v}>{v}×</option>)}</select></label><input aria-label="V6 replay time" type="range" min="0" max={duration} step="any" value={Math.min(time, duration)} onChange={e => { setPlaying(false); setTime(Number(e.target.value)); }}/></div>
          <p className="limitation">Positions are linearly interpolated between recorded display samples for animation; held controls and flags follow the validated adapter. No sample is extrapolated beyond either run's terminal time.</p>
        </section>
        <div className="v6-telemetry-grid"><TelemetryCard run={runs[0]} sample={states.a.sample} side={0} status={states.a.status}/><TelemetryCard run={runs[1]} sample={states.b.sample} side={1} status={states.b.status}/></div>
      </>}
    </main>
  </div>;
}
