# V5 engineering replay contract

## Service and schema

`GET /api/v5/baseline` recomputes from the committed corrected baseline inputs.
`POST /api/v5/simulate` accepts optional `vehicle` and `environment` updates;
unknown fields, nonfinite inputs and out-of-range values are rejected. Results
are cached only in memory (32 entries), with no historical or baseline mutation.
Repeated identical requests return identical results. Simulation failures return
HTTP 422; the UI retains the previous valid replay.

| Editable field | Unit | Allowed range |
|---|---|---|
| mass_kg | kg | 600–1100 |
| cd_a_m2 | m² | 0.6–1.6 |
| cl_a_m2 | m² | 0.5–2.5 |
| tire_mu | dimensionless | 1.1–2.2 |
| power_w | W | 400000–1100000 |
| air_temperature_c | °C | 5–45 |
| track_temperature_c | °C | 15–65 |

These bounds are demonstration inputs, not validated real-car operating limits.
Geometry, pressure, force limits and remaining baseline parameters are fixed in
the viewer. The effective power's baseline is calibrated; an edited power is an
assumed scenario value and is never automatically refitted.

The Pydantic source `schema.py` emits `schema/replay.schema.json`, version
`v5-replay-1`. Frontend types and runtime checks are in `frontend/src/replay.ts`.
Tests consume real Python-generated `output/replay*.json` fixtures and compare
the generated JSON schema with its committed representation.

## Arrays and units

For N cells, distance_m, elapsed_s, speed_mps, speed_cap_mps and xy_m have N+1
nodes; acceleration_mps2 and mode have N cells. The endpoint is explicit:
`distance=L`, `elapsed=T`, `speed=v_start`, and drawing coordinates close.
Time and distance are strictly increasing. `speed_cap_mps` is the combined
sustainable corner/power/top-speed cap, not a telemetry channel or solely a
lateral tire limit. Segment records carry ordered lengths, curvature radius,
bank, start distance, simulated time and assumption provenance.

Modes label active numerical constraints: acceleration, braking, corner_cap,
or steady_or_transition. Acceleration/braking labels require a signed cell
acceleration and agreement with the computed bound within 0.05 m/s²; corner_cap
requires a curve node within 0.05 m/s of its sustainable cap. A curve cap can
still be power limited. These labels do not imply pedal positions or pressure.

The units/provenance blocks identify SI values and assumed track, vehicle,
environment, and the calibrated effective scalar. The historical scalar field
`average_speed_mph` is explicitly mph; frontend conversion is otherwise display
only. Runtime checks reject unsupported versions and inconsistent time integrals.

## Synchronization

A single elapsed-time state drives the timeline, speed cursor and car. Within
cells use exact constant-acceleration kinematics; graph seeking applies its
inverse. The map integrates the same assumed arcs/straights. Seeking pauses
playback. Playback loops at lap end, restart sets time zero, and rate multiplies
wall time only. The baseline ghost uses the same elapsed time capped at its own
lap duration, while the graph compares baseline/scenario at the same distance.

There is no GPS, historical footage, ECU channel, steering, throttle,
brake-pressure reconstruction, or driver controller.
