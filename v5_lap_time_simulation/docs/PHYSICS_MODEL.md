# Corrected V5 physics and numerical method

## Scope and units

This is a quasi-steady point-mass engineering model on a prescribed horizontal
closed path with banked road axes. It produces a conservative speed envelope
under local sustainable-speed caps, not a proven globally optimal transient lap.
SI units are used internally: m, s, m/s, N, kg, W, Pa; temperature inputs are °C
and configured bank angles are degrees. No driver, yaw, steering, suspension,
tire relaxation, axle load transfer, gearshifts or measured controls are modeled.

## Track order and geometric closure

The order is Turn 1 → short chute 1–2 → Turn 2 → back straight → Turn 3 →
short chute 3–4 → Turn 4 → front straight → Turn 1. Four 402.336 m arcs,
two 201.168 m chutes and two 1005.840 m straights sum to **4023.360 m (2.5 mi)**.
The default radius is derived as `402.336 / (π/2) = 256.135052735 m`, so each
constant-radius arc turns exactly 90°. Integrating these segments produces a
closed course with continuous position and tangent. Curvature and banking jump
at segment boundaries; no transition spirals or banking ramps are represented.

Nominal lengths and 9°12′ (9.2°) corner banking are described by
[INDYCAR, The Setup: Indianapolis 500](https://www.indycar.com/news/2023/05/05-19-setup-indy).
Applying that bank uniformly and using circular arcs are assumptions. This is
not a surveyed racing line or GPS trace. The replay origin is Turn 1 entry,
not the official timing line. Custom Python paths need not be geometrically
closed; the replay exporter rejects those that do not close spatially.

## Consistent banked tire forces

Dry-air density: `rho = p / (287.05 * (T_air + 273.15))`.
Drag: `D = 0.5 rho CdA v²`; downforce magnitude: `L = 0.5 rho ClA v²`.
Downforce is assumed **normal to the road**, drag along the path. For inward
positive bank θ and horizontal curvature magnitude κ, resolve forces into the
road-normal and road-lateral axes:

```
N  = m g cosθ + m v² κ sinθ + L
Fy = m v² κ cosθ − m g sinθ
Fx_remaining = sqrt(max(0, (mu N)² − Fy²))
```

The same N and Fy are used for lateral and longitudinal constraints. At zero
bank this reduces to the flat-road friction circle. No tire load sensitivity,
front/rear allocation or combined-slip tire curves are inferred. Rolling
resistance is `Crr N`; tire grip follows the explicitly assumed temperature law
`mu = mu_ref * max(0.5, 1 + slope * (T_track − T_ref))`.

The lateral-only upper cap, on the high-speed branch, is:

```
v² = m g (sinθ + mu cosθ)
     / [m κ (cosθ − mu sinθ) − 0.5 mu rho ClA]
```

When the denominator is nonpositive, the configured top-speed bound applies.
This does not imply unlimited real-world cornering. The supported regime has
positive normal load and a feasible near-rest state; bank/grip combinations
requiring a minimum-speed solution are rejected. Default IMS inputs and the
viewer parameter ranges stay within this intended regime.

## Drive, drag and braking

```
Fdrive = min(Fdrive_max, P / max(v, 1e-6), Fx_remaining)
a_max = (Fdrive − D − Crr N) / m
b_max = (min(Fbrake_max, Fx_remaining) + D + Crr N) / m
```

`a_max` is signed. The original implementation clamped negative acceleration to
zero, permitting a steady speed even when the tires could not supply the force
needed to offset drag. The correction finds a local **sustainable speed** with
`a_max >= 0`, bounded by the analytical lateral cap and top-speed setting.
The exported historical field `corner_speed_limit_mps` now means this combined
sustainable cap; on straights it is generally power limited. Being at a curve's
cap does not establish that lateral grip is the active constraint.

Restricting every cell to a sustainable cap is deliberately conservative: a
transient vehicle could sometimes enter a corner faster while decelerating.
This model does not solve that optimal-control problem. No throttle or brake
pressure is reconstructed from the net force envelope.

## Periodic discrete solver

1. Divide each constant-geometry segment into equal cells no longer than `ds_m`.
2. Cap each node by both the incoming and outgoing cell's sustainable speed.
3. Sweep forward and backward around the ring. Use an implicit bisection solve
   of `v1² − v0² <= 2 a_max ds` and `v0² − v1² <= 2 b_max ds`.
4. In each cell, use the minimum capacity at the two endpoint speeds and their
   speed midpoint. Both acceleration and braking arrays are indexed by cell i.
5. Repeat until node changes are below the iterative tolerance. Reject iteration
   exhaustion, a force-infeasible final lap or a zero-speed lap.
6. Integrate `dt = 2 ds / (v0 + v1)`, including the final-to-first edge.

Three-point force sampling is a discretisation, not a continuum feasibility
proof. Tests independently sample nine speeds in each cell in a corner-limited
case. Spatial refinement is reported separately in
[engineering results](ENGINEERING_RESULTS.md); the 1e-8 m/s stopping tolerance
only measures iteration change on a fixed mesh.

## Replay kinematics

The JSON contract includes an explicit periodic endpoint at `(s=L, t=T, v=v0)`.
Within each cell, `a=(v1²−v0²)/(2 ds)` and
`s(t)=s0+v0 τ+0.5 a τ²`, `v(t)=v0+a τ`.
Inverse seeking uses `τ=2(s−s0)/(v0+sqrt(v0²+2a(s−s0)))`.
The frontend uses these equations for the car, timeline and graph cursor. It
integrates the same constant-curvature segments for drawing coordinates. Playback
speed changes wall-clock rate only; it does not change the simulated physics.
