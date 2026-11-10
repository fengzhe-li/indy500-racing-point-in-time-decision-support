# Versioned comparison and integration contracts

`frontend/src/domain/contract.ts` defines the Explorer-owned `ComparisonSeriesV1` (`schemaVersion: 1.0.0`). Each series identifies observed/simulated data kind, provenance, units, geometry classification, time/distance axes and signal availability. Historical and simulation origins must never be treated as interchangeable. V5 begins at assumed Turn 1 entry, not the official historical timing line.

## Historical export 1.1.0

The generated source asset `frontend/src/data/historical-attempts-v1.json` retains the major version; its required schema is now **1.1.0**. `attempt` accepts a positive integer or null. Added fields include recorded `lapTimesS`, `totalSeconds`, timing/speed provenance, result status, source locator and source IDs. Old 1.0.0 data is rejected with an explicit missing/invalid-data state; it is not silently interpreted under the new timing semantics.

The export contains 196 retained complete Day 1 qualifying attempts (2020–2024: 46/50/39/30/31). See `DATA_AUDIT.md` for provenance, exclusions, exact inclusion rules, reconciliation with V5 and regeneration. Source hashes cover all canonical inputs. The original 168-row membership is pinned solely for regression audit.

`toObservedSeries` emits recorded cumulative lap boundaries with **no distance samples**, so continuous time/distance interpolation returns unavailable. Historical replay shows discrete completed-lap markers, not an oval map. The linked cursor displays the last boundary reached by both cars. Chart/button seeking pauses at the later car's corresponding boundary time; it does not suggest both cars crossed at the same instant. No valid mapped sections are exposed by this adapter.

## V5: published `v5-replay-1`

Pinned upstream branch: `feat/v5-lap-time-simulation`, commit `8879c3095cd11215a0d444e5973bc7a37b36342b`.

`contracts/v5-replay-1/` contains the exact published schema and documentation plus source paths/hashes. Two real committed simulation exports are pinned in `frontend/src/test/fixtures/` for regression testing and in `frontend/src/data/` for the separate SIMULATED production mode. They are actual assumed-model simulations, never official racing results. The historical mode never interprets them as observations. No solver or V5 frontend code is imported or edited.

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

The Explorer now connects this adapter to independent A/B export selection and local JSON imports, common-clock replay and linked comparison graphs. Read-only input snapshots preserve each scenario. New parameter configurations are produced by V5 and imported, not recalculated in Explorer. See `V5_INTEGRATION.md` for seeking and Track Dominance definitions. The Explorer does not launch or depend on the V5 server. Actual contract version changes must be reviewed and versioned; unsupported versions fail explicitly.

## V6: isolated future boundary

`V6IntegrationBoundaryV1` (`explorerBoundaryVersion: v6-boundary-1`) is an **Explorer requirement**, not an invented V6 export format. Its future producer mapping must supply upstream version, units, origin, source provenance and completion/partial/failure status. Time is required. Position, heading, velocity, steering, throttle, braking, yaw rate, tracking error and track distance are optional and may be populated only from actual exported channels.

Distance comparison additionally requires a validated common coordinate ID and supporting evidence. Absent channels remain absent and charts must show unavailable. Partial/failed runs must retain their endpoint and failure reason; no successful completion, extension or trajectory extrapolation may be fabricated. Actual validation awaits the published V6 schema and exports. `V6Adapter` currently rejects payloads with a clear integration requirement; it imports no V6 source.
