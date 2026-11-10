# Frozen V5 replay interface for downstream adapters

**Contract: `v5-replay-1`.** Consume exported JSON or the V5 API through an
adapter owned by the downstream project. V5 does not import V6 or implement the
Dual-Car Performance Explorer. The structural JSON schema is
`../schema/replay.schema.json`; existing valid baseline/scenario files remain
compatible. The scientific meaning below is part of the contract.

## Coordinates, fields and units

| Field | Meaning |
|---|---|
| `distance_m` | N+1 increasing path-distance nodes, from 0 to `track_length_m` |
| `elapsed_s` | N+1 increasing simulated times, from 0 to `lap_time_s`; no wall-clock timestamp |
| `speed_mps` | Simulated positive speed at those nodes; last equals first |
| `acceleration_mps2` | N constant net longitudinal accelerations, one per spatial cell; not throttle/brake commands |
| `xy_m` | N+1 assumed planar path coordinates in metres; not latitude/longitude or GPS |
| `speed_cap_mps` | Node cap combining sustainable corner, power and maximum-speed constraints; not a measured or purely lateral limit |
| `mode` | N qualitative active-constraint labels; see `REPLAY_CONTRACT.md` for tolerances |
| `segments` | Ordered pieces with `start_m`, `distance_m`, `radius_m` (null means straight), `banking_deg`, `time_s` |
| `vehicle`, `environment` | Effective simulation input snapshot, including the scenario values |
| `units`, `provenance`, `origin` | Mandatory interpretation metadata, carried through the adapter |
| `average_speed_mph` | Explicit exception to SI speed units: lap-average mph |

For the shipped IMS path, (x,y)=(0,0) and s=0 are **Turn 1 entry**. Initial
heading is +x, +y is to its left, and positive curvature turns counterclockwise.
The drawing may invert y for screen coordinates. This frame is arbitrary, with
no geographic bearing. It is not the official start/finish timing line. Total
length is 4023.360 m; four circular arcs have radius 256.135052735 m. Segment
intervals are `[start_m, start_m + distance_m)`, except the final endpoint L.
The origin/geometry must agree before comparing two profiles spatially.

Vehicle units are kg, m² (CdA/ClA), W, N and m/s; μ/Crr are dimensionless, grip
slope K⁻¹. Environment uses °C and Pa. A null track temperature means no
track-temperature correction; null or absent telemetry is never converted to
zero. Segment bank is degrees. UI conversion uses 1 m/s = 2.2369362920544 mph.

## Interpolation and lap completion

Binary-search time or distance to locate cell i. With τ=t−t_i and
`a=acceleration_mps2[i]`:

```
s(t) = s_i + v_i τ + 0.5 a τ²
v(t) = v_i + a τ
v(s) = sqrt(v_i² + 2 a (s−s_i))
t(s) = t_i + 2 (s−s_i) / (v_i + v(s))
```

This agrees with `dt=2 ds/(v_i+v_(i+1))`. Do not linearly interpolate distance
in time or speed in distance. To reproduce positions exactly, integrate the
ordered constant-curvature segments (as in `replay.py:geometry_at`); interpolated
xy chords are only a drawing approximation. Cap/mode data describe numerical
constraints, not additional physical channels to interpolate into telemetry.

Keep the explicit endpoint `(L,T,v0)` distinct from `(0,0,v0)` even though both
have the same drawing position. A single-lap comparison should clamp a finished
car at T. For multi-lap playback, the adapter must separately count completed
laps and use `t mod T` for local position. V5's viewer loops the scenario clock;
its baseline ghost clamps to its own finish on each scenario cycle. It does not
model changes across successive laps.

## Comparisons, provenance and versioning

Compare profiles on common **distance coordinates**, not matching array indices:
meshes may differ. Use each profile's own time mapping for a same-elapsed-time
race display. Compute lap delta as scenario T minus baseline T and segment
deltas only for matching geometry, order and boundaries. Do not assume that the
same array index or fraction of time denotes the same physical distance.

The calibrated effective power is conditional on the assumed generic vehicle
and 2020–2023 median target. Edited scalar values are scenario assumptions, never
a fresh historical fit. Preserve all input/provenance blocks. Archive a source
commit identifier and payload checksum in the adapter's own envelope if stronger
lineage is needed; do not add undeclared fields to this frozen payload. A schema
version is not a model calibration or implementation version.

Validate the structural schema **and** semantic invariants: finite positive
speeds/times, increasing coordinates, consistent kinematics, caps, closed geometry,
ordered segment totals and declared units. The frontend now rejects inconsistent
units/geometry rather than drawing them. Existing valid replay files are unchanged.
Unknown schema versions must be rejected or routed to an explicitly supported
adapter. Changing field meaning, units, required fields or arrays requires a new
version; keep the v1 adapter and fixtures. V1 forbids extra top-level fields.

GPS, ECU samples, throttle, steering, brake pressure, yaw/sideslip, wheel/tire
state, suspension travel and historical synchronized footage are unavailable.
Keep them unavailable. Net acceleration or constraint modes cannot identify them.
V6 dynamics, wake/tow interactions and driver control are outside V5's interface
and scientific acceptance.
