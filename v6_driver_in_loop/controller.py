"""Virtual driver: finite map preview, pure pursuit, speed PID and command delay."""
from collections import deque
from dataclasses import dataclass
import math
from typing import Protocol
from .models import VehicleState, VehicleParams, DriverCommand, finite_values
from .track import OvalTrack


@dataclass(frozen=True)
class DriverConfig:
    preview_m: float = 35.0
    kp_speed: float = 0.35
    ki_speed: float = 0.025
    kd_speed: float = 0.02
    max_speed_m_s: float = 75.0
    lateral_accel_limit_m_s2: float = 10.0
    reaction_delay_s: float = 0.0
    steer_filter_tau_s: float = 0.0
    aggression: float = 1.0
    steering_gain: float = 1.0

    def __post_init__(self):
        finite_values(self)
        if min(self.preview_m, self.max_speed_m_s, self.lateral_accel_limit_m_s2, self.steering_gain) <= 0:
            raise ValueError("preview, speed, lateral limit and steering gain must be positive")
        if min(self.kp_speed, self.ki_speed, self.kd_speed, self.reaction_delay_s, self.steer_filter_tau_s) < 0:
            raise ValueError("gains, delay and filter time must be nonnegative")
        if not 0.2 <= self.aggression <= 1.5:
            raise ValueError("aggression must be in [0.2, 1.5]")


class DriverController(Protocol):
    def command(self, state: VehicleState, dt: float) -> tuple[DriverCommand, float]: ...


class PurePursuitPIDDriver:
    def __init__(self, track: OvalTrack, config: DriverConfig | None = None,
                 vehicle_params: VehicleParams | None = None):
        self.track = track
        self.config = config or DriverConfig()
        self.params = vehicle_params or VehicleParams()
        self.integral, self.steer, self.s = 0.0, 0.0, None
        self.prev_error = None
        self.delay = deque()
        self.held = DriverCommand(0, 0, 0)
        self.target_speed_m_s = 0.0

    def command(self, state: VehicleState, dt: float):
        if not math.isfinite(dt) or dt <= 0:
            raise ValueError("controller dt must be positive and finite")
        c = self.config
        here = self.track.nearest(state.x_m, state.y_m, self.s)
        self.s = here.distance_m
        target = self.track.point(self.s + c.preview_m)
        dx, dy = target.x_m - state.x_m, target.y_m - state.y_m
        lateral = -math.sin(state.heading_rad)*dx + math.cos(state.heading_rad)*dy
        # Actual chord length; the old code incorrectly used arc length here.
        desired = c.steering_gain * math.atan2(2*self.params.wheelbase_m*lateral, max(dx*dx+dy*dy, 1e-9))
        if c.steer_filter_tau_s:
            self.steer += -math.expm1(-dt/c.steer_filter_tau_s) * (desired-self.steer)
        else:
            self.steer = desired
        self.target_speed_m_s = self.track.target_speed(
            self.s + c.preview_m, c.lateral_accel_limit_m_s2, c.max_speed_m_s) * c.aggression
        error = self.target_speed_m_s - state.u_m_s
        derivative = 0.0 if self.prev_error is None else (error-self.prev_error)/dt
        proposed = max(-20.0, min(20.0, self.integral + error*dt))
        effort = c.kp_speed*error + c.ki_speed*proposed + c.kd_speed*derivative
        if (-8 <= effort <= 5) or (effort > 5 and error < 0) or (effort < -8 and error > 0):
            self.integral = proposed
        effort = c.kp_speed*error + c.ki_speed*self.integral + c.kd_speed*derivative
        self.prev_error = error
        requested = DriverCommand(self.steer, max(0.0, effort/5), max(0.0, -effort/8))
        self.delay.append((state.time_s + c.reaction_delay_s, requested))
        while self.delay and self.delay[0][0] <= state.time_s + 1e-12:
            _, self.held = self.delay.popleft()
        return self.held, self.track.error(state, here)
