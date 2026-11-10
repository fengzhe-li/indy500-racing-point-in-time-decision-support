"""Analytical, physical-invariant and closed-loop regression checks."""
import csv
from dataclasses import asdict, fields, replace
import json
import math
from pathlib import Path
import tempfile
import unittest

from v6_driver_in_loop import *
from v6_driver_in_loop.experiments import scenarios, compare_trajectories
from v6_driver_in_loop.models import DriverCommand
from v6_driver_in_loop.replay import export_replay, sample_at
from v6_driver_in_loop.simulation import LapProgress


class PhysicsAuditTests(unittest.TestCase):
    def test_world_body_rotation_and_speed_norm(self):
        m = VehicleModel()
        for heading in (0, math.pi/2, math.pi, -.7):
            z = VehicleState(heading_rad=heading, u_m_s=20, v_m_s=3, yaw_rate_rad_s=.1)
            d = m.derivatives(z, DriverCommand(.02,0,0))
            self.assertAlmostEqual(d[0], 20*math.cos(heading)-3*math.sin(heading))
            self.assertAlmostEqual(d[1], 20*math.sin(heading)+3*math.cos(heading))
            self.assertAlmostEqual(math.hypot(d[0],d[1]), math.hypot(20,3))
            self.assertEqual(d[2], .1)

    def test_stationary_car_does_not_creep_or_generate_steering_force(self):
        z = VehicleState(u_m_s=0)
        for command in (DriverCommand(0,0,0), DriverCommand(.2,0,1)):
            final, ax, ay = VehicleModel().step(z, command, .02)
            self.assertEqual((final.x_m, final.y_m, final.u_m_s, final.v_m_s, final.yaw_rate_rad_s), (0,0,0,0,0))
            self.assertEqual((ax,ay),(0,0))

    def test_slip_signs_and_mirror_symmetry(self):
        m=VehicleModel()
        left=m.forces(VehicleState(u_m_s=30),DriverCommand(.02,0,0))
        right=m.forces(VehicleState(u_m_s=30),DriverCommand(-.02,0,0))
        self.assertGreater(left.slip_front_rad,0)
        self.assertGreater(left.tire_front_y_n,0)
        self.assertGreater(left.yaw_moment_n_m,0)
        self.assertAlmostEqual(left.body_y_n,-right.body_y_n)
        self.assertAlmostEqual(left.body_x_n,right.body_x_n)
        side=m.forces(VehicleState(u_m_s=30,v_m_s=1),DriverCommand(0,0,0))
        self.assertLess(side.slip_front_rad,0)
        self.assertLess(side.slip_rear_rad,0)
        self.assertLess(side.body_y_n,0)

    def test_front_wheel_force_is_rotated_into_body(self):
        p=VehicleParams(drag_coefficient_area_m2=0,rolling_resistance=0)
        m=VehicleModel(p)
        f=m.forces(VehicleState(u_m_s=30),DriverCommand(.1,0,.2))
        self.assertAlmostEqual(f.body_x_n,f.tire_front_x_n*math.cos(.1)-f.tire_front_y_n*math.sin(.1)+f.tire_rear_x_n)
        self.assertAlmostEqual(f.body_y_n,f.tire_front_x_n*math.sin(.1)+f.tire_front_y_n*math.cos(.1)+f.tire_rear_y_n)
        self.assertAlmostEqual(f.yaw_moment_n_m,p.lf_m*(f.body_y_n-f.tire_rear_y_n)-p.lr_m*f.tire_rear_y_n)

    def test_combined_friction_circle_and_aero_not_clipped(self):
        p=VehicleParams(friction_coefficient=.2)
        m=VehicleModel(p)
        for command in (DriverCommand(.3,1,0), DriverCommand(.3,0,1)):
            f=m.forces(VehicleState(u_m_s=40,v_m_s=2,yaw_rate_rad_s=.3),command)
            self.assertLessEqual(math.hypot(f.tire_front_x_n,f.tire_front_y_n),p.friction_coefficient*f.normal_front_n+1e-9)
            self.assertLessEqual(math.hypot(f.tire_rear_x_n,f.tire_rear_y_n),p.friction_coefficient*f.normal_rear_n+1e-9)
            self.assertTrue(f.tire_saturated)
        f=m.forces(VehicleState(u_m_s=100), DriverCommand(0,0,1))
        self.assertLess(f.body_x_n, f.tire_front_x_n+f.tire_rear_x_n)

    def test_aero_speed_squared_and_downforce_load_sum(self):
        p=VehicleParams()
        m=VehicleModel(p)
        a=m.forces(VehicleState(u_m_s=20),DriverCommand(0,0,0))
        b=m.forces(VehicleState(u_m_s=40),DriverCommand(0,0,0))
        self.assertAlmostEqual(b.drag_n,4*a.drag_n)
        self.assertAlmostEqual(b.downforce_n,4*a.downforce_n)
        self.assertAlmostEqual(a.normal_front_n+a.normal_rear_n,p.mass_kg*p.gravity_m_s2+a.downforce_n)

    def test_acceleration_is_force_per_mass_not_velocity_derivative(self):
        m=VehicleModel()
        z=VehicleState(u_m_s=30,v_m_s=1,yaw_rate_rad_s=.2)
        cmd=DriverCommand(.03,0,0)
        d=m.derivatives(z,cmd)
        _,ax,ay=m.step(z,cmd,.01)
        self.assertAlmostEqual(ax,d[3]-z.v_m_s*z.yaw_rate_rad_s)
        self.assertAlmostEqual(ay,d[4]+z.u_m_s*z.yaw_rate_rad_s)
        self.assertNotAlmostEqual(ay,z.u_m_s*z.yaw_rate_rad_s)

    def test_analytical_constant_force_acceleration_and_distance(self):
        p=VehicleParams(drag_coefficient_area_m2=0,downforce_coefficient_area_m2=0,rolling_resistance=0)
        m=VehicleModel(p); z=VehicleState(u_m_s=10)
        cmd=DriverCommand(0,.1,0); acceleration=.1*p.max_drive_force_n/p.mass_kg
        for _ in range(100): z=m.step(z,cmd,.01)[0]
        self.assertAlmostEqual(z.u_m_s,10+acceleration,places=10)
        self.assertAlmostEqual(z.x_m,10+.5*acceleration,places=10)
        self.assertAlmostEqual(z.distance_m,z.x_m,places=10)

    def test_analytical_drag_only_coasting(self):
        p=VehicleParams(rolling_resistance=0)
        m=VehicleModel(p); z=VehicleState(u_m_s=70)
        for _ in range(100): z=m.step(z,DriverCommand(0,0,0),.02)[0]
        k=.5*p.air_density_kg_m3*p.drag_coefficient_area_m2/p.mass_kg
        self.assertAlmostEqual(z.u_m_s,70/(1+k*70*2),places=8)
        self.assertAlmostEqual(z.x_m,math.log(1+k*70*2)/k,places=8)

    def test_braking_to_rest_does_not_reverse(self):
        m=VehicleModel(); z=VehicleState(u_m_s=2)
        for _ in range(200):
            nxt=m.step(z,DriverCommand(0,0,1),.02)[0]
            self.assertGreaterEqual(nxt.u_m_s,0)
            self.assertLessEqual(nxt.u_m_s,z.u_m_s+1e-12)
            self.assertGreaterEqual(nxt.x_m,z.x_m)
            z=nxt
        self.assertLess(z.u_m_s,1e-8)

    def test_small_angle_steady_yaw_matches_linear_bicycle_reference(self):
        p=VehicleParams(drag_coefficient_area_m2=0, rolling_resistance=0, downforce_coefficient_area_m2=0)
        model=VehicleModel(p); z=VehicleState(u_m_s=30); delta=.002
        for _ in range(1000): z=model.step(z,DriverCommand(delta,0,0),.01)[0]
        understeer=p.mass_kg/p.wheelbase_m*(p.lr_m/p.cornering_front_n_per_rad-p.lf_m/p.cornering_rear_n_per_rad)
        expected=z.u_m_s*delta/(p.wheelbase_m+understeer*z.u_m_s**2)
        self.assertAlmostEqual(z.yaw_rate_rad_s/expected,1,delta=.01)

    def test_all_numeric_vehicle_fields_reject_nonfinite(self):
        for field in fields(VehicleParams):
            for bad in (float('nan'),float('inf')):
                with self.subTest(field=field.name,bad=bad),self.assertRaises(ValueError):
                    replace(VehicleParams(),**{field.name:bad})

    def test_invalid_configs_states_and_commands(self):
        for constructor,kwargs in [(VehicleParams,{'lf_m':-1}), (VehicleParams,{'front_brake_fraction':2}),
                (DriverConfig,{'kp_speed':-1}), (DriverConfig,{'reaction_delay_s':float('nan')}),
                (SimulationConfig,{'max_laps':1.5}), (SimulationConfig,{'dt_s':.1}),
                (OvalTrack,{'banking_rad':.1}), (OvalTrack,{'radius_m':float('inf')}),
                (OvalTrack,{'width_m':1000}), (DriverCommand,{'steering_rad':float('nan'),'throttle':0,'brake':0})]:
            with self.subTest(constructor=constructor,kwargs=kwargs),self.assertRaises(ValueError): constructor(**kwargs)
        with self.assertRaises(ValueError): VehicleState(u_m_s=-.01).validate()
        with self.assertRaises(ValueError): VehicleModel().step(VehicleState(),DriverCommand(0,0,0),float('nan'))

    def test_actuator_limits_and_brake_priority(self):
        p=VehicleParams(max_steer_rad=.1)
        c=DriverCommand(9,2,3).constrained(p)
        self.assertEqual(c, DriverCommand(.1,0,1))
        self.assertEqual(DriverCommand(-9,-1,-1).constrained(p),DriverCommand(-.1,0,0))

    def test_smooth_fixed_command_rk_refinement(self):
        states=[]
        for dt in (.01,.005,.0025,.000625):
            z=VehicleState(u_m_s=30)
            for _ in range(round(.5/dt)): z=VehicleModel().step(z,DriverCommand(.015,.1,0),dt)[0]
            states.append(z)
        error=[abs(s.y_m-states[-1].y_m)+abs(s.yaw_rate_rad_s-states[-1].yaw_rate_rad_s) for s in states[:-1]]
        self.assertGreater(error[0],error[1]); self.assertGreater(error[1],error[2])
        self.assertLess(error[2],1e-6)


class TrackAndLoopTests(unittest.TestCase):
    def test_exact_projection_independent_of_render_sampling(self):
        track=OvalTrack(samples=20,width_m=.2)
        for s in (3.1,1000.1,2000.8,3000.3,track.length_m-.01):
            p=track.point(s); q=track.nearest(p.x_m,p.y_m)
            self.assertLess(math.hypot(p.x_m-q.x_m,p.y_m-q.y_m),1e-9)
        result=SimulationEngine(track,config=SimulationConfig(.01,.1)).run(VehicleState(x_m=3.1))
        self.assertFalse(result.off_track)

    def test_signed_normal_offset_and_boundaries(self):
        track=OvalTrack()
        for s in (300,1400,2700,4000):
            p=track.point(s)
            for offset in (-7.49,2,7.49):
                z=VehicleState(x_m=p.x_m-math.sin(p.heading_rad)*offset,y_m=p.y_m+math.cos(p.heading_rad)*offset)
                self.assertAlmostEqual(track.error(z),offset,places=8)

    def test_lap_progress_forward_reverse_and_arbitrary_start(self):
        p=LapProgress(100,99)
        self.assertAlmostEqual(p.update(1),2)
        self.assertAlmostEqual(p.update(99),0)
        for s in (20,40,60,80,99):p.update(s)
        self.assertAlmostEqual(p.progress_m,100)

    def test_start_near_finish_is_not_a_completed_lap(self):
        track=OvalTrack(); p=track.point(track.length_m-1)
        r=SimulationEngine(track,config=SimulationConfig(.01,.2,20)).run(
            VehicleState(x_m=p.x_m,y_m=p.y_m,heading_rad=p.heading_rad,u_m_s=20))
        self.assertEqual(r.status,'timeout'); self.assertIsNone(r.lap_time_s)
        self.assertGreater(r.samples[-1].progress_m,1)
        self.assertLess(r.samples[-1].progress_m,10)

    def test_completed_lap_event_and_final_row_align(self):
        r=SimulationEngine().run()
        self.assertEqual(r.status,'completed'); self.assertIsNotNone(r.lap_time_s)
        self.assertAlmostEqual(r.samples[-1].progress_m,OvalTrack().length_m,places=6)
        self.assertEqual(r.samples[-1].sim_time_s,r.lap_time_s)
        self.assertEqual(r.events[-1]['sim_time_s'],r.lap_time_s)
        self.assertGreater(r.samples[-1].distance_m,4400)
        self.assertLess(r.max_abs_path_error_m,7.5)

    def test_offtrack_event_localizes_and_records_crossing(self):
        r=SimulationEngine(config=SimulationConfig(.02,2,15)).run(manual_input=lambda s: DriverCommand(.3,0,0))
        self.assertEqual(r.status,'off_track'); self.assertTrue(r.samples[-1].off_track)
        self.assertAlmostEqual(abs(r.samples[-1].path_error_m),7.5,places=6)
        self.assertEqual(r.events[-1]['sim_time_s'],r.samples[-1].sim_time_s)
        self.assertGreater(abs(r.samples[-1].path_error_m),abs(r.samples[-2].path_error_m))

    def test_initial_offtrack_and_zero_duration_replay(self):
        r=SimulationEngine().run(VehicleState(y_m=8))
        self.assertEqual(r.status,'off_track'); self.assertEqual(len(r.samples),1)
        self.assertEqual(r.elapsed_sim_s,0); self.assertEqual(r.metrics()['rms_path_error_m'],8)

    def test_timeout_exact_and_trajectory_recording(self):
        initial=VehicleState(u_m_s=20)
        r=SimulationEngine(config=SimulationConfig(.02,.055)).run(initial)
        self.assertEqual(r.status,'timeout'); self.assertEqual(r.elapsed_sim_s,.055)
        self.assertEqual([s.sim_time_s for s in r.samples],[0,.02,.04,.055])
        self.assertEqual(initial.time_s,0)
        self.assertGreater(r.samples[-1].x_m,r.samples[0].x_m)
        self.assertTrue(all(s.simulated for s in r.samples))

    def test_manual_callback_applies_limits_and_logs_actual_path_error(self):
        r=SimulationEngine(config=SimulationConfig(.01,.01)).run(VehicleState(y_m=1),manual_input=lambda s:DriverCommand(3,3,3))
        s=r.samples[0]
        self.assertEqual(s.path_error_m,1)
        self.assertEqual(s.steering_command_rad,VehicleParams().max_steer_rad)
        self.assertEqual(s.throttle_command,0);self.assertEqual(s.brake_command,1)
        self.assertTrue(s.steering_saturated);self.assertTrue(s.brake_saturated)
        self.assertEqual(s.steering_requested_rad,3)

    def test_invalid_run_initial_clock_is_rejected(self):
        with self.assertRaises(ValueError):SimulationEngine().run(VehicleState(time_s=2))

    def test_numerical_failure_is_explicit_not_a_silent_nan(self):
        class FailingVehicle(VehicleModel):
            def step(self,*args): raise FloatingPointError('intentional integration failure')
        r=SimulationEngine(vehicle=FailingVehicle()).run()
        self.assertEqual(r.status,'numerical_error');self.assertIn('intentional',r.reason)
        self.assertEqual(r.events[-1]['type'],'numerical_error')
        json.dumps(r.to_dict(),allow_nan=False)

    def test_driver_uses_vehicle_wheelbase(self):
        state=VehicleState(y_m=2)
        a=PurePursuitPIDDriver(OvalTrack()).command(state,.01)[0]
        b=PurePursuitPIDDriver(OvalTrack(),vehicle_params=VehicleParams(wheelbase_m=4,lf_m=2,lr_m=2)).command(state,.01)[0]
        self.assertGreater(abs(b.steering_rad),abs(a.steering_rad))
        self.assertLess(a.steering_rad,0)

    def test_reaction_delay_never_releases_early(self):
        driver=PurePursuitPIDDriver(OvalTrack(),DriverConfig(reaction_delay_s=.025))
        for t in (0,.01,.02):self.assertEqual(driver.command(VehicleState(time_s=t),.01)[0],DriverCommand(0,0,0))
        self.assertGreater(driver.command(VehicleState(time_s=.03),.01)[0].throttle,0)

    def test_full_scenario_sweeps_deterministic_excluding_clocks(self):
        for scenario in scenarios():
            a,b=scenario.run(),scenario.run()
            self.assertEqual(a.samples,b.samples,scenario.name)
            self.assertEqual(a.events,b.events,scenario.name)
            self.assertEqual(a.metadata,b.metadata,scenario.name)
            ma,mb=a.metrics(),b.metrics()
            for field in ('cpu_time_s','wall_time_s'):ma.pop(field);mb.pop(field)
            self.assertEqual(ma,mb,scenario.name)

    def test_lap_refinement_bounds_full_state_not_just_laptime(self):
        results=[scenarios()[0].run(dt) for dt in (.02,.01,.005)]
        self.assertTrue(all(r.status=='completed' for r in results))
        difference=compare_trajectories(results[0],results[-1])
        self.assertLess(difference['position_max_difference_m'],.6)
        self.assertLess(difference['velocity_max_difference_m_s'],.3)
        self.assertLess(abs(results[0].lap_time_s-results[-1].lap_time_s),.02)


class TelemetryReplayTests(unittest.TestCase):
    def test_csv_and_json_telemetry_consistency(self):
        r=SimulationEngine(config=SimulationConfig(.01,.03)).run()
        with tempfile.TemporaryDirectory() as tmp:
            csv_path,json_path=Path(tmp)/'t.csv',Path(tmp)/'t.json'
            r.write_csv(csv_path);r.write_json(json_path)
            with csv_path.open() as csv_file:
                rows=list(csv.DictReader(csv_file))
            data=json.loads(json_path.read_text())
            self.assertEqual(data['label'],'SIMULATED');self.assertEqual(len(rows),len(data['samples']))
            for a,b in zip(rows,data['samples']):
                self.assertEqual(float(a['sim_time_s']),b['sim_time_s'])
                self.assertEqual(float(a['lateral_accel_m_s2']),b['lateral_accel_m_s2'])
            self.assertEqual(data['samples'][-1]['sim_time_s'],data['elapsed_sim_s'])

    def test_replay_rows_are_exact_recorded_values_and_terminal_preserved(self):
        r=scenarios()[5].run()
        with tempfile.TemporaryDirectory() as tmp:
            data=export_replay(r,Path(tmp)/'replay.json','delayed')
        original={s.sim_time_s:asdict(s) for s in r.samples}
        for row in data['rows']:
            actual=original[row[0]]
            self.assertEqual(row,[actual[f] for f in data['fields']])
        self.assertEqual(data['rows'][-1][0],r.elapsed_sim_s)
        self.assertEqual(data['events'][-1]['type'],'off_track')

    def test_committed_baseline_metrics_match_current_model(self):
        path=Path(__file__).resolve().parents[1]/'reports/replays/baseline.json'
        saved=json.loads(path.read_text())['metrics']
        fresh=SimulationEngine().run().metrics()
        for key,value in fresh.items():
            if key in ('cpu_time_s','wall_time_s'):continue
            if isinstance(value,float):self.assertAlmostEqual(value,saved[key],places=8,msg=key)
            else:self.assertEqual(value,saved[key],key)

    def test_timestamp_interpolation_and_clamping(self):
        r=SimulationEngine(config=SimulationConfig(.02,.06)).run()
        p=sample_at(r.samples,.01)
        self.assertAlmostEqual(p['x_m'],(r.samples[0].x_m+r.samples[1].x_m)/2)
        self.assertEqual(p['throttle_command'],r.samples[0].throttle_command)
        self.assertEqual(sample_at(r.samples,999)['sim_time_s'],.06)
        self.assertEqual(sample_at(r.samples,-1)['sim_time_s'],0)


if __name__=='__main__': unittest.main()
