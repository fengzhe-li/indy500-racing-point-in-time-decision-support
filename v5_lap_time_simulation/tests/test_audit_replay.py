import csv
from dataclasses import replace
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import numpy as np
from fastapi.testclient import TestClient

from v5_lap_time_simulation.model import (G, Vehicle, Environment, build_ims_oval_approximation,
    simulate_lap, tire_loads, _corner_speed_limit, _effective_mu)
from v5_lap_time_simulation.replay import geometry_at, replay_payload
from v5_lap_time_simulation.analysis import calibrate_effective_power
from v5_lap_time_simulation.audit import constant_baselines, mesh_study
from v5_lap_time_simulation.schema import ReplayResponse
from v5_lap_time_simulation.server import create_app

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / 'v5_lap_time_simulation'


class EngineeringAuditTests(unittest.TestCase):
    def test_track_sequence_length_and_geometric_closure(self):
        t = build_ims_oval_approximation()
        self.assertEqual([s.name for s in t.segments], ['Turn 1','Short chute 1-2','Turn 2','Back straight','Turn 3','Short chute 3-4','Turn 4','Front straight'])
        np.testing.assert_allclose([s.distance_m for s in t.segments], [402.336,201.168,402.336,1005.84,402.336,201.168,402.336,1005.84])
        self.assertAlmostEqual(t.length_m, 4023.36)
        np.testing.assert_allclose(geometry_at(t,t.length_m), (0,0), atol=1e-9)
        for s in t.segments:
            if s.radius_m:
                self.assertAlmostEqual(s.distance_m/s.radius_m, math.pi/2)

    def test_bank_force_balance_and_independent_no_aero_corner(self):
        v, e = Vehicle(cl_a_m2=0), Environment()
        theta, radius, speed = math.radians(9.2), 250, 70
        n, fy = tire_loads(v,e,speed,1/radius,9.2)
        self.assertAlmostEqual(n*math.cos(theta)-fy*math.sin(theta),v.mass_kg*G)
        self.assertAlmostEqual(n*math.sin(theta)+fy*math.cos(theta),v.mass_kg*speed**2/radius)
        expected = math.sqrt(G*radius*(math.sin(theta)+v.tire_mu*math.cos(theta))/(math.cos(theta)-v.tire_mu*math.sin(theta)))
        self.assertAlmostEqual(_corner_speed_limit(v,e,radius,9.2),expected)

    def test_entire_periodic_lap_satisfies_tire_circle_and_actuator_bounds(self):
        t,v,e = build_ims_oval_approximation(), Vehicle(tire_mu=1.35), Environment(track_temperature_c=35)
        r=simulate_lap(t,v,e)
        for i,speed in enumerate(r.speed_mps):
            j=(i+1)%len(r.speed_mps)
            a=(r.speed_mps[j]**2-speed**2)/(2*r.distance_step_m[i])
            seg=t.segments[r.segment_index[i]]
            for speed_at in np.linspace(speed,r.speed_mps[j],9):
                n,fy=tire_loads(v,e,speed_at,r.curvature_1pm[i],seg.banking_deg)
                resistance=.5*e.air_density_kg_m3*v.cd_a_m2*speed_at**2+v.rolling_resistance_coefficient*n
                fx=v.mass_kg*a+resistance
                self.assertLessEqual(math.hypot(fx,fy),_effective_mu(v,e)*n+1e-3)
                self.assertLessEqual(fx,min(v.drive_force_max_n,v.power_w/speed_at)+1e-3)
                self.assertGreaterEqual(fx,-v.brake_force_max_n-1e-3)
        self.assertTrue(np.any(np.diff(r.speed_mps)>0))
        self.assertTrue(np.any(np.diff(r.speed_mps)<0))

    def test_periodic_origin_rotation_invariant(self):
        track=build_ims_oval_approximation()
        shifted=replace(track,segments=track.segments[2:]+track.segments[:2])
        v=Vehicle(tire_mu=1.35)
        a,b=simulate_lap(track,v),simulate_lap(shifted,v)
        self.assertAlmostEqual(a.lap_time_s,b.lap_time_s,places=7)
        offset=sum(math.ceil(seg.distance_m/10) for seg in track.segments[:2])
        np.testing.assert_allclose(np.roll(a.speed_mps,-offset),b.speed_mps,atol=1e-7)

    def test_mesh_study_separates_spatial_and_iterative_errors(self):
        rows=mesh_study(Vehicle(tire_mu=1.35),Environment(track_temperature_c=35))
        self.assertEqual([r['step_m'] for r in rows],[40,20,10,5,2.5,1.25])
        self.assertGreater(rows[0]['delta_vs_finest_s'],rows[-2]['delta_vs_finest_s'])
        self.assertGreater(rows[0]['profile_rmse_vs_finest_mps'],rows[-2]['profile_rmse_vs_finest_mps'])
        self.assertGreater(rows[0]['delta_vs_finest_s'],1e-8)

    def test_replay_contract_and_constant_acceleration_time_integral(self):
        t,v,e=build_ims_oval_approximation(),Vehicle(tire_mu=1.35),Environment()
        r=simulate_lap(t,v,e); data=replay_payload(t,v,e,r)
        ReplayResponse.model_validate(data)
        self.assertEqual(json.loads((MODULE/'schema/replay.schema.json').read_text()),ReplayResponse.model_json_schema())
        self.assertAlmostEqual(data['elapsed_s'][-1],r.lap_time_s)
        self.assertEqual(data['speed_mps'][-1],data['speed_mps'][0])
        for i,a in enumerate(data['acceleration_mps2']):
            dt=data['elapsed_s'][i+1]-data['elapsed_s'][i]
            self.assertAlmostEqual(r.distance_step_m[i],r.speed_mps[i]*dt+.5*a*dt**2,places=8)

    def test_holdout_outcome_changes_do_not_change_calibration(self):
        data=ROOT/'data/canonical/v1'
        _,original=calibrate_effective_power(data,ds_m=20)
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);shutil.copy(data/'attempt_laps.csv',tmp/'attempt_laps.csv')
            with (data/'attempts.csv').open() as f:
                reader=csv.DictReader(f); fields=reader.fieldnames; rows=list(reader)
            for row in rows:
                if row['session_id']=='INDY500_DAY1_2024':row['four_lap_average_speed_mph']='999'
            with (tmp/'attempts.csv').open('w') as f:
                writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
            _,changed=calibrate_effective_power(tmp,ds_m=20)
            self.assertEqual(original,changed)

    def test_physics_has_no_aggregate_skill_over_its_median_target(self):
        config=json.loads((MODULE/'output/baseline.json').read_text())
        rows=constant_baselines(ROOT/'data/canonical/v1',config['average_speed_mph'])
        for metric in ('speed_mae_mph','speed_rmse_mph','four_lap_time_mae_s'):
            self.assertAlmostEqual(rows[0][metric],rows[1][metric],places=7)

    def test_frozen_trees_unchanged_since_original_v5(self):
        result=subprocess.run(['git','diff','--exit-code','18b8623c01f423f8072996a8ca92ffd2ddc0806e','--',
             'v3_point_in_time','v4_team_normalized','results/final_v2','weather','r4','r5','r5_2','data',
             ':(exclude)v3_point_in_time/src/cpp_pit_bridge.py',
             ':(exclude)v3_point_in_time/tests/test_cpp_engine_parity.py'],
             cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr+result.stdout[:1000])


class ReplayApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.client=TestClient(create_app())

    def test_api_baseline_and_repeatable_scenario_contract(self):
        baseline=self.client.get('/api/v5/baseline')
        self.assertEqual(baseline.status_code,200)
        ReplayResponse.model_validate(baseline.json())
        request={'vehicle':{'tire_mu':1.35},'environment':{'air_temperature_c':30}}
        a=self.client.post('/api/v5/simulate',json=request)
        b=self.client.post('/api/v5/simulate',json=request)
        self.assertEqual(a.status_code,200);self.assertEqual(a.json(),b.json())
        uncached=TestClient(create_app()).post('/api/v5/simulate',json=request)
        self.assertEqual(a.json(),uncached.json())
        self.assertNotEqual(a.json()['lap_time_s'],baseline.json()['lap_time_s'])
        # A scenario cannot mutate the cached baseline.
        self.assertEqual(self.client.get('/api/v5/baseline').json(),baseline.json())

    def test_api_invalid_and_unknown_parameters_are_rejected(self):
        for body in ({'vehicle':{'mass_kg':0}},{'vehicle':{'throttle':1}},{'environment':{'air_temperature_c':None},'telemetry':[]}):
            self.assertEqual(self.client.post('/api/v5/simulate',json=body).status_code,422)


if __name__=='__main__':unittest.main()
