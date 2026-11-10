# V4 Phase 4G — Control-Selection Report

**Pre-specification:** `phase4g_design_diagnostic_spec.md`, committed as `ffdfacd` before any adjacency computation. Its rules were applied without change. **Phase 4F CASE:** `D`. It is unchanged, and the Phase 4F files were verified against `phase4f_freeze_record.csv`.

**Source:** Timing71 archived recordings of the INDYCAR live timing feed (third-party). This is a design diagnostic. It is not a new hierarchy test and not a tow analysis.

## 1. Reproduction of the Phase 4F primary control selection (4G.4)

The Phase 4F nearest-time selection was re-implemented with full candidate pools retained. Every target, teammate, control, D value and time separation matches `phase4f/comparison_pairs.csv` exactly:

| role | comparison_class | phase4f_rows | reconstructed_rows | exact_match |
|---|---|---|---|---|
| PRIMARY | DIFF_TEAM | 1937 | 1937 | True |
| PRIMARY | TEAMMATE_OF_TARGET | 1937 | 1937 | True |
| ERA_C_SECONDARY | DIFF_TEAM | 762 | 762 | True |
| ERA_C_SECONDARY | TEAMMATE_OF_TARGET | 762 | 762 | True |

The Phase 4F sensitivity populations also reproduce Phase 4F:
- adjacent-block DIFF: n and session-balanced D;
- reweighted DIFF: n and weighted D;
- team-balanced DIFF: all 209 block values.

| population | phase4f_n | phase4g_n | phase4f_session_balanced_D | phase4g_session_balanced_D | phase4f_pooled_weighted_D | phase4g_pooled_weighted_D | team_balanced_block_values_match |
|---|---|---|---|---|---|---|---|
| ADJACENT_BLOCK_DIFF | 1006 | 1006 | 2.617 | 2.617 |  |  |  |
| REWEIGHTED_DIFF | 1937 | 1937 |  |  | 2.384 | 2.384 |  |
| TEAM_BALANCED_DIFF | 209 | 209 |  |  |  |  | True |

## 2. Is the selected control an unusual comparison population? (4G.6)

**Answer: yes.** In the 2023–24 primary:
- **Selected control:** 0.577 of controls have **no intervening lap-line record** between them and the target: they are in the same feed update, or they are consecutive observations.
- **Random pick from the same pool:** 0.277 would be expected.
- **Difference:** 0.300, a ratio of 2.083.
- **Pool rank:** the selected control's median percentile rank of intervening records within its own pool is about 0.20 (0 = most adjacent in the pool; 0.5 = what a random pick gives).
- **Teammates:** the nearest teammate (C1) is also more adjacent than the pool (0.447), but less so than the selected control.

**Cumulative adjacency** (share of pairs; "≤k" = same update, or ≤k intervening records on the lower-median target lap):

| role | population | n_pairs | share_same_update | share_consecutive_strict | share_le0_intervening | share_le1_intervening | share_le2_intervening | share_le3_intervening | share_le5_intervening |
|---|---|---|---|---|---|---|---|---|---|
| PRIMARY | A_PRIMARY_CONTROL | 1937 | 0.244 | 0.333 | 0.577 | 0.642 | 0.713 | 0.765 | 0.842 |
| PRIMARY | B_ELIGIBLE_CANDIDATES | 26437 | 0.086 | 0.183 | 0.269 | 0.312 | 0.366 | 0.414 | 0.511 |
| PRIMARY | C1_TEAMMATE_OF_TARGET | 1937 | 0.199 | 0.248 | 0.447 | 0.49 | 0.555 | 0.604 | 0.681 |
| PRIMARY | C2_ALL_TEAMMATES | 3278 | 0.16 | 0.235 | 0.395 | 0.433 | 0.489 | 0.536 | 0.606 |
| PRIMARY | B_RANDOM_PICK_EXPECTATION | 1937 | 0.09 | 0.187 | 0.277 | 0.324 | 0.381 | 0.43 | 0.521 |
| ERA_C_SECONDARY | A_PRIMARY_CONTROL | 762 | 0.27 | 0.366 | 0.636 | 0.71 | 0.773 | 0.816 | 0.885 |
| ERA_C_SECONDARY | B_ELIGIBLE_CANDIDATES | 9056 | 0.091 | 0.198 | 0.289 | 0.337 | 0.391 | 0.438 | 0.529 |
| ERA_C_SECONDARY | C1_TEAMMATE_OF_TARGET | 762 | 0.16 | 0.23 | 0.39 | 0.459 | 0.52 | 0.563 | 0.657 |
| ERA_C_SECONDARY | C2_ALL_TEAMMATES | 1086 | 0.135 | 0.221 | 0.356 | 0.414 | 0.476 | 0.523 | 0.62 |
| ERA_C_SECONDARY | B_RANDOM_PICK_EXPECTATION | 762 | 0.105 | 0.214 | 0.319 | 0.372 | 0.429 | 0.478 | 0.562 |

**Separation quantiles** (car-block time separation and lap-level |Δts| in s; intervening records):

| role | population | carblock_sep_s_p10 | carblock_sep_s_p25 | carblock_sep_s_median | carblock_sep_s_p75 | carblock_sep_s_p90 | lap_ts_sep_s_median | intervening_p25 | intervening_median | intervening_p75 | intervening_p90 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PRIMARY | A_PRIMARY_CONTROL | 0 | 0.837 | 3.345 | 17.381 | 34.326 | 2.524 | 0 | 0 | 4 | 8.5 |
| PRIMARY | B_ELIGIBLE_CANDIDATES | 4.971 | 20.919 | 58.72 | 106.07 | 148.561 | 9.194 | 1 | 6.5 | 21 | 47 |
| PRIMARY | C1_TEAMMATE_OF_TARGET | 1.655 | 6.688 | 37.671 | 81.987 | 127.177 | 3.654 | 0 | 2.5 | 10 | 30 |
| PRIMARY | C2_ALL_TEAMMATES | 1.673 | 17.549 | 43.527 | 102.018 | 147.896 | 5.025 | 0 | 4 | 16 | 42 |
| PRIMARY | B_RANDOM_PICK_EXPECTATION | 17.564 | 37.233 | 60.258 | 88.616 | 124.666 | 11.593 | 4 | 6.5 | 10 | 14.5 |
| ERA_C_SECONDARY | A_PRIMARY_CONTROL | 0 | 0.824 | 3.343 | 18.358 | 35.223 | 1.681 | 0 | 0 | 3 | 6.5 |
| ERA_C_SECONDARY | B_ELIGIBLE_CANDIDATES | 3.358 | 20.016 | 56.711 | 104.281 | 147.726 | 8.34 | 0.5 | 6 | 18 | 44 |
| ERA_C_SECONDARY | C1_TEAMMATE_OF_TARGET | 1.666 | 6.68 | 38.675 | 83.423 | 140.098 | 5.004 | 0 | 3 | 10 | 28 |
| ERA_C_SECONDARY | C2_ALL_TEAMMATES | 1.669 | 13.281 | 45.057 | 93.416 | 142.832 | 5.013 | 0 | 4 | 13 | 34 |
| ERA_C_SECONDARY | B_RANDOM_PICK_EXPECTATION | 17.619 | 31.551 | 56.26 | 92.48 | 127.289 | 9.176 | 3 | 5.75 | 9.5 | 15.5 |

**Selected control's percentile rank within its pool:**

| role | basis | rank_p25 | rank_median | rank_p75 |
|---|---|---|---|---|
| PRIMARY | OBSERVED_FEED_SEQUENCE | 0.125 | 0.2 | 0.375 |
| PRIMARY | DERIVED_LAPTIME_CHAIN_ESTIMATE | 0.083 | 0.196 | 0.391 |
| ERA_C_SECONDARY | OBSERVED_FEED_SEQUENCE | 0.125 | 0.209 | 0.375 |
| ERA_C_SECONDARY | DERIVED_LAPTIME_CHAIN_ESTIMATE | 0.094 | 0.191 | 0.375 |

**Derived laptime-chain sensitivity** (not observed; it breaks feed-update ties using laptime chains):

| role | population | n_pairs | share_same_update | share_consecutive_strict | share_le0_intervening | share_le1_intervening | share_le2_intervening | share_le3_intervening | share_le5_intervening |
|---|---|---|---|---|---|---|---|---|---|
| PRIMARY | A_PRIMARY_CONTROL | 1937 | 0.003 | 0.243 | 0.246 | 0.422 | 0.549 | 0.642 | 0.768 |
| PRIMARY | B_ELIGIBLE_CANDIDATES | 26437 | 0.001 | 0.078 | 0.079 | 0.157 | 0.226 | 0.291 | 0.402 |
| PRIMARY | C1_TEAMMATE_OF_TARGET | 1937 | 0.002 | 0.18 | 0.182 | 0.311 | 0.395 | 0.472 | 0.601 |
| PRIMARY | C2_ALL_TEAMMATES | 3278 | 0.002 | 0.144 | 0.146 | 0.261 | 0.343 | 0.419 | 0.53 |
| PRIMARY | B_RANDOM_PICK_EXPECTATION | 1937 | 0.001 | 0.087 | 0.088 | 0.174 | 0.248 | 0.315 | 0.425 |
| PRIMARY | A_POOL_PERCENTILE_RANK | 1937 |  |  |  |  |  |  |  |
| ERA_C_SECONDARY | A_PRIMARY_CONTROL | 762 | 0.003 | 0.28 | 0.282 | 0.486 | 0.626 | 0.726 | 0.827 |
| ERA_C_SECONDARY | B_ELIGIBLE_CANDIDATES | 9056 | 0.001 | 0.09 | 0.091 | 0.182 | 0.258 | 0.326 | 0.441 |
| ERA_C_SECONDARY | C1_TEAMMATE_OF_TARGET | 762 | 0.001 | 0.154 | 0.155 | 0.261 | 0.354 | 0.428 | 0.559 |
| ERA_C_SECONDARY | C2_ALL_TEAMMATES | 1086 | 0.001 | 0.13 | 0.131 | 0.23 | 0.32 | 0.391 | 0.527 |
| ERA_C_SECONDARY | B_RANDOM_PICK_EXPECTATION | 762 | 0.001 | 0.111 | 0.112 | 0.215 | 0.302 | 0.374 | 0.485 |
| ERA_C_SECONDARY | A_POOL_PERCENTILE_RANK | 762 |  |  |  |  |  |  |  |

- On this basis the selected controls remain about 2.8× the pool expectation.
- The absolute difference (0.246 vs 0.088) falls below the 0.20 "substantial" threshold. It agrees in direction but not in magnitude class.
- It does not enter the case rule (spec §11).

## 3. Year and session category (4G.7)

| role | level | scope | targets | A_share_no_intervening | B_expected_share_no_intervening | A_minus_B_expectation | C1_share_no_intervening | A_minus_C1_share_no_intervening | A_median_carblock_sep_s | C1_median_carblock_sep_s | phase4f_session_balanced_delta_reference |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PRIMARY | YEAR | 2023 | 1076 | 0.586 | 0.275 | 0.31 | 0.488 | 0.098 | 4.179 | 39.302 | 0.103 |
| PRIMARY | YEAR | 2024 | 861 | 0.566 | 0.279 | 0.287 | 0.395 | 0.171 | 3.299 | 33.453 | -0.208 |
| PRIMARY | CATEGORY | CARB_DAY | 554 | 0.585 | 0.274 | 0.311 | 0.404 | 0.181 | 2.479 | 36.375 | -0.001 |
| PRIMARY | CATEGORY | FAST_FRIDAY | 19 | 0.474 | 0.232 | 0.242 | 0 | 0.474 | 21.163 | 223.856 | 0.772 |
| PRIMARY | CATEGORY | POST_QUALIFYING_PRACTICE | 496 | 0.593 | 0.283 | 0.31 | 0.427 | 0.165 | 2.447 | 25.861 | -0.173 |
| PRIMARY | CATEGORY | PRACTICE | 868 | 0.565 | 0.276 | 0.288 | 0.494 | 0.07 | 6.679 | 40.1 | 0.024 |
| ERA_C_SECONDARY | YEAR | 2025 | 762 | 0.636 | 0.319 | 0.317 | 0.39 | 0.247 | 3.343 | 39.256 | -0.387 |
| ERA_C_SECONDARY | CATEGORY | CARB_DAY | 202 | 0.624 | 0.261 | 0.363 | 0.297 | 0.327 | 1.67 | 33.341 |  |
| ERA_C_SECONDARY | CATEGORY | FAST_FRIDAY | 2 | 0.5 | 0.5 | 0 | 0 | 0.5 | 116.804 | 200.239 |  |
| ERA_C_SECONDARY | CATEGORY | POST_QUALIFYING_PRACTICE | 223 | 0.596 | 0.307 | 0.29 | 0.287 | 0.309 | 1.669 | 35.869 |  |
| ERA_C_SECONDARY | CATEGORY | PRACTICE | 329 | 0.669 | 0.362 | 0.306 | 0.517 | 0.152 | 8.388 | 41.984 |  |
| ERA_C_SECONDARY | CATEGORY | QUALIFYING_WEEKEND_PRACTICE | 6 | 0.833 | 0.319 | 0.514 | 0.5 | 0.333 | 21.161 | 50.869 |  |

**Per session** (Phase 4F session-median Δ shown only for reference):

| role | scope | targets | A_share_no_intervening | B_expected_share_no_intervening | C1_share_no_intervening | A_minus_C1_share_no_intervening | phase4f_session_balanced_delta_reference |
|---|---|---|---|---|---|---|---|
| PRIMARY | 6198 | 342 | 0.538 | 0.236 | 0.45 | 0.088 | 0.103 |
| PRIMARY | 6199 | 277 | 0.693 | 0.343 | 0.57 | 0.123 | -0.055 |
| PRIMARY | 6200 | 11 | 0.455 | 0.258 | 0 | 0.455 | 0.835 |
| PRIMARY | 6207 | 192 | 0.51 | 0.281 | 0.5 | 0.01 | -0.01 |
| PRIMARY | 6208 | 254 | 0.594 | 0.252 | 0.461 | 0.134 | 0.215 |
| PRIMARY | 6375 | 17 | 0.118 | 0.166 | 0.529 | -0.412 | 1.007 |
| PRIMARY | 6378 | 232 | 0.483 | 0.264 | 0.466 | 0.017 | -0.208 |
| PRIMARY | 6380 | 8 | 0.5 | 0.196 | 0 | 0.5 | 0.709 |
| PRIMARY | 6387 | 304 | 0.645 | 0.284 | 0.382 | 0.263 | -0.337 |
| PRIMARY | 6388 | 300 | 0.577 | 0.293 | 0.357 | 0.22 | -0.217 |
| ERA_C_SECONDARY | 6651 | 84 | 0.738 | 0.35 | 0.393 | 0.345 |  |
| ERA_C_SECONDARY | 6653 | 76 | 0.434 | 0.221 | 0.408 | 0.026 |  |
| ERA_C_SECONDARY | 6654 | 169 | 0.74 | 0.432 | 0.627 | 0.112 |  |
| ERA_C_SECONDARY | 6655 | 2 | 0.5 | 0.5 | 0 | 0.5 |  |
| ERA_C_SECONDARY | 6657 | 6 | 0.833 | 0.319 | 0.5 | 0.333 |  |
| ERA_C_SECONDARY | 6662 | 202 | 0.624 | 0.261 | 0.297 | 0.327 |  |
| ERA_C_SECONDARY | 6663 | 223 | 0.596 | 0.307 | 0.287 | 0.309 |  |

**Readings** (descriptive, not causal):
- The selected control's excess adjacency over its pool is almost the same in 2023 (0.310) and 2024 (0.287). **Control adjacency by itself does not explain why 2024's primary Δ was negative.**
- What differs by year is how adjacent the *teammate* comparator is. The control-minus-teammate gap in the no-intervening share is:
  - 2023: 0.098;
  - 2024: 0.171;
  - 2025 (secondary): 0.247.
- That ordering matches the ordering of the Phase 4F primary Δ (+0.10, −0.21, −0.39).
- **Caveat:** these are three points. Per session the pattern is mixed. The largest negative sessions (6387, 6388) have large gaps, but 6207 and 6378 have gaps near 0 with Δ ≈ 0 and −0.21.
- **Session category:** all categories with many targets show the same excess adjacency of about 0.29–0.31. Fast Friday (19 targets) is too small to read.

## 4. Negative vs positive Phase 4F blocks (4G.9)

| group | blocks | sessions | targets | median_control_carblock_sep_s | median_control_lap_ts_sep_s | median_control_intervening | share_controls_no_intervening | pool_expectation_no_intervening | excess_no_intervening | median_pool_size | control_reuse_ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NEGATIVE | 110 | 9 | 1072 | 3.34 | 1.691 | 0 | 0.622 | 0.286 | 0.287 | 10 | 1.333 |
| POSITIVE | 99 | 10 | 865 | 7.521 | 6.611 | 1 | 0.5 | 0.25 | 0.25 | 8 | 1.455 |

**Comparison:**
- **Negative-Δ blocks:**
  - selected controls are closer: a median car-block separation of 3.340 s vs 7.521 s in positive blocks, and a lap-level |Δts| of 1.691 s vs 6.611 s;
  - they more often have no intervening record (0.622 vs 0.500);
  - they come from somewhat larger pools (median 10.000 vs 8.000).
- **Excess adjacency over the pool expectation** differs less (median 0.287 vs 0.250).
- **Verdict:** negative blocks are associated with more extreme control adjacency, but the association is moderate, not decisive. Blocks were not redefined or discarded.

## 5. Control reuse (4G.10)

| role | level | scope | targets | unique_control_carblocks | unique_control_cars | mean_targets_per_control | median_targets_per_control | max_targets_per_control | share_controls_reused_ge2 | share_targets_with_reused_control | max_control_car_appearances | share_no_intervening | median_carblock_sep_s | median_intervening | median_pool_size |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PRIMARY | OVERALL | ALL | 1937 | 1398 | 68 | 1.386 | 1 | 5 | 0.305 | 0.498 | 66 |  |  |  |  |
| PRIMARY | YEAR | 2023 | 1076 | 780 | 34 | 1.379 |  | 5 | 0.3 |  |  |  |  |  |  |
| PRIMARY | YEAR | 2024 | 861 | 618 | 34 | 1.393 |  | 5 | 0.311 |  |  |  |  |  |  |
| PRIMARY | ADJACENCY_BY_REUSE | HIGH_REUSE_GE3 | 297 |  |  |  |  |  |  |  |  | 0.633 | 2.525 | 0 | 12 |
| PRIMARY | ADJACENCY_BY_REUSE | REUSE_1_2 | 1640 |  |  |  |  |  |  |  |  | 0.566 | 3.347 | 0 | 14 |
| ERA_C_SECONDARY | OVERALL | ALL | 762 | 544 | 34 | 1.401 | 1 | 4 | 0.324 | 0.517 | 44 |  |  |  |  |
| ERA_C_SECONDARY | YEAR | 2025 | 762 | 544 | 34 | 1.401 |  | 4 | 0.324 |  |  |  |  |  |  |
| ERA_C_SECONDARY | ADJACENCY_BY_REUSE | HIGH_REUSE_GE3 | 116 |  |  |  |  |  |  |  |  | 0.647 | 2.915 | 0 | 8 |
| ERA_C_SECONDARY | ADJACENCY_BY_REUSE | REUSE_1_2 | 646 |  |  |  |  |  |  |  |  | 0.635 | 3.344 | 0 | 11.5 |

**Distribution of targets per control car-block:**

| role | scope | unique_control_carblocks |
|---|---|---|
| PRIMARY | 1 targets | 972 |
| PRIMARY | 2 targets | 334 |
| PRIMARY | 3 targets | 74 |
| PRIMARY | 4 targets | 15 |
| PRIMARY | 5 targets | 3 |
| ERA_C_SECONDARY | 1 targets | 368 |
| ERA_C_SECONDARY | 2 targets | 139 |
| ERA_C_SECONDARY | 3 targets | 32 |
| ERA_C_SECONDARY | 4 targets | 5 |

**Readings:**
- About half of targets share their control car-block with at least one other target. The maximum is 5 targets per control car-block.
- High-reuse controls (≥3 targets) are slightly more timing-adjacent than the rest.
- Reused controls are not independent evidence. The 1,937 primary comparisons rest on 1398 distinct control car-blocks.

## 6. Design populations: primary vs team-balanced / adjacent-block / reweighted (4G.11–4G.12)

| population | n_pairs | n_blocks | weighted | share_same_update | share_le0_intervening | share_le2_intervening | share_le5_intervening | carblock_sep_s_median | lap_ts_sep_s_median | intervening_median | distinct_comparator_teams | largest_single_comparator_team_share | max_carblock_appearances | median_carblock_appearances | blocks_covered |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_PRIMARY_CONTROL | 1937 | 209 | False | 0.244 | 0.577 | 0.713 | 0.842 | 3.345 | 2.524 | 0 | 12 | 0.153 | 6 | 1 | 209 |
| TEAM_BALANCED_DIFF | 17411 | 209 | True | 0.085 | 0.264 | 0.373 | 0.513 | 61.122 | 16.518 | 7 | 12 | 0.156 | 26 | 13 | 209 |
| ADJACENT_BLOCK_DIFF | 1006 | 158 | False | 0 | 0.005 | 0.031 | 0.067 | 147.027 | 138.732 | 47.5 | 12 | 0.162 | 17 | 1 | 158 |
| REWEIGHTED_DIFF | 1937 | 209 | True | 0.056 | 0.151 | 0.195 | 0.296 | 189.335 | 170.814 | 11 | 12 | 0.278 | 6 | 1 | 209 |
| C1_TEAMMATE_OF_TARGET | 1937 | 209 | False | 0.199 | 0.447 | 0.555 | 0.681 | 37.671 | 3.654 | 2.5 | 11 | 0.173 | 4 | 2 | 209 |

**Nothing here is promoted to a primary result.** None of the three Phase 4F sensitivity designs takes the time-nearest different-team car within the target's own block. Team-balanced uses all cross-team pairs; adjacent-block takes the nearest car in the *next* block; reweighted keeps the primary pairs but reweights them to same-car separations. All three move the different-team population away from timing adjacency:

| Population | No-intervening share | Median car-block separation | Notes |
|---|---|---|---|
| Primary control | 0.577 | 3 s | |
| Team-balanced (weighted) | 0.264 | 61 s | close to the pool expectation |
| Reweighted | 0.151 | | the weights concentrate on a few long-separation pairs |
| Adjacent-block | 0.005 | 147 s | the comparator is in the next block by construction |

**Other differences:**
- **Team representation is similar:** 12 control teams in the primary; the largest single-team share is 0.15–0.16, except in the reweighted population, where it is 0.28 because of weight concentration.
- **Reuse:** the team-balanced population reuses each car-block far more (median 13 appearances vs 1).
- **Block coverage:** the same 209 blocks, except adjacent-block (158).

So the sign difference between the Phase 4F primary and these sensitivities coincides with a large difference in the timing adjacency of the different-team comparator.

## 7. Mechanical case (spec §11)

| criterion | value |
|---|---|
| gate_share_A_defined | 1.0 |
| gate_share_B_defined | 1.0 |
| gate_G_pass | True |
| S1_A_share_no_intervening | 0.5766649457924625 |
| S1_B_random_pick_expectation | 0.276893174169386 |
| S1_difference | 0.2997717716230765 |
| S1_ratio | 2.082626079614714 |
| S1_level | SUBSTANTIAL |
| S2_sb_D_no_intervening | 1.51194566652822 |
| S2_sb_D_gt5 | 2.4867108287288033 |
| S2_delta | 0.9747651622005833 |
| S2_2023_delta | 0.8694650851388985 |
| S2_2024_delta | 1.080065239262268 |
| S2_both_years_positive | True |
| S2_sessions_eligible | 10 |
| S2_share_sessions_positive | 0.8 |
| S2_within_target_sb_median | 0.6945919368353799 |
| S2_level | CONSISTENT |
| CASE | A |
| agreement_derived_A_share_no_intervening | 0.24574083634486318 |
| agreement_derived_B_expectation | 0.08829581178456433 |
| agreement_2025_A_share_no_intervening | 0.636482939632546 |
| agreement_2025_B_expectation | 0.31917849616433613 |
| agreement_2025_S2_delta | 0.6426974234990439 |
| phase4f_case_unchanged | D |
| phase4h_justified | YES |
