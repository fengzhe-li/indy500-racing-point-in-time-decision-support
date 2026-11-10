"""Run one reproducible virtual-driver example and export full SI telemetry."""
import argparse
from pathlib import Path
from .experiments import scenarios


def main():
    configs={s.name:s for s in scenarios()}
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dt',type=float,default=.01)
    ap.add_argument('--time',type=float,default=180)
    ap.add_argument('--output',default='v6_driver_in_loop/output')
    ap.add_argument('--driver',choices=configs,default='baseline')
    ap.add_argument('--laps',type=int,default=1)
    ap.add_argument('--plot',action='store_true',help='optional matplotlib engineering figure')
    args=ap.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    result=configs[args.driver].run(args.dt,args.time,args.laps)
    result.write_csv(out/'simulated_telemetry.csv');result.write_json(out/'result.json')
    if args.plot:
        from .plotting import plot_result
        plot_result(result,out/'engineering.png')
    print(f'SIMULATED status={result.status} sim_time={result.elapsed_sim_s:.6f}s lap_time={result.lap_time_s} '
          f'path_error={result.max_abs_path_error_m:.3f}m cpu={result.cpu_time_s:.3f}s '
          f'wall={result.wall_time_s:.3f}s samples={len(result.samples)} reason={result.reason}')
    return 0 if result.status=='completed' else 1


if __name__=='__main__':raise SystemExit(main())
