// Schema-2 V6 replay validation and shared-clock sampling. Coordinates are local
// Cartesian metres on the exported illustrative stadium geometry.
export const requiredV6Fields=['sim_time_s','x_m','y_m','heading_rad','speed_m_s','steering_command_rad','yaw_rate_rad_s','lateral_accel_m_s2','path_error_m','off_track'];
const flags=new Set(['steering_saturated','throttle_saturated','brake_saturated','tire_saturated','off_track']);
const held=new Set([...flags,'steering_command_rad','throttle_command','brake_command','track_distance_m','target_speed_m_s']);
export type V6Sample=Record<string,number|boolean>;
export type V6Replay={schema_version:2;label:'SIMULATED';name:string;metadata:{track:Record<string,any>&{kind:string;length_m:number;straight_length_m:number;radius_m:number;width_m:number;coordinates:string}};metrics:{status:'completed'|'off_track'|string;completed_lap:boolean;elapsed_sim_s:number;lap_time_s:number|null;reason:string};events:Array<{type:string;sim_time_s:number;x_m?:number;y_m?:number}>;fields:string[];rows:(number|boolean)[][];samples:V6Sample[]};
export function decodeV6(value:unknown):V6Replay {
 const d=value as V6Replay;
 if(!d||d.label!=='SIMULATED'||d.schema_version!==2)throw Error('Expected SIMULATED replay schema 2');
 if(!Array.isArray(d.fields)||new Set(d.fields).size!==d.fields.length||requiredV6Fields.some(k=>!d.fields.includes(k)))throw Error('Missing or duplicate SI telemetry fields');
 if(!Array.isArray(d.rows)||!d.rows.length)throw Error('Empty replay');
 let prior=-Infinity;
 const samples=d.rows.map(row=>{if(!Array.isArray(row)||row.length!==d.fields.length)throw Error('Invalid telemetry row');const sample=Object.fromEntries(d.fields.map((k,i)=>[k,row[i]])) as V6Sample;for(const k of d.fields){const v=sample[k];if(flags.has(k)?typeof v!=='boolean':typeof v!=='number'||!Number.isFinite(v))throw Error(`Invalid ${k}`);}const t=sample.sim_time_s as number;if(t<0||t<=prior)throw Error('Timestamps must strictly increase');prior=t;return sample;});
 const track=d.metadata?.track;
 if(samples[0].sim_time_s!==0||!Number.isFinite(d.metrics?.elapsed_sim_s)||Math.abs(prior-d.metrics.elapsed_sim_s)>1e-8)throw Error('Terminal timestamp mismatch');
 if(!track||['straight_length_m','radius_m','width_m','length_m'].some(k=>!Number.isFinite(track[k])||track[k]<=0)||typeof track.coordinates!=='string'||!track.coordinates.includes('metres'))throw Error('Invalid track geometry or coordinate system');
 if(!Array.isArray(d.events)||d.events.some(e=>!Number.isFinite(e.sim_time_s)||e.sim_time_s<0||e.sim_time_s>prior+1e-8))throw Error('Invalid event timestamps');
 if(d.metrics.status==='completed'&&!d.metrics.completed_lap||d.metrics.status==='off_track'&&d.metrics.completed_lap)throw Error('Replay status disagrees with completion metrics');
 if(d.metrics.status==='off_track'&&(!d.events.some(e=>e.type==='off_track'&&Math.abs(e.sim_time_s-prior)<1e-7)||!samples[samples.length-1]?.off_track))throw Error('Off-track terminal event is missing');
 return {...d,samples};
}
export function compatibleV6(a:V6Replay,b:V6Replay){const x=a.metadata.track,y=b.metadata.track;return x.kind===y.kind&&x.coordinates===y.coordinates&&['length_m','straight_length_m','radius_m','width_m'].every(k=>Math.abs(x[k]-y[k])<=1e-6);}
export function sampleV6(samples:V6Sample[],time:number){if(!Number.isFinite(time))throw Error('Time must be finite');const t=Math.max(0,Math.min(samples[samples.length-1].sim_time_s as number,time));let lo=0,hi=samples.length-1;while(lo<hi){const mid=Math.ceil((lo+hi)/2);if((samples[mid].sim_time_s as number)<=t)lo=mid;else hi=mid-1;}const a=samples[lo],b=samples[Math.min(lo+1,samples.length-1)],ta=a.sim_time_s as number,tb=b.sim_time_s as number,w=tb===ta?0:(t-ta)/(tb-ta),out={...a};for(const k of Object.keys(a))if(!held.has(k))out[k]=(a[k] as number)+w*((b[k] as number)-(a[k] as number));out.sim_time_s=t;return out;}
export function nextV6Time(t:number,dt:number,rate:number,end:number){if(![t,dt,rate,end].every(Number.isFinite)||dt<0||rate<=0||end<0)throw Error(`Invalid replay clock: ${[t,dt,rate,end].join(',')}`);return Math.min(end,Math.max(0,t+dt*rate));}
