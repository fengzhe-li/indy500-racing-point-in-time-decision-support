import {describe,it,expect} from 'vitest';
import baseline from '../../output/replay.json';
import {advanceTime,atTime,parseReplay,pointAtDistance,timeAtDistance,Replay} from './replay';
const data=parseReplay(baseline);
describe('Python replay schema and kinematics',()=>{
  it('consumes the genuine Python-generated fixture with its closed boundary',()=>{
    expect(data.schema_version).toBe('v5-replay-1');
    expect(data.segments.map(s=>s.name)).toEqual(['Turn 1','Short chute 1-2','Turn 2','Back straight','Turn 3','Short chute 3-4','Turn 4','Front straight']);
    expect(pointAtDistance(data,data.track_length_m)[0]).toBeCloseTo(0,8);
    expect(pointAtDistance(data,data.track_length_m)[1]).toBeCloseTo(0,8);
    expect(atTime(data,data.lap_time_s).distance).toBeCloseTo(data.track_length_m,7);
  });
  it('rejects schema drift and inconsistent integration',()=>{
    expect(()=>parseReplay({...baseline,schema_version:'next'})).toThrow();
    expect(()=>parseReplay({...baseline,speed_mps:[1,2]})).toThrow();
    expect(()=>parseReplay({...baseline,acceleration_mps2:baseline.acceleration_mps2.map(()=>99)})).toThrow();
  });
  it('uses analytic constant-acceleration time mapping, not linear distance interpolation',()=>{
    const accelerated={...data,lap_time_s:10,track_length_m:150,distance_m:[0,75,150],elapsed_s:[0,5,10],speed_mps:[10,20,10],acceleration_mps2:[2,-2]} as Replay;
    expect(atTime(accelerated,2).distance).toBe(24);
    expect(atTime(accelerated,2).speed).toBe(14);
    expect(timeAtDistance(accelerated,24)).toBeCloseTo(2,12);
    expect(atTime(accelerated,8).distance).toBe(126);
  });
  it('round trips distance/time seeks throughout the actual lap and clamps endpoints',()=>{
    for(let f=0;f<=1;f+=.01){const s=data.track_length_m*f;expect(atTime(data,timeAtDistance(data,s)).distance).toBeCloseTo(s,7);}
    expect(atTime(data,-1).distance).toBe(0);
    expect(timeAtDistance(data,1e6)).toBeCloseTo(data.lap_time_s,8);
  });
  it('advances by wall-clock delta and selected rate including the periodic wrap',()=>{
    expect(advanceTime(2,.5,2,10)).toBe(3);
    expect(advanceTime(9,.5,4,10)).toBe(1);
  });
});

describe('Contract semantic rejection',()=>{
  it('rejects wrong coordinate units and nonclosing segment geometry',()=>{
    expect(()=>parseReplay({...baseline,units:{...baseline.units,distance:'ft'}})).toThrow();
    const wrong=structuredClone(baseline);wrong.segments[0].distance_m+=10;
    expect(()=>parseReplay(wrong)).toThrow();
  });
  it('rejects nonfinite metadata and out-of-envelope speeds',()=>{
    expect(()=>parseReplay({...baseline,average_speed_mph:NaN})).toThrow();
    expect(()=>parseReplay({...baseline,speed_cap_mps:baseline.speed_cap_mps.map(()=>1)})).toThrow();
  });
  it('supports all offered playback rates and exact lap wrap',()=>{
    for(const rate of [.25,.5,1,2,5,10])expect(advanceTime(1,2,rate,100)).toBe(1+2*rate);
    expect(advanceTime(0,data.lap_time_s,1,data.lap_time_s)).toBe(0);
  });
});
