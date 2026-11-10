"""Deterministic fixed-step closed loop, explicit events and SI telemetry."""
from dataclasses import dataclass, asdict, field, replace, fields
import csv
import json
import math
import time
from pathlib import Path
from .models import VehicleState, TelemetrySample, finite_values
from .vehicle import VehicleModel
from .track import OvalTrack
from .controller import PurePursuitPIDDriver, DriverConfig

MODEL_VERSION = 'v6.1-audited-bicycle'


@dataclass(frozen=True)
class SimulationConfig:
    dt_s: float = .01
    max_time_s: float = 180.0
    start_speed_m_s: float = 30.0
    max_laps: int = 1

    def __post_init__(self):
        finite_values(self)
        if not 0 < self.dt_s <= .05 or self.max_time_s <= 0 or self.start_speed_m_s < 0:
            raise ValueError("dt must be in (0,0.05], max_time positive, start speed nonnegative")
        if not isinstance(self.max_laps, int) or isinstance(self.max_laps, bool) or self.max_laps < 1:
            raise ValueError("max_laps must be a positive integer")


@dataclass
class SimulationResult:
    status: str
    lap_time_s: float | None
    elapsed_sim_s: float
    wall_time_s: float
    samples: list[TelemetrySample]
    off_track: bool
    max_abs_path_error_m: float
    reason: str = ''
    cpu_time_s: float = 0.0
    events: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def metrics(self):
        samples = self.samples
        duration = samples[-1].sim_time_s - samples[0].sim_time_s
        def average(fn):
            if not duration:
                return fn(samples[0])
            return sum((b.sim_time_s-a.sim_time_s)*(fn(a)+fn(b))/2
                       for a, b in zip(samples, samples[1:])) / duration
        def occupancy(name):
            if not duration:
                return 0.0
            return sum((b.sim_time_s-a.sim_time_s)*getattr(a, name)
                       for a, b in zip(samples, samples[1:])) / duration
        rates = [(b.steering_command_rad-a.steering_command_rad)/(b.sim_time_s-a.sim_time_s)
                 for a, b in zip(samples, samples[1:])]
        return dict(status=self.status, completed_lap=self.status == 'completed', lap_time_s=self.lap_time_s,
                    elapsed_sim_s=self.elapsed_sim_s, max_path_error_m=max(abs(s.path_error_m) for s in samples),
                    rms_path_error_m=math.sqrt(average(lambda s: s.path_error_m**2)),
                    max_lateral_accel_m_s2=max(abs(s.lateral_accel_m_s2) for s in samples),
                    max_yaw_rate_rad_s=max(abs(s.yaw_rate_rad_s) for s in samples),
                    min_speed_m_s=min(s.speed_m_s for s in samples), mean_speed_m_s=average(lambda s: s.speed_m_s),
                    max_speed_m_s=max(s.speed_m_s for s in samples),
                    steering_saturation_fraction=occupancy('steering_saturated'),
                    throttle_saturation_fraction=occupancy('throttle_saturated'),
                    brake_saturation_fraction=occupancy('brake_saturated'),
                    tire_saturation_fraction=occupancy('tire_saturated'),
                    max_steering_rate_rad_s=max(map(abs, rates), default=0),
                    off_track=self.off_track, reason=self.reason, wall_time_s=self.wall_time_s, cpu_time_s=self.cpu_time_s)

    def to_dict(self):
        return dict(schema_version=2, label='SIMULATED', **self.metrics(),
                    metadata=self.metadata, events=self.events, samples=[asdict(s) for s in self.samples])

    def write_csv(self, path):
        with open(path, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=[item.name for item in fields(TelemetrySample)], lineterminator='\n')
            w.writeheader()
            w.writerows(asdict(s) for s in self.samples)

    def write_json(self, path):
        Path(path).write_text(json.dumps(self.to_dict(), allow_nan=False, separators=(',', ':')) + '\n')


class LapProgress:
    """Signed unwrapped progress from initial coordinate, not a mere s wrap count."""
    def __init__(self, length_m, initial_s):
        self.length_m, self.previous_s, self.progress_m = length_m, initial_s, 0.0

    def delta(self, s):
        return (s-self.previous_s+self.length_m/2) % self.length_m-self.length_m/2

    def update(self, s):
        self.progress_m += self.delta(s)
        self.previous_s = s
        return self.progress_m


class SimulationEngine:
    def __init__(self, track=None, vehicle=None, driver_config=None, config=None):
        self.track = track or OvalTrack()
        self.vehicle = vehicle or VehicleModel()
        self.driver_config = driver_config or DriverConfig()
        self.config = config or SimulationConfig()

    def run(self, initial_state=None, manual_input=None, controller=None):
        cfg, track, vehicle = self.config, self.track, self.vehicle
        state = replace(initial_state) if initial_state else VehicleState(u_m_s=cfg.start_speed_m_s)
        state.validate()
        if state.time_s != 0 or state.distance_m != 0:
            raise ValueError("initial time and accumulated distance must be zero for a new run")
        if controller is not None and manual_input is not None:
            raise ValueError("choose a controller OR manual callback")
        driver = controller or PurePursuitPIDDriver(track, self.driver_config, vehicle.params)
        progress = LapProgress(track.length_m, track.nearest(state.x_m, state.y_m).distance_m)
        start, cpu_start = time.perf_counter(), time.process_time()
        samples, events = [], []
        status, reason, lap_time = 'timeout', 'maximum simulated time reached', None
        metadata = dict(model_version=MODEL_VERSION, label='SIMULATED', integrator='RK4; held controls; stiffness substeps',
                        units='SI', track=track.metadata(), vehicle=asdict(vehicle.params),
                        parameter_provenance='ILLUSTRATIVE, uncalibrated', driver=asdict(self.driver_config),
                        simulation=asdict(cfg), initial_state=asdict(state),
                        control_mode='manual_callback' if manual_input else type(driver).__name__,
                        recording='full control grid plus terminal event; outgoing held commands except terminal',
                        actuator_priority='brake overrides throttle', event_time_tolerance_s=1e-9)
        def boundary(z):
            p = track.nearest(z.x_m, z.y_m)
            return math.hypot(z.x_m-p.x_m, z.y_m-p.y_m) - track.width_m/2
        def record(z, requested, applied, terminal_off=False):
            p = track.nearest(z.x_m, z.y_m)
            f = vehicle.forces(z, applied)
            samples.append(TelemetrySample(
                z.time_s, z.x_m, z.y_m, z.heading_rad, z.u_m_s, z.v_m_s, z.yaw_rate_rad_s,
                applied.steering_rad, applied.throttle, applied.brake,
                f.body_y_n/vehicle.params.mass_kg, f.body_x_n/vehicle.params.mass_kg,
                track.error(z, p), z.distance_m, track_distance_m=p.distance_m,
                progress_m=progress.progress_m, speed_m_s=math.hypot(z.u_m_s, z.v_m_s),
                target_speed_m_s=getattr(driver, 'target_speed_m_s', 0.0),
                steering_requested_rad=requested.steering_rad, throttle_requested=requested.throttle,
                brake_requested=requested.brake,
                steering_saturated=abs(requested.steering_rad) >= vehicle.params.max_steer_rad-1e-12,
                throttle_saturated=applied.throttle >= 1-1e-12, brake_saturated=applied.brake >= 1-1e-12,
                tire_saturated=f.tire_saturated, off_track=terminal_off))
        def localize(z, command, h, predicate):
            low, high = 0.0, h
            endpoint = vehicle.step(z, command, high)[0]
            for _ in range(32):
                if high-low <= 1e-9:
                    break
                mid = (low+high)/2
                candidate = vehicle.step(z, command, mid)[0]
                if predicate(candidate):
                    high, endpoint = mid, candidate
                else:
                    low = mid
            return endpoint
        requested = None
        for tick in range(math.ceil(cfg.max_time_s/cfg.dt_s)):
            h = min(cfg.dt_s, cfg.max_time_s-state.time_s)
            requested = manual_input(replace(state)) if manual_input else driver.command(replace(state), h)[0]
            applied = requested.constrained(vehicle.params)
            initially_off = boundary(state) > 0
            record(state, requested, applied, initially_off)
            if initially_off:
                status, reason = 'off_track', 'initial state outside track boundary'
                break
            if abs(state.v_m_s) > 100 or abs(state.yaw_rate_rad_s) > 10:
                status, reason = 'unstable', 'state limit exceeded (|v|>100 m/s or |r|>10 rad/s)'
                break
            try:
                next_state = vehicle.step(state, applied, h)[0]
                # Set external clock from tick index instead of accumulated roundoff.
                next_state.time_s = min((tick+1)*cfg.dt_s, cfg.max_time_s)
                if next_state.distance_m-state.distance_m >= track.length_m/2:
                    raise FloatingPointError('step spans half a lap: progress ambiguous')
                candidates = []
                if boundary(next_state) > 0:
                    candidates.append((localize(state, applied, h, lambda z: boundary(z) > 0),
                                       'off_track', 'track boundary exceeded'))
                def crossed(z):
                    p = track.nearest(z.x_m, z.y_m)
                    return progress.progress_m + progress.delta(p.distance_m) >= cfg.max_laps*track.length_m
                if crossed(next_state):
                    candidates.append((localize(state, applied, h, crossed), 'completed', 'lap completion'))
                if abs(next_state.v_m_s) > 100 or abs(next_state.yaw_rate_rad_s) > 10:
                    candidates.append((next_state, 'unstable', 'state limit exceeded (|v|>100 m/s or |r|>10 rad/s)'))
                if candidates:
                    next_state, status, reason = min(candidates, key=lambda item: item[0].time_s)
                progress.update(track.nearest(next_state.x_m, next_state.y_m).distance_m)
                state = next_state
            except (ValueError, FloatingPointError, OverflowError) as exc:
                status, reason = 'numerical_error', str(exc)
                break
            if status != 'timeout' or state.time_s >= cfg.max_time_s-1e-12:
                if status == 'completed':
                    lap_time = state.time_s  # elapsed time for requested number of laps
                record(state, requested, applied, status == 'off_track')
                break
        if status != 'timeout' or samples:
            events.append(dict(type=status, sim_time_s=state.time_s, x_m=state.x_m, y_m=state.y_m,
                               progress_m=progress.progress_m, reason=reason))
        return SimulationResult(status, lap_time, state.time_s, time.perf_counter()-start,
                                samples, status == 'off_track', max(abs(s.path_error_m) for s in samples), reason,
                                time.process_time()-cpu_start, events, metadata)


class ExperimentRunner:
    def __init__(self, track=None, vehicle=None, simulation=None):
        self.track, self.vehicle = track or OvalTrack(), vehicle or VehicleModel()
        self.simulation = simulation or SimulationConfig()

    def run(self, configs):
        return [dict(name=name, **SimulationEngine(self.track, self.vehicle, cfg, self.simulation).run().metrics())
                for name, cfg in configs]
