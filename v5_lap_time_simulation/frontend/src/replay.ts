export const MPH = 2.2369362920544;
export type Mode = 'acceleration' | 'braking' | 'corner_cap' | 'steady_or_transition';
export interface Segment {name:string; distance_m:number; radius_m:number|null; banking_deg:number; start_m:number; time_s:number; label_xy_m:[number,number]; evidence_class:string}
export interface Replay {
  schema_version:'v5-replay-1'; units:Record<string,string>; provenance:Record<string,string>; origin:string;
  vehicle:Record<string,number>; environment:Record<string,number|null>;
  lap_time_s:number; track_length_m:number; average_speed_mph:number; segments:Segment[];
  distance_m:number[]; elapsed_s:number[]; speed_mps:number[]; speed_cap_mps:number[];
  acceleration_mps2:number[]; mode:Mode[]; xy_m:[number,number][];
}
const close = (a:number,b:number,tol=1e-6)=>Math.abs(a-b)<=tol;
export function parseReplay(value:unknown):Replay {
  const r=value as Replay;
  if (!r || r.schema_version!=='v5-replay-1') throw new Error('Unsupported simulation schema');
  const n=r.distance_m?.length;
  if (!n || n<3 || !Number.isFinite(r.lap_time_s) || r.lap_time_s<=0 || !Number.isFinite(r.track_length_m) || r.track_length_m<=0) throw new Error('Invalid replay dimensions');
  for (const values of [r.distance_m,r.elapsed_s,r.speed_mps,r.speed_cap_mps]) {
    if (!Array.isArray(values) || values.length!==n || values.some(v=>!Number.isFinite(v))) throw new Error('Invalid replay node arrays');
  }
  if (r.acceleration_mps2?.length!==n-1 || r.acceleration_mps2.some(v=>!Number.isFinite(v)) || r.mode?.length!==n-1 || r.mode.some(v=>!['acceleration','braking','corner_cap','steady_or_transition'].includes(v))) throw new Error('Invalid cell arrays');
  if (r.xy_m?.length!==n || r.xy_m.some(x=>x.length!==2 || x.some(v=>!Number.isFinite(v)))) throw new Error('Invalid geometry');
  if (!close(r.elapsed_s[0],0) || !close(r.distance_m[0],0) || !close(r.elapsed_s[n-1],r.lap_time_s) || !close(r.distance_m[n-1],r.track_length_m) || !close(r.speed_mps[0],r.speed_mps[n-1])) throw new Error('Invalid periodic boundary');
  for(let i=0;i<n-1;i++) {
    const ds=r.distance_m[i+1]-r.distance_m[i],dt=r.elapsed_s[i+1]-r.elapsed_s[i];
    if(ds<=0 || dt<=0 || r.speed_mps[i]<=0 || !close(ds,(r.speed_mps[i]+r.speed_mps[i+1])*dt/2) || !close(r.speed_mps[i+1],r.speed_mps[i]+r.acceleration_mps2[i]*dt)) throw new Error('Inconsistent simulation integration');
  }
  const units={distance:'m',time:'s',speed:'m/s',acceleration:'m/s²',geometry:'m'};
  if (Object.entries(units).some(([key,unit])=>r.units?.[key]!==unit)) throw new Error('Invalid coordinate units');
  if (!r.provenance || ['track','vehicle','power_w','environment','boundary'].some(key=>typeof r.provenance[key]!=='string' || !r.provenance[key]) || typeof r.origin!=='string') throw new Error('Missing provenance');
  if (!Number.isFinite(r.average_speed_mph) || !close(r.average_speed_mph,r.track_length_m/r.lap_time_s*MPH)) throw new Error('Invalid average speed');
  if (r.speed_mps.some((v,i)=>v<=0 || r.speed_cap_mps[i]<=0 || v>r.speed_cap_mps[i]+1e-6)) throw new Error('Speed exceeds envelope');
  if (!r.vehicle || Object.values(r.vehicle).some(v=>!Number.isFinite(v)) || !r.environment || Object.values(r.environment).some(v=>v!==null&&!Number.isFinite(v))) throw new Error('Invalid input metadata');
  if (!Array.isArray(r.segments) || !r.segments.length) throw new Error('Missing segments');
  let end=0,segmentTime=0;
  for(const seg of r.segments){
    if(!Number.isFinite(seg.distance_m)||seg.distance_m<=0||!Number.isFinite(seg.start_m)||!close(seg.start_m,end)||!Number.isFinite(seg.time_s)||seg.time_s<=0||!Number.isFinite(seg.banking_deg)||Math.abs(seg.banking_deg)>=90||!(seg.radius_m===null||(Number.isFinite(seg.radius_m)&&seg.radius_m>0))) throw new Error('Invalid segment boundaries');
    end+=seg.distance_m;segmentTime+=seg.time_s;
  }
  if(!close(end,r.track_length_m)||!close(segmentTime,r.lap_time_s)) throw new Error('Segment totals disagree');
  for(let i=0;i<n;i++){
    const expected=pointAtDistance(r,r.distance_m[i]);
    if(!close(expected[0],r.xy_m[i][0])||!close(expected[1],r.xy_m[i][1])) throw new Error('Geometry disagrees with segments');
  }
  if(!close(r.xy_m[0][0],r.xy_m[n-1][0])||!close(r.xy_m[0][1],r.xy_m[n-1][1])) throw new Error('Geometry does not close');
  return r;
}
function cell(values:number[],value:number) {
  let lo=0,hi=values.length-1;
  while(lo+1<hi){const mid=(lo+hi)>>1;if(values[mid]<=value)lo=mid;else hi=mid;}
  return Math.min(lo,values.length-2);
}
export function atTime(r:Replay,time:number) {
  const t=Math.max(0,Math.min(r.lap_time_s,time)), i=cell(r.elapsed_s,t),dt=t-r.elapsed_s[i],a=r.acceleration_mps2[i];
  return {time:t,distance:r.distance_m[i]+r.speed_mps[i]*dt+.5*a*dt*dt,speed:r.speed_mps[i]+a*dt,index:i};
}
export function timeAtDistance(r:Replay,distance:number) {
  const s=Math.max(0,Math.min(r.track_length_m,distance)),i=cell(r.distance_m,s),ds=s-r.distance_m[i];
  const v=Math.sqrt(Math.max(0,r.speed_mps[i]**2+2*r.acceleration_mps2[i]*ds));
  return r.elapsed_s[i]+2*ds/(r.speed_mps[i]+v);
}
export function pointAtDistance(r:Replay,distance:number):[number,number] {
  let x=0,y=0,heading=0,remaining=Math.max(0,Math.min(r.track_length_m,distance));
  for(const seg of r.segments){const ds=Math.min(remaining,seg.distance_m);
    if(seg.radius_m===null){x+=ds*Math.cos(heading);y+=ds*Math.sin(heading);}
    else {const end=heading+ds/seg.radius_m;x+=seg.radius_m*(Math.sin(end)-Math.sin(heading));y+=seg.radius_m*(Math.cos(heading)-Math.cos(end));heading=end;}
    remaining-=ds;if(remaining<=1e-9)break;
  }return [x,y];
}
export const advanceTime=(time:number,deltaSeconds:number,rate:number,lap:number)=> (time+deltaSeconds*rate)%lap;
