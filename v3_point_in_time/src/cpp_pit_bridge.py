"""Optional native C++17 Point-in-Time Racing Performance Engine bridge.

Provides transparent access to the compiled pybind11 extension
(`_indy500_pit_cpp`) when built, with a safe, deterministic pure-Python
fallback referencing the existing V3/V2 implementation when the native
binary is not compiled.

This module never modifies frozen scientific artifacts and preserves
identical point-in-time invariants and numerical semantics across both
the native C++ and Python paths.
"""
from __future__ import annotations

import importlib
import math
import os
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
CPP_BUILD_PYTHON_DIR = REPO_ROOT / "cpp" / "build" / "python"

_NATIVE_MODULE = None


def _try_load_native():
    global _NATIVE_MODULE
    if os.environ.get("INDY500_DISABLE_CPP", "").strip() in ("1", "true", "TRUE", "yes"):
        return False
    if _NATIVE_MODULE is not None:
        return _NATIVE_MODULE
    if CPP_BUILD_PYTHON_DIR.is_dir():
        build_str = str(CPP_BUILD_PYTHON_DIR)
        if build_str not in sys.path:
            sys.path.insert(0, build_str)
    try:
        _NATIVE_MODULE = importlib.import_module("_indy500_pit_cpp")
    except ImportError:
        _NATIVE_MODULE = False
    return _NATIVE_MODULE


def is_native_available() -> bool:
    """Return True if the compiled pybind11 C++ extension is importable."""
    mod = _try_load_native()
    return bool(mod)


def native_module():
    """Return the underlying `_indy500_pit_cpp` module, or raise ImportError."""
    mod = _try_load_native()
    if not mod:
        raise ImportError(
            "Native C++ module '_indy500_pit_cpp' is not built. "
            "Build it with: cmake -S cpp -B cpp/build && cmake --build cpp/build"
        )
    return mod


def check_point_in_time(
    decision_time: str,
    current_official_speed_known_at: Optional[str],
    current_track_temp_known_at: str,
    current_ambient_temp_known_at: str,
    forecast_issue_times: Iterable[str],
    *,
    prefer_native: bool = True,
):
    """Run the hard point-in-time leakage check via C++ (if available and
    `prefer_native=True`) or fall back to Python `point_in_time_guard`."""
    from schemas import GuardResult
    import point_in_time_guard as py_guard

    issue_list = list(forecast_issue_times)
    # Only None represents an absent optional timestamp; empty or whitespace-only
    # strings are rejected on both native C++ and Python paths.
    for label, ts in (
        ("decision_time", decision_time),
        ("current_official_speed_known_at", current_official_speed_known_at),
        ("current_track_temp_known_at", current_track_temp_known_at),
        ("current_ambient_temp_known_at", current_ambient_temp_known_at),
    ):
        if ts is None and label == "current_official_speed_known_at":
            continue
        if not isinstance(ts, str) or not ts.strip():
            raise ValueError(f"Invalid empty or whitespace timestamp for {label}: {ts!r}")
    for idx, fc_ts in enumerate(issue_list):
        if not isinstance(fc_ts, str) or not fc_ts.strip():
            raise ValueError(f"Invalid empty or whitespace forecast_issue_times[{idx}]: {fc_ts!r}")

    if prefer_native and is_native_available():
        mod = native_module()
        cpp_res = mod.check_point_in_time(
            decision_time,
            current_official_speed_known_at,
            current_track_temp_known_at,
            current_ambient_temp_known_at,
            issue_list,
        )
        return GuardResult(passed=bool(cpp_res.passed), reasons=tuple(cpp_res.reasons))

    return py_guard.check_point_in_time(
        decision_time=decision_time,
        current_official_speed_known_at=current_official_speed_known_at,
        current_track_temp_known_at=current_track_temp_known_at,
        current_ambient_temp_known_at=current_ambient_temp_known_at,
        forecast_issue_times=issue_list,
    )


def solar_elevation_deg(
    timestamp_utc: str,
    latitude_deg: float = 39.7950,
    longitude_deg: float = -86.2348,
    *,
    prefer_native: bool = True,
) -> float:
    """Compute NOAA-style solar elevation angle (deg) via C++ or Python."""
    if prefer_native and is_native_available():
        return float(
            native_module().solar_elevation_deg(
                str(timestamp_utc), float(latitude_deg), float(longitude_deg)
            )
        )
    import final_v2_adapter

    return float(
        final_v2_adapter.solar_elevation_deg(
            timestamp_utc, float(latitude_deg), float(longitude_deg)
        )
    )


def evaluate_applicability(
    horizon_min: int,
    current_track_temp_c: Optional[float],
    current_ambient_temp_c: Optional[float],
    forecast_future_ambient_temp_c: Optional[float],
    *,
    prefer_native: bool = True,
):
    """Evaluate applicability status via C++ or Python `applicability_gate`."""
    import applicability_gate as py_gate

    # Keep the bridge contract consistent without changing the application's
    # authoritative Python gate, which historically treats these as present.
    for name, value in (
        ("current_track_temp_c", current_track_temp_c),
        ("current_ambient_temp_c", current_ambient_temp_c),
        ("forecast_future_ambient_temp_c", forecast_future_ambient_temp_c),
    ):
        if value is not None and not math.isfinite(float(value)):
            raise ValueError(f"Non-finite input passed to evaluate_applicability: {name.upper()}")

    if prefer_native and is_native_available():
        cpp_res = native_module().evaluate_applicability(
            int(horizon_min),
            current_track_temp_c,
            current_ambient_temp_c,
            forecast_future_ambient_temp_c,
        )
        return py_gate.ApplicabilityResult(
            status=str(cpp_res.status),
            reasons=tuple(cpp_res.reasons),
            notes=tuple(cpp_res.notes),
        )
    return py_gate.evaluate(
        horizon_min=horizon_min,
        current_track_temp_c=current_track_temp_c,
        current_ambient_temp_c=current_ambient_temp_c,
        forecast_future_ambient_temp_c=forecast_future_ambient_temp_c,
    )


def summarize_draws(
    draws: Sequence[float],
    *,
    prefer_native: bool = True,
) -> dict:
    """Summarize Monte Carlo speed-delta draws via C++ or Python."""
    if prefer_native and is_native_available():
        cpp_sum = native_module().summarize_draws([float(x) for x in draws])
        return {
            "expected_delta_speed_mph": float(cpp_sum.expected_delta_speed_mph),
            "median_delta_speed_mph": float(cpp_sum.median_delta_speed_mph),
            "lower_80_mph": float(cpp_sum.lower_80_mph),
            "upper_80_mph": float(cpp_sum.upper_80_mph),
            "lower_90_mph": float(cpp_sum.lower_90_mph),
            "upper_90_mph": float(cpp_sum.upper_90_mph),
            "p_improve": float(cpp_sum.p_improve),
            "mc_sd_mph": float(cpp_sum.mc_sd_mph),
        }
    import final_v2_adapter
    import numpy as np

    return final_v2_adapter.summarize_draws(np.asarray(draws, dtype=float))


def infer_physical_response_terms(
    current_track_temp_c: float,
    current_ambient_temp_c: float,
    forecast_future_ambient_temp_c: float,
    decision_time: str,
    target_time: str,
    horizon_min: int,
    latitude_deg: float = 39.7950,
    longitude_deg: float = -86.2348,
    *,
    prefer_native: bool = True,
) -> dict:
    """Evaluate the deterministic M2b_mean_solar track-temperature change and
    zero-intercept physical speed response terms."""
    import final_v2_adapter

    artifacts = final_v2_adapter.load_frozen_artifacts()
    if horizon_min not in artifacts.track_coefficients:
        raise KeyError(f"Unsupported horizon_min={horizon_min}")
    c = artifacts.track_coefficients[horizon_min]

    if prefer_native and is_native_available():
        mod = native_module()
        coef_obj = mod.TrackModelCoefficients(
            horizon_min=int(horizon_min),
            intercept_c=float(c["intercept_c"]),
            beta_delta_ambient_temp_c=float(c["beta_delta_ambient_temp_c"]),
            beta_thermal_gap_0_c=float(c["beta_thermal_gap_0_c"]),
            beta_solar_elevation_mean_deg=float(c["beta_solar_elevation_mean_deg"]),
        )
        res = mod.evaluate_physical_response(
            float(current_track_temp_c),
            float(current_ambient_temp_c),
            float(forecast_future_ambient_temp_c),
            str(decision_time),
            str(target_time),
            coef_obj,
            float(latitude_deg),
            float(longitude_deg),
        )
        return {
            "horizon_minutes": int(res.horizon_minutes),
            "thermal_gap_0_c": float(res.thermal_gap_0_c),
            "delta_ambient_temp_c": float(res.delta_ambient_temp_c),
            "solar_elevation_mean_deg": float(res.solar_elevation_mean_deg),
            "predicted_delta_track_temp_c": float(res.predicted_delta_track_temp_c),
            "predicted_delta_speed_mph": float(res.predicted_delta_speed_mph),
        }

    for name, val in (
        ("current_track_temp_c", current_track_temp_c),
        ("current_ambient_temp_c", current_ambient_temp_c),
        ("forecast_future_ambient_temp_c", forecast_future_ambient_temp_c),
        ("latitude_deg", latitude_deg),
        ("longitude_deg", longitude_deg),
    ):
        if not math.isfinite(float(val)):
            raise ValueError(f"Non-finite numerical value for {name}")

    thermal_gap_0_c = float(current_track_temp_c) - float(current_ambient_temp_c)
    delta_ambient_temp_c = float(forecast_future_ambient_temp_c) - float(current_ambient_temp_c)
    s0 = solar_elevation_deg(decision_time, latitude_deg, longitude_deg, prefer_native=False)
    s1 = solar_elevation_deg(target_time, latitude_deg, longitude_deg, prefer_native=False)
    solar_mean = 0.5 * (s0 + s1)
    point_delta_track_c = (
        c["intercept_c"]
        + c["beta_delta_ambient_temp_c"] * delta_ambient_temp_c
        + c["beta_thermal_gap_0_c"] * thermal_gap_0_c
        + c["beta_solar_elevation_mean_deg"] * solar_mean
    )
    beta_track = -0.03482532976361639
    beta_ambient = 0.18239338404039918
    pred_speed = beta_track * point_delta_track_c + beta_ambient * delta_ambient_temp_c
    return {
        "horizon_minutes": int(horizon_min),
        "thermal_gap_0_c": thermal_gap_0_c,
        "delta_ambient_temp_c": delta_ambient_temp_c,
        "solar_elevation_mean_deg": solar_mean,
        "predicted_delta_track_temp_c": point_delta_track_c,
        "predicted_delta_speed_mph": pred_speed,
    }


# Backward-compatible spelling retained for existing callers.
infer_physical_response_Terms = infer_physical_response_terms


def enforce_point_in_time(guard_result, *, prefer_native: bool = True) -> None:
    """Raise the application's structured PointInTimeViolation exception."""
    if guard_result.passed:
        return
    from point_in_time_guard import PointInTimeViolation

    reasons = tuple(guard_result.reasons)
    if prefer_native and is_native_available():
        try:
            native_module().enforce_point_in_time(
                native_module().GuardResult(False, list(reasons))
            )
        except native_module().PointInTimeViolationError:
            # Use the established Python-facing exception contract and keep
            # the reason tuple/code relied on by application callers.
            raise PointInTimeViolation(reasons) from None
    raise PointInTimeViolation(reasons)
