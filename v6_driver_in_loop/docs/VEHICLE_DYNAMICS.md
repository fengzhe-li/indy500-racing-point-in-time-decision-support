# Vehicle dynamics and fidelity

`vehicle.py` implements a planar dynamic bicycle with body x forward, y left,
positive steering/heading/yaw counterclockwise. World x/y are local east/north,
angles radians. Time seconds, distances metres, mass kg, force N, inertia kg m²,
cornering stiffness N/rad, aero coefficient-area products m². Defaults remain
illustrative: 850 kg, L=3 m, lf=1.35 m, lr=1.65 m, Iz=1200 kg m²,
Cf/Cr=90/100 kN/rad, μ=1.5, CdA=1.2 m², ClA=3 m², rho=1.225 kg/m³.
No confidential or measured IndyCar parameter is implied.

## Governing equations

For front wheel-frame speed uf = u cosδ + (v+lf r) sinδ and
vf = −u sinδ + (v+lf r) cosδ:

```
αf = −atan2(vf, max(|uf|, u_epsilon))
αr = −atan2(v−lr*r, max(u, u_epsilon))
Fy_f_requested = Cf*αf; Fy_r_requested = Cr*αr
q = rho*(u²+v²)/2
D = q*CdA; downforce = q*ClA
Fzf = (mg + downforce)*lr/L; Fzr = (mg + downforce)*lf/L
```

Drive is a constant-force, rear-drive assumption: throttle × 9000 N, no power or
gear ceiling. Brake demand = brake × 18000 N × tanh(u/0.2), split 55% front.
For each axle i, scale both requested tyre components by
`min(1, μFzi / hypot(Fxi,Fyi))`. This enforces a circular combined-force envelope
and preserves demand direction; it is not a measured slip-ratio/combined-slip law.

Rotate the front tyre force into body axes:
`Fxf_body=Fxf*cosδ−Fyf*sinδ`, `Fyf_body=Fxf*sinδ+Fyf*cosδ`.
Subtract the drag vector `D*(u,v)/hypot(u,v)` (zero at rest); subtract longitudinal
rolling opposition `Crr*mg*tanh(u/0.2)` after tyre limiting. Aero acts at the CG;
only tyre forces contribute to yaw moment in this simplified model.

```
x_dot   = u*cosψ − v*sinψ
y_dot   = u*sinψ + v*cosψ
ψ_dot   = r
u_dot   = Fx_body/m + v*r
v_dot   = Fy_body/m − u*r
r_dot   = (lf*Fyf_body − lr*Fyr)/Iz
path_distance_dot = hypot(u,v)
ax_body = u_dot − v*r = Fx_body/m
ay_body = v_dot + u*r = Fy_body/m
```

Zero wind is assumed. The vector drag choice is an isotropic simplification and
is not a calibrated yaw-dependent aero map. Flat-road downforce is split by the
static axle fractions. Nonzero banking is rejected because a banked force balance
is unsupported.

## Integration and low speeds

Held commands, classical RK4; configurable external dt in (0,0.05] s. Internal
substeps have h≤min(0.02 s, 0.25*tau), with tau the smaller of
`m*U/(Cf+Cr)` and `Iz*U/(Cf*lf²+Cr*lr²)`, U=max(u,2 m/s).
Substep count is deterministic; configurations needing >1000 substeps are rejected.
This damping-based heuristic improves low-speed explicit integration stability;
it is not a general nonlinear stability proof. External dt also sets the driver
sample period. Tests compare smooth held-command dynamics and full sampled loops.

Slip denominator floor u_epsilon=2 m/s only regularizes slip calculations. Wheel
lateral velocity supplies the numerator, so steering a stationary vehicle does
not generate artificial force. World motion and q use actual velocities. Reverse
travel is outside scope: accepted u is projected to nonnegative and du is prevented
from driving u negative at rest. This unilateral stop treatment is approximate;
parking, reversing, wheel lock and contact stiction are not validated. Brake/rolling
force smoothing avoids artificial reversal at rest. Finite states are checked at
accepted substeps; invalid arithmetic terminates explicitly or rejects invalid input.

## Geometry and events

Default stadium length is **4527.951643749406 m**, from two 1000 m straights and
two radius 402.336 m semicircles. It is deliberately retained for reproducibility;
it is not a 2.5 mile IMS geometry. Its curvature has step discontinuities.
Exact analytic projection supplies signed lateral error, and minimum Euclidean
distance supplies the boundary check. The CG must remain within 7.5 m of centreline;
no car body width is accounted for. Start reference is the actual initial projection.
Signed net progress must reach the requested whole-lap distance, preventing false
laps from an initial near-finish wrap or reverse crossing.

The first boundary/finish crossing detected between step endpoints is localized
by re-integrating the held command and bisecting time to ≤1 ns. Reported event
precision is not physical accuracy. A path that crosses and returns within one
step may be missed; the sampled study does not establish continuous containment.
Unstable limits remain |v|>100 m/s or |r|>10 rad/s and are checked at control steps.
No claim is made that these broad diagnostic bounds certify real vehicle stability.

## Limits

No suspension, transient load transfer, tyre relaxation, load sensitivity, thermal
state/wear, detailed powertrain, wheel speeds, wind field, track banking or driver
identification. Axle forces are linear in slip before clipping and unreliable at
large slip. Current validation is analytical/software consistency plus sensitivity
checks, not manufacturer or track validation. See [audit](PHYSICS_AUDIT.md).
