"""Dynamic bicycle model: combined axle friction circles and body force rotation."""
from dataclasses import dataclass, fields
import math
from .models import VehicleParams, VehicleState, DriverCommand


@dataclass(frozen=True)
class ForceState:
    slip_front_rad: float
    slip_rear_rad: float
    normal_front_n: float
    normal_rear_n: float
    tire_front_x_n: float  # front wheel frame
    tire_front_y_n: float
    tire_rear_x_n: float   # rear wheel / body frame
    tire_rear_y_n: float
    body_x_n: float
    body_y_n: float
    yaw_moment_n_m: float
    drag_n: float
    downforce_n: float
    tire_saturated: bool


class VehicleModel:
    def __init__(self, params: VehicleParams | None = None):
        self.params = params or VehicleParams()

    def forces(self, z: VehicleState, cmd: DriverCommand) -> ForceState:
        p = self.params
        cmd = cmd.constrained(p)
        # Internal RK stages can briefly cross u=0; the forward-only boundary
        # is projected at each accepted substep, never used to invent motion.
        u, v, r = max(0.0, z.u_m_s), z.v_m_s, z.yaw_rate_rad_s
        co, si = math.cos(cmd.steering_rad), math.sin(cmd.steering_rad)
        front_v = v + p.lf_m * r
        wheel_u = u * co + front_v * si
        wheel_v = -u * si + front_v * co
        af = -math.atan2(wheel_v, max(abs(wheel_u), p.slip_regularization_m_s))
        ar = -math.atan2(v - p.lr_m * r, max(u, p.slip_regularization_m_s))
        speed = math.hypot(u, v)
        q = 0.5 * p.air_density_kg_m3 * speed**2
        down, drag = q * p.downforce_coefficient_area_m2, q * p.drag_coefficient_area_m2
        load = p.mass_kg * p.gravity_m_s2 + down
        fzf, fzr = load * p.lr_m / p.wheelbase_m, load * p.lf_m / p.wheelbase_m
        # Smooth opposition near rest prevents brake and rolling force reversing
        # a stopped car. Rear-only constant-force propulsion is an explicit assumption.
        brake = cmd.brake * p.max_brake_force_n * math.tanh(u / 0.2)
        fxf = -p.front_brake_fraction * brake
        fxr = cmd.throttle * p.max_drive_force_n - (1 - p.front_brake_fraction) * brake
        fyf, fyr = p.cornering_front_n_per_rad * af, p.cornering_rear_n_per_rad * ar
        def circle(fx, fy, normal):
            scale = min(1.0, p.friction_coefficient * normal / max(math.hypot(fx, fy), 1e-15))
            return fx * scale, fy * scale, scale < 1.0
        fxf, fyf, satf = circle(fxf, fyf, fzf)
        fxr, fyr, satr = circle(fxr, fyr, fzr)
        body_front_x, body_front_y = fxf * co - fyf * si, fxf * si + fyf * co
        drag_x = drag * u / speed if speed else 0.0
        drag_y = drag * v / speed if speed else 0.0
        rolling = p.rolling_resistance * p.mass_kg * p.gravity_m_s2 * math.tanh(u / 0.2)
        return ForceState(af, ar, fzf, fzr, fxf, fyf, fxr, fyr,
                          body_front_x + fxr - drag_x - rolling,
                          body_front_y + fyr - drag_y,
                          p.lf_m * body_front_y - p.lr_m * fyr,
                          drag, down, satf or satr)

    def derivatives(self, z: VehicleState, cmd: DriverCommand):
        f = self.forces(z, cmd)
        p, u, v, r = self.params, max(0.0, z.u_m_s), z.v_m_s, z.yaw_rate_rad_s
        du, dv = f.body_x_n / p.mass_kg + v * r, f.body_y_n / p.mass_kg - u * r
        if u == 0 and du < 0:
            du = 0.0
        dx = u * math.cos(z.heading_rad) - v * math.sin(z.heading_rad)
        dy = u * math.sin(z.heading_rad) + v * math.cos(z.heading_rad)
        return dx, dy, r, du, dv, f.yaw_moment_n_m / p.yaw_inertia_kg_m2, 1.0, math.hypot(u, v)

    def step(self, z: VehicleState, cmd: DriverCommand, dt: float):
        z.validate()
        if not math.isfinite(dt) or not 0 < dt <= 0.05:
            raise ValueError("dt must be finite and in (0, 0.05] seconds")
        p = self.params
        # Conservative bound on linear tire damping stiffness; deterministic
        # internal RK4 substeps at low speeds, unchanged external control period.
        speed = max(p.slip_regularization_m_s, z.u_m_s)
        tau = min(p.mass_kg * speed / (p.cornering_front_n_per_rad + p.cornering_rear_n_per_rad),
                  p.yaw_inertia_kg_m2 * speed / (p.cornering_front_n_per_rad * p.lf_m**2 + p.cornering_rear_n_per_rad * p.lr_m**2))
        count = max(1, math.ceil(dt / min(0.02, 0.25 * tau)))
        if count > 1000:
            raise ValueError("parameters require impractically small integration substeps")
        h = dt / count
        names = tuple(field.name for field in fields(VehicleState))
        out = z
        def add(a, k, scale):
            return VehicleState(*(getattr(a, name) + h * scale * value for name, value in zip(names, k)))
        for _ in range(count):
            k1 = self.derivatives(out, cmd)
            k2 = self.derivatives(add(out, k1, .5), cmd)
            k3 = self.derivatives(add(out, k2, .5), cmd)
            k4 = self.derivatives(add(out, k3, 1), cmd)
            out = VehicleState(*(getattr(out, name) + h * (a + 2*b + 2*c + d) / 6
                                 for name, a, b, c, d in zip(names, k1, k2, k3, k4)))
            out.u_m_s = max(0.0, out.u_m_s)
            out.validate()
        f = self.forces(z, cmd)
        return out, f.body_x_n / p.mass_kg, f.body_y_n / p.mass_kg
