"""Versioned read-only replay export derived exclusively from recorded V6 states."""
from dataclasses import asdict
from bisect import bisect_right
import json
from pathlib import Path
from .models import TelemetrySample

REPLAY_FIELDS = [
    'sim_time_s', 'x_m', 'y_m', 'heading_rad', 'speed_m_s', 'u_m_s', 'v_m_s',
    'steering_command_rad', 'throttle_command', 'brake_command', 'yaw_rate_rad_s',
    'lateral_accel_m_s2', 'longitudinal_accel_m_s2', 'path_error_m', 'track_distance_m',
    'progress_m', 'steering_saturated', 'throttle_saturated', 'brake_saturated',
    'tire_saturated', 'off_track', 'target_speed_m_s']
FLAGS = ('steering_saturated', 'throttle_saturated', 'brake_saturated', 'tire_saturated', 'off_track')


def sample_at(samples: list[TelemetrySample], time_s: float):
    """Linear state interpolation; controls/flags held left; heading unwrapped.

    Used for comparing trajectories on a common simulated-time interval.
    Clamps at available data limits, never extrapolates.
    """
    times = [s.sim_time_s for s in samples]
    i = max(0, min(len(samples)-1, bisect_right(times, time_s)-1))
    a = asdict(samples[i])
    if i == len(samples)-1 or time_s <= times[0]:
        return a
    b = asdict(samples[i+1])
    fraction = (time_s-times[i])/(times[i+1]-times[i])
    for key in ('x_m', 'y_m', 'heading_rad', 'u_m_s', 'v_m_s', 'yaw_rate_rad_s', 'lateral_accel_m_s2'):
        a[key] += fraction * (b[key]-a[key])
    a['sim_time_s'] = time_s
    return a


def export_replay(result, path, name, min_interval_s=0.05):
    """Keep original samples at <=20 Hz plus every flag transition and terminal.

    No synthetic states are saved. Metrics are always computed on full telemetry.
    Viewer interpolates only the vehicle glyph and cursor between saved samples.
    """
    if min_interval_s <= 0:
        raise ValueError('positive display interval required')
    selected, previous = [], None
    for i, s in enumerate(result.samples):
        changed = previous and any(getattr(s, f) != getattr(previous, f) for f in FLAGS)
        if i == 0 or i == len(result.samples)-1 or changed or s.sim_time_s-selected[-1].sim_time_s >= min_interval_s-1e-9:
            if changed and selected[-1] != previous:
                selected.append(previous)
            selected.append(s)
        previous = s
    payload = dict(schema_version=2, label='SIMULATED', name=name,
                   metadata=result.metadata, metrics=result.metrics(), events=result.events,
                   fields=REPLAY_FIELDS,
                   sampling=dict(source='actual V6 samples', min_interval_s=min_interval_s,
                                 full_sample_count=len(result.samples), replay_sample_count=len(selected),
                                 transitions_preserved=list(FLAGS), numbers='full float precision'),
                   rows=[[getattr(s, f) for f in REPLAY_FIELDS] for s in selected])
    Path(path).write_text(json.dumps(payload, allow_nan=False, separators=(',', ':'))+'\n')
    return payload
