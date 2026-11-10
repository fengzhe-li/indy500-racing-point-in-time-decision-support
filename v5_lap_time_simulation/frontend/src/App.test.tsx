import React from 'react';
import {afterEach,beforeEach,describe,it,expect,vi} from 'vitest';
import {cleanup,fireEvent,render,screen,waitFor,act} from '@testing-library/react';
import App from './App';
import baseline from '../../output/replay.json';
import modified from '../../output/replay_low_grip.json';
const response=(x:unknown):Promise<Response>=>Promise.resolve({ok:true,json:()=>Promise.resolve(x)} as Response);
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

describe('Final acceptance coverage',()=>{
  it('serializes rapid repeated submissions even before React flushes busy state',async()=>{
    await ready();let resolve!:(value:Response)=>void;
    vi.mocked(fetch).mockImplementationOnce(()=>new Promise(r=>{resolve=r;}));
    const button=screen.getByText('Recompute with Python');
    act(()=>{button.click();button.click();});
    expect(vi.mocked(fetch).mock.calls).toHaveLength(3);
    expect((screen.getByText('Reset scenario to baseline') as HTMLButtonElement).disabled).toBe(true);
    await act(async()=>{resolve(await response(baseline));});
    expect(screen.getByText('Replay and metrics reflect the computed inputs.')).toBeTruthy();
  });
  it('resets all editable inputs and time to the actual baseline',async()=>{
    await ready();fireEvent.change(screen.getByRole('slider',{name:'Mass'}),{target:{value:900}});
    fireEvent.change(screen.getByRole('slider',{name:'Replay time'}),{target:{value:20}});
    fireEvent.click(screen.getByText('Reset scenario to baseline'));
    await waitFor(()=>expect(screen.getByRole('slider',{name:'Tire grip μ'}).getAttribute('aria-valuetext')).toBe('1.8 –'));
    const body=JSON.parse(String(vi.mocked(fetch).mock.calls[2][1]?.body));
    expect(body.vehicle.mass_kg).toBe(baseline.vehicle.mass_kg);expect(body.vehicle.power_w).toBe(baseline.vehicle.power_w);
    expect(body.environment.air_temperature_c).toBe(baseline.environment.air_temperature_c);
    expect(screen.getByTestId('car-marker').getAttribute('data-distance')).toBe('0');expectSync();
  });
  it('does not quantize the calibrated power to a different HTML slider value',async()=>{
    await ready();const power=screen.getByRole('slider',{name:'Effective power'}) as HTMLInputElement;
    expect(power.step).toBe('any');expect(Number(power.value)).toBe(baseline.vehicle.power_w);
  });
  it('clamps the ghost at its finish while the slower scenario completes',async()=>{
    await ready();expect((screen.getByRole('slider',{name:'Replay time'}) as HTMLInputElement).step).toBe('any');fireEvent.change(screen.getByRole('slider',{name:'Replay time'}),{target:{value:modified.lap_time_s}});
    expectSync();expect(Number(screen.getByTestId('car-marker').getAttribute('data-distance'))).toBeCloseTo(modified.track_length_m,6);
    expect(Number(screen.getByTestId('baseline-marker').getAttribute('data-distance'))).toBeCloseTo(baseline.track_length_m,6);
  });
  it('supports keyboard endpoints on the graph',async()=>{
    await ready();const graph=screen.getByRole('slider',{name:'Speed graph distance'});
    fireEvent.keyDown(graph,{key:'End'});expectSync();
    expect(Number(screen.getByTestId('car-marker').getAttribute('data-distance'))).toBeCloseTo(modified.track_length_m,6);
    fireEvent.keyDown(graph,{key:'Home'});expect(screen.getByTestId('car-marker').getAttribute('data-distance')).toBe('0');
  });
  it('reports unavailable backend on initial load',async()=>{
    vi.mocked(fetch).mockReset().mockRejectedValue(new TypeError('Failed to fetch'));
    render(<App/>);expect((await screen.findByRole('alert')).textContent).toMatch(/Failed to fetch/);
    expect(screen.queryByRole('button',{name:'Play replay'})).toBeNull();
  });
  it('ignores late initial responses after unmount',async()=>{
    let resolve!:(value:Response)=>void;vi.mocked(fetch).mockReset().mockImplementationOnce(()=>new Promise(r=>{resolve=r;}));
    const mounted=render(<App/>);mounted.unmount();
    await act(async()=>{resolve(await response(baseline));});
    expect(vi.mocked(fetch).mock.calls).toHaveLength(1);
  });
});

describe('Recompute failure recovery',()=>{
  it('preserves the last replay on network and non-JSON errors and permits retry',async()=>{
    await ready();fireEvent.change(screen.getByRole('slider',{name:'Replay time'}),{target:{value:12}});
    const distance=screen.getByTestId('car-marker').getAttribute('data-distance');
    vi.mocked(fetch).mockRejectedValueOnce(new TypeError('Failed to fetch'));
    fireEvent.click(screen.getByText('Recompute with Python'));await screen.findByRole('alert');
    expect(screen.getByTestId('car-marker').getAttribute('data-distance')).toBe(distance);
    vi.mocked(fetch).mockImplementationOnce(()=>Promise.resolve({ok:false,status:503,statusText:'Unavailable',json:()=>Promise.reject(new SyntaxError('html'))} as Response));
    fireEvent.click(screen.getByText('Recompute with Python'));
    await waitFor(()=>expect(screen.getByRole('alert').textContent).toMatch(/503.*Unavailable/));
    expectSync();expect(screen.getByTestId('car-marker').getAttribute('data-distance')).toBe(distance);
    fireEvent.click(screen.getByText('Recompute with Python'));
    await waitFor(()=>expect(screen.queryByRole('alert')).toBeNull());
    expect(screen.getByTestId('car-marker').getAttribute('data-distance')).toBe('0');
  });
});
