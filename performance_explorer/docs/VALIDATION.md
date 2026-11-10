# Verification and Git delivery

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

## Previous audit and delivery record (superseded integration status)

The following records the earlier historical audit/adapter-only delivery. Its
statements that the production UI is historical-only describe that earlier commit.
See the integration results above and `V5_INTEGRATION.md` for current capabilities.

Verified on 2026-11-10 in `/private/tmp/indy500-performance-explorer`, continuing commit `f15a323` on `feat/dual-car-performance-explorer`.

## Executed checks

| Check | Actual outcome |
|---|---|
| `npm test` in Explorer frontend | 43 passed across 6 files; all 11 original tests preserved and passing |
| `npm run build` in Explorer frontend | TypeScript + Vite production build passed |
| Explorer Python export regression suite | 6 passed |
| `export_historical.py --check` | Committed export/audit exactly reproduce from canonical files |
| Root `python3 -m unittest discover -s tests -v` | 33 passed (pipeline and portfolio) |
| `python3 -m unittest discover -s r4/tests -v` | 21 passed |
| V3 `test_v2_immutability.py` | 1 passed |
| Existing V3 frontend `npm test` | 9 passed |
| Browser inspection | 2024 displays 31 retained complete attempts, unknown order labels, recorded totals and discrete boundary markers |
| `git diff --check` | Passed |

Explorer tests/build were repeated after installing its own declared dependencies with a new `package-lock.json`; they do not require the V3 checkout's dependencies. Existing V3 frontend tests used a temporary dependency link in the isolated checkout; that link was removed afterward. No test fixtures were added to the production UI.

Numerical checks cover recorded versus speed-derived duration, official total/lap sums, invalid and duplicate identities, nullable attempt order, partial lap rejection, unequal-lap boundary support, cross-session rejection, delta sign/ties, independent car completion, common-clock seeking, rate/pause/restart and missing data. V5 checks cover the published schema, malformed/unsupported versions, units/configuration, monotonicity, time/speed/acceleration integrals, geometry/segment consistency, interior-cell time/distance round trips, scenario independence, completion, matched-coordinate rejection, and cumulative versus incremental advantage conservation. Actual simulated exports are pinned by upstream commit and SHA-256.

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
| Pinned V5 contract/docs/real test exports | 4 / 4 | Pass |
| All non-Explorer tracked files versus original `f15a323` checkout | 2643 / 2643 | Byte-for-byte unchanged |

The three V3 Phase 4 mismatches are `v3_point_in_time/api/main.py`, `v3_point_in_time/api/models.py`, and `v3_point_in_time/app/replay_service.py`. Each matches the original Explorer commit's bytes; their last changes predate this work (`9aafae6`, FINAL_V3 finalization). This is reported as an existing historical-manifest mismatch; no frozen content was changed to make the check pass. Exact expected/actual hashes are in `audit/frozen_integrity.json`.

V4 was added to main after Explorer's base and is absent from this older worktree. Its 735 entries were verified directly against Git blobs at `fe65ddf73a4de6b9c645de74830c8db7b88d64cb`, the verified target-main commit. No V4 checkout, regeneration or write was performed.

## Git history and safe delivery

Correct repository: `https://github.com/fengzhe-li/indy500-racing-point-in-time-decision-support`.

Remote main was verified with `git ls-remote`, returning `fe65ddf73a4de6b9c645de74830c8db7b88d64cb`. The original Explorer parent `c7797837535ce20e425d1466aba2a4ca43bea375` is an ancestor of that commit. The original feature commit contains only `performance_explorer/` paths; comparison against target main's merge base also contains only those paths. The repositories share the correct Indy 500 history, so no transplant or history rewrite is required.

Only after this verification, `origin` was changed to the correct URL and main fetched. GitHub CLI authentication works with normal network/keychain access outside the restricted sandbox; the earlier reported invalid-token result was not a continuing delivery blocker. Delivery uses an ordinary feature-branch push and PR targeting `main`, with no merge, force-push or destructive cleaning. V5/V6 worktree changes are never staged.

## Integration limitations

- Historical UI remains Day 1 qualifying and `VALID_RETAINED` only. Broader complete-but-not-retained populations are audited, not silently included.
- Canonical sections need an explicit validated boundary mapping before region comparisons can be exposed.
- V5 adapter and comparison engine are ready for actual `v5-replay-1` payloads. UI/service wiring and independent scenario editors are intentionally a subsequent integration step.
- V6 needs an actual published export version, units, signal availability, origin/common-distance validation and completion/failure semantics. Its placeholder rejects input rather than inventing channels.
- The historical V3 Phase 4 manifest mismatch remains outside this module's scope.
