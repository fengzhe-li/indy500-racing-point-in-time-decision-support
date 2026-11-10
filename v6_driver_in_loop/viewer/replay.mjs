// Pure replay data operations shared by the browser and Node contract tests.
export const requiredFields = ['sim_time_s','x_m','y_m','heading_rad','speed_m_s','steering_command_rad',
  'throttle_command','brake_command','yaw_rate_rad_s','lateral_accel_m_s2','path_error_m',
  'steering_saturated','throttle_saturated','brake_saturated','tire_saturated','off_track'];
const flagFields = new Set(['steering_saturated','throttle_saturated','brake_saturated','tire_saturated','off_track']);
const heldFields = new Set([...flagFields, 'steering_command_rad', 'throttle_command', 'brake_command', 'track_distance_m', 'target_speed_m_s']);
export function decodeRun(data) {
  if (data?.label !== 'SIMULATED' || data.schema_version !== 2) throw Error('Expected SIMULATED replay schema 2');
  if (!Array.isArray(data.fields) || new Set(data.fields).size !== data.fields.length ||
      requiredFields.some(f => !data.fields.includes(f))) throw Error('Missing or duplicate SI telemetry fields');
  if (!Array.isArray(data.rows) || !data.rows.length) throw Error('Empty replay');
  let prior = -Infinity;
  const samples = data.rows.map(row => {
    if (!Array.isArray(row) || row.length !== data.fields.length) throw Error('Invalid telemetry row');
    const sample = Object.fromEntries(data.fields.map((key,i) => [key,row[i]]));
    for (const key of data.fields) {
      if (flagFields.has(key) ? typeof sample[key] !== 'boolean' : !Number.isFinite(sample[key])) throw Error(`Invalid ${key}`);
    }
    if (sample.sim_time_s <= prior || sample.sim_time_s < 0) throw Error('Timestamps must strictly increase');
    prior = sample.sim_time_s;
    return sample;
  });
  if (samples[0].sim_time_s !== 0 || !Number.isFinite(data.metrics?.elapsed_sim_s) ||
      Math.abs(prior - data.metrics.elapsed_sim_s) > 1e-8) throw Error('Terminal timestamp mismatch');
  const track = data.metadata?.track;
  if (!track || ['straight_length_m','radius_m','width_m','length_m'].some(k => !Number.isFinite(track[k]) || track[k]<=0)) throw Error('Invalid track geometry');
  if (!Array.isArray(data.events) || data.events.some(e => !Number.isFinite(e.sim_time_s) || e.sim_time_s<0 || e.sim_time_s>prior+1e-8)) throw Error('Invalid event timestamps');
  return {...data, samples};
}
export function sampleAt(samples, time) {
  if (!Number.isFinite(time)) throw Error('Time must be finite');
  const t = Math.max(samples[0].sim_time_s, Math.min(samples.at(-1).sim_time_s, time));
  let lo=0, hi=samples.length-1;
  while (lo<hi) { const m=Math.ceil((lo+hi)/2); if(samples[m].sim_time_s<=t) lo=m; else hi=m-1; }
  const a=samples[lo], b=samples[Math.min(lo+1,samples.length-1)];
  const weight=b.sim_time_s===a.sim_time_s ? 0 : (t-a.sim_time_s)/(b.sim_time_s-a.sim_time_s);
  const out={...a};
  for(const k of Object.keys(a)) if(!heldFields.has(k)) out[k]=a[k]+weight*(b[k]-a[k]);
  out.sim_time_s=t;
  return out;
}
export function advanceTime(current, deltaSeconds, rate, end) {
  if (![current,deltaSeconds,rate,end].every(Number.isFinite) || deltaSeconds<0 || rate<=0 || end<0) throw Error('Invalid replay clock');
  return Math.min(end, Math.max(0,current+deltaSeconds*rate));
}
