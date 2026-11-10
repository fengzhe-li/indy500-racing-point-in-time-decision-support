# Verification and Git delivery

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
