"""Quasi-steady longitudinal lap simulation on a closed, discretised track."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
import numpy as np

G = 9.80665
MPS_TO_MPH = 2.2369362920544
MILE_M = 1609.344


@dataclass(frozen=True)
class TrackSegment:
    name: str
    distance_m: float
    radius_m: float | None = None
    banking_deg: float = 0.0
    evidence_class: str = "ASSUMED"


@dataclass(frozen=True)
class Track:
    segments: tuple[TrackSegment, ...]
    name: str = "Indianapolis Motor Speedway oval (parameterised approximation)"

    @property
    def length_m(self) -> float:
        return sum(s.distance_m for s in self.segments)

    def validate(self) -> None:
        if len(self.segments) < 2:
            raise ValueError("track must contain at least two segments")
        for s in self.segments:
            if not math.isfinite(s.distance_m) or s.distance_m <= 0:
                raise ValueError(f"segment {s.name}: distance_m must be finite and positive")
            if s.radius_m is not None and (not math.isfinite(s.radius_m) or s.radius_m <= 0):
                raise ValueError(f"segment {s.name}: radius_m must be positive or None")
            if not 0 <= abs(s.banking_deg) < 90:
                raise ValueError(f"segment {s.name}: banking_deg must be between -90 and 90")


@dataclass(frozen=True)
class Vehicle:
    mass_kg: float = 800.0
    cd_a_m2: float = 1.00
    cl_a_m2: float = 1.50
    tire_mu: float = 1.80
    power_w: float = 900_000.0
    drive_force_max_n: float = 12_000.0
    brake_force_max_n: float = 20_000.0
    rolling_resistance_coefficient: float = 0.015
    # Explicit sensitivity assumption; this is not a measured tire law.
    grip_per_track_temp_k: float = 0.0015
    max_speed_mps: float = 120.0

    def validate(self) -> None:
        positive = ("mass_kg", "cd_a_m2", "tire_mu", "power_w",
                    "drive_force_max_n", "brake_force_max_n", "max_speed_mps")
        for key in positive:
            value = getattr(self, key)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{key} must be finite and positive")
        if not math.isfinite(self.cl_a_m2) or self.cl_a_m2 < 0:
            raise ValueError("cl_a_m2 must be finite and nonnegative")
        if not 0 <= self.rolling_resistance_coefficient < 1:
            raise ValueError("rolling_resistance_coefficient must be in [0, 1)")
        if not math.isfinite(self.grip_per_track_temp_k):
            raise ValueError("grip_per_track_temp_k must be finite")


@dataclass(frozen=True)
class Environment:
    air_temperature_c: float = 25.0
    pressure_pa: float = 101_325.0
    track_temperature_c: float | None = None
    reference_track_temperature_c: float = 35.0

    @property
    def air_density_kg_m3(self) -> float:
        # Dry-air ideal gas approximation; humidity correction is unsupported.
        return self.pressure_pa / (287.05 * (self.air_temperature_c + 273.15))

    def validate(self) -> None:
        if not math.isfinite(self.air_temperature_c) or self.air_temperature_c <= -273.15:
            raise ValueError("air_temperature_c must be above absolute zero")
        if not math.isfinite(self.pressure_pa) or self.pressure_pa <= 0:
            raise ValueError("pressure_pa must be finite and positive")
        for value in (self.track_temperature_c, self.reference_track_temperature_c):
            if value is not None and (not math.isfinite(value) or value <= -273.15):
                raise ValueError("track temperatures must be above absolute zero")


@dataclass(frozen=True)
class SimulationResult:
    distance_m: np.ndarray
    distance_step_m: np.ndarray
    speed_mps: np.ndarray
    curvature_1pm: np.ndarray
    corner_speed_limit_mps: np.ndarray
    acceleration_limit_mps2: np.ndarray
    braking_limit_mps2: np.ndarray
    segment_index: np.ndarray
    time_step_s: np.ndarray
    lap_time_s: float
    average_speed_mph: float
    iterations: int
    converged: bool
    track_length_m: float


def build_ims_oval_approximation(corner_radius_m: float = 256.0,
                                banking_deg: float = 9.2) -> Track:
    """Build a 2.5-mile, eight-piece oval approximation.

    Distances follow the commonly described 4 x 1/4-mile turns, 2 x 5/8-mile
    main straights and 2 x 1/8-mile short chutes. Corner radius and banking are
    engineering assumptions, not surveyed lane-centre geometry.
    """
    track = Track((
        TrackSegment("Turn 1", MILE_M / 4, corner_radius_m, banking_deg),
        TrackSegment("Back straight", MILE_M * 5 / 8),
        TrackSegment("Turn 2", MILE_M / 4, corner_radius_m, banking_deg),
        TrackSegment("Short chute 2-3", MILE_M / 8),
        TrackSegment("Turn 3", MILE_M / 4, corner_radius_m, banking_deg),
        TrackSegment("Main straight", MILE_M * 5 / 8),
        TrackSegment("Turn 4", MILE_M / 4, corner_radius_m, banking_deg),
        TrackSegment("Short chute 4-1", MILE_M / 8),
    ))
    track.validate()
    if not math.isclose(track.length_m, 2.5 * MILE_M, rel_tol=0, abs_tol=1e-8):
        raise RuntimeError("IMS oval approximation does not close to 2.5 miles")
    return track


def _density(environment: Environment) -> float:
    return environment.air_density_kg_m3


def _downforce(vehicle: Vehicle, rho: float, speed: float) -> float:
    return 0.5 * rho * vehicle.cl_a_m2 * speed * speed


def _drag(vehicle: Vehicle, rho: float, speed: float) -> float:
    return 0.5 * rho * vehicle.cd_a_m2 * speed * speed


def _effective_mu(vehicle: Vehicle, environment: Environment) -> float:
    if environment.track_temperature_c is None:
        return vehicle.tire_mu
    scale = 1.0 + vehicle.grip_per_track_temp_k * (
        environment.track_temperature_c - environment.reference_track_temperature_c
    )
    return vehicle.tire_mu * max(0.5, scale)


def _corner_speed_limit(vehicle: Vehicle, environment: Environment,
                        radius: float, banking_deg: float) -> float:
    rho, mu = _density(environment), _effective_mu(vehicle, environment)
    theta = math.radians(banking_deg)
    # m*v²/R - m*g*sin(theta) <= mu*(m*g*cos(theta) + 0.5*rho*ClA*v²)
    denom = vehicle.mass_kg / radius - mu * 0.5 * rho * vehicle.cl_a_m2
    if denom <= 0:
        return vehicle.max_speed_mps
    numerator = vehicle.mass_kg * G * (math.sin(theta) + mu * math.cos(theta))
    return min(vehicle.max_speed_mps, math.sqrt(max(0.0, numerator / denom)))


def _top_speed(vehicle: Vehicle, environment: Environment) -> float:
    rho = _density(environment)
    lo, hi = 0.1, vehicle.max_speed_mps
    for _ in range(70):
        mid = (lo + hi) / 2
        resist = _drag(vehicle, rho, mid) + vehicle.rolling_resistance_coefficient * vehicle.mass_kg * G
        available = min(vehicle.drive_force_max_n, vehicle.power_w / mid)
        if available >= resist:
            lo = mid
        else:
            hi = mid
    return lo


def _longitudinal_tire_capacity(vehicle: Vehicle, environment: Environment,
                                speed: float, curvature: float) -> float:
    rho, mu = _density(environment), _effective_mu(vehicle, environment)
    # This approximation uses flat-road normal load for propagation. Banking is
    # included in the lateral speed limit; detailed banked tire load transfer is
    # not represented in this point-mass model.
    normal = vehicle.mass_kg * G + _downforce(vehicle, rho, speed)
    lateral = vehicle.mass_kg * speed * speed * abs(curvature)
    return math.sqrt(max(0.0, (mu * normal) ** 2 - lateral ** 2))


def simulate_lap(track: Track | None = None, vehicle: Vehicle | None = None,
                 environment: Environment | None = None, *, ds_m: float = 10.0,
                 tolerance_mps: float = 1e-8, max_iterations: int = 20_000) -> SimulationResult:
    """Solve periodic speed limits by repeated forward and backward passes."""
    track = track or build_ims_oval_approximation()
    vehicle = vehicle or Vehicle()
    environment = environment or Environment()
    track.validate(); vehicle.validate(); environment.validate()
    if not math.isfinite(ds_m) or ds_m <= 0:
        raise ValueError("ds_m must be finite and positive")
    if tolerance_mps <= 0 or max_iterations < 1:
        raise ValueError("tolerance_mps and max_iterations must be positive")

    distances: list[float] = []
    curvature: list[float] = []
    banks: list[float] = []
    segments: list[int] = []
    edges: list[float] = []
    for si, seg in enumerate(track.segments):
        n = max(1, math.ceil(seg.distance_m / ds_m))
        step = seg.distance_m / n
        for _ in range(n):
            distances.append(step)
            curvature.append(0.0 if seg.radius_m is None else 1.0 / seg.radius_m)
            banks.append(seg.banking_deg)
            segments.append(si)
            edges.append(step)
    ds = np.asarray(distances)
    kappa = np.asarray(curvature)
    seg_idx = np.asarray(segments, dtype=int)
    n = len(ds)
    limits = np.array([
        _top_speed(vehicle, environment) if k == 0 else
        min(_top_speed(vehicle, environment), _corner_speed_limit(vehicle, environment, 1 / k, b))
        for k, b in zip(kappa, banks)
    ])
    speed = limits.copy()
    rho = _density(environment)
    converged = False
    iters = 0
    for iters in range(1, max_iterations + 1):
        previous = speed.copy()
        for i in range(n):
            j = (i + 1) % n
            cap_fx = _longitudinal_tire_capacity(vehicle, environment, speed[i], kappa[i])
            drive = min(vehicle.drive_force_max_n, vehicle.power_w / max(speed[i], 1.0), cap_fx)
            resistance = _drag(vehicle, rho, speed[i]) + vehicle.rolling_resistance_coefficient * vehicle.mass_kg * G
            accel = max(0.0, (drive - resistance) / vehicle.mass_kg)
            speed[j] = min(speed[j], limits[j], math.sqrt(max(0.0, speed[i] ** 2 + 2 * accel * ds[i])))
        for i in range(n - 1, -1, -1):
            j = (i + 1) % n
            cap_fx = _longitudinal_tire_capacity(vehicle, environment, speed[j], kappa[j])
            brake = min(vehicle.brake_force_max_n, cap_fx)
            resistance = _drag(vehicle, rho, speed[j]) + vehicle.rolling_resistance_coefficient * vehicle.mass_kg * G
            decel = max(0.0, (brake + resistance) / vehicle.mass_kg)
            speed[i] = min(speed[i], limits[i], math.sqrt(max(0.0, speed[j] ** 2 + 2 * decel * ds[i])))
        if float(np.max(np.abs(speed - previous))) <= tolerance_mps:
            converged = True
            break
    if not converged:
        raise RuntimeError(f"closed-lap speed solution did not converge in {max_iterations} iterations")

    accel_bounds = np.zeros(n)
    brake_bounds = np.zeros(n)
    for i in range(n):
        fx = _longitudinal_tire_capacity(vehicle, environment, speed[i], kappa[i])
        drive = min(vehicle.drive_force_max_n, vehicle.power_w / max(speed[i], 1.0), fx)
        resistance = _drag(vehicle, rho, speed[i]) + vehicle.rolling_resistance_coefficient * vehicle.mass_kg * G
        accel_bounds[i] = max(0.0, (drive - resistance) / vehicle.mass_kg)
        brake_bounds[i] = max(0.0, (min(vehicle.brake_force_max_n, fx) + resistance) / vehicle.mass_kg)
    next_speed = np.roll(speed, -1)
    time_steps = 2 * ds / np.maximum(speed + next_speed, 1e-9)
    lap_time = float(np.sum(time_steps))
    avg_mph = track.length_m / lap_time * MPS_TO_MPH
    return SimulationResult(
        distance_m=np.concatenate(([0.0], np.cumsum(ds[:-1]))), distance_step_m=ds,
        speed_mps=speed,
        curvature_1pm=kappa, corner_speed_limit_mps=limits,
        acceleration_limit_mps2=accel_bounds, braking_limit_mps2=brake_bounds,
        segment_index=seg_idx, time_step_s=time_steps, lap_time_s=lap_time,
        average_speed_mph=avg_mph, iterations=iters, converged=converged,
        track_length_m=track.length_m,
    )


def with_changes(obj: Vehicle | Environment, **changes: float) -> Vehicle | Environment:
    """Typed immutable-config helper used by reproducible parameter studies."""
    return replace(obj, **changes)
