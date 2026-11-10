import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {decodeRun,sampleAt,advanceTime,requiredFields} from './replay.mjs';
const root=new URL('../reports/',import.meta.url);
const index=JSON.parse(fs.readFileSync(new URL('index.json',root)));
const payload=name=>JSON.parse(fs.readFileSync(new URL(index.runs.find(r=>r.name===name).file,root)));
const baseline=decodeRun(payload('baseline'));
test('all generated scenarios conform to frontend contract and terminal time',()=>{
 assert.equal(index.runs.length,19);
 for(const item of index.runs){const run=decodeRun(payload(item.name));assert.equal(run.samples.at(-1).sim_time_s,run.metrics.elapsed_sim_s);assert.equal(run.metrics.status,item.status);}
});
test('seek aligns position and holds actuator commands between saved samples',()=>{
 const [a,b]=baseline.samples,t=(a.sim_time_s+b.sim_time_s)/2,p=sampleAt(baseline.samples,t);
 assert.equal(p.sim_time_s,t);assert.equal(p.x_m,(a.x_m+b.x_m)/2);assert.equal(p.throttle_command,a.throttle_command);
});
test('seek clamps to endpoints and retains off-track event flag',()=>{
 const run=decodeRun(payload('delay_0.6s'));
 assert.equal(sampleAt(run.samples,-1).sim_time_s,0);
 assert.equal(sampleAt(run.samples,1e9).sim_time_s,run.metrics.elapsed_sim_s);
 assert.equal(sampleAt(run.samples,1e9).off_track,true);
});
test('playback clock uses supplied rate and stops exactly at terminal time',()=>{
 assert.equal(advanceTime(1,.25,2,10),1.5);assert.equal(advanceTime(9,5,5,10),10);
 assert.equal(advanceTime(5,0,1,10),5);assert.throws(()=>advanceTime(0,1,NaN,10));
});
test('zero-duration failed initial condition is valid replay',()=>{
 const run=decodeRun(payload('offset_+8m'));assert.equal(run.samples.length,1);
 assert.equal(sampleAt(run.samples,0).off_track,true);assert.equal(advanceTime(0,1,5,0),0);
});
test('rejects schema, duplicate fields, missing fields and nonfinite data',()=>{
 for(const edit of [x=>x.label='REAL',x=>x.schema_version=1,x=>x.fields.push(x.fields[0]),
                   x=>x.fields[0]='wrong',x=>x.rows[0][0]=null,x=>x.rows[0][1]=NaN]){
   const p=payload('baseline');edit(p);assert.throws(()=>decodeRun(p));
 }
});
test('rejects unordered timestamps and mismatched terminal time',()=>{
 const p=payload('baseline');p.rows[1][0]=p.rows[0][0];assert.throws(()=>decodeRun(p));
 const q=payload('baseline');q.metrics.elapsed_sim_s+=1;assert.throws(()=>decodeRun(q));
});
test('unwrapped heading interpolation stays continuous through 2pi',()=>{
 const a={...baseline.samples[0],heading_rad:6.2},b={...baseline.samples[1],heading_rad:6.4};
 assert.ok(Math.abs(sampleAt([a,b],(a.sim_time_s+b.sim_time_s)/2).heading_rad-6.3)<1e-12);
});
test('preserved terminal sample agrees with reported outcome and event',()=>{
 for(const item of index.runs){const run=decodeRun(payload(item.name));assert.equal(run.events.at(-1).type,run.metrics.status);assert.equal(run.events.at(-1).sim_time_s,run.samples.at(-1).sim_time_s);}
});
