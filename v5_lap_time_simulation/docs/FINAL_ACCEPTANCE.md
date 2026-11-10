# V5 final engineering acceptance and release candidate

Review date: **2026-11-10**. Decision: **RELEASE READY** for the bounded V5 engineering scope.

## 1. Repository and commit identity

- Repository: [fengzhe-li/indy500-racing-point-in-time-decision-support](https://github.com/fengzhe-li/indy500-racing-point-in-time-decision-support).
- Branch: `feat/v5-lap-time-simulation`; PR [#2](https://github.com/fengzhe-li/indy500-racing-point-in-time-decision-support/pull/2), base `main`.
- Starting head, verified locally and through GitHub: `81674ea7d27e1a0f7305c215da8b4c049c8fbbfe`.
- Audited executable-code candidate after acceptance corrections: **`1ef2ee81a8f9aa7875ff132fd8ccf6b57e822e8b`**.
- This report and its README links are a subsequent documentation-only delivery. Resolve its containing commit with `git log -1 --format=%H -- v5_lap_time_simulation/docs/FINAL_ACCEPTANCE.md`; the exact delivery head and its live checks are recorded in PR #2.
- Initial tracked working tree was clean. Only untracked `v6_driver_in_loop/` was present. It was not opened, edited or staged; no C++ work was imported or modified.
- The local `origin` retains the older repository-name URL. The audit and pushes used the explicit repository above; remote configuration was not changed.
- PR was OPEN, non-draft and MERGEABLE at initial identity verification. No merge was performed.

This was a fresh source/contract review with independent force calculations,
regression execution and browser interaction. It is not third-party vehicle
certification or an empirical validation of real IndyCar dynamics.

## 2. Physics findings

| Area | Finding |
|---|---|
| IMS order | T1 → short chute 1–2 → T2 → back straight → T3 → short chute 3–4 → T4 → front straight; correct |
| Length and closure | Four 402.336 m arcs, two 201.168 m chutes and two 1005.840 m straights total 4023.360 m. Radius 256.135052735 m gives four 90° turns, closed position and tangent |
| Periodic boundary | Final cell connects to the first node; incoming/outgoing caps both constrain a boundary. Origin-rotation regression passes |
| Banking/tire circle | Consistent `N=mg cosθ + mv²κ sinθ + L` and `Fy=mv²κ cosθ − mg sinθ`; longitudinal capacity uses the same N/Fy |
| Aero and resistance | `D=0.5 rho CdA v²`, road-normal `L=0.5 rho ClA v²`, `Crr N`, ideal dry-air density; units and signs consistent with stated assumptions |
| Drive/braking | Drive bounded by force, P/v and remaining tire capacity; braking includes drag/rolling resistance. No fabricated controls |
| Sustainable speed | Signed available acceleration retained; local caps require enough drive force to offset resistance. Lateral-only cap and top-speed bound applied |
| Propagation | Periodic implicit forward/backward sweeps, conservative cell bounds, explicit force-feasibility postcondition |
| Integration | `dt=2 ds/(v0+v1)`, including wraparound. Replay constant-acceleration interpolation agrees with this integral |
| Invalid inputs | Existing physical/range rejection retained; noninteger iteration limits and nonfinite internal force states now explicitly rejected |

### Negative acceleration and fail-closed behavior

The historical negative-acceleration clamp has not returned. A direct low-power,
120 m/s test produces negative available acceleration. Fault injection of a
negative acceleration bound causes the final force-feasibility check to reject
the lap, rather than silently accepting steady speed.

The acceptance review found that IEEE NaN comparisons could bypass that final
inequality check if an internal force calculation became nonfinite. Injected
NaN/Infinity reproduced this gap. Finite positive caps, finite force bounds and
finite final speed/acceleration states are now explicit requirements. Valid
baseline/scenario calculations are unchanged. This guards the numerical contract;
it does not assert validity for every physically imaginable custom Python input.

An independent parameter-domain audit evaluated all **128 corners** of the seven
editable ranges: mass 600/1100 kg, CdA 0.6/1.6 m², ClA 0.5/2.5 m², μ 1.1/2.2,
power 400000/1100000 W, air 5/45 °C and track 15/65 °C. For every ≤10 m cell,
17 speeds between its endpoints were checked with independently reconstructed
normal, lateral and required longitudinal forces. All cases had positive normal
load and satisfied the friction circle, drive-force, power and brake-force bounds.
Largest floating-point force excess was **3.64e-12 N**, below the stated 1e-3 N
comparison tolerance. This finite audit is not an exhaustive parameter-space proof.

No physics assumptions, fitted objective or 2024 outcomes were optimized during
acceptance. No change to computed numerical outputs was required.

## 3. Numerical verification and reproducibility

The 40, 20, 10, 5, 2.5 and 1.25 m experiments were rerun with fixed fitted inputs.
The finest grid is a finite reference, not an exact solution. All runs used two
iterative passes; their different spatial results demonstrate why stopping
tolerance alone cannot establish discretisation accuracy.

| 10 m vs 1.25 m reference | Baseline | Grip −25% |
|---|---:|---:|
| Lap-time difference / s | 0.000670233 | 0.005680946 |
| Speed-profile RMSE / m/s | 0.014219 | 0.026001 |
| Maximum absolute profile difference / m/s | 0.315171 | 0.352606 |

The profile comparison uses 8001 common distance samples and interpolation of
v². Differences decrease with the tested refinement; local transition errors
remain larger than aggregate lap errors. No universal error bound or formal
asymptotic order is claimed. The ≤10 m viewer remains suitable for this bounded
engineering demonstration, not precision setup optimization.

Unchanged generated expectations:

- Baseline **38.987452538 s**, **230.843500 mph**.
- Effective calibrated scalar **682824.947115 W**.
- Grip −25% **40.963471675 s**, delta **+1.976019137 s**.
- 2024 speed MAE/RMSE **1.142815 / 1.400540 mph**.
- Four-lap time MAE/RMSE **0.769258 / 0.944403 s**.

All **17** JSON/CSV/PNG output files regenerated to a separate directory and
matched committed files **byte-for-byte** on the review machine, including mesh,
calibration, validation and both replay fixtures. Platform-to-platform byte
identity of PNGs is not guaranteed by this observation.

## 4. Viewer acceptance

| Check | Evidence and result |
|---|---|
| Start/pause/restart | Automated state/synchronization tests and live browser interaction passed |
| Lap endpoint and ghost | Explicit endpoint reaches L/T; baseline ghost clamps at its own finish. Scenario playback wraps; single-lap endpoint remains seekable |
| Playback rates | All six offered rates checked by deterministic clock tests; live 10× playback checked |
| Timeline / graph | Click, drag, arrow-key seek and Home/End endpoints passed; marker and graph use the same distance |
| Exact slider values | Fixed native step quantization of calibrated power and the fractional lap endpoint; displayed controls now preserve actual values |
| Valid recomputation | Live 900 kg / μ=1.35 scenario returned 42.3287 s; tests verify submitted input snapshots and returned metrics |
| Invalid API inputs | Range/unknown fields rejected; NaN/Infinity/overflow inputs now return 422 instead of error-response serialization causing 500 |
| Rapid requests | Reproduced two submissions before React flushed busy state; synchronous in-flight guard now permits only one. Controls remain disabled while pending |
| Stale asynchronous work | Initial unmount does not start a second request; generation guard discards late recomputation results. No overlapping UI recomputations can overwrite a newer scenario |
| Reset | All supported vehicle/environment values restored from baseline; zero lap delta and time reset verified |
| API/backend failure | JSON error, non-JSON 503 and network failure tests preserve the last valid replay and allow retry |
| Live unavailable backend | Stopped only this chat's local V5 server: fetch error displayed, car/cursor remained at L. Restart/retry cleared the error and reset time to zero |
| Responsive / keyboard | Visually checked 375, 768 and 1440 px widths; controls wrap without page-width overflow. Labeled controls, arrow seeking, Home/End and focus operation checked |

Only defect-driven changes were made; no layout redesign or major feature was
added. Temporary browser viewport overrides were reset. Mobile plot annotations
are compact; desktop is preferable for quantitative inspection. This is not a
formal WCAG certification or an assistive-technology compatibility matrix.

## 5. Schema stability

`v5-replay-1` remains frozen. Neither `schema.py`, the JSON schema, `replay.py`,
nor the exported replay fixtures changed during acceptance. Python generation
still matches the committed JSON schema. Frontend semantic validation now rejects
wrong units, inconsistent geometry/segment totals, nonfinite summary metadata and
speeds above caps before accepting the replay. Valid v1 files remain compatible.

SHA-256 anchors:

| Artifact | SHA-256 |
|---|---|
| `schema/replay.schema.json` | `db85d20fa99e759b6a0b3eeedc6165b39600eca32e0c32bf7c4cbb6088125d85` |
| `output/replay.json` | `e0394c8255b23c2c969a7c87a696b11829102e68184223dcc7dde872cd778f03` |
| `output/replay_low_grip.json` | `919f3900b90aa7d17b2e24e50a68eb0184e06be9f723128e737e3cb10e21c6e3` |

The concise [downstream adapter contract](EXPLORER_ADAPTER.md) specifies coordinate
frames, node/cell arrays, units, segment boundaries, lap completion, interpolation,
comparison rules, provenance, missing channels and versioning. Validation-error
responses were made serializable; this does not alter the successful replay schema.

## 6. Actual test and integrity results

Local environment: macOS ARM64, Python 3.14.5, Node 26.8.2, npm 11.19.1.
The V5 GitHub workflow independently uses Python 3.12 and Node 20 on Ubuntu.

| Suite/check | Passed | Failed | Skipped |
|---|---:|---:|---:|
| V5 Python | 25 | 0 | 0 |
| V5 frontend | 21 | 0 | 0 |
| Repository Python | 33 | 0 | 0 |
| V3 Python | 92 | 0 | 0 |
| Existing V3 frontend | 9 | 0 | 0 |
| V3 application/scenario smoke | 10 | 0 | 0 |
| V5 / V3 production frontend builds | 2 | 0 | 0 |
| Frozen V2 hash inventory | 32 files | 0 | 0 |
| V3/V2 historical behavioral regression | 5 horizons | 0 | 0 |
| Portfolio integrity validator | 1 run | 0 | 0 |
| Output reproduction | 17 files | 0 | 0 |
| Schema regeneration equivalence | 1 | 0 | 0 |
| Parameter-range endpoint audit | 128 cases | 0 | 0 |

The earlier deliberately failing defect-reproduction tests are not counted as
passing acceptance evidence. They failed before correction and pass now.
No unit tests were skipped. Local Docker rebuilding was **not run**; the actual
remote Docker result is recorded separately below.

A before/after SHA-256 inventory of **3384 tracked non-V5 files** found no changes.
Frozen V2/V3/V4/data trees also compare cleanly to the original V5 commit
`18b8623c01f423f8072996a8ca92ffd2ddc0806e`. This audit did not touch concurrent
untracked work and does not claim that other processes cannot change their files.

### GitHub Actions

All five runs for the audited executable-code commit `1ef2ee8` completed
successfully on 2026-11-10; 0 failed and 0 skipped workflows:

| Workflow | Event | Actual status |
|---|---|---|
| [V5 engineering replay](https://github.com/fengzhe-li/indy500-racing-point-in-time-decision-support/actions/runs/42836988811) | push | Success |
| [V5 engineering replay](https://github.com/fengzhe-li/indy500-racing-point-in-time-decision-support/actions/runs/42837000084) | pull_request | Success |
| [Repository integrity](https://github.com/fengzhe-li/indy500-racing-point-in-time-decision-support/actions/runs/42836988827) | push | Success |
| [Repository integrity](https://github.com/fengzhe-li/indy500-racing-point-in-time-decision-support/actions/runs/42836999842) | pull_request | Success |
| [V3 CI](https://github.com/fengzhe-li/indy500-racing-point-in-time-decision-support/actions/runs/42837000398) | pull_request | Success: Python, frontend and Docker |

These runs validate the executable code and adapter document. This report's
subsequent documentation-only commit triggers new runs; their actual status is
recorded in the PR delivery update rather than inferred from this table.
Action-runtime deprecation/runner-image notices remain non-failing CI maintenance
items; they are not physics or release blockers.

Missing, queued or inaccessible runs are not counted as successful checks. The
GitHub connector required an unconnected account, so actual run pages were read
in the authenticated browser. PR metadata was separately checked with GitHub CLI.

### Reproduction commands

From the repository root:

```bash
python3 -m unittest discover -s v5_lap_time_simulation/tests -v
npm test --prefix v5_lap_time_simulation/frontend
npm run build --prefix v5_lap_time_simulation/frontend
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s v3_point_in_time/tests -v
npm test --prefix v3_point_in_time/frontend
npm run build --prefix v3_point_in_time/frontend
python3 v3_point_in_time/scripts/run_v2_immutability_check.py
python3 v3_point_in_time/scripts/run_v3_v2_behavioral_regression.py
python3 v3_point_in_time/scripts/smoke_test.py
python3 scripts/validate_portfolio.py
python3 -m v5_lap_time_simulation.cli --output-dir /tmp/v5-final-regenerated
# Compare each generated file's SHA-256 with v5_lap_time_simulation/output/.
```

## 7. Scientific limitations and claims

The documentation correctly separates assumed mass/aero/grip/geometry/environment,
the one calibrated effective scalar, observed official timing, simulated spatial
profiles, scenario sensitivities and retrospective descriptive comparison.

The scalar is fitted to 206 complete 2020–2023 attempts. The 54 complete 2024
attempts are excluded from scalar fitting but have been inspected in development.
The legacy metadata key `held_out_validation_year` is explicitly qualified by
`holdout_scope`; it is not evidence of an untouched model-development holdout.
No further tuning against 2024 occurred in this acceptance review.

**No demonstrated aggregate MAE improvement over the training-median baseline**
is preserved. Equal errors follow from the median-speed calibration target.
Comparison against training mean or fixed 230 mph does not isolate physics skill.
No individual-car, setup-specific or telemetry prediction claim is accepted.

Known limits remain: prescribed circular path, step changes in curvature/bank,
road-normal constant-coefficient aero, simplified tires without load sensitivity
or axle allocation, no wind/wake, no transient driver/suspension/yaw model, and
conservative sustainable-speed caps rather than a full optimal-control solution.
The numerical study is finite, and the physical model is not uniquely identifiable
from aggregate historical speeds. No unsupported section-to-distance alignment,
GPS or ECU channel is manufactured.

## 8. Integration readiness for V6 and Explorer

**Ready as a versioned quasi-steady reference and replay-data producer.** Downstream
work should consume v1 through a separate adapter, preserve metadata, use each
profile's own time/distance mapping, and compare on a shared spatial grid. Keep
completed-lap count distinct from the closed drawing position. Preserve missing
telemetry as unavailable and keep calibration lineage outside the frozen payload
if additional bookkeeping is needed.

This does not certify unfinished V6/C++ code or implement a driver controller,
real-time dynamics, dual-car wake interaction or the Explorer itself. Those
projects need their own verification and scientific claims.

## 9. Release decision

**RELEASE READY.** The scoped acceptance defects are corrected, all required local
checks passed, all audited-code CI workflows passed, generated results and the
v1 payload contract are unchanged, and no blocking engineering defect remains
within the documented quasi-steady domain. V5 is suitable to merge as a stable
reference implementation and adapter-based integration foundation.

The decision does not enlarge the scientific claims or certify unfinished
integrations. There is no demonstrated aggregate prediction gain over the median
baseline and no telemetry validation. Keep the stated numerical/model limitations
with any downstream demonstration. PR #2 remains open for the user's merge
decision; this audit does not merge it.
