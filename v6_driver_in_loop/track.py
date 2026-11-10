"""Analytic closed stadium oval; deliberately NOT a surveyed IMS centreline."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class TrackPoint:
    x_m: float
    y_m: float
    heading_rad: float
    curvature_per_m: float
    distance_m: float
    width_m: float
    banking_rad: float = 0.0


class OvalTrack:
    def __init__(self, straight_length_m=1000.0, radius_m=402.336,
                 width_m=15.0, banking_rad=0.0, samples=800):
        if any(not math.isfinite(x) or x <= 0 for x in (straight_length_m, radius_m, width_m)):
            raise ValueError("track dimensions must be finite and positive")
        if not math.isfinite(banking_rad) or banking_rad != 0:
            raise ValueError("banked force balance is unsupported; banking must be zero")
        if width_m >= 2 * radius_m:
            raise ValueError("width must be smaller than oval diameter")
        if not isinstance(samples, int) or samples < 20:
            raise ValueError("render samples must be an integer >=20")
        self.straight_length_m = float(straight_length_m)
        self.radius_m = float(radius_m)
        self.width_m = float(width_m)
        self.banking_rad = float(banking_rad)
        self.samples = samples
        self.length_m = 2 * self.straight_length_m + 2 * math.pi * self.radius_m

    def point(self, s: float) -> TrackPoint:
        if not math.isfinite(s):
            raise ValueError("distance must be finite")
        s = s % self.length_m
        L, R = self.straight_length_m, self.radius_m
        if s < L:
            x, y, th, k = s, 0., 0., 0.
        elif s < L + math.pi * R:
            q = (s-L)/R
            x, y, th, k = L + R*math.sin(q), R*(1-math.cos(q)), q, 1/R
        elif s < 2*L + math.pi*R:
            x, y, th, k = 2*L + math.pi*R-s, 2*R, math.pi, 0.
        else:
            q = (s-(2*L+math.pi*R))/R
            x, y, th, k = -R*math.sin(q), R+R*math.cos(q), math.pi+q, 1/R
        return TrackPoint(x, y, th, k, s, self.width_m, self.banking_rad)

    def nearest(self, x: float, y: float, around_s=None, window_m=100.0) -> TrackPoint:
        """Exact closest point on four analytic pieces; hint resolves ties only.

        samples affects rendering only. No along-track discretization error can
        turn a centreline state into a false boundary violation.
        """
        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError("position must be finite")
        L, R = self.straight_length_m, self.radius_m
        ss = [min(L, max(0., x)), L+math.pi*R + min(L, max(0., L-x)),
              L, L+math.pi*R, 2*L+math.pi*R, 0.0]
        if x >= L:
            ss.append(L+R*math.atan2(x-L, R-y))
        if x <= 0:
            ss.append(2*L+math.pi*R + R*math.atan2(-x, y-R))
        points = [self.point(s) for s in ss]
        def key(p):
            distance = (p.x_m-x)**2 + (p.y_m-y)**2
            hint = 0 if around_s is None else abs((p.distance_m-around_s+self.length_m/2) % self.length_m-self.length_m/2)
            return distance, hint
        return min(points, key=key)

    def error(self, state, point=None):
        p = point or self.nearest(state.x_m, state.y_m)
        return -(state.x_m-p.x_m)*math.sin(p.heading_rad) + (state.y_m-p.y_m)*math.cos(p.heading_rad)

    def target_speed(self, s, lateral_accel_limit=12.0, max_speed_m_s=85.0):
        if not all(math.isfinite(x) and x > 0 for x in (lateral_accel_limit, max_speed_m_s)):
            raise ValueError("target speed and lateral limit must be positive and finite")
        k = abs(self.point(s).curvature_per_m)
        return min(max_speed_m_s, math.sqrt(lateral_accel_limit/k)) if k else max_speed_m_s

    def metadata(self):
        return dict(kind='approximate_stadium', provenance='ILLUSTRATIVE, not official IMS GPS',
                    length_m=self.length_m, straight_length_m=self.straight_length_m,
                    radius_m=self.radius_m, width_m=self.width_m, banking_rad=self.banking_rad,
                    coordinates='local Cartesian x east, y north; metres; CCW radians')
