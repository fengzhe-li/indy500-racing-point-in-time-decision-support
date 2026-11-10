"""Reproducible sensitivity study and historical comparison helpers."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from .model import (
    Environment, MPS_TO_MPH, Track, Vehicle, build_ims_oval_approximation,
    simulate_lap, with_changes,
)


def sensitivity_study(base_vehicle: Vehicle | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    track = build_ims_oval_approximation()
    base_vehicle = base_vehicle or Vehicle()
    base_environment = Environment(track_temperature_c=35.0)
    base = simulate_lap(track, base_vehicle, base_environment)
    experiments: list[tuple[str, str, float, str, Vehicle, Environment]] = []
    for name, field, value in (
        ("Mass +10%", "mass_kg", base_vehicle.mass_kg * 1.1),
        ("Drag area +10%", "cd_a_m2", base_vehicle.cd_a_m2 * 1.1),
        ("Downforce area +10%", "cl_a_m2", base_vehicle.cl_a_m2 * 1.1),
        ("Tire grip +5%", "tire_mu", base_vehicle.tire_mu * 1.05),
        ("Available power +10%", "power_w", base_vehicle.power_w * 1.1),
    ):
        experiments.append((name, field, value, "vehicle", with_changes(base_vehicle, **{field: value}), base_environment))
    for name, field, value in (
        ("Air temperature +10 C", "air_temperature_c", 35.0),
        ("Track temperature +10 C", "track_temperature_c", 45.0),
    ):
        experiments.append((name, field, value, "environment", base_vehicle, with_changes(base_environment, **{field: value})))

    rows: list[dict[str, Any]] = []
    segrows: list[dict[str, Any]] = []
    for name, field, value, kind, veh, env in experiments:
        result = simulate_lap(track, veh, env)
        delta = result.lap_time_s - base.lap_time_s
        rows.append({
            "experiment": name, "parameter": field, "parameter_value": value,
            "parameter_unit": {"mass_kg": "kg", "cd_a_m2": "m^2", "cl_a_m2": "m^2",
                               "tire_mu": "dimensionless", "power_w": "W",
                               "air_temperature_c": "degC", "track_temperature_c": "degC"}[field],
            "baseline_lap_time_s": base.lap_time_s, "modified_lap_time_s": result.lap_time_s,
            "delta_lap_time_s": delta, "delta_percent": 100 * delta / base.lap_time_s,
            "baseline_average_speed_mph": base.average_speed_mph,
            "modified_average_speed_mph": result.average_speed_mph,
            "model_classification": "SIMULATED_ASSUMPTION_SENSITIVITY",
        })
        base_contrib = _segment_times(base, track)
        modified_contrib = _segment_times(result, track)
        for i, seg in enumerate(track.segments):
            segrows.append({
                "experiment": name, "segment": seg.name,
                "baseline_time_s": base_contrib[i], "modified_time_s": modified_contrib[i],
                "delta_time_s": modified_contrib[i] - base_contrib[i],
                "classification": "SIMULATED_SEGMENT_CONTRIBUTION",
            })
    return rows, segrows


def _segment_times(result: Any, track: Track) -> list[float]:
    return [float(np.sum(result.time_step_s[result.segment_index == i])) for i in range(len(track.segments))]


def load_historical_records(data_dir: Path) -> list[dict[str, Any]]:
    """Load canonical official complete-four-lap attempts with valid distance/time."""
    attempts_path = data_dir / "attempts.csv"
    laps_path = data_dir / "attempt_laps.csv"
    if not attempts_path.exists() or not laps_path.exists():
        raise FileNotFoundError(f"expected attempts.csv and attempt_laps.csv under {data_dir}")
    with attempts_path.open(newline="", encoding="utf-8-sig") as f:
        attempts = list(csv.DictReader(f))
    with laps_path.open(newline="", encoding="utf-8-sig") as f:
        laps = list(csv.DictReader(f))
    counts: dict[str, int] = {}
    for row in laps:
        if row.get("lap_completion_status") == "COMPLETE":
            counts[row["attempt_id"]] = counts.get(row["attempt_id"], 0) + 1
    rows: list[dict[str, Any]] = []
    for a in attempts:
        if counts.get(a["attempt_id"]) != 4:
            continue
        try:
            observed_mph = float(a["four_lap_average_speed_mph"])
            observed_total = float(a["four_lap_total_seconds"])
        except (ValueError, TypeError):
            continue
        if not (math.isfinite(observed_mph) and observed_mph > 0 and math.isfinite(observed_total) and observed_total > 0):
            continue
        rows.append({
            "attempt_id": a["attempt_id"], "year": 2024, "car_number": a.get("car_number", ""),
            "driver_name": a.get("driver_name", ""), "session_id": a.get("session_id", ""),
            "observed_four_lap_average_speed_mph": observed_mph,
            "observed_four_lap_total_seconds": observed_total,
        })
        rows[-1]["year"] = int(a["session_id"].rsplit("_", 1)[-1])
    return rows


def calibrate_effective_power(data_dir: Path, *, ds_m: float = 10.0) -> tuple[Vehicle, dict[str, Any]]:
    """Fit one effective power parameter to pre-2024 training attempts.

    The fitted scalar is an aggregate performance knob conditional on the fixed
    assumed mass/aero/grip/track model. It is not a measurement of engine power.
    Minimising absolute error in a constant-speed model is equivalent to matching
    the training median speed.
    """
    records = load_historical_records(data_dir)
    training = [r for r in records if 2020 <= r["year"] <= 2023]
    if not training:
        raise ValueError("no complete 2020-2023 attempts available for calibration")
    target = float(np.median([r["observed_four_lap_average_speed_mph"] for r in training]))
    track, env = build_ims_oval_approximation(), Environment(track_temperature_c=35.0)
    template = Vehicle()
    lo, hi = 300_000.0, 1_600_000.0
    def speed(power: float) -> float:
        return simulate_lap(track, with_changes(template, power_w=power), env, ds_m=ds_m).average_speed_mph
    if not speed(lo) <= target <= speed(hi):
        raise ValueError("training median lies outside configured effective-power calibration bracket")
    for _ in range(40):
        mid = (lo + hi) / 2
        if speed(mid) < target:
            lo = mid
        else:
            hi = mid
    fitted_power = (lo + hi) / 2
    calibrated_vehicle = with_changes(template, power_w=fitted_power)
    actual_speed = speed(fitted_power)
    report = {
        "calibration_years": "2020-2023",
        "training_attempts": len(training),
        "objective": "minimise absolute official average-speed error; target pooled median",
        "training_median_average_speed_mph": target,
        "fitted_effective_power_w": fitted_power,
        "simulated_speed_at_fit_mph": actual_speed,
        "absolute_fit_residual_mph": abs(actual_speed - target),
        "parameter_classification": "CALIBRATED_EFFECTIVE_SCALAR_CONDITIONAL_ON_ASSUMED_MODEL",
        "interpretation_limit": "Not engine power measurement; different mass/aero/grip combinations can produce similar aggregate speed.",
        "held_out_validation_year": 2024,
        "holdout_scope": "Excluded from scalar fitting; retrospective descriptive comparison, not an untouched model-development holdout.",
        "calibration_mesh_max_step_m": ds_m,
    }
    return calibrated_vehicle, report


def historical_validation(data_dir: Path, simulated_lap_time_s: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Retrospective 2024 comparison; excluded from the scalar fit."""
    records = [r for r in load_historical_records(data_dir) if r["year"] == 2024]
    rows: list[dict[str, Any]] = []
    for a in records:
        sim_four_lap_time = 4 * simulated_lap_time_s
        sim_speed = 2.5 * 4 * 3600 / sim_four_lap_time
        observed_mph = a["observed_four_lap_average_speed_mph"]
        observed_total = a["observed_four_lap_total_seconds"]
        rows.append({
            "attempt_id": a["attempt_id"], "year": a["year"], "car_number": a["car_number"],
            "driver_name": a["driver_name"], "observed_four_lap_average_speed_mph": observed_mph,
            "simulated_four_lap_average_speed_mph": sim_speed,
            "speed_residual_sim_minus_obs_mph": sim_speed - observed_mph,
            "observed_four_lap_total_seconds": observed_total,
            "simulated_four_lap_total_seconds": sim_four_lap_time,
            "time_residual_sim_minus_obs_s": sim_four_lap_time - observed_total,
            "evaluation_role": "YEAR_SEPARATED_2024_RETROSPECTIVE_DESCRIPTIVE_CHECK",
            "fit_role": "NOT_USED_FOR_CALIBRATION",
        })
    speed_errors = [r["speed_residual_sim_minus_obs_mph"] for r in rows]
    time_errors = [r["time_residual_sim_minus_obs_s"] for r in rows]
    def metrics(errors: list[float]) -> dict[str, float | None]:
        if not errors:
            return {"n": 0, "mae": None, "rmse": None, "mean_error": None}
        return {"n": len(errors), "mae": float(np.mean(np.abs(errors))),
                "rmse": float(np.sqrt(np.mean(np.square(errors)))), "mean_error": float(np.mean(errors))}
    report = {
        "validation_year": 2024, "method": "one effective scalar fit on 2020-2023; all remaining parameters assumed",
        "sample_size": len(rows), "average_speed_mph": metrics(speed_errors),
        "four_lap_time_seconds": metrics(time_errors),
        "claim_boundary": "Descriptive agreement only; aggregate speed does not identify vehicle dynamics.",
        "development_boundary": "2024 results have been inspected during development; exclusion from scalar fitting is not an untouched prospective holdout.",
    }
    return rows, report


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def run_analysis(output_dir: Path, data_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    track = build_ims_oval_approximation()
    environment = Environment(track_temperature_c=35.0)
    vehicle, calibration = calibrate_effective_power(data_dir)
    (output_dir / "calibration.json").write_text(json.dumps(calibration, indent=2), encoding="utf-8")
    result = simulate_lap(track, vehicle, environment)
    summary = {
        "model": "V5 quasi-steady point-mass lap simulation",
        "physics_revision": "banked-force-consistency-audit-1",
        "mesh_max_step_m": 10.0,
        "track": track.name, "track_length_m": track.length_m,
        "track_length_mi": track.length_m / 1609.344,
        "lap_time_s": result.lap_time_s, "average_speed_mph": result.average_speed_mph,
        "iterations": result.iterations, "converged": result.converged,
        "air_density_kg_m3": environment.air_density_kg_m3,
        "vehicle": vehicle.__dict__, "environment": environment.__dict__,
        "track_segments": [s.__dict__ for s in track.segments],
        "parameter_status": "one CALIBRATED effective scalar; all other vehicle/track inputs ASSUMED",
    }
    (output_dir / "baseline.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    profile = []
    edge_accel = (np.roll(result.speed_mps, -1) ** 2 - result.speed_mps ** 2) / (2 * result.distance_step_m)
    for i, x in enumerate(result.distance_m):
        j = (i + 1) % len(result.speed_mps)
        accel_limited = edge_accel[i] > 1e-4 and abs(edge_accel[i] - result.acceleration_limit_mps2[i]) < 0.05
        braking_limited = edge_accel[i] < -1e-4 and abs(-edge_accel[i] - result.braking_limit_mps2[i]) < 0.05
        corner_limited = result.curvature_1pm[i] > 0 and abs(result.speed_mps[i] - result.corner_speed_limit_mps[i]) < 0.05
        profile.append({
            "distance_m": float(x), "distance_mi": float(x / 1609.344),
            "distance_step_m": float(result.distance_step_m[i]),
            "speed_mps": float(result.speed_mps[i]), "speed_mph": float(result.speed_mps[i] * MPS_TO_MPH),
            "corner_speed_limit_mph": float(result.corner_speed_limit_mps[i] * MPS_TO_MPH),
            "acceleration_limit_mps2": float(result.acceleration_limit_mps2[i]),
            "braking_limit_mps2": float(result.braking_limit_mps2[i]),
            "edge_acceleration_mps2": float(edge_accel[i]),
            "acceleration_limited_region": accel_limited,
            "braking_limited_region": braking_limited,
            "corner_speed_limited_region": corner_limited,
            "segment": track.segments[result.segment_index[i]].name,
            "time_step_s": float(result.time_step_s[i]),
        })
    write_csv(output_dir / "speed_profile.csv", profile)
    segrows = []
    for i, s in enumerate(track.segments):
        mask = result.segment_index == i
        segrows.append({"segment": s.name, "distance_m": s.distance_m,
                        "radius_m": s.radius_m or "", "banking_deg": s.banking_deg,
                        "time_s": float(np.sum(result.time_step_s[mask])),
                        "mean_speed_mph": float(s.distance_m / np.sum(result.time_step_s[mask]) * MPS_TO_MPH),
                        "max_speed_mph": float(np.max(result.speed_mps[mask]) * MPS_TO_MPH),
                        "classification": "SIMULATED"})
    write_csv(output_dir / "segment_times.csv", segrows)
    sensitivity, sensitivity_segments = sensitivity_study(vehicle)
    write_csv(output_dir / "sensitivity.csv", sensitivity)
    write_csv(output_dir / "sensitivity_segment_contributions.csv", sensitivity_segments)
    historical_rows, validation = historical_validation(data_dir, result.lap_time_s)
    write_csv(output_dir / "historical_validation_2024.csv", historical_rows)
    (output_dir / "validation_metrics.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    from .audit import write_audit
    from .replay import replay_payload
    write_audit(output_dir, data_dir, vehicle, environment, result)
    (output_dir / "replay.json").write_text(json.dumps(replay_payload(track, vehicle, environment, result), indent=2), encoding="utf-8")
    low_vehicle = with_changes(vehicle, tire_mu=vehicle.tire_mu * .75)
    low_result = simulate_lap(track, low_vehicle, environment)
    (output_dir / "replay_low_grip.json").write_text(json.dumps(replay_payload(track, low_vehicle, environment, low_result), indent=2), encoding="utf-8")
    _plot(output_dir, result, track, historical_rows, sensitivity)
    return {"baseline": summary, "validation": validation, "sensitivity": sensitivity}


def _plot(output_dir: Path, result: Any, track: Track, observed: list[dict[str, Any]],
          sensitivities: list[dict[str, Any]]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    x_mi = result.distance_m / 1609.344
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(x_mi, result.speed_mps * MPS_TO_MPH, color="#145da0", label="Simulated speed")
    ax.plot(x_mi, result.corner_speed_limit_mps * MPS_TO_MPH, color="#c43c35", alpha=.65,
            linestyle="--", label="Local sustainable corner / power cap")
    next_v = np.roll(result.speed_mps, -1)
    edge_a = (next_v ** 2 - result.speed_mps ** 2) / (2 * result.distance_step_m)
    accel_mask = (edge_a > 1e-4) & (np.abs(edge_a - result.acceleration_limit_mps2) < 0.05)
    brake_mask = (edge_a < -1e-4) & (np.abs(-edge_a - result.braking_limit_mps2) < 0.05)
    corner_mask = (result.curvature_1pm > 0) & (np.abs(result.speed_mps - result.corner_speed_limit_mps) < 0.05)
    ax.scatter(x_mi[accel_mask], (result.speed_mps * MPS_TO_MPH)[accel_mask], s=8,
               color="#238636", label="Acceleration limited")
    ax.scatter(x_mi[brake_mask], (result.speed_mps * MPS_TO_MPH)[brake_mask], s=8,
               color="#e67700", label="Braking limited")
    ax.scatter(x_mi[corner_mask], (result.speed_mps * MPS_TO_MPH)[corner_mask], s=8,
               color="#c43c35", label="At local curve cap (may be power limited)")
    ax.set(xlabel="Track distance (mi)", ylabel="Speed (mph)", title="V5 quasi-steady speed profile — assumed IMS oval")
    ax.grid(alpha=.25); ax.legend(); fig.tight_layout()
    fig.savefig(output_dir / "speed_profile.png", dpi=160); plt.close(fig)
    if observed:
        fig, ax = plt.subplots(figsize=(7, 6))
        obs = np.array([r["observed_four_lap_average_speed_mph"] for r in observed])
        sim = np.array([r["simulated_four_lap_average_speed_mph"] for r in observed])
        ax.scatter(obs, sim, alpha=.75, color="#145da0")
        lo, hi = min(obs.min(), sim.min()) - 1, max(obs.max(), sim.max()) + 1
        ax.plot([lo, hi], [lo, hi], "k--", linewidth=1)
        ax.set(xlabel="Observed official four-lap average speed (mph)",
               ylabel="Simulated average speed (mph)", title="2024 retrospective descriptive comparison")
        ax.grid(alpha=.25); fig.tight_layout()
        fig.savefig(output_dir / "historical_comparison.png", dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(9, 5))
    names = [r["experiment"] for r in sensitivities]
    deltas = [r["delta_lap_time_s"] for r in sensitivities]
    ax.barh(names, deltas, color=["#c43c35" if d > 0 else "#238636" for d in deltas])
    ax.axvline(0, color="black", linewidth=.8)
    ax.set(xlabel="Lap-time change from baseline (s)", title="Assumption sensitivity — simulated, not measured")
    ax.grid(axis="x", alpha=.25); fig.tight_layout()
    fig.savefig(output_dir / "sensitivity.png", dpi=160); plt.close(fig)
