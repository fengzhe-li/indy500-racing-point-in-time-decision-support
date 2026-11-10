"""SI interfaces; x east, y north, positive heading/steering/yaw counterclockwise."""
from dataclasses import dataclass, fields
import math


def finite_values(obj):
    for field in fields(obj):
        value = getattr(obj, field.name)
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{field.name} must be finite")


@dataclass(frozen=True)
class VehicleParams:
    # All defaults are illustrative, uncalibrated engineering assumptions.
    mass_kg: float = 850.0
    wheelbase_m: float = 3.0
    yaw_inertia_kg_m2: float = 1200.0
    lf_m: float = 1.35
    lr_m: float = 1.65
    cornering_front_n_per_rad: float = 90000.0
    cornering_rear_n_per_rad: float = 100000.0
    friction_coefficient: float = 1.5
    max_steer_rad: float = math.radians(18)
    max_drive_force_n: float = 9000.0
    max_brake_force_n: float = 18000.0
    drag_coefficient_area_m2: float = 1.2
    air_density_kg_m3: float = 1.225
    rolling_resistance: float = 0.015
    downforce_coefficient_area_m2: float = 3.0
    gravity_m_s2: float = 9.80665
    front_brake_fraction: float = 0.55
    slip_regularization_m_s: float = 2.0

    def __post_init__(self):
        finite_values(self)
        nonnegative = {'drag_coefficient_area_m2', 'downforce_coefficient_area_m2',
                       'rolling_resistance', 'front_brake_fraction'}
        for field in fields(self):
            value = getattr(self, field.name)
            if value < 0 or (value == 0 and field.name not in nonnegative):
                raise ValueError(f"invalid {field.name}")
        if abs(self.lf_m + self.lr_m - self.wheelbase_m) > 1e-6:
            raise ValueError("lf + lr must equal wheelbase")
        if not 0 < self.max_steer_rad < math.pi / 2:
            raise ValueError("steering limit must lie in (0, pi/2)")
        if not 0 <= self.front_brake_fraction <= 1 or self.rolling_resistance >= 1:
            raise ValueError("invalid brake split or rolling resistance")


@dataclass
class VehicleState:
    x_m: float = 0.0
    y_m: float = 0.0
    heading_rad: float = 0.0
    u_m_s: float = 30.0
    v_m_s: float = 0.0
    yaw_rate_rad_s: float = 0.0
    time_s: float = 0.0
    distance_m: float = 0.0

    def validate(self):
        finite_values(self)
        if self.u_m_s < 0 or self.time_s < 0 or self.distance_m < 0:
            raise ValueError("forward-only state requires nonnegative u, time and distance")


@dataclass(frozen=True)
class DriverCommand:
    steering_rad: float
    throttle: float
    brake: float

    def __post_init__(self):
        finite_values(self)

    def constrained(self, params: VehicleParams):
        brake = min(1.0, max(0.0, self.brake))
        return DriverCommand(
            min(params.max_steer_rad, max(-params.max_steer_rad, self.steering_rad)),
            0.0 if brake > 0 else min(1.0, max(0.0, self.throttle)), brake)


@dataclass(frozen=True)
class TelemetrySample:
    sim_time_s: float
    x_m: float
    y_m: float
    heading_rad: float
    u_m_s: float
    v_m_s: float
    yaw_rate_rad_s: float
    steering_command_rad: float
    throttle_command: float
    brake_command: float
    lateral_accel_m_s2: float
    longitudinal_accel_m_s2: float
    path_error_m: float
    distance_m: float
    simulated: bool = True
    track_distance_m: float = 0.0
    progress_m: float = 0.0
    speed_m_s: float = 0.0
    target_speed_m_s: float = 0.0
    steering_requested_rad: float = 0.0
    throttle_requested: float = 0.0
    brake_requested: float = 0.0
    steering_saturated: bool = False
    throttle_saturated: bool = False
    brake_saturated: bool = False
    tire_saturated: bool = False
    off_track: bool = False
