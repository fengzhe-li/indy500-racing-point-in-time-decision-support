# V4 Phase 4J — FINAL Pre-registered Performance-Control Hierarchy

**Pre-result specification:** `phase4j_final_hierarchy_spec.md`, committed as **`28af221`** before any D, contrast, bootstrap or leave-one-out value was computed.

**Frozen inputs (verified before the spec; `phase4j_input_verification.csv`):**
- Phase 4F **D**, 4G **A**, 4H **D** and 4I **B**, all unchanged;
- the Phase 4H classes and the Phase 4I eligibility, reproduced exactly.

**Finality:** this is the final V4 hierarchy analysis, and its result is accepted as it is.

## Primary result: CASE B (partial hierarchy)

Population: Tier 1 (class A ↔ A), 2023–2024, strict adjacency common support. There are **6 evaluable sessions** (the replication unit) and 53 common-support same-team contexts.

**Session-balanced medians:**

| Quantity | mph | Lap-time equivalent at 225 mph |
|---|---|---|
| D_same-car | 0.368 | |
| D_same-team | 1.226 | |
| D_different-team | 1.093 | |
| **C1** = D_same-team − D_same-car | **+0.696** | +0.124 s |
| **C2** = paired D_diff-team − D_same-team | **+0.199** | +0.035 s |
| C3 = D_diff-team − D_same-car | +0.702 | +0.125 s |

**C1 is `POSITIVE_CONSISTENT`: supported.**
- The session-bootstrap interval is [0.087, 1.721].
- It is positive in 83% of sessions and in every leave-one-session-out and leave-one-team-out recomputation.

**C2 is `INCONSISTENT`: not supported.**
- The session-bootstrap interval is [-0.528, 0.528].
- It is positive in only 67% of sessions (below the pre-registered 75%).
- Removing Ed Carpenter Racing turns it negative.
- The difference of layer medians is -0.134, so its sign depends on the construction.

**What is supported:** *same car < same team*.

**What is not established:** *same team < different team*. The same-team and different-team layers overlap within the adjacency-balanced design.

**Interpretation:**
- This is an **empirical control hierarchy in a restricted population**: 2023–24 practice-type sessions, frozen class-A car-blocks, and 5-min blocks with exact adjacency-stratum support.
- It is **not** a causal team effect, not a variance decomposition, and not a team or driver ranking.
- Tier 2 and 2025 can neither overturn nor replace it.

## All analyses

| analysis | role | case | C1_status | C2_status | evaluable_sessions | common_support_contexts | D_same_car | D_same_team | D_diff_team | C1 | C1_boot_lo | C1_boot_hi | share_sessions_C1_pos | C2 | C2_boot_lo | C2_boot_hi | share_sessions_C2_pos | C3 | C3_boot_lo | C3_boot_hi | C1_from_layer_medians | C2_from_layer_medians |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PRIMARY_TIER1_2023_2024 | PRIMARY | B | POSITIVE_CONSISTENT | INCONSISTENT | 6 | 53 | 0.368 | 1.226 | 1.093 | 0.696 | 0.087 | 1.721 | 0.833 | 0.199 | -0.528 | 0.528 | 0.667 | 0.702 | 0.283 | 1.623 | 0.858 | -0.134 |
| TIER2_SENSITIVITY_2023_2024 | EXTENDED MEASUREMENT-VALIDITY SENSITIVITY | B | POSITIVE_CONSISTENT | INCONSISTENT | 8 | 103 | 0.716 | 1.093 | 1.382 | 0.369 | 0.13 | 2.411 | 0.875 | -0.094 | -1.298 | 0.764 | 0.5 | 0.69 | 0.557 | 1.561 | 0.377 | 0.289 |
| REPLICATION_2025_TIER1 | 2025 HYBRID-ERA SECONDARY REPLICATION | B | POSITIVE_CONSISTENT | INCONSISTENT | 5 | 25 | 0.684 | 1.018 | 2.009 | 0.266 | -0.107 | 1.585 | 0.8 | 0.743 | -0.904 | 3.068 | 0.6 | 1.624 | 0.054 | 2.961 | 0.334 | 0.99 |

## Session level

| analysis | session_key | contexts | same_car_pairs | evaluable | D_same_car | D_same_team | D_diff_team | C1 | C2 | C3 |
|---|---|---|---|---|---|---|---|---|---|---|
| PRIMARY_TIER1_2023_2024 | 6199 | 6 | 19 | True | 0.404 | 0.162 | 0.988 | -0.243 | 0.764 | 0.584 |
| PRIMARY_TIER1_2023_2024 | 6207 | 3 | 10 | True | 0.323 | 0.74 | 0.953 | 0.417 | 0.213 | 0.63 |
| PRIMARY_TIER1_2023_2024 | 6208 | 20 | 17 | True | 0.424 | 1.349 | 1.197 | 0.925 | -0.41 | 0.774 |
| PRIMARY_TIER1_2023_2024 | 6375 | 0 | 2 | False | 0.531 |  |  |  |  |  |
| PRIMARY_TIER1_2023_2024 | 6378 | 9 | 13 | True | 0.332 | 2.257 | 1.705 | 1.926 | -0.646 | 1.373 |
| PRIMARY_TIER1_2023_2024 | 6380 | 0 | 5 | False | 0.618 |  |  |  |  |  |
| PRIMARY_TIER1_2023_2024 | 6387 | 7 | 18 | True | 0.637 | 1.104 | 0.619 | 0.467 | 0.184 | -0.018 |
| PRIMARY_TIER1_2023_2024 | 6388 | 8 | 8 | True | 0.225 | 1.742 | 2.099 | 1.517 | 0.293 | 1.874 |
| TIER2_SENSITIVITY_2023_2024 | 6198 | 2 | 18 | True | 0.777 | 3.188 | 1.746 | 2.411 | -1.442 | 0.969 |
| TIER2_SENSITIVITY_2023_2024 | 6199 | 6 | 25 | True | 0.431 | 0.162 | 0.988 | -0.27 | 0.764 | 0.557 |
| TIER2_SENSITIVITY_2023_2024 | 6200 | 0 | 8 | False | 1.036 |  |  |  |  |  |
| TIER2_SENSITIVITY_2023_2024 | 6207 | 7 | 13 | True | 0.61 | 0.739 | 1.217 | 0.13 | 0.633 | 0.607 |
| TIER2_SENSITIVITY_2023_2024 | 6208 | 31 | 23 | True | 0.735 | 1.082 | 1.041 | 0.347 | -0.348 | 0.306 |
| TIER2_SENSITIVITY_2023_2024 | 6375 | 5 | 4 | True | 0.679 | 3.213 | 2.623 | 2.534 | -1.298 | 1.944 |
| TIER2_SENSITIVITY_2023_2024 | 6378 | 13 | 23 | True | 0.719 | 1.067 | 1.492 | 0.348 | -0.392 | 0.773 |
| TIER2_SENSITIVITY_2023_2024 | 6380 | 0 | 5 | False | 0.618 |  |  |  |  |  |
| TIER2_SENSITIVITY_2023_2024 | 6387 | 17 | 26 | True | 0.713 | 1.104 | 1.272 | 0.391 | 0.159 | 0.559 |
| TIER2_SENSITIVITY_2023_2024 | 6388 | 22 | 19 | True | 0.741 | 1.711 | 2.301 | 0.97 | 0.831 | 1.561 |
| REPLICATION_2025_TIER1 | 6651 | 3 | 8 | True | 0.698 | 0.591 | 3.659 | -0.107 | 3.068 | 2.961 |
| REPLICATION_2025_TIER1 | 6653 | 2 | 13 | True | 0.684 | 2.269 | 1.366 | 1.585 | -0.904 | 0.681 |
| REPLICATION_2025_TIER1 | 6654 | 2 | 19 | True | 0.481 | 0.746 | 2.104 | 0.266 | 1.358 | 1.624 |
| REPLICATION_2025_TIER1 | 6655 | 0 | 8 | False | 0.488 |  |  |  |  |  |
| REPLICATION_2025_TIER1 | 6662 | 12 | 13 | True | 0.293 | 1.736 | 2.009 | 1.443 | 0.743 | 1.716 |
| REPLICATION_2025_TIER1 | 6663 | 6 | 17 | True | 0.802 | 1.018 | 0.856 | 0.216 | -0.126 | 0.054 |

## Case evaluation

| criterion | value |
|---|---|
| analysis | PRIMARY_TIER1_2023_2024 |
| pre_result_spec_commit | 28af221 |
| evaluable_sessions | 6 |
| common_support_contexts | 53 |
| C1 | 0.6960428524871105 |
| C2 | 0.1986703266731098 |
| C3 | 0.7017592266601227 |
| C1_status | POSITIVE_CONSISTENT |
| C2_status | INCONSISTENT |
| PRIMARY_CASE | B |
| TIER2_SENSITIVITY_LABEL | B [EXTENDED MEASUREMENT-VALIDITY SENSITIVITY; never replaces primary] |
| REPLICATION_2025_LABEL | B [2025 HYBRID-ERA SECONDARY REPLICATION; never replaces primary] |

## Tier 2 sensitivity (extended measurement validity; never replaces the primary)

**Result:** CASE B. C1 is +0.369 (`POSITIVE_CONSISTENT`) and C2 is -0.094 (`INCONSISTENT`). Direction agrees with the primary: C1 is supported, C2 is not (its sign reverses).

**Composition** (A_ONLY / B_ONLY / MIXED_AB car-blocks):

| layer | composition | share | n |
|---|---|---|---|
| same-team context (target|teammate) | A_ONLY|A_ONLY | 0.388 | 40 |
| same-team context (target|teammate) | B_ONLY|A_ONLY | 0.146 | 15 |
| same-team context (target|teammate) | A_ONLY|B_ONLY | 0.126 | 13 |
| same-team context (target|teammate) | B_ONLY|B_ONLY | 0.097 | 10 |
| same-team context (target|teammate) | MIXED_AB|A_ONLY | 0.087 | 9 |
| same-team context (target|teammate) | A_ONLY|MIXED_AB | 0.078 | 8 |
| same-team context (target|teammate) | B_ONLY|MIXED_AB | 0.029 | 3 |
| same-team context (target|teammate) | MIXED_AB|B_ONLY | 0.029 | 3 |
| same-team context (target|teammate) | MIXED_AB|MIXED_AB | 0.019 | 2 |
| same-car pair | A_ONLY|A_ONLY | 0.537 | 88 |
| same-car pair | B_ONLY|B_ONLY | 0.213 | 35 |
| same-car pair | A_ONLY|MIXED_AB | 0.067 | 11 |
| same-car pair | MIXED_AB|A_ONLY | 0.061 | 10 |
| same-car pair | B_ONLY|A_ONLY | 0.037 | 6 |
| same-car pair | A_ONLY|B_ONLY | 0.03 | 5 |
| same-car pair | B_ONLY|MIXED_AB | 0.03 | 5 |
| same-car pair | MIXED_AB|B_ONLY | 0.024 | 4 |
| admissible candidate | A_ONLY | 0.592 | 186 |
| admissible candidate | B_ONLY | 0.322 | 101 |
| admissible candidate | MIXED_AB | 0.086 | 27 |

## 2025 hybrid-era secondary replication (not pooled)

**Result:** CASE B, with 5 evaluable sessions and 25 contexts.
- C1 is +0.266 (`POSITIVE_CONSISTENT`); C2 is +0.743 (`INCONSISTENT`, 60% of sessions positive; interval [-0.90, 3.07]).
- It agrees with the primary pattern: C1 is supported and C2 is not consistent.

## Scale (4J.17)

| analysis | quantity | mph | pct_of_median_speed | laptime_equiv_s_at_225 | median_eligible_speed |
|---|---|---|---|---|---|
| PRIMARY_TIER1_2023_2024 | D_same_car | 0.368 | 0.166 | 0.065 | 221.1 |
| PRIMARY_TIER1_2023_2024 | D_same_team | 1.226 | 0.555 | 0.218 | 221.1 |
| PRIMARY_TIER1_2023_2024 | D_diff_team | 1.093 | 0.494 | 0.194 | 221.1 |
| PRIMARY_TIER1_2023_2024 | C1 | 0.696 | 0.315 | 0.124 | 221.1 |
| PRIMARY_TIER1_2023_2024 | C2 | 0.199 | 0.09 | 0.035 | 221.1 |
| PRIMARY_TIER1_2023_2024 | C3 | 0.702 | 0.317 | 0.125 | 221.1 |
| TIER2_SENSITIVITY_2023_2024 | D_same_car | 0.716 | 0.324 | 0.127 | 221.256 |
| TIER2_SENSITIVITY_2023_2024 | D_same_team | 1.093 | 0.494 | 0.194 | 221.256 |
| TIER2_SENSITIVITY_2023_2024 | D_diff_team | 1.382 | 0.625 | 0.246 | 221.256 |
| TIER2_SENSITIVITY_2023_2024 | C1 | 0.369 | 0.167 | 0.066 | 221.256 |
| TIER2_SENSITIVITY_2023_2024 | C2 | -0.094 | -0.043 | -0.017 | 221.256 |
| TIER2_SENSITIVITY_2023_2024 | C3 | 0.69 | 0.312 | 0.123 | 221.256 |
| REPLICATION_2025_TIER1 | D_same_car | 0.684 | 0.312 | 0.122 | 219.482 |
| REPLICATION_2025_TIER1 | D_same_team | 1.018 | 0.464 | 0.181 | 219.482 |
| REPLICATION_2025_TIER1 | D_diff_team | 2.009 | 0.915 | 0.357 | 219.482 |
| REPLICATION_2025_TIER1 | C1 | 0.266 | 0.121 | 0.047 | 219.482 |
| REPLICATION_2025_TIER1 | C2 | 0.743 | 0.338 | 0.132 | 219.482 |
| REPLICATION_2025_TIER1 | C3 | 1.624 | 0.74 | 0.289 | 219.482 |
| PHASE4I_REFERENCE | QUALIFYING_OFFICIAL_WITHIN_ATTEMPT [2023] | 0.586 |  | 0.104 |  |
| PHASE4I_REFERENCE | QUALIFYING_OFFICIAL_WITHIN_ATTEMPT [2024] | 0.373 |  | 0.066 |  |
| PHASE4I_REFERENCE | SAME_CAR_A_WITHIN_CARBLOCK [2023_2024_PRIMARY] | 0.579 |  | 0.103 |  |
| PHASE4I_REFERENCE | SAME_CAR_A_CONSECUTIVE_LAP_ABS_DELTA [2023_2024_PRIMARY] | 0.509 |  | 0.09 |  |
| PHASE4I_REFERENCE | SAME_CAR_A_CROSS_SESSION_SD_OF_SESSION_MEDIANS [2023_2024_PRIMARY] | 2.701 |  | 0.48 |  |
| PHASE4I_REFERENCE | SAME_CAR_A_WITHIN_CARBLOCK [2025_SECONDARY] | 0.52 |  | 0.093 |  |
| PHASE4I_REFERENCE | SAME_CAR_A_CONSECUTIVE_LAP_ABS_DELTA [2025_SECONDARY] | 0.457 |  | 0.081 |  |
| PHASE4I_REFERENCE | SAME_CAR_A_CROSS_SESSION_SD_OF_SESSION_MEDIANS [2025_SECONDARY] | 5.279 |  | 0.938 |  |
| PHASE4I_REFERENCE | LAPTIME_PRECISION [1e-4 s recorded precision] | 0.001 |  | 0 |  |
| PHASE4I_REFERENCE | TIMESTAMP_RESOLUTION [Timing71 feed update] |  |  |  |  |

**Empirical separation vs competitive significance:**
- **C1 (0.70 mph ≈ 0.12 s per lap)** is larger than the Phase 4I same-car local variation (consecutive A-lap median |Δ| about 0.5 mph) and than the qualifying within-attempt SD (0.37–0.59 mph). It is empirically separated at the session level in this population.
- **C2's point value** (0.20 mph ≈ 0.035 s) is below those references, and its sign is unstable.
- Whether a given mph difference matters competitively depends on context (for example, qualifying margins are often hundredths of a second). **No universal threshold is claimed.**
