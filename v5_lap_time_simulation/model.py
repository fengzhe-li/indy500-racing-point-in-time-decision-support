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


def build_ims_oval_approximation(corner_radius_m: float = MILE_M / (2 * math.pi),
                                banking_deg: float = 9.2) -> Track:
    """Build a 2.5-mile, eight-piece oval approximation.

    Distances follow the commonly described 4 x 1/4-mile turns, 2 x 5/8-mile
    main straights and 2 x 1/8-mile short chutes. Corner radius and banking are
    engineering assumptions, not surveyed lane-centre geometry.
    """
    track = Track((
        TrackSegment("Turn 1", MILE_M / 4, corner_radius_m, banking_deg),
        TrackSegment("Short chute 1-2", MILE_M / 8),
        TrackSegment("Turn 2", MILE_M / 4, corner_radius_m, banking_deg),
        TrackSegment("Back straight", MILE_M * 5 / 8),
        TrackSegment("Turn 3", MILE_M / 4, corner_radius_m, banking_deg),
        TrackSegment("Short chute 3-4", MILE_M / 8),
        TrackSegment("Turn 4", MILE_M / 4, corner_radius_m, banking_deg),
        TrackSegment("Front straight", MILE_M * 5 / 8),
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


def tire_loads(vehicle: Vehicle, environment: Environment, speed: float,
               curvature: float, banking_deg: float = 0.0) -> tuple[float, float]:
    """Road-normal aero; horizontal path acceleration resolved into road axes.

    Returns (normal tire load, signed lateral tire demand), in newtons.
    """
    theta = math.radians(banking_deg)
    centripetal = vehicle.mass_kg * speed ** 2 * abs(curvature)
    weight = vehicle.mass_kg * G
    normal = weight * math.cos(theta) + centripetal * math.sin(theta)
    normal += _downforce(vehicle, _density(environment), speed)
    lateral = centripetal * math.cos(theta) - weight * math.sin(theta)
    return normal, lateral


def _corner_speed_limit(vehicle: Vehicle, environment: Environment,
                        radius: float, banking_deg: float) -> float:
    """Lateral-only analytical cap; the solver also reserves force for drag."""
    rho, mu = _density(environment), _effective_mu(vehicle, environment)
    theta = math.radians(banking_deg)
    denom = vehicle.mass_kg / radius * (math.cos(theta) - mu * math.sin(theta))
    denom -= mu * 0.5 * rho * vehicle.cl_a_m2
    if denom <= 0:
        return vehicle.max_speed_mps
    numerator = vehicle.mass_kg * G * (math.sin(theta) + mu * math.cos(theta))
    return min(vehicle.max_speed_mps, math.sqrt(max(0.0, numerator / denom)))


def _longitudinal_tire_capacity(vehicle: Vehicle, environment: Environment,
                                speed: float, curvature: float,
                                banking_deg: float = 0.0) -> float:
    normal, lateral = tire_loads(vehicle, environment, speed, curvature, banking_deg)
    return math.sqrt(max(0.0, (_effective_mu(vehicle, environment) * normal) ** 2 - lateral ** 2))


def force_limits(vehicle: Vehicle, environment: Environment, speed: float,
                 curvature: float, banking_deg: float = 0.0) -> tuple[float, float]:
    """Signed maximum acceleration and positive braking magnitude, m/s².

    Rolling resistance uses the same normal load as the tire circle.
    """
    normal, _ = tire_loads(vehicle, environment, speed, curvature, banking_deg)
    remaining = _longitudinal_tire_capacity(vehicle, environment, speed, curvature, banking_deg)
    resistance = _drag(vehicle, _density(environment), speed)
    resistance += vehicle.rolling_resistance_coefficient * normal
    drive = min(vehicle.drive_force_max_n, vehicle.power_w / max(speed, 1e-6), remaining)
    return ((drive - resistance) / vehicle.mass_kg,
            (min(vehicle.brake_force_max_n, remaining) + resistance) / vehicle.mass_kg)


def sustainable_speed(vehicle: Vehicle, environment: Environment,
                      curvature: float, banking_deg: float) -> float:
    """Maximum local steady speed, including longitudinal force to offset drag.

    Applicability: positive normal load and a feasible near-rest state. Curves
    use the high-speed branch of the banked tire envelope; no minimum-speed
    banked-track solver is supplied.
    """
    normal, lateral = tire_loads(vehicle, environment, 0, curvature, banking_deg)
    if normal <= 0 or abs(lateral) >= _effective_mu(vehicle, environment) * normal:
        raise ValueError("bank/grip combination requires a minimum-speed solver; unsupported")
    lo, hi = 0.0, vehicle.max_speed_mps
    if curvature:
        hi = min(hi, _corner_speed_limit(vehicle, environment, 1 / abs(curvature), banking_deg))
    if force_limits(vehicle, environment, lo, curvature, banking_deg)[0] <= 0:
        raise ValueError("propulsion cannot overcome resistance")
    for _ in range(55):
        mid = (lo + hi) / 2
        if force_limits(vehicle, environment, mid, curvature, banking_deg)[0] >= 0:
            lo = mid
        else:
            hi = mid
    return lo


def simulate_lap(track: Track | None = None, vehicle: Vehicle | None = None,
                 environment: Environment | None = None, *, ds_m: float = 10.0,
                 tolerance_mps: float = 1e-8, max_iterations: int = 1000) -> SimulationResult:
    """Periodic envelope with implicit, conservative per-cell force constraints.

    Each cell has constant geometry. Its acceleration/braking constraint uses
    the minimum capacity at both endpoints and the midpoint of the speed range.
    Root solving avoids the artificial zero-acceleration clamp of the first V5.
    This is a discretisation, not proof of continuous transient feasibility.
    """
    track = track or build_ims_oval_approximation()
    vehicle, environment = vehicle or Vehicle(), environment or Environment()
    track.validate(); vehicle.validate(); environment.validate()
    if not math.isfinite(ds_m) or ds_m <= 0:
        raise ValueError("ds_m must be finite and positive")
    if not math.isfinite(tolerance_mps) or tolerance_mps <= 0 or max_iterations < 1:
        raise ValueError("tolerance_mps and max_iterations must be positive")
    ds, kappa, banks, indices, caps = [], [], [], [], []
    for si, seg in enumerate(track.segments):
        n = max(1, math.ceil(seg.distance_m / ds_m))
        k = 0.0 if seg.radius_m is None else 1 / seg.radius_m
        cap = sustainable_speed(vehicle, environment, k, seg.banking_deg)
        ds.extend([seg.distance_m / n] * n)
        kappa.extend([k] * n); banks.extend([seg.banking_deg] * n)
        indices.extend([si] * n); caps.extend([cap] * n)
    ds, kappa, banks = np.array(ds), np.array(kappa), np.array(banks)
    indices, caps = np.array(indices, dtype=int), np.array(caps)
    # A boundary node must satisfy the incoming AND outgoing geometry.
    limits = np.minimum(caps, np.roll(caps, 1))
    speed = limits.copy()
    n = len(speed)

    def bounds(i: int, v0: float, v1: float) -> tuple[float, float]:
        vals = [force_limits(vehicle, environment, v, kappa[i], banks[i])
                for v in (v0, (v0 + v1) / 2, v1)]
        return min(x[0] for x in vals), min(x[1] for x in vals)

    def reachable(i: int, fixed: float, upper: float, braking: bool) -> float:
        if upper <= fixed:
            return upper
        which = 1 if braking else 0
        def residual(candidate: float) -> float:
            capacity = bounds(i, fixed, candidate)[which]
            return candidate ** 2 - fixed ** 2 - 2 * ds[i] * capacity
        if residual(upper) <= 0:
            return upper
        lo, hi = fixed, upper
        for _ in range(34):
            mid = (lo + hi) / 2
            if residual(mid) <= 0:
                lo = mid
            else:
                hi = mid
        return lo

    for iteration in range(1, max_iterations + 1):
        old = speed.copy()
        for i in range(n):
            j = (i + 1) % n
            speed[j] = reachable(i, speed[i], speed[j], False)
        for i in range(n - 1, -1, -1):
            j = (i + 1) % n
            speed[i] = reachable(i, speed[j], speed[i], True)
        if float(np.max(np.abs(speed - old))) <= tolerance_mps:
            break
    else:
        raise RuntimeError(f"closed-lap speed solution did not converge in {max_iterations} iterations")
    next_speed = np.roll(speed, -1)
    cell_bounds = np.array([bounds(i, speed[i], next_speed[i]) for i in range(n)])
    actual_a = (next_speed ** 2 - speed ** 2) / (2 * ds)
    if np.any(actual_a > cell_bounds[:, 0] + 1e-6) or np.any(-actual_a > cell_bounds[:, 1] + 1e-6):
        raise RuntimeError("converged iteration is not a force-feasible lap")
    if np.any(speed <= 1e-6):
        raise ValueError("zero-speed state has no finite periodic lap time")
    time_steps = 2 * ds / (speed + next_speed)
    lap_time = float(np.sum(time_steps))
    return SimulationResult(
        distance_m=np.concatenate(([0.0], np.cumsum(ds[:-1]))), distance_step_m=ds,
        speed_mps=speed, curvature_1pm=kappa, corner_speed_limit_mps=limits,
        acceleration_limit_mps2=cell_bounds[:, 0], braking_limit_mps2=cell_bounds[:, 1],
        segment_index=indices, time_step_s=time_steps, lap_time_s=lap_time,
        average_speed_mph=track.length_m / lap_time * MPS_TO_MPH,
        iterations=iteration, converged=True, track_length_m=track.length_m,
    )


def with_changes(obj: Vehicle | Environment, **changes: float) -> Vehicle | Environment:
    """Typed immutable-config helper used by reproducible parameter studies."""
    return replace(obj, **changes)
