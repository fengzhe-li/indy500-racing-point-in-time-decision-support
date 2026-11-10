# Versioned comparison and integration contracts

`frontend/src/domain/contract.ts` defines the Explorer-owned `ComparisonSeriesV1` (`schemaVersion: 1.0.0`). Each series identifies observed/simulated data kind, provenance, units, geometry classification, time/distance axes and signal availability. Historical and simulation origins must never be treated as interchangeable. V5 begins at assumed Turn 1 entry, not the official historical timing line.

## Historical export 1.1.0

The generated source asset `frontend/src/data/historical-attempts-v1.json` retains the major version; its required schema is now **1.1.0**. `attempt` accepts a positive integer or null. Added fields include recorded `lapTimesS`, `totalSeconds`, timing/speed provenance, result status, source locator and source IDs. Old 1.0.0 data is rejected with an explicit missing/invalid-data state; it is not silently interpreted under the new timing semantics.

The export contains 196 retained complete Day 1 qualifying attempts (2020–2024: 46/50/39/30/31). See `DATA_AUDIT.md` for provenance, exclusions, exact inclusion rules, reconciliation with V5 and regeneration. Source hashes cover all canonical inputs. The original 168-row membership is pinned solely for regression audit.

`toObservedSeries` emits recorded cumulative lap boundaries with **no distance samples**, so continuous time/distance interpolation returns unavailable. Historical replay shows discrete completed-lap markers, not an oval map. The linked cursor displays the last boundary reached by both cars. Chart/button seeking pauses at the later car's corresponding boundary time; it does not suggest both cars crossed at the same instant. No valid mapped sections are exposed by this adapter.

## V5: published `v5-replay-1`

Pinned upstream branch: `feat/v5-lap-time-simulation`, commit `8879c3095cd11215a0d444e5973bc7a37b36342b`.

`contracts/v5-replay-1/` contains the exact published schema and documentation plus source paths/hashes. Two real committed simulation exports are pinned in both `frontend/src/test/fixtures/` and `frontend/src/data/`. Production V5 mode loads the latter, clearly labelled SIMULATED. They are actual assumed-model outputs, never official racing results. Historical mode retains only its original official timing data. No solver or V5 frontend code is imported or edited.

`V5Adapter.adapt(payload: unknown)` validates:

- Version, required/unknown fields, SI units, source provenance, origin and separate vehicle/environment configurations.
- Finite N+1 node arrays, N cell arrays, positive speeds and strictly increasing time/distance.
- Periodic endpoints, track/lap totals, average speed, constant-acceleration time/speed integrals.
- Ordered contiguous segment coverage, segment-time integrals, closed geometry and coordinate samples consistent with the documented arc/straight path.

It returns a `V5Series` with the common series contract plus the validated simulation and independent scenario configuration. Original export objects are cloned. Available signals are labelled SIMULATED. Acceleration/braking constraint labels do not become pedal or brake-pressure telemetry.

The integration helpers in `adapters/v5.ts` are ready to consume **two actual exports**:

```ts
const adapter = new V5Adapter();
const a = adapter.adapt(actualExportA);
const b = adapter.adapt(actualExportB);
const comparison = compareV5(a, b);
const { a: carA, b: carB } = comparison.atTime(elapsedSeconds);
```

`compareV5` requires identical origin, length and assumed track segment definitions. Different sample grids are evaluated on a common distance grid. It returns distance-aligned speed comparison, cumulative B − A time delta, incremental region differences and one common-clock playback function. Each car caps at its own lap duration; playback duration is the slower lap. Negative incremental delta means B gains time in that interval; cumulative delta is the net time gap from origin. Identical runs produce ties. Region evidence describes an interval-time difference, never a causal claim.

`v5AtTime` and `v5TimeAtDistance` use the upstream constant-acceleration cell model and its inverse, not generic linear interpolation. Position follows the same assumed arc/straight geometry. The generic domain interpolation helpers remain explicitly piecewise linear and are not used for V5 kinematics.

## Interactive V5 semantics

The UI consumes this engine for replay, charts, segment selection and insights. Timeline time is shared; each car has its own time-to-distance inverse. Graph seeking anchors A at the selected distance and evaluates B at the same elapsed time. The two chart cursors show independent vehicle distances. Hover adds a separate white inspection cursor/point, does not change playback time, and highlights the matching interval.

`delta_AB(s) = t_B(s) - t_A(s)`: positive means B arrives later. Incremental region advantage is delta at exit minus delta at entry. Summed increments reproduce final lap delta within **1e-9 seconds** in tests (validation of rounded upstream integrals uses **1e-6 seconds/metres**). Track dominance is the percentage of total matched segment length won by interval elapsed time; a segment is tied when absolute delta is below 1e-9 seconds. It is partition-dependent, not instantaneous-speed dominance. Corner/straight totals group published segments by non-null/null radius, and describe numerical model contributions without causal attribution.

Seven editable fields use the published server's bounds: mass 600–1100 kg, drag area 0.6–1.6 m², downforce area 0.5–2.5 m², tire friction 1.1–2.2, power 400000–1100000 W, air temperature 5–45 °C and track temperature 15–65 °C. `POST /api/v5/simulate` receives separate vehicle/environment maps; `GET /api/v5/baseline` restores the service baseline. Other configuration fields come from that baseline. API/imported producer commit is explicitly unverified; bundled files have exact upstream SHA-256 provenance. Any returned payload passes the same numerical validator. A failed request leaves both valid configurations intact. Per-car request generations and abort controllers prevent stale success/error overwrites, including mode unmount, preset selection and file import.

## V6: actual published schema 2

Pinned PR #4 commit: `71128258e809b1a34906d0e2a39754db473f7996`. `contracts/v6-replay-2/SOURCE.json` pins original baseline, conservative, delay-0.6s failure and initial-offset +8m zero-duration failure exports plus upstream documentation. These fixtures are used only in tests, never shown as official results or bundled into the V5 UI. The old speculative boundary interface has been removed.

`V6Adapter` validates schema 2, SIMULATED label, SI metadata, the known audited model coordinate semantics, approximate stadium dimensions, unique aligned fields, finite numeric samples, boolean flags, strictly increasing timestamps starting at zero, terminal metrics and matching event position/time/status. Unknown versions/models/coordinate descriptions fail explicitly. Core time/pose/speed/off-track fields are required. Known optional controls, progress, yaw rate and tracking error stay absent when not exported; unknown numeric channels are validated but ignored with a provenance note rather than assigned invented meaning or units.

The published coordinate convention is a local Cartesian CCW stadium starting at (0,0), along +x; signed unwrapped `progress_m` tracks reference progress. `track_distance_m` is wrapped, not travelled trajectory distance. `compareV6` requires identical validated geometry and coordinates. Distance comparison additionally requires both runs to begin at reference progress and wrapped distance zero, strictly increasing progress, and wrapped/unwrapped coordinate consistency (1e-6 m). Nonmonotonic/absent progress or zero-duration runs can still replay on a shared clock, but their distance comparison is unavailable. The common interval ends at the earlier recorded progress, capped to one course length. No extrapolation past a failed run or V5/V6 cross-course comparison is allowed.

`v6AtTime` interpolates recorded position, unwrapped heading and numeric state channels linearly, holding actuator commands, flags, wrapped distance and target speed at the left sample as documented upstream. Endpoint queries return actual terminal samples. `complete` requires both the terminal time and `status=completed`; off-track, timeout, unstable and numerical-error statuses retain their true reason and endpoint. One-row initial off-track exports are valid. Arrival-time delta over valid progress uses linear interpolation of the reduced recorded samples, not V5 constant-acceleration kinematics.

Sampling retains first/last rows and flag transitions; non-flag extrema between display rows can be absent. Full-resolution metrics must not be reconstructed from reduced rows. V6 UI/control panels remain a later integration step; the adapter, actual-pose common-clock replay and restricted same-course comparisons are tested here with no simulator imports.
