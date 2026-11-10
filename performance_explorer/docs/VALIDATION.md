# Verification and Git delivery

Verified on 2026-11-10 against merged `main` (`de49616eda74224e1f07475c24e40eb6b9486f58`, containing C++17 PR #3 `2ac5b9615095f440560d809986d608e36c989962`, V5 PR #2 `aeb67fc28488974e6ec1c11cf30ab2f5bbb8ff4f`, and V6 PR #4 `de49616eda74224e1f07475c24e40eb6b9486f58`) on branch `feat/dual-car-performance-explorer` (PR #5).

## Final audit fixes and dependency remediation

- **High-density V5 graph rendering (`src/V5Explorer.tsx`)**: Replaced spread `Math.min(...values)` and `Math.max(...values)` in `DistanceGraph` with a linear scan over `points` and `second`, preventing `RangeError: Maximum call stack size exceeded` on valid high-density V5 replay imports (verified with a 73,441-node / 7.7 MiB replay in unit tests and Chrome).
- **V6 completed-run lap-distance consistency (`src/adapters/v6.ts`)**: Added validation requiring runs with `metrics.status === "completed"` and `metrics.completed_lap === true` to reach at least `max_laps * track.length_m - 1e-6` on `terminal.progress_m` (and final sample `progress_m` when present).
- **Frontend dependency advisories (`frontend/package.json`, `frontend/package-lock.json`)**: Upgraded devDependencies (`vite` to `6.4.6`, `vitest` to `4.1.12`, `@vitejs/plugin-react` to `4.7.0`). `npm audit` reports **0 vulnerabilities** across all dependencies while preserving Node 20 compatibility.
- **Dedicated Explorer CI workflow (`.github/workflows/explorer.yml`)**: Added `performance-explorer-ci` covering Explorer historical exporter unit tests, `export_historical.py --check` reproducibility, `npm ci`, `npx tsc -b`, `npm test`, and `npm run build`.

## Executed checks

| Check | Actual outcome |
|---|---|
| `npm test` in Explorer frontend | 95 passed across 8 files; all 11 original tests preserved and passing |
| `npx tsc -b && npm run build` in Explorer frontend | TypeScript + Vite production build passed |
| `npm audit` in Explorer frontend | 0 vulnerabilities (0 critical, 0 high, 0 moderate, 0 low) |
| Explorer Python export regression suite | 6 passed |
| `export_historical.py --check` | Committed export/audit exactly reproduce from canonical files |
| Root `python3 -m unittest discover -s tests -v` | 33 passed (pipeline and portfolio) |
| `python3 -m unittest discover -s r4/tests -v` | 21 passed |
| C++17 `ctest --test-dir cpp/build --output-on-failure` | 16 passed |
| V3 `python3 -m unittest discover -s v3_point_in_time/tests -v` | 104 passed (including C++ parity and V2 immutability) |
| Existing V3 frontend `npm test` + `npm run build` | 9 passed + build passed |
| V5 `python3 -m unittest discover -s v5_lap_time_simulation/tests -v` | 25 passed |
| V5 frontend `npm test` + `npm run build` | 21 passed (2 files) + build passed |
| V6 `python3 -m unittest discover -s v6_vehicle_dynamics_control/tests -v` | 44 passed |
| V6 viewer `node --test v6_vehicle_dynamics_control/viewer/test/*.test.mjs` | 9 passed |
| Browser inspection (Chrome + merged V5 API) | 2024 displays 31 retained complete attempts; V5 presets, Track Dominance, live POST recompute, and 73,441-node JSON import verified with 0 console/page errors |
| `git diff --check` | Passed |

Explorer tests/build were repeated after installing its own declared dependencies with the updated `package-lock.json`; they do not require the V3 or V5 checkouts' frontend dependencies. V5 production mode uses two actual published exports pinned separately from test fixtures and connects to the merged `v5_lap_time_simulation.server` FastAPI service on `127.0.0.1:8005` via `/api/v5`; V6 fixtures are test-only.

Numerical checks cover recorded versus speed-derived duration, official total/lap sums, invalid and duplicate identities, nullable attempt order, partial lap rejection, unequal-lap boundary support, cross-session rejection, delta sign/ties, independent car completion, common-clock seeking, rate/pause/restart and missing data. V5 checks cover the published schema, malformed/unsupported versions, units/configuration, monotonicity, time/speed/acceleration integrals, geometry/segment consistency, interior-cell time/distance round trips, scenario independence, completion, matched-coordinate rejection, high-density replay rendering, and cumulative versus incremental advantage conservation. Actual simulated exports are pinned by upstream commit and SHA-256.

## Frozen asset audit: actual outcomes

`python3 performance_explorer/scripts/check_integrity.py` deliberately exits **1** because the older V3 Phase 4 manifest contains three pre-existing source-code hash discrepancies. It does not rewrite manifests or classify that check as passing.

| Manifest/scope | Matched / checked | Result |
|---|---:|---|
| V2 final manifest | 13 / 13 | Pass |
| V2 pre-implementation dependency hashes | 32 / 32 | Pass |
| V3 Phase 2 | 7 / 7 | Pass |
| V3 Phase 3 | 12 / 12 | Pass |
| V3 Phase 4 | 4 / 7 | Three pre-existing code differences |
| V4 final manifest at verified target main | 735 / 735 | Pass |
| Pinned V5 contract/docs/actual exports | 7 / 7 | Pass |
| Pinned V6 docs/actual test exports | 6 / 6 | Pass |
| All non-Explorer tracked files versus merged `main` (`de49616`) | 3509 / 3509 | Byte-for-byte unchanged |

The three V3 Phase 4 mismatches are `v3_point_in_time/api/main.py`, `v3_point_in_time/api/models.py`, and `v3_point_in_time/app/replay_service.py`. Each matches the original Explorer commit's bytes; their last changes predate this work (`9aafae6`, FINAL_V3 finalization). This is reported as an existing historical-manifest mismatch; no frozen content was changed to make the check pass. Exact expected/actual hashes are in `audit/frozen_integrity.json`.

V4 was added to main after Explorer's base and is absent from this older worktree. Its 735 entries were verified directly against Git blobs at `fe65ddf73a4de6b9c645de74830c8db7b88d64cb`, the verified target-main commit. No V4 checkout, regeneration or write was performed.

## Git history and safe delivery

Correct repository: `https://github.com/fengzhe-li/indy500-racing-point-in-time-decision-support`.

Remote main was verified with `git ls-remote`, returning `fe65ddf73a4de6b9c645de74830c8db7b88d64cb`. The original Explorer parent `c7797837535ce20e425d1466aba2a4ca43bea375` is an ancestor of that commit. The original feature commit contains only `performance_explorer/` paths; comparison against target main's merge base also contains only those paths. The repositories share the correct Indy 500 history, so no transplant or history rewrite is required.

Only after this verification, `origin` was changed to the correct URL and main fetched. GitHub CLI authentication works with normal network/keychain access outside the restricted sandbox; the earlier reported invalid-token result was not a continuing delivery blocker. Delivery uses an ordinary feature-branch push and PR targeting `main`, with no merge, force-push or destructive cleaning. V5/V6 worktree changes are never staged.

## Integration limitations

- Historical UI remains Day 1 qualifying and `VALID_RETAINED` only. Broader complete-but-not-retained populations are audited, not silently included.
- Canonical sections need an explicit validated boundary mapping before region comparisons can be exposed.
- V5 UI, file imports and API client are implemented. Runtime recomputation needs the separate V5 service from PR #2 (or a compatible deployed service); static exports need no backend. Production hosting must route `/api/v5` to it.
- V6 schema-2 adapter and same-course comparison are tested against real PR #4 exports. V6 UI is intentionally not connected. Failed runs truncate comparison coverage; absent/nonmonotonic progress disables distance comparison.
- The historical V3 Phase 4 manifest mismatch remains outside this module's scope.

## Interactive V1 browser smoke (2026-11-10)

The API ran in an isolated detached worktree at verified V5 `8879c30`, on 127.0.0.1:8007; Explorer at 127.0.0.1:5175 proxied `/api/v5` there. Other existing services on ports 8005/5174 were left untouched. No V5 source or combined integration history was created.

- Actual browser submissions: A mass 900 kg returned 39.0331526207 s; independently B tire friction 1.5 returned 38.9874525382 s. Both POST requests returned HTTP 200. Applied input snapshots and separate API scenario selections updated.
- At shared time ~0.4014 s with 2× playback, A/B progressed independently (~41.32/~41.37 m). Pause and graph keyboard seeking updated linked cursors without forcing equal vehicle distances.
- Published baseline vs low-grip: seeking A to its finish at 38.9874525382 s left A at 4023.36 m (complete), B at 3821.50 m (in progress). The slower endpoint is 40.9634716751 s.
- Back-straight selection sought A to 1005.84 m, B to 937.91 m on the common 9.7578508582 s clock. Selected interval insight: A gains 0.2789 s; full-lap delta +1.9760 s. Corner contributions +1.1848 s and straight contributions +0.7912 s sum to it.
- Stopping only the isolated API produced a visible HTTP 500 connection error from the proxy, retaining the valid runs and replay. Restarting the service and loading its baseline recovered successfully.
- Mode switching preserved observed historical timing and the 31 retained 2024 attempts; simulation markers/channels do not enter historical replay.

Automated UI tests cover independent drafts/submissions, successful API loads, validation/network/schema failures, stale success and error responses, selection/unmount cancellation, graph hover/pointer/keyboard seeking, replay rates, independent completion, import failures and provenance labels. V6 tests cover real completed/failed/zero-duration samples, held controls, unwrapped heading, missing/unknown channels, incompatible geometry, terminal event consistency, restricted progress comparisons and delta conservation.

## Concurrent export-only integration record (e2d8319)

The record below is retained from the concurrent same-branch delivery. Its export-only/API/V6 scope describes that earlier commit; current functionality and tests are documented above. Its additional regression and dependency findings are preserved.

## Accepted V5 integration — 2026-11-10

Base Explorer commit `164588128c9910463a7cbaa6c5e62defae6540e4`;
accepted producer `8879c3095cd11215a0d444e5973bc7a37b36342b`.
Verified repository/remote main and historical audit before implementation.
The final isolated checkout is `/private/tmp/indy500-explorer-v5-integration`.
Concurrent API/V6 edits appeared in the original Explorer worktree during work;
that worktree was left untouched after isolation. Only this V5 export integration
is included in this delivery; no V6 files or proxy edits are staged.

### Actual executed results

| Check | Passed | Failed | Skipped |
|---|---:|---:|---:|
| Explorer frontend (7 files) | 61 | 0 | 0 |
| Explorer Python historical export | 6 | 0 | 0 |
| Repository Python | 33 | 0 | 0 |
| R4 Python | 21 | 0 | 0 |
| V3 Python | 92 | 0 | 0 |
| TypeScript/Vite production build | 1 | 0 | 0 |
| Historical export/audit regeneration check | 1 | 0 | 0 |
| V3 smoke checks | 10 | 0 | 0 |
| V3/V2 behavioral regression | 5 horizons | 0 | 0 |
| Portfolio integrity | 1 | 0 | 0 |
| Pinned V5 artifacts | 7 | 0 | 0 |

All suites above were rerun in the isolated checkout. The 18 added frontend
cases cover independent selections, import failures/stale completion, incompatible
origins, common-clock rates and completion, graph dragging/keyboard seeking,
track synchronization, delta signs, segment dominance and different sample meshes.
The original 43 tests still pass. No unit tests were skipped.

`check_integrity.py` still exits **1**, accurately reporting the **three existing
V3 Phase 4 source-hash mismatches** detailed below. V2 final/pre-implementation
(13/13 and 32/32), V3 phases 2/3 (7/7 and 12/12), V4 at verified target main
(735/735), and all seven pinned V5 artifacts match. All **2643 non-Explorer
tracked files** match the original Explorer commit. No frozen manifest was
rewritten to conceal the discrepancies. The report change only updates the count
of pinned V5 files from four to seven.

The schema, both canonical timing inputs and both shipped V5 replay outputs match
the accepted producer commit byte-for-byte. No new historical fit, physics
regeneration or model change is part of this integration.

Browser verification: independent preset selection and real local JSON import,
shared playback/pause, keyboard seeking, A-finished/B-running state, track
selection, and desktop/mobile layout at 1440 and 375 px. Both cases use actual
V5 outputs. No horizontal page overflow at the mobile width. Temporary viewport
settings were restored. Automated import tests mock digest completion; the live
browser additionally exercised real SHA-256 and file import. This is not a formal
accessibility certification or a full browser compatibility matrix.

Dependencies retain the existing lockfile. `npm ci` reported six dependency
advisories (3 moderate, 1 high, 2 critical); dependency upgrades/security remediation
were not performed here. The local development server binds to loopback.

Remote workflow results, when available, are recorded in the PR delivery update.
Local passes do not imply GitHub Actions passed. The pre-existing workflows run
V3 and portfolio checks; they do not run the new Explorer frontend suite.

### Commands

```sh
npm ci --prefix performance_explorer/frontend
npm test --prefix performance_explorer/frontend
npm run build --prefix performance_explorer/frontend
python3 performance_explorer/scripts/export_historical.py --check
python3 -m unittest discover -s performance_explorer/tests -v
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s r4/tests -v
python3 -m unittest discover -s v3_point_in_time/tests -v
python3 performance_explorer/scripts/check_integrity.py # expected existing exit 1
python3 v3_point_in_time/scripts/run_v3_v2_behavioral_regression.py
python3 v3_point_in_time/scripts/smoke_test.py
python3 scripts/validate_portfolio.py
```
