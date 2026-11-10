# Validation report

## Procedure

The calibration set is all canonical complete four-lap attempts from 2020–2023.
One effective scalar, `power_w`, is fit by matching the model's average speed to
the pooled median official average speed (equivalent to minimizing absolute
error for a constant-output model). Mass, aero, tire grip, force limits, track
radius and banking remain assumed. This scalar is not an engine-power estimate;
many parameter combinations are observationally equivalent. The comparison
uses complete 2024 four-lap attempts as a chronological held-out descriptive
set. No 2024 rows are used to tune parameters. For each official
attempt, the simulated lap time is multiplied by four and compared with the
official total elapsed time; average speed is compared with the official
four-lap average. This simple comparison does not account for car, driver, setup,
fuel, tire state, wind direction, tow, traffic or run-specific configuration.

The simulation uses a fixed 2.5 mile lap. The official four-lap duration is kept
as recorded. An incomplete attempt is excluded by requiring exactly four
complete canonical lap rows and finite positive official total time/speed.

## Results

Numbers are generated in `output/validation_metrics.json` and rows in
`output/historical_validation_2024.csv`. The table is updated from the actual
run; no metric is hard-coded into the analysis.

| Metric | Value |
|---|---:|
| Held-out year | 2024 |
| Complete attempt count | 54 |
| Calibration observations / fitted scalars | 2020–2023 attempts / 1 effective scalar |
| Speed MAE / RMSE | 1.143 / 1.401 mph |
| Speed mean residual (sim − observed) | −0.756 mph |
| Four-lap duration MAE / RMSE | 0.769 / 0.944 s |
| Four-lap duration mean residual (sim − observed) | +0.505 s |

## Interpretation

This is a deliberately limited validation: one assumed vehicle and one assumed
oval cannot represent the variation among historical entrants and attempts. The
calibration matches one median speed, not the historical vehicle physics. The
2024 residuals are out of sample and not evidence of a high-fidelity predictive
model.

The canonical data contains official section aggregates (nine-section reports
for 2020–2023 and a different 17-section set for 2024). V5 does not report a
section-by-section historical score: those timing boundaries do not yet have a
verified distance crosswalk to the approximated eight-part track, and the 2024
section schema differs from the training-era schema. The simulated segment
contributions are retained separately. Creating a mapped section score without
that crosswalk would imply unsupported spatial alignment.

Lap and section aggregates can quantify broad discrepancy. They cannot recover
the unique aero map, tire model, setup, driver line, or transient controls
required for a high-fidelity simulation.
