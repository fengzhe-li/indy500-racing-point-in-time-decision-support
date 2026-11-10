"""Reproducible robustness matrix, convergence study, reports and replay data.

Run: python3 -m v6_driver_in_loop.experiments
No V5 imports, measured telemetry, or network calls.
"""
import argparse
from bisect import bisect_right
from dataclasses import dataclass, asdict, replace
import csv
import json
import math
from pathlib import Path
from .models import VehicleParams, VehicleState
from .controller import DriverConfig
from .simulation import SimulationEngine, SimulationConfig
from .vehicle import VehicleModel
from .track import OvalTrack
from .replay import export_replay


@dataclass(frozen=True)
class Scenario:
    name: str
    driver: DriverConfig = DriverConfig()
    vehicle: VehicleParams = VehicleParams()
    lateral_offset_m: float = 0.0
    heading_error_rad: float = 0.0
    initial_speed_m_s: float = 30.0

    def run(self, dt=.01, max_time_s=180, max_laps=1):
        return SimulationEngine(vehicle=VehicleModel(self.vehicle), driver_config=self.driver,
                                config=SimulationConfig(dt, max_time_s, self.initial_speed_m_s, max_laps)).run(
            VehicleState(y_m=self.lateral_offset_m, heading_rad=self.heading_error_rad, u_m_s=self.initial_speed_m_s))


def scenarios():
    base = Scenario('baseline')
    return [base,
            replace(base, name='conservative', driver=DriverConfig(aggression=.82, max_speed_m_s=65)),
            replace(base, name='aggressive', driver=DriverConfig(aggression=1.15, max_speed_m_s=82)),
            *[replace(base, name=f'delay_{d:g}s', driver=DriverConfig(reaction_delay_s=d)) for d in (.1, .3, .6)],
            *[replace(base, name=f'offset_{d:+g}m', lateral_offset_m=d) for d in (-2., 2., 8.)],
            *[replace(base, name=f'heading_{d:+g}deg', heading_error_rad=math.radians(d)) for d in (-3., 3.)],
            *[replace(base, name=f'start_{s:g}mps', initial_speed_m_s=s) for s in (0., 70.)],
            *[replace(base, name=f'grip_{mu:g}', vehicle=VehicleParams(friction_coefficient=mu)) for mu in (.8, 1.)],
            *[replace(base, name=f'steering_gain_{gain:g}', driver=DriverConfig(steering_gain=gain)) for gain in (.6, 1.6)],
            *[replace(base, name=f'speed_gain_{gain:g}', driver=DriverConfig(kp_speed=gain)) for gain in (.175, .7)]]


def write_csv(path, rows):
    with Path(path).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def compare_trajectories(result, reference):
    end = min(result.elapsed_sim_s, reference.elapsed_sim_s)
    errors = []
    # Common simulated-time grid includes [0,end]; compare only the overlap.
    times = [i*.1 for i in range(math.floor(end/.1)+1)]
    if times[-1] < end:
        times.append(end)
    columns = ('x_m', 'y_m', 'u_m_s', 'v_m_s', 'heading_rad', 'yaw_rate_rad_s')
    def interpolator(samples):
        stamps = [s.sim_time_s for s in samples]
        def at(t):
            i = min(len(samples)-2, max(0, bisect_right(stamps, t)-1))
            a, b = samples[i], samples[i+1]
            w = (t-a.sim_time_s)/(b.sim_time_s-a.sim_time_s)
            return [getattr(a,k)+w*(getattr(b,k)-getattr(a,k)) for k in columns]
        return at
    current, ref = interpolator(result.samples), interpolator(reference.samples)
    for t in times:
        a, b = current(t), ref(t)
        angle = (a[4]-b[4]+math.pi)%(2*math.pi)-math.pi
        errors.append((math.hypot(a[0]-b[0], a[1]-b[1]), math.hypot(a[2]-b[2], a[3]-b[3]), abs(angle), abs(a[5]-b[5])))
    return dict(comparison_end_s=end,
                position_max_difference_m=max(e[0] for e in errors),
                position_rms_difference_m=math.sqrt(sum(e[0]**2 for e in errors)/len(errors)),
                velocity_max_difference_m_s=max(e[1] for e in errors),
                heading_max_difference_rad=max(e[2] for e in errors),
                yaw_rate_max_difference_rad_s=max(e[3] for e in errors))


def markdown_table(rows, columns):
    def format_value(v):
        if v is None: return '—'
        return f'{v:.6g}' if isinstance(v, float) else str(v)
    return '\n'.join(['| '+' | '.join(columns)+' |', '| '+' | '.join('---' for _ in columns)+' |'] +
                     ['| '+' | '.join(format_value(row[k]) for k in columns)+' |' for row in rows])


def run_all(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    replay_dir = output / 'replays'
    replay_dir.mkdir(exist_ok=True)
    runs, index, definitions = [], [], []
    for scenario in scenarios():
        result = scenario.run()
        row = dict(name=scenario.name, **result.metrics())
        runs.append(row)
        filename = f'{scenario.name}.json'
        export_replay(result, replay_dir/filename, scenario.name)
        definitions.append(asdict(scenario))
        index.append(dict(name=scenario.name, file='replays/'+filename, status=result.status))
        print(f'{scenario.name}: {result.status}, lap={result.lap_time_s}', flush=True)
        if scenario.name == 'baseline':
            result.write_csv(output/'baseline_telemetry.csv')
            (output/'baseline_metadata.json').write_text(json.dumps(result.metadata, indent=2)+'\n')
    write_csv(output/'robustness.csv', runs)
    (output/'scenario_definitions.json').write_text(json.dumps(definitions, indent=2)+'\n')
    (output/'index.json').write_text(json.dumps(dict(schema_version=2, label='SIMULATED', runs=index), indent=2)+'\n')
    convergence = []
    for scenario in scenarios()[:3]:
        series = [(dt, scenario.run(dt)) for dt in (.02, .01, .005, .0025)]
        for dt, result in series:
            convergence.append(dict(name=scenario.name, dt_s=dt, **result.metrics(),
                                    **compare_trajectories(result, series[-1][1])))
    write_csv(output/'convergence.csv', convergence)
    (output/'ROBUSTNESS_RESULTS.md').write_text(
        '# SIMULATED driver robustness results\n\nGenerated by `python3 -m v6_driver_in_loop.experiments`. '
        '19 deterministic one-factor scenarios, unchanged 15 m track width and state limits. '
        'This is a sensitivity screen, not a probabilistic reliability estimate. '
        'Full precision metrics/configurations are in robustness.csv and scenario_definitions.json.\n\n'+
        markdown_table(runs, ['name','status','lap_time_s','max_path_error_m','rms_path_error_m','max_lateral_accel_m_s2',
                             'steering_saturation_fraction','throttle_saturation_fraction','brake_saturation_fraction','tire_saturation_fraction'])+'\n\n'+
        'All runs include terminal reason/event, including the deliberately invalid initial lane position. '
        'Saturation fractions are time occupancy of upper actuator limits or tyre clipping; zero throttle/brake is not saturation. '
        'Acceleration is net body force/mass, including transients. No failure threshold was relaxed.\n')
    (output/'CONVERGENCE_RESULTS.md').write_text(
        '# SIMULATED timestep refinement\n\nBaseline, conservative and boundary-sensitive aggressive drivers; fixed external control/record steps of 20, 10, 5, 2.5 ms. '
        'Deterministic internal substeps bound low-speed stiffness. Finest run is a numerical reference, not ground truth. '
        'Compare same-time states on the shared [0, min(end times)] interval at 0.1 s plus endpoint using linear interpolation. '
        'RMS position difference is over this comparison grid; tracking RMS in the CSV is time-weighted.\n\n'+
        markdown_table(convergence, ['name','dt_s','status','lap_time_s','max_path_error_m','rms_path_error_m',
                                    'max_lateral_accel_m_s2','max_yaw_rate_rad_s','position_max_difference_m',
                                    'position_rms_difference_m','velocity_max_difference_m_s','cpu_time_s'])+'\n\n'+
        'See convergence.csv for all actuator/tyre saturation fractions, heading/yaw differences and wall time. '
        'The study refines both sampled control and dynamics, so RK4 order cannot be inferred from these laps. '
        'Curvature steps, PID derivative response, clipping and event localization are nonsmooth. '
        'Timing is a single local process measurement, excludes exports and is not a real-time guarantee.\n')
    return runs, convergence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='v6_driver_in_loop/reports')
    args = parser.parse_args()
    run_all(args.output)


if __name__ == '__main__':
    main()
