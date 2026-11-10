import {describe,it,expect} from "vitest";import{distanceAtTime,runningDelta,segmentDelta,tickReplay}from"./replay";
const points=[{distanceM:0,elapsedTimeS:0},{distanceM:100,elapsedTimeS:10},{distanceM:300,elapsedTimeS:30}];
describe("replay math",()=>{
 it("interpolates time and distance both ways",()=>{expect(distanceAtTime(points,15)).toBe(150)});
 it("delta sign is B minus A: negative means B ahead",()=>{expect(runningDelta(12,11.8)).toBeCloseTo(-.2)});
 it("computes incremental segment delta independently",()=>{expect(segmentDelta(2,7,2,6.8)).toBeCloseTo(-.2)});
 it("stops at lap completion",()=>{expect(tickReplay({playing:true,elapsedS:9,durationS:10,speed:2},1)).toEqual({playing:false,elapsedS:10,durationS:10,speed:2})});
 it("keeps paused replay unchanged",()=>{const s={playing:false,elapsedS:3,durationS:10,speed:1};expect(tickReplay(s,1)).toBe(s)});
});
