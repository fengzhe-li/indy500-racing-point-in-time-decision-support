import React from 'react';
import {afterEach,beforeEach,describe,it,expect,vi} from 'vitest';
import {cleanup,fireEvent,render,screen,waitFor,act} from '@testing-library/react';
import App from './App';
import baseline from '../../output/replay.json';
import modified from '../../output/replay_low_grip.json';
const response=(x:unknown)=>Promise.resolve({ok:true,json:()=>Promise.resolve(x)});
beforeEach(()=>{
  vi.stubGlobal('PointerEvent',MouseEvent);
  vi.stubGlobal('fetch',vi.fn().mockImplementationOnce(()=>response(baseline)).mockImplementationOnce(()=>response(modified)).mockImplementation(()=>response(baseline)));
});
afterEach(()=>{cleanup();vi.unstubAllGlobals();vi.useRealTimers();});
async function ready(){render(<App/>);await screen.findByRole('button',{name:'Play replay'});}
function expectSync(){expect(Number(screen.getByTestId('car-marker').getAttribute('data-distance'))).toBeCloseTo(Number(screen.getByTestId('graph-cursor').getAttribute('data-distance')),10);}
describe('Engineering replay interactions',()=>{
  it('seeks the timeline and synchronizes car and graph; restart resets both',async()=>{
    await ready();fireEvent.change(screen.getByRole('slider',{name:'Replay time'}),{target:{value:10}});expectSync();
    expect(Number(screen.getByTestId('car-marker').getAttribute('data-distance'))).toBeGreaterThan(0);
    fireEvent.click(screen.getByText('↺ Restart'));expectSync();expect(screen.getByTestId('car-marker').getAttribute('data-distance')).toBe('0');
  });
  it('clicks and drags graph cursor, then supports keyboard seeking',async()=>{
    await ready();const graph=screen.getByRole('slider',{name:'Speed graph distance'});
    graph.getBoundingClientRect=()=>({left:0,width:1000,top:0,height:300,right:1000,bottom:300,x:0,y:0,toJSON(){}});
    fireEvent.pointerDown(graph,{clientX:517.5,pointerId:1});expectSync();
    expect(Number(graph.getAttribute('aria-valuenow'))).toBe(Math.round(modified.track_length_m/2));
    fireEvent.pointerMove(graph,{clientX:748.75,pointerId:1});fireEvent.pointerUp(graph);expectSync();
    expect(Number(graph.getAttribute('aria-valuenow'))).toBe(Math.round(modified.track_length_m*.75));
    fireEvent.keyDown(graph,{key:'ArrowRight'});expectSync();
  });
  it('plays, changes speed and pauses without desynchronizing',async()=>{
    await ready();vi.useFakeTimers();
    vi.stubGlobal('requestAnimationFrame',(callback:FrameRequestCallback)=>setTimeout(()=>callback(performance.now()),16));
    vi.stubGlobal('cancelAnimationFrame',(id:number)=>clearTimeout(id));
    fireEvent.change(screen.getByRole('combobox',{name:'Playback speed'}),{target:{value:'2'}});
    fireEvent.click(screen.getByRole('button',{name:'Play replay'}));
    await act(async()=>{vi.advanceTimersByTime(1000);});expectSync();
    fireEvent.click(screen.getByRole('button',{name:'Pause replay'}));
    const stopped=screen.getByTestId('car-marker').getAttribute('data-distance');
    await act(async()=>{vi.advanceTimersByTime(500);});expect(screen.getByTestId('car-marker').getAttribute('data-distance')).toBe(stopped);
  });
  it('sends parameter changes to Python and presents returned metrics without refitting',async()=>{
    await ready();fireEvent.change(screen.getByRole('slider',{name:'Mass'}),{target:{value:'900'}});
    expect(screen.getByText(/Unapplied inputs/)).toBeTruthy();
    fireEvent.click(screen.getByText('Recompute with Python'));
    await waitFor(()=>expect(screen.getByText('Replay and metrics reflect the computed inputs.')).toBeTruthy());
    const calls=vi.mocked(fetch).mock.calls;
    const payload=JSON.parse(String(calls[2][1]?.body));expect(payload.vehicle.mass_kg).toBe(900);
    expect(calls[2][0]).toBe('/api/v5/simulate');expectSync();
  });
  it('keeps the last computed replay and reports server errors',async()=>{
    await ready();vi.mocked(fetch).mockImplementationOnce(()=>Promise.resolve({ok:false,status:422,json:()=>Promise.resolve({detail:'infeasible'})} as Response));
    fireEvent.click(screen.getByText('Recompute with Python'));await screen.findByRole('alert');expectSync();
    expect(screen.getByText(/infeasible/)).toBeTruthy();
  });
});
