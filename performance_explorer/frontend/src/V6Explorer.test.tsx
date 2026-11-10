import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react';
import V6Explorer from './V6Explorer';
import baseline from './test/fixtures/v6-baseline.json';
import offtrack from './test/fixtures/v6-delay_0.6s.json';
let payloads: Record<string, unknown>;
beforeEach(() => {
  payloads = { baseline: structuredClone(baseline), 'delay_0.6s': structuredClone(offtrack) };
  vi.stubGlobal('fetch', vi.fn(async (url: string) => ({ ok: true, json: async () => payloads[decodeURIComponent(url.split('/').pop()!.replace('.json',''))] })));
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); vi.useRealTimers(); });
async function ready() { render(<V6Explorer/>); await screen.findByText('Synchronized speed telemetry'); }
const time = (i: number) => Number(screen.getByTestId(`v6-car-${i}`).getAttribute('data-time'));
describe('V6 controls and telemetry', () => {
  it('uses a shared plot time scale and independent terminal positions', async () => {
    await ready();
    const points = [0,1].map(i => screen.getByTestId(`v6-speed-${i}`).getAttribute('points')!.split(' '));
    expect(Number(points[1][points[1].length-1].split(',')[0])).toBeLessThan(Number(points[0][points[0].length-1].split(',')[0]));
    fireEvent.change(screen.getByLabelText('V6 simulation time'), {target: {value: String(baseline.metrics.elapsed_sim_s)}});
    expect(time(0)).toBe(baseline.metrics.elapsed_sim_s); expect(time(1)).toBe(offtrack.metrics.elapsed_sim_s);
    expect(Number(screen.getByTestId('v6-car-1').getAttribute('data-x'))).toBe(offtrack.events[offtrack.events.length-1].x_m);
    expect(screen.getByText(`delay_0.6s telemetry at ${offtrack.metrics.elapsed_sim_s.toFixed(3)} s`)).toBeInTheDocument();
  });
  it('plays at the chosen rate, pauses, restarts and supports identical selections', async () => {
    await ready(); vi.useFakeTimers();
    fireEvent.change(screen.getByLabelText('V6 playback speed'), {target: {value:'2'}});
    fireEvent.click(screen.getByRole('button', {name:'▶ Play both vehicles'}));
    await act(async () => { vi.advanceTimersByTime(320); });
    expect(time(0)).toBeGreaterThan(.4); expect(time(0)).toBe(time(1));
    fireEvent.click(screen.getByRole('button', {name:'Ⅱ Pause'}));
    const paused = time(0); await act(async () => {vi.advanceTimersByTime(200);}); expect(time(0)).toBe(paused);
    fireEvent.click(screen.getByRole('button', {name:'↺ Restart'})); expect(time(0)).toBe(0);
    vi.useRealTimers();
    fireEvent.change(screen.getByLabelText('Vehicle B scenario'), {target:{value:'baseline'}});
    await screen.findByText('Synchronized speed telemetry');
    expect(screen.getAllByText('baseline telemetry at 0.000 s')).toHaveLength(2);
  });
  it('shows missing optional measurements as unavailable', async () => {
    const run = payloads.baseline as typeof baseline;
    for (const field of ['steering_command_rad','yaw_rate_rad_s','lateral_accel_m_s2','path_error_m','throttle_command','brake_command']) {
      const index = run.fields.indexOf(field); run.fields.splice(index,1); run.rows.forEach(row => row.splice(index,1));
    }
    await ready(); expect(screen.getAllByText('Not exported')).toHaveLength(6); expect(document.body.textContent).not.toContain('NaN');
  });
  it.each(['schema', 'geometry'])('rejects invalid %s before playback', async kind => {
    const run = payloads.baseline as typeof baseline;
    if(kind==='schema') run.schema_version = 99; else run.metadata.track.coordinates = 'incompatible coordinate system';
    render(<V6Explorer/>);
    expect(await screen.findByRole('alert')).toHaveTextContent('Invalid V6 schema 2');
    expect(screen.queryByRole('button', {name:'▶ Play both vehicles'})).not.toBeInTheDocument();
  });
});
