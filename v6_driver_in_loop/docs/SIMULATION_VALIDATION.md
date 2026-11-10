# V6.1 validation report

Execution date 2026-11-10. Local environment: Python 3.14.5, Node 26.8.2, macOS.
Stable repository base `fe65ddf`; isolated `feat/v6-driver-in-loop` worktree.
V6-specific CI uses Python 3.12 and Node 22, and has not been assumed to pass
until the remote workflow actually runs. All results below are actual local runs.

| Suite / check | Passed | Failed | Skipped |
| --- | ---: | ---: | ---: |
| V6 Python engineering + original regressions | 44 | 0 | 0 |
| V6 frontend replay contracts / clock | 9 | 0 | 0 |
| Repository pipeline / portfolio tests | 33 | 0 | 0 |
| V3 scientific / API regressions | 92 | 0 | 0 |
| V3 smoke checks | 10 | 0 | 0 |

Additional checks: `scripts/validate_portfolio.py` PASS;
`v3_point_in_time/scripts/run_v2_immutability_check.py` PASS;
`v3_point_in_time/scripts/run_v3_v2_behavioral_regression.py` PASS across five
supported horizons. No V5 module was imported or executed. Frozen V2/V3/V4 files
were not modified. V3 frontend/Docker builds were not rerun for this isolated
Python/static-viewer addition; this is a scope exclusion, not a skipped test.

## Reproduce

```bash
python3 -m unittest discover -s v6_driver_in_loop/tests -v
node --test v6_driver_in_loop/viewer/replay.test.mjs
python3 -m v6_driver_in_loop.experiments
python3 -m v6_driver_in_loop.cli --plot --output v6_driver_in_loop/output
python3 -m v6_driver_in_loop.audit_legacy
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m unittest discover -s v3_point_in_time/tests -p 'test_*.py' -v
python3 scripts/validate_portfolio.py
python3 v3_point_in_time/scripts/run_v2_immutability_check.py
python3 v3_point_in_time/scripts/run_v3_v2_behavioral_regression.py
python3 v3_point_in_time/scripts/smoke_test.py
```

The core/experiments/replay tests require only Python stdlib and Node. Plotting
requires matplotlib. Existing repository regressions use their existing dependencies.
Wall/CPU fields vary between runs; scientific states, commands, events and non-timing
metrics reproduce exactly on the same interpreter/platform. The suite reruns all
19 scenarios twice and compares these scientific results. A separate regression
checks the committed baseline metrics against a fresh run to catch stale data.

## Physical consistency evidence

Analytical tests cover constant longitudinal force (u=u0+at, x=u0t+at²/2),
quadratic-drag coasting (u=u0/(1+ku0t), x=log(1+ku0t)/k), and small-angle steady
yaw against the linear bicycle reference. Other tests cover world/body rotation,
mirror symmetry/slip-force signs, front force rotation, per-axle combined-force
capacity, aerodynamic speed-squared scaling/load sum, actual body acceleration,
stationary zero force, brake-to-rest behavior, invalid numeric parameters,
actuator priority, model substep refinement, controller/lap/event consistency and
full-resolution/replay serialization. The original ten tests remain; its vacuous
all-status off-track assertion is now strengthened to require off_track.

These are internal/analytical plausibility checks, not measured-car validation.
Finite trajectories do not prove physical accuracy or nonlinear closed-loop stability.

## Numerical refinement and robustness

[Full convergence table](../reports/CONVERGENCE_RESULTS.md) and
[CSV](../reports/convergence.csv) contain 12 runs (baseline/conservative/aggressive,
20/10/5/2.5 ms). All completed. Baseline lap changes shrink to ~0.0009 s between
5 and 2.5 ms. Maximum same-time position error relative to 2.5 ms is 0.4063 m at
20 ms, 0.2019 m at 10 ms and 0.0573 m at 5 ms. Peak ay decreases from 12.849 to
12.816 m/s²; peak yaw from 0.21110 to 0.21035 rad/s. Conservative lap estimates
are non-monotonic (90.3735, 90.3739, 90.3751, 90.3754 s), while state discrepancies
decrease. The target curvature steps and sampled controller can shift transition
timing. Thus no global order or convergence claim follows from lap times alone.
A separate smooth held-command test checks RK refinement without changing controller
sample timing. Event-localization tolerance is not a model accuracy bound.

[Robustness report](../reports/ROBUSTNESS_RESULTS.md) and
[CSV](../reports/robustness.csv) retain 19 scenarios: 14 completed, 5 off-track.
Baseline/max/RMS error 5.18681/2.76899 m; conservative 3.12874/1.82252 m. Aggressive
completes but has only 5.6–28.0 mm clearance across tested timesteps. Its success
cannot be taken as safe performance. Reduced μ=0.8/1.0, 600 ms delay, steering
gain 0.6 and +8 m initial lateral offset fail. The latter terminates at t=0.
No thresholds were changed to make a scenario pass. Failed runs preserve their
terminal state, event time and reason. This one-factor matrix is not a Monte Carlo
reliability estimate and does not explore all interactions.

## Telemetry, replay and remaining limits

Full baseline CSV includes outgoing commands, requested controls, actual body
accelerations, actual/reference distances, saturation flags and terminal sample.
Metadata captures parameter/track/controller settings and initial conditions.
[Replay verification](INTERACTIVE_REPLAY.md) covers browser controls and actual
export compatibility. Presentation interpolation/downsampling is isolated from
simulation and metrics. Browser rendering accuracy is not solver validation.

Limitations: approximate 4.528 km flat stadium, point-CG boundaries, no suspension,
load transfer, detailed tyre transients/thermal state, power-limited drivetrain,
actuator latency calibration, wind, or official track data. Dynamics below 2 m/s
use an explicit regularization and deterministic substeps; reverse is unsupported.
No real hardware DIL, real driver performance or hard real-time claim is made.
