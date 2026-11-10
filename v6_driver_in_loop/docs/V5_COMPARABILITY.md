# V5/V6 baseline compatibility review

Snapshot: V5 commit `18b8623` (read-only), committed `output/baseline.json`,
`model.py`, `docs/ENGINEERING_RESULTS.md`; V6.1 generated metadata/telemetry in
`../reports`. These V5 observations describe that snapshot, not its evolving branch.
No V5 code was imported, executed or modified for this comparison.

| Quantity / units | V5 reported baseline | V6 baseline | Mapping / limitation |
| --- | --- | --- | --- |
| Lap time s | 38.9874525 | 72.4099967 (old V6: 72.05) | Different path, model and operating objective |
| Reference length m | 4023.36 | 4527.95164375 | V6 12.54% longer; do not just rescale time |
| Geometry | 4×402.336 m arcs, 2×1005.84 m mains, 2×201.168 m chutes | 2×1000 m straights, 2 semicircles | No common centreline |
| Radius m / curvature 1/m | 256 / 0.00390625 | 402.336 / 0.00248549 | Different lateral acceleration demand |
| Banking | 9.2 degrees assumed | 0 rad; nonzero rejected | Degree/radian conversion and force-balance mismatch |
| Mass kg | `mass_kg` 800 | `mass_kg` 850 | Direct SI mapping, different values |
| Wheelbase m / inertia kg m² | absent | 3 / 1200 | V5 point mass has no yaw dynamics |
| Drag area m² | `cd_a_m2` 1.0 | `drag_coefficient_area_m2` 1.2 | Same area-product meaning |
| Downforce area m² | `cl_a_m2` 1.5 | `downforce_coefficient_area_m2` 3.0 | Same area-product meaning; V6 static axle split |
| Air density kg/m³ | 1.18392515 | 1.225 | Ideal-air environmental vs fixed illustrative value |
| Friction coefficient | `tire_mu` 1.8 at reference temperature | `friction_coefficient` 1.5 | V5 temperature sensitivity unsupported in V6 |
| Cornering stiffness N/rad | absent | front/rear 90000/100000 | Cannot derive from a friction scalar |
| Propulsion | min(12000 N, 820816.877 W / speed, available tyre force) | rear throttle×9000 N, axle circle | V6 has no power cap; 9000×v is variable effective power |
| Braking force N | 20000 maximum | 18000, split 55% front | V5 aggregate vs V6 axle capacity |
| Rolling coefficient | 0.015 | 0.015 | V6 smooths at low speed |
| Speed objective m/s | fastest quasi-steady periodic feasible envelope, cap 120 | target 75 straight / 63.430 corner, aggression 1 | Driver targets restrict speed below force envelope |
| Initialization | periodic speed profile / flying lap | initial 30 m/s, straight at s=0 | V6 includes startup acceleration |
| Speed output | reported curves ~99.76 m/s, peak ~109.770 m/s; mean 103.196 m/s | see measured distribution below | Both SIMULATED, not ECU measurements |
| Tracking error | absent, prescribed path | max 5.18681 m, RMS 2.76899 m | V6 path length differs from reference |

V5 total integrated heading from four stated arcs is 4×402.336/256=6.2865 rad,
not exactly 2π. Its distance sum is closed as a ring, but that alone does not
specify a geometrically closed lane. Reference coordinates, heading closure,
width and a consistent lane geometry are still needed for a V6 adapter.

The corrected V6 speed min/time-weighted mean/max is 30.000 / 62.842 / 70.441 m/s.
Its telemetry contains a 30 m/s launch, closed-loop speed droop and
corner transients; see `reports/robustness.csv` for min/time-weighted mean/max speed
and full-resolution `baseline_telemetry.csv`. V6 aggression multiplies both straight
and corner target speeds. V5's effective power scalar was fitted on historical
aggregate speeds; V6 parameters have no such calibration. These differences explain
why direct numeric agreement is neither expected nor a useful acceptance criterion.
No parameter was fitted to make V6 reproduce the V5 lap time.

Missing conditions: agreed surveyed or explicitly shared approximate centreline;
consistent bank treatment; matching aero/grip/propulsion assumptions; V6-specific
axle/inertia/stiffness provenance; equivalent periodic initial state or discarded
warm-up laps; comparable target objective; independent refinement and uncertainty
bounds. Until then, compare software contracts and assumptions rather than ranking
accuracy from the two lap times.
