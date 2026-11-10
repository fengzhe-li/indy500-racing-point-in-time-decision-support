# Release-ready V5 integration

## Identity and scope

Integration base: Explorer PR #5 refreshed onto merged `main` (`de49616eda74224e1f07475c24e40eb6b9486f58`) in `fengzhe-li/indy500-racing-point-in-time-decision-support`, after sequential merges of C++17 PR #3 (`2ac5b9615095f440560d809986d608e36c989962`), V5 PR #2 (`aeb67fc28488974e6ec1c11cf30ab2f5bbb8ff4f`), and V6 PR #4 (`de49616eda74224e1f07475c24e40eb6b9486f58`). No solver port or V5 viewer copy is involved.

Producer: accepted V5 `8879c3095cd11215a0d444e5973bc7a37b36342b` (merged to `main` via PR #2).
The exact schema, upstream replay notes, downstream adapter guide and two real
exports are pinned by SHA-256 in `contracts/v5-replay-1/SOURCE.json` and match the merged `v5_lap_time_simulation/` files on `main` byte-for-byte.
The frozen `v5-replay-1` schema and the Explorer `ComparisonSeriesV1` 1.0.0
contract are unchanged. No V5 scientific calculation or calibration is altered.

Existing historical discrepancies were audited before integration. The export
still contains 196 retained complete attempts (46/50/39/30/31 by year), including
28 restored unknown-order 2024 records. V5's 260 complete records use a different
status policy. Both canonical timing files match accepted V5 byte-for-byte.
See [the historical audit](DATA_AUDIT.md); no historical observations were changed.

## Use

```sh
cd performance_explorer/frontend
npm ci
npm test
npm run build
npm run dev
```

Open the displayed Vite URL (default port 5174), then choose **V5 simulation ·
SIMULATED**. Select A and B independently: either accepted baseline, grip −25%,
or an imported JSON export. Identical selections are supported. Imports are local,
validated and hashed; their producer commit is explicitly unverified. Files above
10 MiB are rejected. Failed reads/validation preserve the last valid run; newer
selections invalidate pending imports. Imports are session-only, not persisted.

This integration now also has independent scenario forms using the existing V5 API.
Bundled and imported JSON work without a service. Recompute requires the separate
V5 service; see [setup instructions](../README.md#connect-the-v5-api). Applied output
snapshots remain distinct from editable drafts. No solver is duplicated.

Play/pause, restart, rate (0.5/1/2/4/10×) and timeline use Explorer's existing
`tickReplay` clock. Each car uses its own constant-acceleration cell mapping;
playback stops at the slower lap. A completed car clamps at its own `(L,T)`.
The endpoint's simulated speed remains a profile value, not a stopped-car state.

Both graphs support click/drag, arrows (25 m) and Home/End seeking. Seeking a
distance places **A** at that distance and uses A's arrival time for the shared
clock. B is therefore generally elsewhere. The solid and dashed cursors show A
and B distance. Segment row selection seeks the entry; hover/focus highlights the
corresponding track piece. The diagram integrates the assumed constant-curvature
segments with uniform coordinate scaling and y inversion for the screen.

## Comparison definitions

- Require identical origin, track length, ordered segment names, boundaries,
  radius and banking. Validate units, closed sampled geometry, array dimensions,
  finite values, periodicity, caps, monotonicity and kinematic/segment integrals.
  Incompatible pairs disable replay/comparison; they are never silently shifted.
- Sample both speed profiles on the union of their distance grids and segment
  starts. Different meshes are supported. `v(s)` and `t(s)` use the published cell
  equations; graph lines between samples are a drawing approximation.
- Running delta: `t_B(s) − t_A(s)` in seconds, evaluated at A's current distance.
  Positive means B takes longer to reach the same point; negative means B is faster.
  This is not an instantaneous time gap between differently positioned markers.
- Incremental segment delta: the difference between the running delta at segment
  exit and entry. These signed contributions sum to the full-lap delta.
- **Track Dominance**: percentage of total matched segment length assigned to A,
  B or tie according to the smaller segment time. Tie threshold is absolute delta
  below `1e-9 s`. It is partition-dependent, not pointwise speed superiority.
- Values describe outputs of assumed-model scenarios, not causal estimates or
  real-driver corner advantages. Source/input blocks remain visible for both cars.

## Numerical example from the accepted exports

| Metric | Actual calculated value |
|---|---:|
| A baseline lap | 38.987452538 s |
| B grip −25% lap | 40.963471675 s |
| B − A full lap | +1.976019137 s |
| Track length | 4023.360 m |
| A segment-length dominance | 100% |
| B / tied segment-length dominance | 0% / 0% |

The UI shows each segment's A/B time and incremental delta, equal-distance speed
difference in m/s, elapsed time in s and path distance in m. It retains assumed
geometry/vehicle/environment provenance and the calibrated effective-power label.
The 2024 comparison remains retrospective descriptive evidence with **no
demonstrated aggregate MAE improvement over the training-median baseline**.

## V6 integration requirements

The published V6 schema-2 adapter is now tested against exact PR #4 exports,
including failure and zero-duration termination. Its UI remains disconnected.
See [the current contract](DATA_CONTRACT.md#v6-actual-published-schema-2) for
signal availability, same-course comparison and distance-coverage restrictions.
No V5/V6 source is imported or modified.

See [verification](VALIDATION.md) for actual test results and the known historical
V3 manifest discrepancies.
