"""Acceptance gaps: fail-closed numerics and error-boundary behavior."""
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from v5_lap_time_simulation.model import Environment, Vehicle, force_limits, simulate_lap
from v5_lap_time_simulation.server import create_app


class FinalAcceptanceTests(unittest.TestCase):
    def test_negative_available_acceleration_is_not_clamped_or_accepted(self):
        self.assertLess(force_limits(Vehicle(power_w=400000),Environment(),120,0)[0],0)
        with patch('v5_lap_time_simulation.model.sustainable_speed',return_value=100.), patch('v5_lap_time_simulation.model.force_limits',return_value=(-1.,30.)):
            with self.assertRaisesRegex(RuntimeError,'force-feasible'):
                simulate_lap()

    def test_nonfinite_force_bounds_cannot_pass_feasibility_comparisons(self):
        for invalid in (float('nan'),float('inf')):
            with self.subTest(invalid=invalid), patch('v5_lap_time_simulation.model.sustainable_speed',return_value=100.), patch('v5_lap_time_simulation.model.force_limits',return_value=(invalid,30.)):
                with self.assertRaisesRegex(RuntimeError,'nonfinite'):
                    simulate_lap()

    def test_invalid_iteration_limits_and_nonfinite_inputs_are_rejected(self):
        for value in (0,-1,2.5,float('nan'),True):
            with self.subTest(value=value),self.assertRaises(ValueError):
                simulate_lap(max_iterations=value)
        for field in ('mass_kg','cd_a_m2','cl_a_m2','tire_mu','power_w','rolling_resistance_coefficient'):
            with self.subTest(field=field),self.assertRaises(ValueError):
                simulate_lap(vehicle=Vehicle(**{field:float('nan')}))

    def test_nonfinite_api_inputs_return_422_not_error_handler_500(self):
        client=TestClient(create_app(),raise_server_exceptions=False)
        for value in ('NaN','Infinity','-Infinity','1e309','"NaN"'):
            with self.subTest(value=value):
                result=client.post('/api/v5/simulate',content='{"vehicle":{"mass_kg":'+value+'}}',headers={'Content-Type':'application/json'})
                self.assertEqual(result.status_code,422,result.text)
                self.assertIn('detail',result.json())

    def test_solver_failure_becomes_api_422_and_baseline_remains_usable(self):
        client=TestClient(create_app())
        original=client.get('/api/v5/baseline').json()
        with patch('v5_lap_time_simulation.server.simulate_lap',side_effect=RuntimeError('force-feasible check failed')):
            result=client.post('/api/v5/simulate',json={'vehicle':{'mass_kg':901}})
            self.assertEqual(result.status_code,422)
        self.assertEqual(client.get('/api/v5/baseline').json(),original)
