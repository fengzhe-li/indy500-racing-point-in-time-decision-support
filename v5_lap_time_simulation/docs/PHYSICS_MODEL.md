# Physics model and numerical method

## Scope

The solver is a quasi-steady, single-track-width, point-mass model. It finds the
maximum feasible speed envelope for a car that follows a prescribed closed path.
It does not integrate yaw, sideslip, steering, suspension, tire relaxation,
gearshifts, transient load transfer or a driver controller.

All distances are metres, time seconds, speed m/s, force N, mass kg, power W,
pressure Pa, temperature °C, and angles degrees at configuration boundaries.

## Track

The provided oval has a nominal length of 2.5 mi = 4023.36 m. It is split into
four 1/4 mile corner arcs, two 5/8 mile main straights and two 1/8 mile short
chutes. Each curved section has a configurable constant effective radius and
bank angle. Segment lengths sum exactly to 2.5 mi. This parameterisation follows
the conventional oval description; radius and bank are assumptions, and the
geometry does not define a surveyed lane centreline. Every segment is divided
into equal distance cells no longer than the requested `ds_m`.

## Environment and aero

For dry air, density is

`rho = p / (R_air * (T_air + 273.15))`, `R_air = 287.05 J/(kg K)`.

Aerodynamic drag and downforce magnitudes are

`D = 0.5 * rho * CdA * v^2`

`L = 0.5 * rho * ClA * v^2`.

Humidity, yaw-dependent aero, ground effect and ride-height maps are not modeled.
Rolling resistance is `Crr * m * g`.

## Lateral constraint

For a bank angle `theta` (positive when the bank supports inward centripetal
force), the local corner cap solves

`m v^2/R - m g sin(theta) <= mu * (m g cos(theta) + L)`.

Thus, where the denominator is positive,

`v_corner^2 = m g (sin(theta) + mu cos(theta)) / (m/R - 0.5 mu rho ClA)`.

The result is bounded by the configured vehicle maximum speed. If the denominator
is non-positive, the assumed aero/grip combination predicts no lateral cap below
that maximum; this is reported as a consequence of the assumptions, not evidence
that the real car has unlimited cornering capability.

For longitudinal propagation, remaining tire force is computed with a friction
circle:

`F_x,max = sqrt(max(0, (mu * (m g + L))^2 - (m v^2 |kappa|)^2))`.

The propagation approximation uses flat-road normal load in this combined-force
calculation. Banking is included in the scalar corner-speed cap. The difference
is a known simplification. Track temperature changes `mu` only through an
explicitly assumed coefficient in `Vehicle.grip_per_track_temp_k`; it is a
sensitivity knob, not a measured tire law.

## Longitudinal constraints

Propulsive tire force is bounded by

`F_drive = min(F_drive,max, P/v, F_x,max)`.

Net acceleration is

`a = max(0, (F_drive - D - Crr*m*g)/m)`.

Braking capability is `min(F_brake,max, F_x,max)` plus aerodynamic and rolling
resistance, divided by mass. No engine braking or separate front/rear axle model
is included.

## Closed loop solution

1. Construct each cell's local speed cap from top speed and, for a curve, the
   lateral formula above.
2. Initialize all cells at their local caps.
3. Sweep forward around the ring, constraining the next cell by
   `v[j]^2 <= v[i]^2 + 2*a[i]*ds[i]`.
4. Sweep backward around the ring, constraining the previous cell by
   `v[i]^2 <= v[j]^2 + 2*b[j]*ds[i]`.
5. Repeat until the maximum speed change is below the configured tolerance.
6. Integrate each cell using constant acceleration kinematics in average-speed
   form: `dt = 2*ds/(v[i]+v[j])`.

The profile only decreases from its local caps, is periodic by wraparound edge,
and fails explicitly if the iteration limit is reached. A zero or invalid
configuration raises a `ValueError`; non-convergence raises a `RuntimeError`.

## Outputs

The structured result includes distance, speed, curvature, local speed cap,
available acceleration/braking, segment index, time increment, lap time,
average speed, convergence flag and iteration count. The CLI exports these with
units to CSV/JSON. The profile plots simulated values only; the separate
historical comparison plot identifies observed official average speeds.
