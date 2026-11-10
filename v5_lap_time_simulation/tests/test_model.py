import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

from v5_lap_time_simulation.analysis import calibrate_effective_power, historical_validation
from v5_lap_time_simulation.model import (
    Environment, G, MILE_M, Track, TrackSegment, Vehicle,
    build_ims_oval_approximation, simulate_lap,
)


class LapSimulationTests(unittest.TestCase):
    def test_track_length_and_units(self):
        track = build_ims_oval_approximation()
        self.assertAlmostEqual(track.length_m, 2.5 * MILE_M, places=7)
        result = simulate_lap(track, ds_m=20)
        self.assertAlmostEqual(result.track_length_m, 4023.36, places=2)
        self.assertGreater(result.average_speed_mph, 0)
        self.assertAlmostEqual(result.lap_time_s, track.length_m / (result.average_speed_mph / 2.2369362920544), places=7)

    def test_straight_has_zero_curvature(self):
        track = Track((TrackSegment("straight A", 500), TrackSegment("straight B", 500)))
        result = simulate_lap(track, vehicle=Vehicle(max_speed_mps=50), ds_m=25)
        self.assertTrue(np.all(result.curvature_1pm == 0))
        self.assertTrue(np.all(result.corner_speed_limit_mps == result.corner_speed_limit_mps[0]))

    def test_constant_radius_corner_analytic_limit(self):
        vehicle = Vehicle(cd_a_m2=0.8, cl_a_m2=0.0, tire_mu=1.2, power_w=1_000_000,
                          drive_force_max_n=20_000, max_speed_mps=120)
        env = Environment(air_temperature_c=20, pressure_pa=101325)
        radius, bank = 80.0, 0.0
        track = Track((TrackSegment("corner", 2 * math.pi * radius, radius, bank),
                       TrackSegment("straight", 100)))
        result = simulate_lap(track, vehicle, env, ds_m=15)
        expected = math.sqrt(vehicle.tire_mu * G * radius)
        self.assertAlmostEqual(result.corner_speed_limit_mps[0], expected, places=8)
        self.assertLessEqual(float(np.max(result.speed_mps[:int(2 * math.pi * radius / 15) + 1])), expected + 1e-7)

    def test_closed_loop_speed_bounds_and_convergence(self):
        track = build_ims_oval_approximation()
        result = simulate_lap(track, ds_m=10)
        self.assertTrue(result.converged)
        self.assertLess(result.iterations, 100)
        self.assertTrue(np.all(result.speed_mps <= result.corner_speed_limit_mps + 1e-9))
        n = len(result.speed_mps)
        for i in range(n):
            j = (i + 1) % n
            self.assertLessEqual(result.speed_mps[j] ** 2,
                                 result.speed_mps[i] ** 2 + 2 * result.acceleration_limit_mps2[i] * result.distance_step_m[i] + 1e-5)
            self.assertLessEqual(result.speed_mps[i] ** 2,
                                 result.speed_mps[j] ** 2 + 2 * result.braking_limit_mps2[j] * result.distance_step_m[i] + 1e-5)

    def test_constant_speed_integration_analytic(self):
        track = Track((TrackSegment("straight A", 137.0), TrackSegment("straight B", 263.0)))
        vehicle = Vehicle(power_w=10_000_000, drive_force_max_n=100_000, max_speed_mps=50)
        result = simulate_lap(track, vehicle, ds_m=13)
        self.assertAlmostEqual(result.lap_time_s, 400 / 50, places=7)

    def test_sensitivity_directions_and_determinism(self):
        track = build_ims_oval_approximation()
        base_vehicle = Vehicle()
        env = Environment(track_temperature_c=35)
        baseline = simulate_lap(track, base_vehicle, env)
        drag = simulate_lap(track, Vehicle(**{**base_vehicle.__dict__, "cd_a_m2": base_vehicle.cd_a_m2 * 1.1}), env)
        power = simulate_lap(track, Vehicle(**{**base_vehicle.__dict__, "power_w": base_vehicle.power_w * 1.1}), env)
        repeat = simulate_lap(track, base_vehicle, env)
        self.assertGreater(drag.lap_time_s, baseline.lap_time_s)
        self.assertLess(power.lap_time_s, baseline.lap_time_s)
        self.assertEqual(baseline.lap_time_s, repeat.lap_time_s)

    def test_parameter_validation(self):
        with self.assertRaises(ValueError):
            simulate_lap(vehicle=Vehicle(mass_kg=0))
        with self.assertRaises(ValueError):
            simulate_lap(ds_m=0)
        with self.assertRaises(ValueError):
            simulate_lap(environment=Environment(air_temperature_c=-273.16))
        with self.assertRaises(ValueError):
            Track((TrackSegment("bad", -1),)).validate()

    def test_missing_historical_data_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                historical_validation(Path(tmp), 40)

    def test_calibration_and_validation_years_are_separated(self):
        vehicle, report = calibrate_effective_power(Path("data/canonical/v1"), ds_m=20)
        self.assertGreater(vehicle.power_w, 0)
        self.assertEqual(report["calibration_years"], "2020-2023")
        self.assertEqual(report["held_out_validation_year"], 2024)
        self.assertIn("Not engine power measurement", report["interpretation_limit"])


if __name__ == "__main__":
    unittest.main()
