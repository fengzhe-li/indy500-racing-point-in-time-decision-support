import { useEffect, useMemo, useState } from "react";
import data from "./data/historical-attempts-v1.json";
import type { HistoricalAttempt } from "./domain/contract";
import { validateHistoricalData } from "./adapters/historical";
import { completedLaps, historicalComparison, tickReplay, type ReplayState } from "./domain/replay";

const fmt = (n: number, d = 4) => n.toFixed(d);
const attemptLabel = (r: HistoricalAttempt) => r.attempt === null ? `Order unknown · ID ${r.attemptId.slice(0, 8)}` : `Attempt ${r.attempt}`;
function Selector({ label, value, values, onChange, labels }: {
  label: string; value: string; values: string[]; onChange: (value: string) => void; labels?: (value: string) => string;
}) {
  return <label className="selector"><span>{label}</span><select aria-label={label} value={value} onChange={e => onChange(e.target.value)}>
    {values.map(v => <option key={v} value={v}>{labels ? labels(v) : v}</option>)}
  </select></label>;
}
export function App({ dataset = data }: { dataset?: unknown }) {
  if (!validateHistoricalData(dataset)) return <p role="alert">Historical dataset failed schema validation.</p>;
  if (!dataset.rows.length) return <p role="status">No retained complete attempts available.</p>;
  return <Explorer rows={dataset.rows} />;
}
function Explorer({ rows }: { rows: HistoricalAttempt[] }) {
  const years = [...new Set(rows.map(r => String(r.year)))].sort();
  const [year, setYear] = useState(years[years.length - 1]);
  const sessions = [...new Set(rows.filter(r => String(r.year) === year).map(r => r.sessionId))];
  const [sessionChoice, setSession] = useState("");
  const session = sessions.includes(sessionChoice) ? sessionChoice : sessions[0];
  const options = useMemo(() => rows.filter(r => r.sessionId === session).sort((a, b) =>
    a.driver.localeCompare(b.driver) || (a.attempt ?? Infinity) - (b.attempt ?? Infinity) || a.attemptId.localeCompare(b.attemptId)), [rows, session]);
  const [idA, setIdA] = useState(""), [idB, setIdB] = useState("");
  const a = options.find(r => r.attemptId === idA) ?? options[0];
  const b = options.find(r => r.attemptId === idB) ?? options.find(r => r.attemptId !== a.attemptId) ?? a;
  const comparison = useMemo(() => historicalComparison(a, b), [a, b]);
  const { aTimes, bTimes, count, duration, deltaAt, seekTime } = comparison;
  const [play, setPlay] = useState<ReplayState>({ playing: false, elapsedS: 0, durationS: duration, speed: 1 });
  useEffect(() => { setPlay(s => ({ ...s, playing: false, elapsedS: 0, durationS: duration })); }, [a.attemptId, b.attemptId, duration]);
  useEffect(() => {
    if (!play.playing) return;
    let previous = performance.now();
    const timer = window.setInterval(() => {
      const now = performance.now(), dt = (now - previous) / 1000;
      previous = now;
      setPlay(s => tickReplay(s, dt));
    }, 50);
    return () => window.clearInterval(timer);
  }, [play.playing]);
  const aLap = completedLaps(aTimes, play.elapsedS), bLap = completedLaps(bTimes, play.elapsedS);
  const lap = Math.min(aLap, bLap, count), delta = deltaAt(lap)!;
  const seek = (time: number) => setPlay(s => ({ ...s, playing: false, elapsedS: Math.max(0, Math.min(duration, time)) }));
  const seekLap = (n: number) => seek(seekTime(n));
  const label = (key: string) => { const r = options.find(x => x.attemptId === key)!; return `#${r.carNumber} · ${r.driver} · ${attemptLabel(r)}`; };
  const lead = Math.abs(delta) < .00005 ? "TIED AT BOUNDARY" : delta < 0 ? "CAR B AHEAD" : "CAR A AHEAD";
  return <div className="shell">
    <header><div className="brand"><span className="mark">500</span><div><h1>PERFORMANCE EXPLORER</h1><p>DUAL-CAR COMPARISON · HISTORICAL TIMING</p></div></div><div className="header-tag"><i /> OBSERVED DATA MODE</div></header>
    <main>
      <section className="intro"><div><div className="eyebrow">ENGINEERING WORKSPACE / HISTORICAL</div><h2>Compare the run.<br /><em>Read the evidence.</em></h2></div>
        <p>Retained four-lap qualifying results. Official lap durations and four-lap average speeds, with replay restricted to recorded lap boundaries.</p></section>
      <section className="controls panel"><div className="control-head"><h3>Choose two attempts</h3><span className="pill">OBSERVED · {year} · {options.length} RETAINED COMPLETE ATTEMPTS</span></div>
        <div className="select-grid">
          <Selector label="YEAR" value={year} values={years} onChange={setYear} />
          <Selector label="SESSION" value={session} values={sessions} onChange={setSession} />
          <Selector label="CAR A · DRIVER / ATTEMPT" value={a.attemptId} values={options.map(r => r.attemptId)} onChange={setIdA} labels={label} />
          <Selector label="CAR B · DRIVER / ATTEMPT" value={b.attemptId} values={options.map(r => r.attemptId)} onChange={setIdB} labels={label} />
        </div>
        <div className="car-pair"><CarCard side="A" row={a} /><div className="versus">VS</div><CarCard side="B" row={b} /></div>
        <p className="limitation">Unknown attempt order does not mean missing timing. Stable record IDs identify these attempts without assigning a chronological number.</p>
      </section>
      <div className="grid">
        <section className="panel replay-panel">
          <div className="panel-title"><h3>Four-lap progression</h3><span className="subtle">LAP BOUNDARY ONLY</span></div>
          <div className="track-wrap"><BoundaryReplay aLap={aLap} bLap={bLap} count={count} lap={lap} delta={delta} />
            <div className="track-caption"><span>TIMING BOUNDARIES · NOT A TRACK MAP</span><span>2.5 MI PER LAP</span></div></div>
          <div className="timeline"><div className="lap-markers">{Array.from({ length: count + 1 }, (_, i) =>
            <button key={i} aria-label={`Seek to lap ${i}`} className={lap === i ? "selected" : ""} onClick={() => seekLap(i)}>{i ? `LAP ${i}` : "START"}</button>)}</div>
            <input aria-label="Replay timeline" type="range" min="0" max={duration} step="0.0001" value={play.elapsedS} onChange={e => seek(Number(e.target.value))} />
            <div className="timeline-bottom"><span>ELAPSED {fmt(play.elapsedS)} S</span><span>FINISH {fmt(duration)} S</span></div>
          </div>
          <div className="replay-controls">
            <button className="primary" aria-label={play.playing ? "Pause replay" : "Play replay"} onClick={() => setPlay(s => ({ ...s, elapsedS: s.elapsedS >= duration ? 0 : s.elapsedS, playing: !s.playing }))}>{play.playing ? "Ⅱ PAUSE" : "▶ PLAY BOTH"}</button>
            <button aria-label="Restart replay" onClick={() => seek(0)}>↺ RESTART</button>
            <label className="speed-control">SPEED<select aria-label="Playback speed" value={play.speed} onChange={e => setPlay(s => ({ ...s, speed: Number(e.target.value) }))}>{[.5, 1, 2, 4].map(v => <option key={v} value={v}>{v}×</option>)}</select></label>
          </div>
          <p data-testid="car-a-status">Car A: {aLap} / {a.lapTimesS.length} laps{aLap === a.lapTimesS.length ? " · complete" : " · awaiting next boundary"}</p>
          <p data-testid="car-b-status">Car B: {bLap} / {b.lapTimesS.length} laps{bLap === b.lapTimesS.length ? " · complete" : " · awaiting next boundary"}</p>
          <p className="limitation">Each marker steps only when its car completes a recorded lap. Positions between timing boundaries are unknown. Elapsed time starts at zero for both attempts; no continuous GPS trajectory is reconstructed.</p>
        </section>
        <section className="panel delta-panel"><div className="panel-title"><h3>Lap-boundary time delta</h3><span className="subtle">B − A · S</span></div>
          <div className="delta-readout"><strong className={delta < 0 ? "orange-text" : "cyan-text"}>{delta > 0 ? "+" : ""}{fmt(delta)}<small> s</small></strong><span>{lead}<br /><small>at lap {lap}</small></span></div>
          <DeltaChart values={Array.from({ length: count + 1 }, (_, i) => deltaAt(i)!)} lap={lap} seekLap={seekLap} />
          <div className="chart-legend"><span className="legend-a">● CAR A</span><span className="legend-b">● CAR B</span><span>Negative delta: B ahead</span></div>
          <div className="insight"><p>{Math.abs(delta) < .00005 ? "Equal elapsed time" : `Car ${delta < 0 ? "B" : "A"} is ${fmt(Math.abs(delta))} seconds ahead`} at the lap {lap} boundary.
            <small>A: {a.driver} ({attemptLabel(a)}). B: {b.driver} ({attemptLabel(b)}). Metric: cumulative B − A elapsed time (s), start to lap {lap}. Source: canonical official lap durations. Delta is shown only at the last boundary reached by both cars; it is not a live spatial gap.</small></p></div>
          <p className="limitation">Canonical section records exist, but this adapter does not expose a validated section-boundary mapping. Section dominance is unavailable; no corner advantage is inferred.</p>
        </section>
      </div>
      <div className="bottom-grid"><section className="panel"><div className="panel-title"><h3>Lap speed & recorded duration</h3><span className="subtle">MPH · S</span></div>
        <div className="lap-table"><div className="table-row table-head"><span>LAP</span><span>CAR A</span><span>CAR B</span><span>INCREMENTAL B − A (S)</span></div>
          {Array.from({ length: count }, (_, n) => n + 1).map(i => <button key={i} className={`table-row ${lap === i ? "active-row" : ""}`} onClick={() => seekLap(i)}>
            <span>LAP {i}</span><span>{fmt(a.lapSpeedsMph[i - 1], 3)} · {fmt(a.lapTimesS[i - 1])}</span><span>{fmt(b.lapSpeedsMph[i - 1], 3)} · {fmt(b.lapTimesS[i - 1])}</span><span>{fmt(b.lapTimesS[i - 1] - a.lapTimesS[i - 1])}</span>
          </button>)}</div>
        <p className="limitation">Lap durations are recorded official timing values. Canonical lap-average speeds are rounded derivations (9000 ÷ lap seconds). The four-lap average speed and total duration are official result fields.</p>
      </section><section className="panel"><h3>Signals & provenance</h3><div className="availability"><div><b className="ok">● AVAILABLE</b><span>Official 4-lap average speed</span><span>Official lap durations</span><span>Derived lap-average speed</span></div><div><b className="missing">○ NOT AVAILABLE IN EXPLORER</b><span>Matched section times</span><span>GPS / continuous position</span><span>Vehicle control telemetry</span></div></div>
        <div className="source-line"><span>DATASET</span><code>canonical/v1 · attempts + attempt_laps</code></div>
        <div className="source-line"><span>EXPORT</span><code>historical-attempts · v1.1.0</code></div>
        <p className="limitation">Source A: {a.sourceIds.join(", ")} · {a.sourceLocator}<br />Source B: {b.sourceIds.join(", ")} · {b.sourceLocator}</p>
      </section></div>
      <footer>Independent research tool · Not affiliated with INDYCAR or IMS · Historical observed timing · Simulation UI integration remains separate</footer>
    </main>
  </div>;
}
function CarCard({ side, row }: { side: "A" | "B"; row: HistoricalAttempt }) {
  return <article className={`car-card ${side === "A" ? "cyan" : "orange"}`}><div className="car-index">CAR {side}</div><strong>{row.driver}</strong><div className="car-meta">#{row.carNumber} · {row.team}</div><div className="car-stat"><span>OFFICIAL 4-LAP AVG</span><b>{fmt(row.averageSpeedMph, 3)} <small>MPH</small></b></div><p>{fmt(row.totalSeconds)} s · official total</p><div className="attempt-label">{attemptLabel(row)}</div></article>;
}
function BoundaryReplay({ aLap, bLap, count, lap, delta }: { aLap: number; bLap: number; count: number; lap: number; delta: number }) {
  const x = (n: number) => 45 + n * 320 / count;
  return <svg viewBox="0 0 420 190" role="img" aria-label="Discrete completed-lap markers; not geographic vehicle positions">
    {Array.from({ length: count + 1 }, (_, i) => <g key={i}><line x1={x(i)} x2={x(i)} y1="40" y2="135" stroke="#33434a" /><text x={x(i)} y="28" textAnchor="middle" fill="#aebbc0" fontSize="11">{i ? `LAP ${i}` : "START"}</text></g>)}
    <g data-testid="marker-a" data-lap={aLap}><circle cx={x(aLap)} cy="65" r="9" fill="#50d9e7" /><text x={x(aLap)} y="69" textAnchor="middle" fontSize="11">A</text></g>
    <g data-testid="marker-b" data-lap={bLap}><circle cx={x(bLap)} cy="110" r="9" fill="#ff9c50" /><text x={x(bLap)} y="114" textAnchor="middle" fontSize="11">B</text></g>
    <text x="210" y="165" textAnchor="middle" fill="#aebbc0" fontSize="11">LAP {lap} · Δ {delta > 0 ? "+" : ""}{fmt(delta)}s</text>
  </svg>;
}
function DeltaChart({ values, lap, seekLap }: { values: number[]; lap: number; seekLap: (lap: number) => void }) {
  const lo = Math.min(...values, 0) - .05, hi = Math.max(...values, 0) + .05;
  const y = (value: number) => 112 - (value - lo) / (hi - lo) * 92;
  return <svg className="delta-chart" viewBox="0 0 300 140" role="img" aria-label="Discrete running time deltas at lap boundaries; negative means B ahead">
    <line x1="18" x2="282" y1={y(0)} y2={y(0)} stroke="#53636b" strokeDasharray="3 4" />
    {values.map((value, i) => <g key={i} role="button" tabIndex={0} aria-label={`Select lap ${i}`} onClick={() => seekLap(i)} onKeyDown={e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); seekLap(i); } }} style={{ cursor: "pointer" }}>
      <circle cx={20 + i * 260 / (values.length - 1)} cy={y(value)} r={lap === i ? 6 : 4} fill={value < 0 ? "#ff9951" : "#52d7e2"} />
      <text x={20 + i * 260 / (values.length - 1)} y="132" fill="#aebbc0" fontSize="9" textAnchor="middle">{i ? `L${i}` : "S"}</text>
      <title>{fmt(value)} s at lap {i}</title>
    </g>)}
  </svg>;
}
