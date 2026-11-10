# Performance Explorer data contract

The frontend contract is `ComparisonSeriesV1` (`schemaVersion: 1.0.0`) in `frontend/src/domain/contract.ts`. Every series declares its mode and data kind, provenance, units, geometry classification, axis types, signal availability and data granularity. Observed historical timing summaries remain distinguishable from simulations.

## Historical adapter

`historical-attempts-v1.json` is a compact browser dataset exported from canonical `r4/output/r4p1_attempt_four_lap_panel_v1.csv`. It contains retained complete four-lap attempts and lap-average speed values. The adapter converts average mph over a standard 2.5-mile lap to a lap duration for a schematic boundary replay. These values are not official transponder line-crossing times. The dataset has no matched section boundaries or GPS coordinates, so historical sector dominance and continuous track progression are unavailable.

## V5 provider boundary

Implement `SimulationAdapter` with mode `v5-quasi-steady` once V5 publishes its versioned output schema. Required mapping inputs include the speed-vs-distance grid, distance units, interval semantics, source provenance, and data availability. Compare time only over matched distance intervals. Do not import `v5_lap_time_simulation` from this independent module.

## V6 provider boundary

Implement `SimulationAdapter` with mode `v6-dynamic` once V6 publishes its versioned telemetry schema. Required mapping inputs include a validated common track-distance coordinate, monotonic time, distance and speed units, sample provenance, and optional signal availability for steering, throttle, braking, yaw rate and tracking error. Never substitute synthetic values for absent telemetry. Do not import `v6_driver_in_loop` from this module.

The V5/V6 classes currently fail explicitly until those contracts exist. Example data should be labelled illustrative and must not be represented as official results.
