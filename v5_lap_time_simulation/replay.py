"""Versioned engineering replay contract; the frontend consumes these SI values."""
from dataclasses import asdict
import math

import numpy as np

from .model import Environment, SimulationResult, Track, Vehicle

SCHEMA_VERSION = "v5-replay-1"


def geometry_at(track: Track, distance_m: float) -> tuple[float, float]:
    """Integrate constant-curvature segments. This is an assumed path, not GPS."""
    x = y = heading = 0.0
    remaining = max(0.0, min(distance_m, track.length_m))
    for seg in track.segments:
        ds = min(remaining, seg.distance_m)
        if seg.radius_m is None:
            x += ds * math.cos(heading)
            y += ds * math.sin(heading)
        else:
            end = heading + ds / seg.radius_m
            x += seg.radius_m * (math.sin(end) - math.sin(heading))
            y += seg.radius_m * (math.cos(heading) - math.cos(end))
            heading = end
        remaining -= ds
        if remaining <= 1e-9:
            break
    return x, y


def replay_payload(track: Track, vehicle: Vehicle, environment: Environment,
                   result: SimulationResult) -> dict:
    """Nodes include an explicit periodic endpoint; cells have constant a in s.

    Mapping within each cell: s(t)=s0+v0*t+0.5*a*t²; this exactly matches
    dt=2*ds/(v0+v1), rather than linearly interpolating distance in time.
    """
    distance = np.append(result.distance_m, result.track_length_m)
    elapsed = np.r_[0.0, np.cumsum(result.time_step_s)]
    speeds = np.append(result.speed_mps, result.speed_mps[0])
    accel = (speeds[1:] ** 2 - speeds[:-1] ** 2) / (2 * result.distance_step_m)
    corner = (result.curvature_1pm > 0) & (np.abs(result.speed_mps-result.corner_speed_limit_mps) < .05)
    modes = []
    for i, a in enumerate(accel):
        if a > 1e-4 and abs(a-result.acceleration_limit_mps2[i]) < .05:
            modes.append("acceleration")
        elif a < -1e-4 and abs(-a-result.braking_limit_mps2[i]) < .05:
            modes.append("braking")
        elif corner[i]:
            modes.append("corner_cap")
        else:
            modes.append("steady_or_transition")
    offset = 0.0
    segments = []
    for i, seg in enumerate(track.segments):
        mask = result.segment_index == i
        segments.append({**asdict(seg), "start_m": offset,
                         "time_s": float(result.time_step_s[mask].sum()),
                         "label_xy_m": geometry_at(track, offset+seg.distance_m/2)})
        offset += seg.distance_m
    end = geometry_at(track, track.length_m)
    if math.hypot(*end) > 1e-6:
        raise ValueError("replay geometry does not close; use a separately labelled schematic")
    return {
        "schema_version": SCHEMA_VERSION,
        "units": {"distance": "m", "time": "s", "speed": "m/s", "acceleration": "m/s²", "geometry": "m"},
        "provenance": {
            "track": "ASSUMED constant-radius path; nominal dimensions referenced to INDYCAR; not surveyed GPS",
            "vehicle": "ASSUMED generic mass, drag area, downforce area, tire grip and force limits",
            "power_w": "CALIBRATED effective scalar on 2020–2023; edited values are scenario assumptions, not refitted",
            "environment": "ASSUMED fixed air and track conditions",
            "boundary": "Simulated V5 quasi-steady replay. No ECU telemetry, historical footage or V6 driver dynamics.",
        },
        "origin": "Turn 1 entry (simulation origin; not the official timing line)",
        "vehicle": asdict(vehicle), "environment": asdict(environment),
        "lap_time_s": result.lap_time_s, "track_length_m": track.length_m,
        "average_speed_mph": result.average_speed_mph, "segments": segments,
        "distance_m": distance.tolist(), "elapsed_s": elapsed.tolist(), "speed_mps": speeds.tolist(),
        "speed_cap_mps": np.append(result.corner_speed_limit_mps, result.corner_speed_limit_mps[0]).tolist(),
        "acceleration_mps2": accel.tolist(), "mode": modes,
        "xy_m": [geometry_at(track, float(s)) for s in distance],
    }
