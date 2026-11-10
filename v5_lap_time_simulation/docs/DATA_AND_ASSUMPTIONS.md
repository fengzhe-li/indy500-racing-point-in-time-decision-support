# Data inventory and assumptions

## Repository evidence reviewed

The audit used `data/canonical/v1/attempts.csv`, `attempt_laps.csv`,
`attempt_sections.csv`, `qualifying_events.csv`, `weather_forecasts.csv`,
`forecast_snapshots.csv`, `field_evidence_links.csv`, and the repository's
`data_reconnaissance_report.md` and `data/canonical/README.md`.

| Quantity | Classification | Availability and use |
|---|---|---|
| Event/session, car number, driver/team, attempt ID/status | OBSERVED | Canonical attempt rows; identifiers are retained in historical output |
| Four-lap average speed and official elapsed time | OBSERVED | Used for 2024 held-out comparison only |
| Individual lap times and speeds | OBSERVED | Canonical lap records; the report inventory describes year-specific completeness |
| Section/lap speeds and section timing | OBSERVED | Present for report-supported sections; not treated as high-rate sampling |
| Selected event timestamps | OBSERVED or evidence-qualified | Canonical chronology may be approximate or order-only; not required for V5 speed-profile fitting |
| Weather forecast fields | OBSERVED in available forecast snapshots | Air temperature and pressure are configurable; standard run uses stated baseline values |
| Air density | DERIVED | Ideal dry-air equation from air temperature and pressure |
| Lap-average conversion from 4 x 2.5 mi / elapsed time | DERIVED | Used only as a physical consistency relationship; official average speed is compared directly |
| 2.5 mi track length and segment split | DERIVED/parameterised | Closure convention for IMS oval, not GPS geometry |
| Corner radius and banking | ASSUMED | Configurable effective values, not surveyed line-specific measurements |
| Vehicle mass, CdA, ClA, tire mu, brake/drive limits, Crr | ASSUMED | Generic configurable scenario; no claim of exact current or confidential IndyCar values |
| Effective power scalar | CALIBRATED | Fit to pooled 2020–2023 median average speed, conditional on all other assumptions; not an engine power estimate |
| Track-temperature effect on grip | ASSUMED | A small explicit coefficient used only for sensitivity; empirical weather association is not causal evidence |
| Unique vehicle dynamics calibration | UNAVAILABLE | Aggregate speeds are insufficient to uniquely identify mass, aero, tire, power and setup |
| GPS path, steering, throttle, brake pressure, tire temperature, wheel speed, suspension travel | UNAVAILABLE | No telemetry is synthesized |

The `attempt_sections` values are section summaries from official reports. Four
lap speeds are averages over a lap, not continuous telemetry. The simulation's
spatial profile is model-generated and must not be interpreted as measured
distance-resolved vehicle speed.

## Baseline parameters

Baseline values are recorded in `output/baseline.json`; the fitted scalar and
training objective are in `output/calibration.json`. Vehicle parameters are
configurable in `model.py` and deliberately labelled assumptions. Environmental
baseline: 25 °C air, 101325 Pa pressure, and 35 °C track temperature as the
reference point for the sensitivity-only grip relation. These are simulation
conditions, not a reconstructed historical session's aligned environment.

## Independence and preservation

V5 reads the canonical V1 data read-only. It writes only inside its own
`output/` folder. It neither updates nor reinterprets frozen V2/V3/V4 assets,
claims, hashes, historical results, or model coefficients.
