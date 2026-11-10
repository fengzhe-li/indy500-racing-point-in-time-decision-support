"""Python <-> C++17 Point-in-Time Engine parity, leakage, and fallback tests.

Exercises the compiled pybind11 extension (`_indy500_pit_cpp`) via
`v3_point_in_time/src/cpp_pit_bridge.py` against the authoritative Python
implementations (`point_in_time_guard`, `forecast_vintage_store`,
`applicability_gate`, `final_v2_adapter`, and `v2_build_future_track_samples`).
"""
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

import fixtures  # noqa: E402,F401  (adds src/ to sys.path)

import applicability_gate
import cpp_pit_bridge
import final_v2_adapter
import point_in_time_guard
from forecast_vintage_store import ForecastVintageStore

REPO_ROOT = fixtures.REPO_ROOT


@unittest.skipUnless(
    cpp_pit_bridge.is_native_available(),
    "Native C++ pybind11 module (_indy500_pit_cpp) not built",
)
class CppPythonParityTests(unittest.TestCase):
    def setUp(self):
        self.cpp = cpp_pit_bridge.native_module()

    def test_point_in_time_guard_parity_across_boundary_and_leakage_cases(self):
        decision_time = "2020-08-15T12:00:00Z"
        cases = [
            # Exact boundary equality
            (decision_time, decision_time, decision_time, decision_time, [decision_time]),
            # Future forecast leak (+1 second)
            (decision_time, None, decision_time, decision_time, ["2020-08-15T12:00:01Z"]),
            # Future track temp leak
            (decision_time, None, "2020-08-15T12:00:05Z", decision_time, [decision_time]),
            # Multiple violations
            (
                decision_time,
                "2020-08-15T12:00:02Z",
                "2020-08-15T12:00:03Z",
                "2020-08-15T12:00:04Z",
                [decision_time, "2020-08-15T12:05:00Z"],
            ),
        ]
        for dt, spd_t, trk_t, amb_t, fc_times in cases:
            py_res = point_in_time_guard.check_point_in_time(dt, spd_t, trk_t, amb_t, fc_times)
            cpp_res = cpp_pit_bridge.check_point_in_time(
                dt, spd_t, trk_t, amb_t, fc_times, prefer_native=True
            )
            self.assertEqual(py_res.passed, cpp_res.passed)
            self.assertEqual(py_res.reasons, cpp_res.reasons)

    def test_empty_optional_speed_timestamp_and_malformed_timestamps(self):
        decision = "2020-08-15T12:00:00Z"
        for prefer_native in (True, False):
            # None is accepted as an absent optional timestamp
            result = cpp_pit_bridge.check_point_in_time(
                decision, None, decision, decision, [decision], prefer_native=prefer_native
            )
            self.assertTrue(result.passed)
            # Empty or whitespace-only strings are rejected on both paths
            for bad_ts in ("", "   ", "not-a-timestamp"):
                with self.assertRaises(ValueError):
                    cpp_pit_bridge.check_point_in_time(
                        decision, bad_ts, decision, decision, [], prefer_native=prefer_native
                    )
                with self.assertRaises(ValueError):
                    cpp_pit_bridge.check_point_in_time(
                        decision, None, bad_ts, decision, [], prefer_native=prefer_native
                    )
                with self.assertRaises(ValueError):
                    cpp_pit_bridge.check_point_in_time(
                        decision, None, decision, bad_ts, [], prefer_native=prefer_native
                    )
                with self.assertRaises(ValueError):
                    cpp_pit_bridge.check_point_in_time(
                        decision, None, decision, decision, [bad_ts], prefer_native=prefer_native
                    )

    def test_non_finite_applicability_values_rejected_consistently(self):
        for value in (float("nan"), float("inf"), float("-inf")):
            for position in range(3):
                args = [35.0, 27.0, 28.0]
                args[position] = value
                for prefer_native in (True, False):
                    with self.subTest(value=value, position=position, prefer_native=prefer_native):
                        with self.assertRaisesRegex(ValueError, "Non-finite input"):
                            cpp_pit_bridge.evaluate_applicability(
                                60, *args, prefer_native=prefer_native
                            )

    def test_python_facing_point_in_time_exception_has_details(self):
        from point_in_time_guard import PointInTimeViolation
        from schemas import GuardResult

        reasons = ("CURRENT_TRACK_TEMP_KNOWN_AT_AFTER_DECISION_TIME",)
        for prefer_native in (True, False):
            with self.assertRaises(PointInTimeViolation) as caught:
                cpp_pit_bridge.enforce_point_in_time(
                    GuardResult(False, reasons), prefer_native=prefer_native
                )
            self.assertEqual(caught.exception.reasons, reasons)
            self.assertEqual(caught.exception.code, "POINT_IN_TIME_VIOLATION")

    def test_snake_case_and_legacy_physical_response_names_match(self):
        kwargs = dict(
            current_track_temp_c=35.0,
            current_ambient_temp_c=27.0,
            forecast_future_ambient_temp_c=29.0,
            decision_time="2021-05-22T16:00:00Z",
            target_time="2021-05-22T17:00:00Z",
            horizon_min=60,
            prefer_native=True,
        )
        snake = cpp_pit_bridge.infer_physical_response_terms(**kwargs)
        legacy = cpp_pit_bridge.infer_physical_response_Terms(**kwargs)
        self.assertEqual(snake, legacy)

    def test_solar_elevation_parity_across_all_656_frozen_samples(self):
        samples_path = REPO_ROOT / "weather/output/v2_future_track/future_track_samples_with_solar_v1.csv"
        df = pd.read_csv(samples_path)
        self.assertEqual(len(df), 656)
        for _, row in df.iterrows():
            t0 = str(row["t0_utc"])
            t1 = str(row["future_utc"])
            cpp_s0 = self.cpp.solar_elevation_deg(t0, 39.7950, -86.2348)
            cpp_s1 = self.cpp.solar_elevation_deg(t1, 39.7950, -86.2348)
            self.assertAlmostEqual(cpp_s0, float(row["solar_elevation_0_deg"]), places=12)
            self.assertAlmostEqual(cpp_s1, float(row["future_solar_elevation_deg"]), places=12)

    def test_forecast_vintage_selection_parity_on_real_hrrr_dataset(self):
        hrrr_path = REPO_ROOT / "weather/output/hrrr_ims_2020_2024_features.csv"
        py_store = ForecastVintageStore.load_hrrr_features(hrrr_path, 39.7950, -86.2348)
        cpp_store = self.cpp.ForecastVintageStore()
        for v in py_store.all():
            cpp_store.add(
                self.cpp.ForecastVintageRecord(
                    forecast_id=v.forecast_id,
                    source=v.source,
                    model_name=v.model_name,
                    model_run=v.model_run,
                    issue_time=v.issue_time,
                    valid_time=v.valid_time,
                    lead_minutes=v.lead_minutes,
                    ambient_temp_c=v.ambient_temp_c,
                )
            )
        self.assertEqual(cpp_store.size(), len(py_store.all()))

        decision_times = [
            "2020-08-15T14:30:00Z",
            "2021-05-22T16:15:00Z",
            "2022-05-21T17:00:00Z",
            "2023-05-20T18:45:00Z",
            "2024-05-18T15:20:00Z",
        ]
        for dt in decision_times:
            for h in (15, 30, 60, 90, 120):
                target_t = self.cpp.target_time_for(dt, h)
                py_sel = py_store.select(dt, target_t)
                cpp_sel = cpp_store.select(dt, target_t)
                self.assertIsNotNone(py_sel)
                self.assertIsNotNone(cpp_sel)
                self.assertEqual(py_sel["vintage"].forecast_id, cpp_sel.vintage.forecast_id)
                self.assertAlmostEqual(
                    py_sel["valid_time_error_minutes"],
                    cpp_sel.valid_time_error_minutes,
                    places=12,
                )

    def test_applicability_gate_parity(self):
        test_inputs = [
            (15, 35.0, 27.0, 28.0),
            (30, 35.0, 27.0, 28.0),
            (60, 35.0, 27.0, 28.0),
            (90, 35.0, 27.0, 28.0),
            (120, 35.0, 27.0, 28.0),
            (45, 35.0, 27.0, 28.0),
            (0, 35.0, 27.0, 28.0),
            (-10, 35.0, 27.0, 28.0),
            (150, 35.0, 27.0, 28.0),
            (60, None, 27.0, 28.0),
            (60, 35.0, None, None),
        ]
        for h, trk, amb, fc in test_inputs:
            py_res = applicability_gate.evaluate(h, trk, amb, fc)
            cpp_res = cpp_pit_bridge.evaluate_applicability(h, trk, amb, fc, prefer_native=True)
            self.assertEqual(py_res.status, cpp_res.status)
            self.assertEqual(py_res.reasons, cpp_res.reasons)
            self.assertEqual(py_res.notes, cpp_res.notes)

    def test_monte_carlo_draw_summary_and_combination_exact_parity(self):
        rng = np.random.default_rng(20260914)
        artifacts = final_v2_adapter.load_frozen_artifacts()
        for h in (15, 30, 60, 90, 120):
            coef = artifacts.track_coefficients[h]
            n_mc = 5000
            track_noise = final_v2_adapter.symmetrized_draws_from_values(
                artifacts.track_residual_pools[h], n_mc, rng
            )
            coef_idx = rng.integers(0, len(artifacts.bootstrap_pairs), size=n_mc)
            beta_track = artifacts.bootstrap_pairs["beta_track_temp"].to_numpy()[coef_idx]
            beta_ambient = artifacts.bootstrap_pairs["beta_ambient_temp"].to_numpy()[coef_idx]
            perf_noise = final_v2_adapter.symmetrized_draws_from_values(
                artifacts.performance_residual_pool, n_mc, rng
            )

            point_delta_track = 1.75
            delta_ambient = 1.25
            py_draws = beta_track * (point_delta_track + track_noise) + beta_ambient * delta_ambient + perf_noise
            py_sum = final_v2_adapter.summarize_draws(py_draws)

            cpp_out = self.cpp.evaluate_monte_carlo_draws(
                h,
                point_delta_track,
                delta_ambient,
                track_noise.tolist(),
                beta_track.tolist(),
                beta_ambient.tolist(),
                perf_noise.tolist(),
            )
            self.assertAlmostEqual(py_sum["expected_delta_speed_mph"], cpp_out.expected_delta_v, places=12)
            self.assertAlmostEqual(py_sum["median_delta_speed_mph"], cpp_out.median_delta_v, places=12)
            self.assertAlmostEqual(py_sum["lower_80_mph"], cpp_out.pi80_low, places=12)
            self.assertAlmostEqual(py_sum["upper_80_mph"], cpp_out.pi80_high, places=12)
            self.assertAlmostEqual(py_sum["lower_90_mph"], cpp_out.pi90_low, places=12)
            self.assertAlmostEqual(py_sum["upper_90_mph"], cpp_out.pi90_high, places=12)
            self.assertAlmostEqual(py_sum["p_improve"], cpp_out.p_improve, places=12)
            self.assertAlmostEqual(py_sum["mc_sd_mph"], cpp_out.mc_sd, places=12)

    def test_standalone_cpp_monte_carlo_statistical_agreement_and_determinism(self):
        artifacts = final_v2_adapter.load_frozen_artifacts()
        boot_pairs = list(
            zip(
                artifacts.bootstrap_pairs["beta_track_temp"].astype(float).tolist(),
                artifacts.bootstrap_pairs["beta_ambient_temp"].astype(float).tolist(),
            )
        )
        perf_pool = artifacts.performance_residual_pool.astype(float).tolist()
        decision_time = "2021-05-22T16:00:00Z"
        n_mc = 20000
        seed = 20260914

        for h in (15, 30, 60, 90, 120):
            target_time = self.cpp.target_time_for(decision_time, h)
            c = artifacts.track_coefficients[h]
            coef_obj = self.cpp.TrackModelCoefficients(
                horizon_min=h,
                intercept_c=float(c["intercept_c"]),
                beta_delta_ambient_temp_c=float(c["beta_delta_ambient_temp_c"]),
                beta_thermal_gap_0_c=float(c["beta_thermal_gap_0_c"]),
                beta_solar_elevation_mean_deg=float(c["beta_solar_elevation_mean_deg"]),
            )
            track_pool = artifacts.track_residual_pools[h].astype(float).tolist()

            cpp_out1 = self.cpp.run_monte_carlo_inference(
                35.0, 27.0, 29.0, decision_time, target_time,
                coef_obj, track_pool, boot_pairs, perf_pool,
                39.7950, -86.2348, seed, n_mc,
            )
            cpp_out2 = self.cpp.run_monte_carlo_inference(
                35.0, 27.0, 29.0, decision_time, target_time,
                coef_obj, track_pool, boot_pairs, perf_pool,
                39.7950, -86.2348, seed, n_mc,
            )
            # Identical seed in C++ std::mt19937_64 is strictly deterministic
            self.assertEqual(cpp_out1.expected_delta_v, cpp_out2.expected_delta_v)
            self.assertEqual(cpp_out1.median_delta_v, cpp_out2.median_delta_v)
            self.assertEqual(cpp_out1.p_improve, cpp_out2.p_improve)

            # Statistical agreement against Python NumPy PCG64 stream
            py_out = final_v2_adapter.infer(
                35.0, 27.0, 29.0, decision_time, target_time,
                h, 39.7950, -86.2348, seed, n_mc,
            )
            tol = 5.0 * py_out.mc_sd * math.sqrt(2.0 / n_mc)
            self.assertLess(abs(cpp_out1.expected_delta_v - py_out.expected_delta_v), tol)

    def test_point_in_time_thermal_rate_parity_with_real_2020_ptsc_series(self):
        ptsc_path = REPO_ROOT / "weather/evidence/ptsc/indy500_day1_track_temp_2020_2024_time_normalized.csv"
        df = pd.read_csv(ptsc_path)
        df_2020 = df[df["year"] == 2020].reset_index(drop=True)

        obs_list = []
        for idx, row in df_2020.iterrows():
            ts = str(row["utc_datetime"])
            obs_list.append(
                self.cpp.TimestampedObservation(
                    id=f"2020_{idx:03d}",
                    observed_at=ts,
                    known_at=ts,
                    track_temp_c=float(row["track_c"]),
                    ambient_temp_c=float(row["ambient_c"]),
                )
            )

        # At 12:30:00Z (second reading, 15 min after 12:15:00Z): rate should be valid
        rate_1230 = self.cpp.compute_point_in_time_thermal_rate(obs_list, "2020-08-15 12:30:00+00:00")
        self.assertTrue(rate_1230.valid)
        self.assertAlmostEqual(rate_1230.lookback_minutes, 15.0, places=9)
        expected_rate = (float(df_2020.loc[1, "track_c"]) - float(df_2020.loc[0, "track_c"])) / 15.0
        self.assertAlmostEqual(rate_1230.track_rate_c_per_min, expected_rate, places=12)

        # At 14:45:00Z (after a 75-min gap from 13:30:00Z): no observation in [10, 20] min lookback
        rate_1445 = self.cpp.compute_point_in_time_thermal_rate(obs_list, "2020-08-15 14:45:00+00:00")
        self.assertFalse(rate_1445.valid)

    def test_bridge_fallback_matches_native_path(self):
        for prefer_native in (True, False):
            res = cpp_pit_bridge.infer_physical_response_terms(
                current_track_temp_c=35.0,
                current_ambient_temp_c=27.0,
                forecast_future_ambient_temp_c=29.0,
                decision_time="2021-05-22T16:00:00Z",
                target_time="2021-05-22T17:00:00Z",
                horizon_min=60,
                prefer_native=prefer_native,
            )
            self.assertEqual(res["horizon_minutes"], 60)
            self.assertAlmostEqual(res["thermal_gap_0_c"], 8.0, places=12)
            self.assertAlmostEqual(res["delta_ambient_temp_c"], 2.0, places=12)

        nat = cpp_pit_bridge.infer_physical_response_terms(
            35.0, 27.0, 29.0, "2021-05-22T16:00:00Z", "2021-05-22T17:00:00Z", 60, prefer_native=True
        )
        py = cpp_pit_bridge.infer_physical_response_terms(
            35.0, 27.0, 29.0, "2021-05-22T16:00:00Z", "2021-05-22T17:00:00Z", 60, prefer_native=False
        )
        for k in nat:
            self.assertAlmostEqual(nat[k], py[k], places=12)


if __name__ == "__main__":
    unittest.main()
