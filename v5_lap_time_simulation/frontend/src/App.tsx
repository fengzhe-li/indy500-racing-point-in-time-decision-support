import React, {useEffect, useRef, useState} from 'react';
import {advanceTime, atTime, MPH, parseReplay, pointAtDistance, Replay, timeAtDistance} from './replay';
import './style.css';

const colors={acceleration:'#65dfb0',braking:'#ffb36b',corner_cap:'#d897ff',steady_or_transition:'#61788b'};
const parameters=[
  ['mass_kg','Mass','kg',600,1100,10],['cd_a_m2','Drag area CdA','m²',.6,1.6,.02],
  ['cl_a_m2','Downforce area ClA','m²',.5,2.5,.05],['tire_mu','Tire grip μ','–',1.1,2.2,.01],
  ['power_w','Effective power','kW',400000,1100000,5000],
] as const;
async function getReplay(url:string,body?:unknown):Promise<Replay>{
  const response=await fetch(url,body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:undefined);
  if(!response.ok)throw new Error(`Simulation failed (${response.status}): ${JSON.stringify((await response.json()).detail)}`);
  return parseReplay(await response.json());
}
export function TrackView({baseline,scenario,time}:{baseline:Replay;scenario:Replay;time:number}){
  const xs=scenario.xy_m.map(p=>p[0]),ys=scenario.xy_m.map(p=>p[1]);
  const minX=Math.min(...xs),maxY=Math.max(...ys),width=Math.max(...xs)-minX,height=maxY-Math.min(...ys);
  const scale=Math.min(470/width,230/height);
  const project=([x,y]:[number,number]):[number,number]=>[25+(x-minX)*scale,35+(maxY-y)*scale];
  const car=project(pointAtDistance(scenario,atTime(scenario,time).distance));
  const ghost=project(pointAtDistance(baseline,atTime(baseline,Math.min(time,baseline.lap_time_s)).distance));
  return <svg viewBox="0 0 520 310" aria-label="Approximate closed IMS oval with simulated car" role="img">
    <polyline points={scenario.xy_m.map(p=>project(p).join(',')).join(' ')} fill="none" stroke="#233d4c" strokeWidth="19" strokeLinejoin="round"/>
    <polyline points={scenario.xy_m.map(p=>project(p).join(',')).join(' ')} fill="none" stroke="#6c8496" strokeWidth="1" strokeDasharray="4 5"/>
    {scenario.segments.map(s=>{const [x,y]=project(s.label_xy_m);return <text key={s.name} x={x} y={y+(y>140?-20:27)} textAnchor="middle" className="map-label">{s.name}</text>;})}
    <circle cx={ghost[0]} cy={ghost[1]} r="9" fill="none" stroke="#c4d2dd" strokeWidth="2"/>
    <circle data-testid="car-marker" data-distance={atTime(scenario,time).distance} cx={car[0]} cy={car[1]} r="7" fill="#59d5ff" stroke="#07131d" strokeWidth="2"/>
    <text x="260" y="140" textAnchor="middle" className="map-title">2.500 mi / 4,023.36 m</text>
    <text x="260" y="163" textAnchor="middle" className="map-label">ASSUMED CONSTANT-RADIUS COURSE</text>
    <text x="260" y="293" textAnchor="middle" className="map-label">● Scenario · ○ Baseline at same elapsed time (stops at lap end)</text>
  </svg>;
}
export function SpeedGraph({baseline,scenario,time,onSeek}:{baseline:Replay;scenario:Replay;time:number;onSeek:(t:number)=>void}){
  const dragging=useRef(false),current=atTime(scenario,time);
  const speeds=[...baseline.speed_mps,...scenario.speed_mps,...scenario.speed_cap_mps].map(v=>v*MPH);
  const lo=Math.floor(Math.min(...speeds)/5)*5-2,hi=Math.ceil(Math.max(...speeds)/5)*5+2;
  const X=(s:number)=>55+925*s/scenario.track_length_m,Y=(v:number)=>245-210*(v*MPH-lo)/(hi-lo);
  const path=(r:Replay,cap=false)=>r.distance_m.map((s,i)=>`${X(s)},${Y(cap?r.speed_cap_mps[i]:r.speed_mps[i])}`).join(' ');
  const seek=(e:React.PointerEvent<SVGSVGElement>)=>{const box=e.currentTarget.getBoundingClientRect();const x=(e.clientX-box.left)*1000/box.width;onSeek(timeAtDistance(scenario,(x-55)/925*scenario.track_length_m));};
  return <svg viewBox="0 0 1000 300" role="slider" aria-label="Speed graph distance" aria-valuemin={0} aria-valuemax={Math.round(scenario.track_length_m)} aria-valuenow={Math.round(current.distance)} tabIndex={0}
    onKeyDown={e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();onSeek(timeAtDistance(scenario,current.distance+(e.key==='ArrowRight'?1:-1)*scenario.track_length_m/100));}}}
    onPointerDown={e=>{dragging.current=true;e.currentTarget.setPointerCapture?.(e.pointerId);seek(e);}}
    onPointerMove={e=>{if(dragging.current)seek(e);}} onPointerUp={()=>{dragging.current=false;}} onPointerCancel={()=>{dragging.current=false;}} className="speed-graph">
    {[0,1,2,3,4].map(i=>{const mph=lo+(hi-lo)*i/4,y=Y(mph/MPH);return <g key={i}><line x1="55" x2="980" y1={y} y2={y} stroke="#203541"/><text x="46" y={y+4} textAnchor="end">{mph.toFixed(0)}</text></g>;})}
    {[0,1,2,3,4,5].map(i=><g key={i}><text x={X(i*scenario.track_length_m/5)} y="283" textAnchor="middle">{(i*scenario.track_length_m/5).toFixed(0)}</text></g>)}
    {scenario.mode.map((mode,i)=><line key={i} x1={X(scenario.distance_m[i])} x2={X(scenario.distance_m[i+1])} y1="258" y2="258" stroke={colors[mode]} strokeWidth="5"/>)}
    <polyline points={path(baseline)} fill="none" stroke="#9cabb6" strokeWidth="2"/>
    <polyline points={path(scenario,true)} fill="none" stroke="#d897ff" strokeWidth="1.5" strokeDasharray="5 5"/>
    <polyline points={path(scenario)} fill="none" stroke="#59d5ff" strokeWidth="2.7"/>
    <line data-testid="graph-cursor" data-distance={current.distance} x1={X(current.distance)} x2={X(current.distance)} y1="25" y2="265" stroke="#fff" strokeWidth="1"/>
    <circle cx={X(current.distance)} cy={Y(current.speed)} r="5" fill="#fff"/>
    <text x="55" y="17">SPEED / mph</text><text x="980" y="299" textAnchor="end">DISTANCE / m</text>
  </svg>;
}
export default function App(){
  const [baseline,setBaseline]=useState<Replay>(),[scenario,setScenario]=useState<Replay>();
  const [inputs,setInputs]=useState<Record<string,number>>({}),[environment,setEnvironment]=useState<Record<string,number>>({});
  const [time,setTime]=useState(0),[playing,setPlaying]=useState(false),[rate,setRate]=useState(1);
  const [busy,setBusy]=useState(true),[dirty,setDirty]=useState(false),[error,setError]=useState('');
  useEffect(()=>{let cancelled=false;(async()=>{try{
    const base=await getReplay('/api/v5/baseline');
    const initial={...base.vehicle,tire_mu:base.vehicle.tire_mu*.75};
    const env={air_temperature_c:base.environment.air_temperature_c!,track_temperature_c:base.environment.track_temperature_c!};
    const modified=await getReplay('/api/v5/simulate',{vehicle:{tire_mu:initial.tire_mu}});
    if(!cancelled){setBaseline(base);setScenario(modified);setInputs(initial);setEnvironment(env);}
  }catch(e){if(!cancelled)setError(String(e));}finally{if(!cancelled)setBusy(false);}})();return()=>{cancelled=true;};},[]);
  useEffect(()=>{if(!playing||!scenario)return;let frame:number,last:number|undefined;
    const tick=(now:number)=>{if(last!==undefined)setTime(t=>advanceTime(t,(now-last!)/1000,rate,scenario.lap_time_s));last=now;frame=requestAnimationFrame(tick);};frame=requestAnimationFrame(tick);return()=>cancelAnimationFrame(frame);
  },[playing,rate,scenario]);
  async function recompute(reset=false){if(!baseline)return;setBusy(true);setPlaying(false);setError('');
    const vehicle=Object.fromEntries(parameters.map(([key])=>[key,reset?baseline.vehicle[key]:inputs[key]]));
    const env=reset?{air_temperature_c:baseline.environment.air_temperature_c,track_temperature_c:baseline.environment.track_temperature_c}:environment;
    try{const r=await getReplay('/api/v5/simulate',{vehicle,environment:env});setScenario(r);setInputs({...r.vehicle});setEnvironment({air_temperature_c:r.environment.air_temperature_c!,track_temperature_c:r.environment.track_temperature_c!});setDirty(false);setTime(0);}catch(e){setError(String(e));}finally{setBusy(false);}
  }
  function seek(t:number){setPlaying(false);setTime(t);}
  if(!baseline||!scenario)return <main className="loading"><h1>V5 / Engineering replay</h1><p role={error?'alert':'status'}>{error||'Computing baseline and parameter scenario with the Python solver…'}</p>{error&&<p>Start the API with <code>python3 -m v5_lap_time_simulation.server</code>, then reload.</p>}</main>;
  const current=atTime(scenario,time),delta=scenario.lap_time_s-baseline.lap_time_s;
  return <main>
    <header><div><div className="eyebrow">INDIANAPOLIS / VEHICLE PERFORMANCE LAB</div><h1>V5 Engineering Replay <span>QUASI-STEADY</span></h1><p>One generic model · assumed path · Python simulation outputs</p></div><a href="/docs" target="_blank" rel="noreferrer">API & schema ↗</a></header>
    <div className="notice">SIMULATION ONLY · Approximate geometry and assumed vehicle characteristics. No GPS or ECU telemetry, individual-car forecast, or V6 driver dynamics.</div>
    <section className="metrics" aria-label="Simulation summary">
      <article><label>BASELINE LAP</label><strong>{baseline.lap_time_s.toFixed(4)} <small>s</small></strong><span>{baseline.average_speed_mph.toFixed(3)} mph average</span></article>
      <article><label>COMPUTED SCENARIO</label><strong>{scenario.lap_time_s.toFixed(4)} <small>s</small></strong><span>{scenario.average_speed_mph.toFixed(3)} mph average</span></article>
      <article><label>LAP-TIME CHANGE</label><strong className={delta>0?'slower':'faster'}>{delta>=0?'+':''}{delta.toFixed(4)} <small>s</small></strong><span>{(delta/baseline.lap_time_s*100).toFixed(3)}% vs baseline</span></article>
      <article><label>CURSOR / SIMULATED SPEED</label><strong>{(current.speed*MPH).toFixed(2)} <small>mph</small></strong><span>{current.speed.toFixed(2)} m/s · {current.distance.toFixed(1)} m</span></article>
    </section>
    <div className="workspace">
      <aside className="panel"><div className="section-title"><h2>Parameter scenario</h2><span>ASSUMED</span></div><p className="muted">Initial scenario: grip −25%. Edits are not refitted to historical results.</p>
        {parameters.map(([key,label,unit,min,max,step])=><label className="parameter" key={key}>{label} <output>{(inputs[key]/(key==='power_w'?1000:1)).toFixed(key==='mass_kg'?0:2)} {unit}</output>
          <input aria-label={label} aria-valuetext={`${inputs[key]} ${key==='power_w'?'W':unit}`} type="range" min={min} max={max} step={step} value={inputs[key]} disabled={busy} onChange={e=>{setInputs({...inputs,[key]:Number(e.target.value)});setDirty(true);}}/>
          <small>{key==='power_w'?'Baseline: calibrated effective scalar; scenario: assumed':'Baseline and scenario: assumed'}</small></label>)}
        {(['air_temperature_c','track_temperature_c'] as const).map((key,i)=><label className="parameter" key={key}>{i?'Track':'Air'} temperature <output>{environment[key].toFixed(1)} °C</output><input aria-label={i?'Track temperature':'Air temperature'} type="range" min={i?15:5} max={i?65:45} value={environment[key]} disabled={busy} onChange={e=>{setEnvironment({...environment,[key]:Number(e.target.value)});setDirty(true);}}/></label>)}
        <button className="primary" disabled={busy} onClick={()=>recompute()}>{busy?'Computing…':'Recompute with Python'}</button>
        <button disabled={busy} onClick={()=>recompute(true)}>Reset scenario to baseline</button>
        <p role="status" className="muted">{dirty?'Unapplied inputs. Replay shows the last computed scenario.':'Replay and metrics reflect the computed inputs.'}</p>
        {error&&<p role="alert" className="error">{error}</p>}
      </aside>
      <div className="main-panels">
        <section className="panel"><div className="section-title"><h2>Closed-course replay</h2><span>{scenario.origin}</span></div>
          <div className="course-row"><TrackView baseline={baseline} scenario={scenario} time={time}/><div className="play-info"><label>ELAPSED TIME</label><strong>{time.toFixed(3)} <small>s</small></strong><p>/{scenario.lap_time_s.toFixed(3)} s</p><p className="muted">Position follows integrated V5 speed. Timeline and graph share one time state.</p></div></div>
          <div className="controls"><button aria-label={playing?'Pause replay':'Play replay'} className="primary" onClick={()=>setPlaying(!playing)}>{playing?'Ⅱ Pause':'▶ Play'}</button><button onClick={()=>{seek(0);}}>↺ Restart</button><label>Playback <select aria-label="Playback speed" value={rate} onChange={e=>setRate(Number(e.target.value))}>{[.25,.5,1,2,5,10].map(r=><option key={r} value={r}>{r}×</option>)}</select></label><input aria-label="Replay time" type="range" min="0" max={scenario.lap_time_s} step="0.001" value={time} onChange={e=>seek(Number(e.target.value))}/></div>
        </section>
        <section className="panel"><div className="section-title"><h2>Speed envelope</h2><span>Click / drag to seek · arrow keys move 1% of distance</span></div>
          <div className="legend"><span className="cyan">━ Scenario</span><span>━ Baseline</span><span className="purple">┄ Corner / power sustainable cap</span><span className="green">● Acceleration limited</span><span className="orange">● Braking limited</span><span className="purple">● Corner cap</span></div>
          <SpeedGraph baseline={baseline} scenario={scenario} time={time} onSeek={seek}/>
        </section>
        <section className="panel"><div className="section-title"><h2>Segment time contributions</h2><span>Simulated · seconds</span></div><table><thead><tr><th>Ordered segment</th><th>Length / m</th><th>Baseline / s</th><th>Scenario / s</th><th>Δ / s</th></tr></thead><tbody>{scenario.segments.map((seg,i)=><tr key={seg.name}><td>{i+1}. {seg.name}</td><td>{seg.distance_m.toFixed(3)}</td><td>{baseline.segments[i].time_s.toFixed(4)}</td><td>{seg.time_s.toFixed(4)}</td><td className={seg.time_s>baseline.segments[i].time_s?'slower':'faster'}>{(seg.time_s-baseline.segments[i].time_s).toFixed(4)}</td></tr>)}</tbody></table></section>
      </div>
    </div>
    <section className="panel provenance"><h2>Inputs & interpretation</h2><p>{scenario.provenance.track}. Radius {scenario.segments[0].radius_m?.toFixed(3)} m; nominal banking 9.2°. No measured racing line.</p><p>{scenario.provenance.power_w}. Baseline { (baseline.vehicle.power_w/1000).toFixed(3)} kW. The generic median-speed fit has the same aggregate validation error as a training-median constant-speed predictor.</p><p>Air density uses ideal dry air at {scenario.environment.pressure_pa} Pa. Track-temperature grip slope is an assumed sensitivity law. Tire load sensitivity, aero maps, transient steering, suspension and driver controls are not represented. Mesh: ≤10 m; see the generated mesh-convergence experiments for discretisation errors.</p></section>
  </main>;
}
