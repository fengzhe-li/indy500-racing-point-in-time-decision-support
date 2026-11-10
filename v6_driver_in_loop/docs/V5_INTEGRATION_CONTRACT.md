# Proposed V5/V6 contract and comparison limits

V6 imports no V5 module. The review below reads the immutable **18b8623** V5
commit and its committed baseline report; the parallel V5 working tree is mutable
and is not a dependency. This is a proposed contract, not an agreed/shared API.
See [compatibility report](V5_COMPARABILITY.md) for exact baseline mappings.

## Neutral input interface (SI)

Track: `length_m`, closed distance `s_m` in [0,length), reference `x_m`,`y_m`,
`heading_rad`, `curvature_per_m`, `width_m`, optional `banking_rad`, and declared
coordinate origin/orientation. Geometry must close in position and tangent;
curvature, distance and coordinates must be mutually consistent. Samples should
include units, resolution, provenance, source hash and approximation status.
V6 `OvalTrack.point()` returns `TrackPoint` with these fields (`distance_m` for s).
V5's reviewed segment-distance model has no reference x/y/heading/width. An adapter
must not invent surveyed coordinates. Bank is unsupported by current V6: require
zero or reject until its force balance is implemented. V5 degrees require an
explicit `radians = degrees*pi/180` conversion.

Vehicle: mass kg, wheelbase/axle distances m, yaw inertia kg m², CdA/ClA m²,
air density kg/m³, Crr dimensionless, tyre friction dimensionless and axle cornering
stiffness N/rad, propulsion/braking force N, optional power W, brake split and
steering limits radians. V5 point-mass fidelity does not require inertia, wheelbase,
stiffness or axle split. V6 constant force cannot impersonate V5's min(P/v,Fmax)
power law. An explicit parameter-provenance record must distinguish assumed,
measured and calibrated fields and carry version/source/uncertainty where known.
Defaults remain illustrative. Any future adapter must reject missing required
fields rather than silently substitute values that appear calibrated.

## Output interface

Use explicit SIMULATED label and schema/model versions. Lap duration s (V6
`lap_time_s` is elapsed time for `max_laps`; default one), distance m, speed m/s,
body longitudinal/lateral acceleration m/s², yaw rad/s, heading rad, controls
normalized [0,1], steering rad. Distinguish actual trajectory arc length
`distance_m`, wrapped reference `track_distance_m`, and unwrapped signed
`progress_m`. Use current metadata for model/track/vehicle/controller provenance,
initial conditions, units, fixed control dt, substep method, status and termination
reason. `wall_time_s` and `cpu_time_s` are execution measurements, not simulation time.

Replay schema 2 is a V6 display export, not a cross-solver physics contract.
It contains original sampled rows with reduced display frequency, preserved
saturation transitions and terminal events; metrics come from full telemetry.

## Conditions for a meaningful comparison

Agree on a closed geometric path, banking support, vehicle/environment parameter
provenance, combined-force/aero conventions, power/force laws, and flying-lap vs
startup initial conditions. Separate solver-limit envelopes from deliberately
limited driver targets. Then compare speed against reference distance, sector
integration, force budgets and lap totals. V6's actual driven path and transients
must remain visible. Conduct independent mesh/time refinement before drawing
conclusions. Do not demand identical values from quasi-steady and transient models.
Current data do not satisfy these conditions; a lap-time ratio is not a fidelity metric.
