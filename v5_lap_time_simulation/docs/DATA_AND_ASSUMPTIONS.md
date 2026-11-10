# Data provenance and assumptions

## Evidence inventory

V5 reads canonical `data/canonical/v1/attempts.csv` and `attempt_laps.csv`.
The repository also contains report-supported section summaries, chronology,
forecast snapshots and evidence links. Their existence does not provide vehicle
telemetry or a surveyed spatial crosswalk to V5's eight segments.

| Quantity | Classification and use |
|---|---|
| Official four-lap average speed and elapsed time | OBSERVED canonical data; 2020–2023 calibrates one scalar, 2024 supplies descriptive comparisons |
| Attempt, driver, car and session identifiers | OBSERVED identifiers retained for traceability; no per-car parameter fitting |
| Lap and section summaries | OBSERVED where report coverage supports them; never continuous speed measurements |
| Nominal oval lengths and 9.2° corner bank | Published nominal description from [INDYCAR](https://www.indycar.com/news/2023/05/05-19-setup-indy); application to one ideal path is ASSUMED |
| Four circular arcs, uniform bank, flat straights | ASSUMED geometry; radius 256.135052735 m is DERIVED from quarter-mile arc and 90° turn |
| Mass, CdA, ClA, tire μ, force limits, Crr, top speed | ASSUMED generic parameters, not actual or confidential IndyCar specifications |
| Effective power | CALIBRATED scalar conditional on all other assumptions; not measured engine power |
| Air/track conditions | ASSUMED fixed conditions, not historical conditions aligned to an attempt |
| Air density | DERIVED ideal dry air from configured temperature and pressure |
| Track-temperature grip slope | ASSUMED sensitivity law, not empirical causal evidence |
| GPS, ECU, steering, throttle, brake pressure, tire state, suspension | UNAVAILABLE; no such traces are fabricated |

## Baseline

`output/baseline.json` records all effective inputs. Baseline mass is 800 kg,
CdA 1.00 m², ClA 1.50 m², μ 1.80, drive/brake limits 12000/20000 N,
Crr 0.015, top-speed bound 120 m/s, and grip slope 0.0015 K⁻¹. Air is 25 °C,
101325 Pa; track is 35 °C, the reference grip temperature. Effective power is
682824.947115 W after correcting the physics and refitting the same 2020–2023
median target. These choices are not uniquely identifiable from aggregate speeds.
The baseline is power limited; a grip reduction of 25% provides a separate
corner-limited viewer example without changing the fitted scalar.

## Independence and interpretation

The scalar fit uses 206 complete 2020–2023 attempts. A test mutates 2024 outcomes
and checks that the fit is unchanged. However, 2024 results have been inspected
during development. This is a retrospective, year-separated descriptive
comparison, not an untouched prospective validation of model selection.

V5 writes only its own outputs and serves a separate local API/frontend. V2/V3/V4
assets and scientific claims remain frozen. The V6 directory and concurrent C++
work are outside this implementation. V5 has no driver-in-the-loop dynamics.
