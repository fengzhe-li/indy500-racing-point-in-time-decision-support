import math, tempfile, unittest
from pathlib import Path
from v6_driver_in_loop import *
from v6_driver_in_loop.simulation import ExperimentRunner
from v6_driver_in_loop.vehicle import VehicleModel
from v6_driver_in_loop.models import DriverCommand

class V6Tests(unittest.TestCase):
    def test_invalid_parameters(self):
        with self.assertRaises(ValueError): VehicleParams(mass_kg=0)
        with self.assertRaises(ValueError): SimulationConfig(dt_s=0)
    def test_zero_input_decelerates_due_to_resistance(self):
        model=VehicleModel(); z=VehicleState(u_m_s=20)
        nxt,ax,_=model.step(z,DriverCommand(0,0,0),.01)
        self.assertLess(nxt.u_m_s,z.u_m_s); self.assertLess(ax,0)
    def test_straight_acceleration_positive(self):
        model=VehicleModel(); z=VehicleState(u_m_s=10)
        nxt,ax,_=model.step(z,DriverCommand(0,1,0),.01)
        self.assertGreater(nxt.u_m_s,z.u_m_s); self.assertGreater(ax,0)
    def test_constant_steer_yaw_response(self):
        model=VehicleModel(); z=VehicleState(u_m_s=30)
        for _ in range(20): z,_,_=model.step(z,DriverCommand(.04,0,0),.01)
        self.assertGreater(z.yaw_rate_rad_s,0)
    def test_saturation_and_determinism(self):
        model=VehicleModel(); a=VehicleState(u_m_s=40); b=VehicleState(u_m_s=40)
        for _ in range(100): a,_,_=model.step(a,DriverCommand(5,3,0),.01); b,_,_=model.step(b,DriverCommand(5,3,0),.01)
        self.assertEqual(a,b); self.assertTrue(math.isfinite(a.yaw_rate_rad_s)); self.assertLessEqual(a.yaw_rate_rad_s,10)
    def test_track_closure(self):
        t=OvalTrack(); a=t.point(0); b=t.point(t.length_m-1e-5)
        self.assertLess(math.hypot(a.x_m-b.x_m,a.y_m-b.y_m),1e-3)
    def test_run_and_telemetry(self):
        t=OvalTrack(straight_length_m=40,radius_m=30,width_m=12,samples=200)
        r=SimulationEngine(t,config=SimulationConfig(.01,20,12,1),driver_config=DriverConfig(max_speed_m_s=18,preview_m=12)).run()
        self.assertTrue(r.samples); self.assertTrue(all(s.simulated for s in r.samples)); self.assertTrue(all(math.isfinite(s.u_m_s) for s in r.samples))
        with tempfile.TemporaryDirectory() as d:
            r.write_csv(Path(d)/'telemetry.csv'); r.write_json(Path(d)/'result.json')
            self.assertTrue((Path(d)/'telemetry.csv').exists())
    def test_manual_input_offtrack_termination(self):
        t=OvalTrack(straight_length_m=30,radius_m=20,width_m=4,samples=200)
        r=SimulationEngine(t,config=SimulationConfig(.02,2,15),driver_config=DriverConfig()).run(manual_input=lambda s: DriverCommand(.3,0,0))
        self.assertEqual(r.status,'off_track')
    def test_timestep_refinement_finite(self):
        outputs=[]
        for dt in (.02,.01,.005):
            m=VehicleModel(); z=VehicleState(u_m_s=25)
            for _ in range(round(1/dt)): z,_,_=m.step(z,DriverCommand(.02,.1,0),dt)
            outputs.append(z)
        self.assertTrue(all(math.isfinite(z.u_m_s) for z in outputs)); self.assertLess(abs(outputs[-1].u_m_s-outputs[0].u_m_s),.1)
    def test_experiment_reports_each_run(self):
        rows=ExperimentRunner(track=OvalTrack(straight_length_m=30,radius_m=20,samples=100),simulation=SimulationConfig(.02,.2,10)).run([('calm',DriverConfig()),('delay',DriverConfig(reaction_delay_s=.1))])
        self.assertEqual(len(rows),2); self.assertTrue(all('status' in x and 'reason' in x for x in rows))

if __name__=='__main__': unittest.main()
