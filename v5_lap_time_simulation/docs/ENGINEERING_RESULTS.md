# Updated engineering results

Reproduce with `python3 -m v5_lap_time_simulation.cli`. The output directory
contains the actual corrected run, including CSV/JSON and regenerated plots.
All sensitivity experiments hold the calibrated scalar fixed unless power itself
is the deliberately edited parameter. These are assumed-model responses, not
measured setup improvements or causal weather effects.

## Physics audit against the original V5

The original V5 commit was `18b8623c01f423f8072996a8ca92ffd2ddc0806e`.
Its mixed banked-cap/flat-circle calculation at 99.761386 m/s gave lateral
utilisation **103.572%**, hence zero remaining longitudinal tire capacity, while
still allowing steady corner speed through a zero-acceleration clamp. The
consistent banked calculation at that same legacy radius and speed gives
**75.899%** lateral utilisation. Normal load changes from **16682.434 N** to
**21553.986 N**. These are model calculations, not measured tire loads.

With the original effective power 820816.877240 W held fixed, the combined
corrections (banked forces, signed acceleration, sustained-speed caps, segment
order, exactly closing radius and cell/boundary handling) change lap time from
**38.987453 s to 36.642180 s**. This is not an isolated estimate of banking alone.
The corrected zero-bank counterfactual at the same vehicle parameters gives
**40.553032 s**, versus 36.642180 s at 9.2°. That comparison is model sensitivity.
See `physics_audit.json` for exact values and the legacy anchor.

## Recalibrated generic baseline

Refitting the same 206-attempt 2020–2023 median-speed objective gives
**682824.947115 W** effective power, **230.843500 mph** average speed and
**38.987452538 s** lap time at ≤10 m spatial step. The unchanged average/lap
relative to the original fit follows from fitting the same median; it does not
mean the physics correction had no effect. The baseline profile is nearly
constant and power limited, with small bank-dependent rolling-loss changes.
Its simulated speed range is **230.548823–231.375288 mph**.

| Scenario | Lap delta / s | Relative delta / % | Largest absolute segment contribution |
|---|---:|---:|---|
| Mass +10% | +0.036528 | +0.093692 | Back straight: +0.008559 s |
| Drag area +10% | +1.212310 | +3.109487 | Back straight: +0.303325 s |
| Downforce area +10% | +0.028116 | +0.072115 | Back straight: +0.007034 s |
| Tire grip +5% | +0.000000 | +0.000000 | Turn 1: +0.000000 s |
| Available power +10% | -1.232977 | -3.162497 | Back straight: -0.307912 s |
| Air temperature +10 C | -0.419448 | -1.075853 | Back straight: -0.104943 s |
| Track temperature +10 C | +0.000000 | +0.000000 | Turn 1: +0.000000 s |

The baseline has unused grip, so increasing μ or the assumed track-temperature
grip factor does not change the lap. Increasing ClA alone increases rolling loss
in this power-limited regime; CdA is independently held fixed. A real aero setup
would generally couple drag, downforce, ride height and tire behavior. Warmer
air reduces drag in this regime; this is not a universal performance law.

The viewer's initial grip −25% scenario gives **40.963471675 s**, a delta of
**+1.976019137 s (+5.068346%)**. Each turn contributes +0.296197 s, each chute
+0.116753 s, and each long straight +0.278862 s (rounded). Exact contributions
are in `replay_low_grip.json`, alongside the baseline `replay.json`.

## Numerical mesh experiments

Keep vehicle/environment parameters fixed at the 10 m fit; do not recalibrate
on each grid. Each segment is divided into equal cells no longer than the stated
step. Compare speed on 8001 common distance samples using linear interpolation
of v² (the constant-acceleration spatial representation). The finest 1.25 m grid
is a reference, not an exact solution. All these solves stop after two iterative
passes, despite nonzero differences between spatial grids.

### Baseline

| Maximum step / m | Lap / s | Lap minus finest / s | Profile RMSE / m/s | Profile max absolute error / m/s |
|---|---:|---:|---:|---:|
| 40 | 38.989574527 | 0.002792222 | 0.031195 | 0.357037 |
| 20 | 38.988188107 | 0.001405802 | 0.021490 | 0.343077 |
| 10 | 38.987452538 | 0.000670233 | 0.014219 | 0.315171 |
| 5 | 38.987071422 | 0.000289116 | 0.008577 | 0.258831 |
| 2.5 | 38.986879215 | 0.000096910 | 0.003992 | 0.149291 |
| 1.25 | 38.986782305 | 0.000000000 | 0.000000 | 0.000000 |

### Grip −25% (corner-limited example)

| Maximum step / m | Lap / s | Lap minus finest / s | Profile RMSE / m/s | Profile max absolute error / m/s |
|---|---:|---:|---:|---:|
| 40 | 40.998360512 | 0.040569783 | 0.312171 | 3.109802 |
| 20 | 40.972237794 | 0.014447065 | 0.098935 | 1.530555 |
| 10 | 40.963471675 | 0.005680946 | 0.026001 | 0.352606 |
| 5 | 40.960257338 | 0.002466608 | 0.014269 | 0.274408 |
| 2.5 | 40.958613681 | 0.000822951 | 0.005995 | 0.167631 |
| 1.25 | 40.957790729 | 0.000000000 | 0.000000 | 0.000000 |

Refinement reduces the reported lap and profile differences in both scenarios.
At 10 m, the differences are **0.000670233 s / 0.014219 m/s RMSE / 0.315171 m/s
maximum** for baseline and **0.005680946 s / 0.026001 m/s RMSE / 0.352606 m/s
maximum** for low grip. Short transition cells dominate local maxima; a small lap
delta does not establish pointwise profile accuracy. No formal asymptotic order,
Richardson limit or universal error bound for all parameter choices is claimed.
The viewer uses ≤10 m; smaller displayed decimal places describe the numerical
output, not comparable physical accuracy.

## Historical comparison

2024 speed MAE/RMSE are 1.142815/1.400540 mph and four-lap duration MAE/RMSE are
0.769258/0.944403 s. The training-median constant-speed predictor has the same
errors. See [the benchmark report](VALIDATION_REPORT.md) for all four predictors
and the retrospective interpretation. No spatial telemetry validation is available.
