# V6.1 physics and numerical audit

Audit date: 2026-11-10. Original V6 preserved before editing; baseline reproduced
at 72.05 s. The dynamic bicycle, RK4 and pure-pursuit/PID architecture are retained.
Changes below correct demonstrated errors or make previously implicit assumptions
explicit. Historical test passes were not treated as physical validation.

| Identified issue | Evidence and correction | Regression coverage |
| --- | --- | --- |
| Axle lateral limits and total longitudinal limit were independent | Could demand a resultant exceeding μFz. Project each axle's requested (Fx,Fy) radially onto its friction circle. This is an explicit simplified combined-slip law. | `test_combined_friction_circle_and_aero_not_clipped` |
| Front wheel forces treated as body forces | Missing cosδ/sinδ force rotation and associated yaw moment. Rotate front force before body/yaw balance. | `test_front_wheel_force_is_rotated_into_body`, mirror/sign tests |
| Drag and rolling resistance inside tyre clipping | Aerodynamic resistance is external to the tyre contact capacity. Apply aero after tyre projection; rolling opposition remains a separate lumped loss. | friction-circle and drag-only analytical tests |
| Minimum u=0.5 m/s used for world motion | Zero-speed car crept 0.005 m each 10 ms step. Use actual u/v for motion and dynamic pressure, floor only wheel slip denominator. No slip force from steering at rest. | `test_stationary_car_does_not_creep_or_generate_steering_force` |
| Braking/rolling had full nonzero force at rest | Smooth signed opposition with tanh(u/0.2); forward-only accepted-state projection. Add deterministic low-speed stiffness substeps. | braking-to-rest, zero-speed start sweep |
| Reported ay=ur and ax=du/dt | Missed transient dv/dt and rotating-frame correction. Record ax=du/dt−vr=Fx/m, ay=dv/dt+ur=Fy/m at each row. | `test_acceleration_is_force_per_mass_not_velocity_derivative` |
| Only some nonfinite/invalid inputs rejected | Validate all numeric config/state/command fields; reject nonzero bank rather than silently ignore it; reject invalid dt; explicit numerical_error termination. | invalid fields/config/state/failure tests |
| Hardcoded controller wheelbase/steer limit | Use configured vehicle dimensions; engine enforces common actuator limits, including brake priority. Log requested and applied commands. | wheelbase and actuator tests |
| Pure pursuit used arc-length preview as chord | Use actual target chord squared. Keep 35 m permitted preview, expose steering gain. | offset/sign tests and sweeps |
| Round(delay/dt) could release early | Timestamp command queue releases at first control tick at/after due time. No derivative kick on PID initialization; bounded conditional integral. | non-grid delay test |
| Sampled nearest-point position contaminated lane test | Replace grid search with exact minimum over two segments/two semicircles. Rendering resolution no longer affects physics. | coarse-grid narrow-lane and normal-offset tests |
| A wrap of s alone counted as a lap | Track signed net unwrapped progress from the actual initial coordinate. Starting near the finish cannot complete a lap immediately. | arbitrary start/forward/reverse/full-lap tests |
| Time ceiling could exceed max time; terminal row omitted | Truncate last step; localize first detected finish/boundary event by RK4 bisection. Record final state, actual time and reason. | timeout/event/replay alignment tests |
| Old off-track test accepted every possible outcome | Strengthened to require off_track; added crossing position/time assertions. No existing assertion was relaxed. | original suite + new event test |

## Explicit assumptions introduced by the corrections

Rear-only propulsion, 55% front brake split, proportional combined-force projection,
2 m/s slip denominator floor and 0.2 m/s brake/rolling smoothing are illustrative,
unmeasured assumptions. Aero magnitude still follows the original speed-squared
model; its direction now opposes the body velocity vector (zero wind). Static axle
load/downforce split remains unchanged. No suspension, weight transfer or wheel
spin is introduced. No thresholds were expanded: width 15 m, |v|≤100 m/s,
|r|≤10 rad/s. The boundary constrains the point at the CG, not the vehicle footprint.

## Old aggressive off-track result was a projection artefact

`reports/legacy_projection_audit.json` contains a one-off run of the preserved
original source, followed by a run changing **only** its nearest-point function.
Original aggressive run stopped at 15.57 s; the actual continuous-centreline
separation at its terminal integrated state was **6.967683 m**, below the 7.5 m
half-width. With analytic projection alone it completed in 62.86 s, max error
7.492559 m. Baseline changed from 72.05 to 72.11 s under this isolated change.
Other force/controller/event fixes then produced the current baseline/aggressive
72.410/63.221 s. This ablation isolates the projection issue; it does not separately
attribute every later lap-time change. The original API omitted terminal rows,
so the audit reconstructed the last failed step from the stored state/command.

Current aggressive max errors at 20/10/5/2.5 ms are approximately
7.4944/7.4890/7.4735/7.4720 m. Completion has only millimetres of clearance and is
not a robust or recommended operating point. Changing to a real finite vehicle
footprint would invalidate such a tiny margin.

## Equation references

Coordinate and rigid-body balance were cross-checked with the primary
[MathWorks Bicycle Model reference](https://www.mathworks.com/help/driving/ref/bicyclemodel.html)
and [vehicle dynamics identification example](https://www.mathworks.com/help/ident/ug/modeling-a-vehicle-dynamics-system.html).
The present radial friction-circle limiter and low-speed treatment are documented
engineering simplifications; this package does not implement or claim equivalence
to a commercial tyre model.
