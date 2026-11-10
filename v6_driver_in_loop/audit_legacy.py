"""Reproduce legacy-vs-exact-projection ablation from the preserved source archive."""
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile


def main():
    root=Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory() as directory:
        dest=Path(directory)
        with tarfile.open(root/'archive/pre_audit_v6.tar.gz') as archive:
            for member in archive.getmembers():
                # Only regular files below the known package prefix are materialized.
                path=Path(member.name)
                if member.isfile() and not path.name.startswith('._'):
                    if path.is_absolute() or '..' in path.parts or path.parts[0]!='v6_driver_in_loop':
                        raise ValueError('unsafe archived path')
                    target=dest/path;target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(archive.extractfile(member).read())
        script = '''
import importlib.util,sys,json,math
from v6_driver_in_loop import *
from v6_driver_in_loop.models import DriverCommand
spec=importlib.util.spec_from_file_location('analytic_track',sys.argv[1])
mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
track=mod.OvalTrack();rows=[]
for mode in ['original','exact_projection_only']:
 if mode=='exact_projection_only':OvalTrack.nearest=mod.OvalTrack.nearest
 for name,cfg in [('baseline',DriverConfig()),('aggressive',DriverConfig(aggression=1.15,max_speed_m_s=82))]:
  r=SimulationEngine(driver_config=cfg).run();s=r.samples[-1]
  z=VehicleState(s.x_m,s.y_m,s.heading_rad,s.u_m_s,s.v_m_s,s.yaw_rate_rad_s,s.sim_time_s,s.distance_m)
  if r.off_track:z=VehicleModel().step(z,DriverCommand(s.steering_command_rad,s.throttle_command,s.brake_command),.01)[0]
  p=track.nearest(z.x_m,z.y_m)
  rows.append(dict(mode=mode,name=name,status=r.status,lap_time_s=r.lap_time_s,reported_max_error_m=r.max_abs_path_error_m,
      terminal_exact_distance_to_reference_m=math.hypot(z.x_m-p.x_m,z.y_m-p.y_m),terminal_time_s=z.time_s))
print(json.dumps(rows,indent=2))
'''
        output=subprocess.check_output([sys.executable,'-c',script,str(root/'track.py')],cwd=dest,text=True)
        result=json.loads(output)
        (root/'reports/legacy_projection_audit.json').write_text(json.dumps(result,indent=2)+'\n')
        print(output)


if __name__=='__main__':main()
