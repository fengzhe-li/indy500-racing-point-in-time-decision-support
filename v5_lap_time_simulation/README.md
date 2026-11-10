# V5 — Physics audit and interactive engineering replay

An isolated Python/NumPy quasi-steady lap model and React/TypeScript viewer using
the repository's existing frontend stack. The viewer consumes genuine Python
simulation results through a separate FastAPI service. It uses an explicitly
assumed closed IMS oval, not GPS or ECU telemetry, individual-car forecasts,
measured aero maps or V6 driver-in-the-loop dynamics.

## Run the viewer

From the repository root (Python 3.10+ and Node 20):

```bash
python3 -m pip install -r v5_lap_time_simulation/requirements.txt
npm ci --prefix v5_lap_time_simulation/frontend
npm run build --prefix v5_lap_time_simulation/frontend
python3 -m v5_lap_time_simulation.server
```

Open **http://127.0.0.1:8005**. The committed baseline configuration is recomputed
by the corrected solver. The initial scenario reduces assumed grip by 25%, showing
acceleration and braking regions. Play/pause, restart, rate control and timeline
seeking share one simulation clock. Click/drag the graph or use its arrow keys
to seek by distance. A baseline ghost is shown at the same elapsed time and stops
at its lap end. Compare the speed profiles, lap delta and segment contributions.

The **V5 Explorer / V6 Replay** selector also opens the V6 interactive replay.
V6 loads the published schema-2 JSON exports from `v6_driver_in_loop/reports`,
lets you pair two V6 runs with matching coordinate-system and stadium geometry,
and animates their recorded Cartesian positions on one shared elapsed-time
clock. Play/pause, restart, seeking and playback-rate controls apply to both
vehicles. Each vehicle stops at its own recorded terminal sample; an off-track
run is marked and never extrapolated. The telemetry cards show exported speed,
position, steering, yaw rate, lateral acceleration and tracking error, plus
throttle/brake only when present. Missing measurements are not synthesized.
The mode is labeled **SIMULATED — V6**. Its illustrative vehicle parameters and
approximate stadium are not official IMS geometry or measured car data. V5 and
V6 are separate simulation domains; the UI does not compare their lap times or
Track Dominance.

## V6 Performance Explorer demonstration

The integrated V6 Explorer replays two runs from the saved V6 simulation telemetry:
the completed baseline and the 600 ms steering-delay run that terminates off track.
The standalone V6 viewer is a separate interface and is not shown as this integrated Explorer.

**Recording pending browser capture.** A full-resolution MP4 and an optimized GIF
demonstration will be linked here after capture from the running Explorer.

Edit mass, CdA, ClA, grip, effective power, air or track temperature, then press
**Recompute with Python**. Pending edits are labeled; errors preserve the last
valid result. **Reset scenario to baseline** restores all supported inputs.
Scenario edits never refit the scalar or alter historical files. Inputs carry
units and assumed/calibrated provenance. The API and schema are at `/docs`.

For development, run the API as above and
`npm run dev --prefix v5_lap_time_simulation/frontend`; Vite on port 5175 proxies
`/api/v5` to port 8005. Production serving uses the built `frontend/dist` folder.

## Reproduce outputs and checks

```bash
python3 -m v5_lap_time_simulation.cli --data-dir data/canonical/v1 --output-dir v5_lap_time_simulation/output
python3 -m v5_lap_time_simulation.schema
python3 -m unittest discover -s v5_lap_time_simulation/tests -p 'test_*.py' -v
npm test --prefix v5_lap_time_simulation/frontend
npm run build --prefix v5_lap_time_simulation/frontend
```

The CLI regenerates calibration, profiles, segment times, sensitivities, historical
comparisons, constant-speed benchmarks, two mesh experiments and replay JSON.
Same inputs produce the same outputs within floating-point/platform precision.
The versioned contract is `schema/replay.schema.json` (`v5-replay-1`); runtime
frontend checks verify periodic endpoints and integration consistency.

## Results and evidence boundary

- Correct order and 4023.360 m total distance; quarter-mile arcs give 90° turns.
- Consistent banked normal/lateral loads and longitudinal friction circle;
  sustainable-speed limits reserve tire force against drag.
- Baseline: **38.987453 s**, effective scalar **682.824947 kW**.
- Grip −25% example: **40.963472 s**, **+1.976019 s** at ≤10 m mesh.
- 2024 speed MAE/RMSE: **1.142815 / 1.400540 mph**, exactly matching the
  training-median benchmark. No demonstrated aggregate predictive gain.
- Refinement from ≤10 m to ≤1.25 m changes baseline lap time by 0.000670 s and
  the low-grip lap by 0.005681 s; local profile errors remain separately reported.

2024 is excluded from scalar fitting but was inspected during development. The
comparison is retrospective and descriptive. This generic model offers spatial
engineering experiments, not measured individual-car dynamics.

Read [physics and numerical method](docs/PHYSICS_MODEL.md),
[data and assumptions](docs/DATA_AND_ASSUMPTIONS.md),
[historical benchmarks](docs/VALIDATION_REPORT.md),
[updated numerical results](docs/ENGINEERING_RESULTS.md),
[viewer contract](docs/REPLAY_CONTRACT.md),
[downstream adapter integration](docs/EXPLORER_ADAPTER.md),
[final release acceptance](docs/FINAL_ACCEPTANCE.md), and
[verification record](docs/VERIFICATION.md).

V5 does not modify frozen V2/V3/V4 assets, import the V3 API, or implement V6 driver
interaction. Its Python package, output, frontend, local server and CI workflow
are isolated under the existing feature branch.
