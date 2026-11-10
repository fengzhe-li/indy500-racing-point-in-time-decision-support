import type { ComparisonSeriesV1 } from "./contract";

export function timeAtDistance(points: ComparisonSeriesV1["points"], distance: number): number | null {
  const p = points.filter(x => x.distanceM !== undefined).slice().sort((a,b) => a.distanceM! - b.distanceM!);
  if (!p.length || distance < p[0].distanceM! || distance > p[p.length-1].distanceM!) return null;
  for (let i=1;i<p.length;i++) if(distance<=p[i].distanceM!) {
    const a=p[i-1],b=p[i],f=(distance-a.distanceM!)/(b.distanceM!-a.distanceM!);
    return a.elapsedTimeS+f*(b.elapsedTimeS-a.elapsedTimeS);
  }
  return p[p.length-1].elapsedTimeS;
}
export function distanceAtTime(points: ComparisonSeriesV1["points"], time: number): number | null {
  const p=points.filter(x=>x.distanceM!==undefined).slice().sort((a,b)=>a.elapsedTimeS-b.elapsedTimeS);
  if(!p.length||time<p[0].elapsedTimeS||time>p[p.length-1].elapsedTimeS)return null;
  for(let i=1;i<p.length;i++)if(time<=p[i].elapsedTimeS){const a=p[i-1],b=p[i],f=(time-a.elapsedTimeS)/(b.elapsedTimeS-a.elapsedTimeS);return a.distanceM!+f*(b.distanceM!-a.distanceM!)}
  return p[p.length-1].distanceM!;
}
export interface ReplayState { playing: boolean; elapsedS: number; durationS: number; speed: number }
export function tickReplay(s: ReplayState, dt: number): ReplayState {
  if(!s.playing)return s;
  const elapsedS=Math.min(s.durationS,s.elapsedS+Math.max(0,dt)*s.speed);
  return {...s,elapsedS,playing:elapsedS<s.durationS};
}
export const runningDelta = (aSeconds:number,bSeconds:number) => bSeconds-aSeconds; // positive means B is behind; negative means B ahead.
export function segmentDelta(aStart:number,aEnd:number,bStart:number,bEnd:number){return (bEnd-bStart)-(aEnd-aStart)}
