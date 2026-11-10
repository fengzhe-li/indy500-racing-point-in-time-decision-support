# V6 — audited vehicle dynamics and interactive replay

Independent **Software-in-the-Loop** vehicle simulation with a virtual driver.
Every trajectory, trace and lap time is **SIMULATED**. Parameters are illustrative;
this is not measured IndyCar ECU telemetry, a surveyed IMS lane, a real-time
certification or a validated hardware Driver-in-the-Loop system.

The existing dynamic bicycle/RK4/pure-pursuit/PID architecture is retained. The
follow-up audit corrects combined tyre forces, front-force rotation, low-speed
creep, acceleration telemetry, geometry projection, lap events and validation.
[Audit and legacy comparison](docs/PHYSICS_AUDIT.md).

## Run and replay

Python 3.10+ standard library is sufficient for the model, tests and data exports.
Node 22+ runs frontend contract tests; a modern browser runs the viewer. Matplotlib
is optional for static engineering figures. No V5 imports or frontend build step.

From the repository root:

```bash
python3 -m v6_driver_in_loop.cli --dt 0.01 --output v6_driver_in_loop/output
python3 -m v6_driver_in_loop.experiments
python3 -m http.server 8766 --bind 127.0.0.1
```

Open **http://127.0.0.1:8766/v6_driver_in_loop/viewer/**. Committed reports/replays
already let the viewer work before regeneration. It displays the reference path,
boundaries, actual trajectory and heading, play/pause/reset/seek/rate controls,
synchronized speed/steering/pedals/yaw/lateral-acceleration/tracking-error traces,
saturation marks, off-track events and termination reasons for all 19 runs.
The viewer only reads files; it never runs or edits the physical model. Native
HTML/Canvas/ES modules avoid coupling this small replay to frozen V3's React/Vite
application or adding package dependencies. See [replay guide](docs/INTERACTIVE_REPLAY.md).

```bash
# One alternate scenario; failure exits 1 while still exporting its telemetry.
python3 -m v6_driver_in_loop.cli --driver delay_0.6s --output v6_driver_in_loop/output/delayed
# Optional standalone plot (requires matplotlib):
python3 -m v6_driver_in_loop.cli --plot --output v6_driver_in_loop/output/plotted
# Original legacy-projection ablation from preserved source:
python3 -m v6_driver_in_loop.audit_legacy
```

For multi-lap elapsed time use `--laps 2 --time 180`. Configurations and initial
states are also exposed through the typed Python interfaces.

## Actual follow-up results

Baseline at 10 ms: **72.409997 s**, max/RMS tracking error **5.18681 / 2.76899 m**.
Speed min/time-weighted mean/max: **30.000 / 62.842 / 70.441 m/s**. Reference
length is **4527.951644 m**. It is not the 4023.36 m V5/nominal IMS distance.
Historical 72.05 s belonged to the earlier implementation, before the audit.

| Scenario | Result | Simulated lap time s | Maximum path error m |
| --- | --- | --- | --- |
| Baseline | completed | 72.409997 | 5.18681 |
| Conservative | completed | 90.373859 | 3.12874 |
| Aggressive | completed, only ~11 mm boundary margin | 63.221075 | 7.48895 |
| 100 ms command delay | completed | 72.481166 | 5.48751 |
| 600 ms command delay | off-track | — | 7.50000 |

The 19-scenario matrix has **14 completed and 5 off-track** runs. Failures include
reduced grip, weak lateral control, excessive delay and initially off-track state.
No failure threshold was relaxed. These counts are designed scenarios, not a
statistical success rate. [Full robustness results](reports/ROBUSTNESS_RESULTS.md).

Baseline lap times at 20/10/5/2.5 ms are **72.4132 / 72.4100 / 72.4077 / 72.4068 s**.
Relative to 2.5 ms, maximum same-time position differences are **0.4063 / 0.2019 /
0.0573 m**. Full convergence results also cover conservative/aggressive drivers,
acceleration, yaw, errors, saturation and CPU/wall timing. Lap-time agreement alone
is insufficient: [refinement results](reports/CONVERGENCE_RESULTS.md).

## Tests and evidence

```bash
python3 -m unittest discover -s v6_driver_in_loop/tests -v
node --test v6_driver_in_loop/viewer/replay.test.mjs
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m unittest discover -s v3_point_in_time/tests -p 'test_*.py' -v
python3 scripts/validate_portfolio.py
```

Recorded local execution: **44 V6 Python + 9 frontend + 33 repository + 92 V3
Python tests passed; 0 failures, 0 skips**. V2 immutability, V3/V2 behavioural
regression, portfolio integrity and 10/10 smoke checks passed. Browser smoke
checks covered playback, pause, seek, rate selection, reset and event alignment.
See [validation report](docs/SIMULATION_VALIDATION.md) for scope and limits.

## Files and interfaces

- `models.py`, `vehicle.py`: SI states/commands and audited force/integration model.
- `track.py`: analytic closed stadium geometry, projection and boundaries.
- `controller.py`: configurable driver, typed controller protocol.
- `simulation.py`: deterministic engine, event records, metrics, CSV/JSON exports.
- `experiments.py`, `replay.py`, `viewer/`: sweeps, actual-sample export, read-only replay.
- `reports/`: full baseline CSV, metadata, all scenario configurations, metrics,
  convergence, replays and [engineering figure](reports/engineering.png).
- `archive/pre_audit_v6.tar.gz`: full preserved original V6 source, for audit only.

[Vehicle equations and limits](docs/VEHICLE_DYNAMICS.md) ·
[Driver design](docs/CONTROLLER_DESIGN.md) ·
[V5 compatibility review](docs/V5_COMPARABILITY.md) ·
[Proposed V5 contract](docs/V5_INTEGRATION_CONTRACT.md) ·
[Future hardware DIL](docs/FUTURE_HARDWARE_DIL.md) ·
[Git delivery](docs/GIT_DELIVERY.md)
