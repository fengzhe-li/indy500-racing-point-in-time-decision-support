# Engineering results

The command `python3 -m v5_lap_time_simulation.cli` writes the actual run to
`output/`. `calibration.json` records the 2020–2023 training fit of one effective
scalar. `baseline.json` is the resulting baseline; `sensitivity.csv` reports each
parameter value, baseline and modified lap time, absolute seconds and relative
percentage delta. `sensitivity_segment_contributions.csv` identifies the segment
time changes. `speed_profile.csv` and `segment_times.csv` are model-generated
results, not observed telemetry.

Sensitivity perturbations are fixed engineering scenarios: mass +10%, drag area
+10%, downforce area +10%, grip +5%, power +10%, air temperature +10 °C, and
track temperature +10 °C. The track-temperature experiment passes only through
the assumed grip coefficient; ambient temperature changes density. No result is
a measured setup improvement, and the model does not prove causal weather effects.

## Actual run (current repository data)

The calibrated effective power scalar is 820,817 W, with 206 complete attempts
from 2020–2023 and a training median of 230.8435 mph. The nominal baseline lap
time is 38.9875 s (230.844 mph). It has four modeled turns at 223.160 mph, with
straight speed peaking at 245.545 mph. These are simulated outputs under the
stated assumptions.

The 54 complete 2024 attempts produce held-out average-speed MAE/RMSE of
1.143/1.401 mph and four-lap time MAE/RMSE of 0.769/0.944 s. Mean residuals are
−0.756 mph and +0.505 s. This compares one generic simulated car to the range of
actual cars and attempts, so the aggregate error is a descriptive scale, not a
performance claim.

| Scenario | Lap time delta | Relative delta | Largest segment contributors |
|---|---:|---:|---|
| Mass +10% | +1.316 s | +3.376% | Back straight and main straight (+0.206 s each) |
| Drag area +10% | +0.354 s | +0.908% | Back straight and main straight (+0.167 s each) |
| Downforce area +10% | −1.438 s | −3.688% | Each turn (−0.217 s) |
| Tire grip +5% | −1.284 s | −3.294% | Each turn (−0.194 s) |
| Effective power +10% | −0.397 s | −1.019% | Each main straight (−0.186 s) |
| Air temperature +10 °C | +0.333 s | +0.854% | Each turn (+0.068 s) |
| Track temperature +10 °C | −0.388 s | −0.995% | Each turn (−0.059 s) |

All changes are model sensitivity under the configured assumptions, not measured
setup changes. In particular the track-temperature case acts through the
assumed grip slope only.

The PNGs provide an engineering view of the speed envelope, the held-out
observed/simulated comparison, and assumed-parameter lap-time deltas. Every axis
shows units and the profiles distinguish simulation from actual historical
observations.
