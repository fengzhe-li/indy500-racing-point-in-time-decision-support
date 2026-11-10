# V5 — Physics Based Quasi Steady Lap Simulation

V5 is an independent Python/NumPy simulation module. It computes a periodic speed
profile and lap time from a parameterised oval, a point mass vehicle model and
air/track conditions. It is deliberately separated from the frozen V2/V3/V4
scientific and application assets.

This is an engineering reference model, not an IndyCar performance predictor.
Vehicle values and unsurveyed oval lane geometry are labelled assumptions. One
effective power scalar is calibrated to the pooled 2020–2023 median average
speed, conditional on the remaining assumed parameters; it is not a physical
engine-power estimate. 2024 is held out for validation.

## Quick run

From the repository root, with Python 3.10+, NumPy and Matplotlib installed:

```bash
python3 -m v5_lap_time_simulation.cli \
  --data-dir data/canonical/v1 \
  --output-dir v5_lap_time_simulation/output
```

This writes a JSON baseline, per-distance and per-segment CSVs, a historical
comparison, sensitivity tables, and PNG engineering plots. All outputs are
deterministic for the same source/configuration. The data path can be changed;
no user-specific absolute paths are embedded in the code.

Run the V5 verification suite:

```bash
python3 -m unittest discover -s v5_lap_time_simulation/tests -p 'test_*.py' -v
```

## What is included

- Parameterised 2.5 mile IMS oval approximation, with straights, four turns and
  optional banking. It is the oval, not the IMS road course.
- Drag, downforce, rolling resistance, power/drive force, braking, a friction
  circle and a bank-adjusted lateral corner speed cap.
- Closed loop forward acceleration and backward braking propagation followed by
  distance/time integration.
- Air density from ideal dry air and a separately labelled track-temperature
  grip sensitivity assumption.
- 2024 official four-lap comparison, fixed assumed-parameter sensitivity
  experiments, segment time contributions, CSV/JSON export and plots.

## Status and evidence boundary

| Item | State |
|---|---|
| Official four-lap average speeds, total times and lap records | Observed in canonical data |
| Section speeds/times | Observed for supported report coverage; not treated as telemetry |
| IMS total oval distance | 2.5 mi nominal configuration; approximation constraint |
| Turn radius and banking in this module | Assumed parameter values, not surveyed or lane-specific |
| Vehicle mass, aero, power, tire grip and force limits | Assumed configurable values; not asserted as confidential IndyCar specifications |
| Weather fields | Present in canonical forecast/evidence tables; V5 uses an ideal-air baseline and does not fit weather effects |
| GPS, steering, throttle, brake pressure, tire temperature traces | Unavailable and not fabricated |
| Calibration | 2020–2023 median-speed fit of one effective scalar; remaining parameters assumed |
| Validation | Chronological 2024 descriptive comparison; not high fidelity validation |

See [the physics model](docs/PHYSICS_MODEL.md),
[data and assumptions](docs/DATA_AND_ASSUMPTIONS.md),
[validation report](docs/VALIDATION_REPORT.md), and
[engineering results](docs/ENGINEERING_RESULTS.md).

## V6 compatibility

Track, immutable vehicle/environment configurations, speed state and simulation
result are separate interfaces. V5 does not implement a driver controller,
real-time driver interaction or hardware in the loop.
