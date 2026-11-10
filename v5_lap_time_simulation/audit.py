"""Reproducible discretisation, banking and constant-predictor audit."""
import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from .model import G, MPS_TO_MPH, Environment, Vehicle, build_ims_oval_approximation, simulate_lap, tire_loads, _effective_mu


def mesh_study(vehicle: Vehicle, environment: Environment) -> list[dict]:
    """Freeze fitted parameters across grids; compare spatially interpolated v²."""
    steps = (40., 20., 10., 5., 2.5, 1.25)
    runs = [simulate_lap(vehicle=vehicle, environment=environment, ds_m=dx) for dx in steps]
    x = np.linspace(0, runs[-1].track_length_m, 8001)
    def profile(run):
        return np.sqrt(np.interp(x, np.r_[run.distance_m, run.track_length_m],
                                np.r_[run.speed_mps**2, run.speed_mps[0]**2]))
    reference = profile(runs[-1])
    return [{"step_m": dx, "cells": len(r.speed_mps), "lap_time_s": r.lap_time_s,
             "delta_vs_finest_s": r.lap_time_s-runs[-1].lap_time_s,
             "profile_rmse_vs_finest_mps": float(np.sqrt(np.mean((profile(r)-reference)**2))),
             "profile_max_abs_vs_finest_mps": float(np.max(np.abs(profile(r)-reference))),
             "iterative_passes": r.iterations}
            for dx, r in zip(steps, runs)]


def constant_baselines(data_dir: Path, physics_speed: float) -> list[dict]:
    from .analysis import load_historical_records
    rows = load_historical_records(data_dir)
    train = [r["observed_four_lap_average_speed_mph"] for r in rows if 2020 <= r["year"] <= 2023]
    test = [r for r in rows if r["year"] == 2024]
    predictors = [("physics_generic", physics_speed), ("training_median", float(np.median(train))),
                  ("training_mean", float(np.mean(train))), ("fixed_230_mph", 230.)]
    results = []
    for name, speed in predictors:
        residual = np.array([speed-r["observed_four_lap_average_speed_mph"] for r in test])
        time_residual = np.array([36000/speed-r["observed_four_lap_total_seconds"] for r in test])
        results.append({"predictor": name, "speed_mph": speed, "n_2024": len(test),
                        "speed_mae_mph": float(np.mean(abs(residual))),
                        "speed_rmse_mph": float(np.sqrt(np.mean(residual**2))),
                        "speed_bias_mph": float(residual.mean()),
                        "four_lap_time_mae_s": float(np.mean(abs(time_residual))),
                        "four_lap_time_rmse_s": float(np.sqrt(np.mean(time_residual**2)))})
    return results


def write_audit(output_dir, data_dir, vehicle, environment, result):
    from .analysis import write_csv
    mesh = mesh_study(vehicle, environment)
    # A corner-limited perturbation is also required: baseline may be power limited.
    grip_mesh = mesh_study(replace(vehicle, tire_mu=vehicle.tire_mu*.75), environment)
    write_csv(output_dir / "mesh_convergence.csv", mesh)
    write_csv(output_dir / "mesh_convergence_low_grip.csv", grip_mesh)
    write_csv(output_dir / "constant_baselines_2024.csv", constant_baselines(data_dir, result.average_speed_mph))
    old_vehicle = replace(Vehicle(), power_w=820816.877239622)
    corrected_fixed = simulate_lap(vehicle=old_vehicle, environment=environment)
    unbanked = simulate_lap(build_ims_oval_approximation(banking_deg=0), old_vehicle, environment)
    # The old output is anchored to the committed initial V5 revision, not refitted.
    old_v = 223.15986460529984 / MPS_TO_MPH
    rho, mu = environment.air_density_kg_m3, _effective_mu(old_vehicle, environment)
    old_n = old_vehicle.mass_kg*G + .5*rho*old_vehicle.cl_a_m2*old_v**2
    old_fy = old_vehicle.mass_kg*old_v**2/256
    normal, fy = tire_loads(old_vehicle, environment, old_v, 1/256, 9.2)
    audit = {"legacy_revision": "18b8623c01f423f8072996a8ca92ffd2ddc0806e",
             "legacy_lap_time_s": 38.987452538190574,
             "corrected_fixed_legacy_parameters_lap_s": corrected_fixed.lap_time_s,
             "corrected_zero_bank_same_parameters_lap_s": unbanked.lap_time_s,
             "legacy_corner_speed_mps": old_v,
             "legacy_flat_circle_lateral_utilisation": old_fy/(mu*old_n),
             "consistent_banked_lateral_utilisation_at_legacy_speed": abs(fy)/(mu*normal),
             "legacy_flat_normal_n": old_n, "consistent_banked_normal_n": normal,
             "interpretation": "Old mixed equations gave zero remaining tire capacity while drag still required drive force. Corrections include banked loads, sustained-speed caps, cell geometry, signed force limits and boundary caps; fixed-parameter lap delta is their combined effect.",
             "mesh_note": "Fitted parameters held fixed across steps; finest grid is a reference, not an exact solution. Baseline and -25% grip scenario both reported."}
    (output_dir / "physics_audit.json").write_text(json.dumps(audit, indent=2))
