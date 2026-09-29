# V4 Phase 4G — Timing-Sequence Adjacency Report

## What was reconstructed

**Sequence:**
- For each session, every Timing71 lap-line record (all cars, flags and laps) is placed in chronological order.
- **Feed timestamps are update times.** Distinct timestamps are never closer than about 1.5–1.7 s. In the long practice sessions, 54–78% of records share their timestamp with another car's record.
- **Order within one feed update is not observed** and was **not invented**. Such pairs are labelled `SAME_UPDATE` (order unobserved).

**Per target–comparator car-block pair:**
- each target lap is matched to the comparator's nearest lap in the block;
- the number of other records strictly between them is counted;
- the lower-median target lap gives the pair's category.

**Sequence completeness:**

| session_key | role | category | lap_records | distinct_feed_updates | share_records_in_shared_update | median_update_spacing_s | share_records_after_capture_gap |
|---|---|---|---|---|---|---|---|
| 2023|2023-05-21|QUALIFYING_OTHER|6204+6205+6206 | PRIMARY | QUALIFYING_OTHER | 104 | 102 | 0.029 | 38.509 | 0.606 |
| 6198 | PRIMARY | PRACTICE | 3595 | 2362 | 0.537 | 5.018 | 0.062 |
| 6199 | PRIMARY | PRACTICE | 3284 | 2054 | 0.584 | 5.026 | 0.047 |
| 6200 | PRIMARY | FAST_FRIDAY | 1051 | 1023 | 0.053 | 16.693 | 0.112 |
| 6202 | PRIMARY | QUALIFYING_DAY1 | 285 | 254 | 0.112 | 38.584 | 0.281 |
| 6203 | PRIMARY | QUALIFYING_WEEKEND_PRACTICE | 197 | 189 | 0.061 | 12.646 | 0.223 |
| 6207 | PRIMARY | POST_QUALIFYING_PRACTICE | 1875 | 917 | 0.767 | 1.675 | 0.025 |
| 6208 | PRIMARY | CARB_DAY | 2363 | 1118 | 0.78 | 1.679 | 0.033 |
| 6375 | PRIMARY | PRACTICE | 238 | 185 | 0.387 | 5.068 | 0.155 |
| 6378 | PRIMARY | PRACTICE | 2134 | 1208 | 0.664 | 3.313 | 0.06 |
| 6380 | PRIMARY | FAST_FRIDAY | 301 | 291 | 0.066 | 9.76 | 0.086 |
| 6382 | PRIMARY | QUALIFYING_DAY1 | 210 | 201 | 0.062 | 39.129 | 0.238 |
| 6386 | PRIMARY | QUALIFYING_OTHER | 46 | 46 | 0 | 39.157 | 0.087 |
| 6387 | PRIMARY | POST_QUALIFYING_PRACTICE | 2502 | 1165 | 0.78 | 1.674 | 0.066 |
| 6388 | PRIMARY | CARB_DAY | 2728 | 1275 | 0.779 | 1.656 | 0.027 |
| 6651 | ERA_C_SECONDARY | PRACTICE | 863 | 569 | 0.546 | 5.035 | 0.034 |
| 6653 | ERA_C_SECONDARY | PRACTICE | 1033 | 734 | 0.472 | 5.033 | 0.044 |
| 6654 | ERA_C_SECONDARY | PRACTICE | 2399 | 1642 | 0.508 | 8.375 | 0.09 |
| 6655 | ERA_C_SECONDARY | FAST_FRIDAY | 618 | 605 | 0.042 | 21.627 | 0.113 |
| 6656 | ERA_C_SECONDARY | QUALIFYING_DAY1 | 337 | 337 | 0 | 39.929 | 0.151 |
| 6657 | ERA_C_SECONDARY | QUALIFYING_WEEKEND_PRACTICE | 202 | 196 | 0.059 | 9.995 | 0.064 |
| 6660 | ERA_C_SECONDARY | QUALIFYING_OTHER | 61 | 58 | 0.066 | 39.92 | 0.328 |
| 6661 | ERA_C_SECONDARY | QUALIFYING_WEEKEND_PRACTICE | 118 | 117 | 0.017 | 16.952 | 0.068 |
| 6662 | ERA_C_SECONDARY | CARB_DAY | 1988 | 1067 | 0.707 | 1.673 | 0.011 |
| 6663 | ERA_C_SECONDARY | POST_QUALIFYING_PRACTICE | 2076 | 1049 | 0.749 | 1.672 | 0.01 |

- In practice-type sessions (2023–2025), about 1–16% of records follow a capture gap.
- Missing records would **understate** intervening counts, i.e. make pairs look more adjacent than they were. This affects all populations alike and does not favour the selected control.

## D by adjacency stratum (4G.8, different-team candidate pairs)

**Strata were fixed in the spec before D was seen.**

| role | stratum_type | stratum | scope | n_pairs | n_sessions | D_p25 | D_median | D_p75 | D_session_balanced_median |
|---|---|---|---|---|---|---|---|---|---|
| PRIMARY | SEQUENCE | SAME_UPDATE | ALL | 2280 | 8 | 0.56 | 1.301 | 2.692 | 1.348 |
| PRIMARY | SEQUENCE | SAME_UPDATE | 2023 | 1136 | 4 | 0.665 | 1.373 | 2.798 | 1.304 |
| PRIMARY | SEQUENCE | SAME_UPDATE | 2024 | 1144 | 4 | 0.5 | 1.207 | 2.615 | 1.357 |
| PRIMARY | SEQUENCE | CONSECUTIVE | ALL | 4835 | 10 | 0.641 | 1.459 | 2.817 | 1.605 |
| PRIMARY | SEQUENCE | CONSECUTIVE | 2023 | 2401 | 5 | 0.689 | 1.539 | 2.909 | 1.685 |
| PRIMARY | SEQUENCE | CONSECUTIVE | 2024 | 2434 | 5 | 0.623 | 1.416 | 2.705 | 1.562 |
| PRIMARY | SEQUENCE | BETWEEN_1_2 | ALL | 2556 | 10 | 0.818 | 1.815 | 3.379 | 1.776 |
| PRIMARY | SEQUENCE | BETWEEN_1_2 | 2023 | 1235 | 5 | 0.817 | 1.817 | 3.427 | 1.847 |
| PRIMARY | SEQUENCE | BETWEEN_1_2 | 2024 | 1321 | 5 | 0.819 | 1.814 | 3.348 | 1.759 |
| PRIMARY | SEQUENCE | BETWEEN_3_5 | ALL | 3846 | 10 | 0.779 | 1.79 | 3.443 | 1.953 |
| PRIMARY | SEQUENCE | BETWEEN_3_5 | 2023 | 1902 | 5 | 0.794 | 1.856 | 3.496 | 1.884 |
| PRIMARY | SEQUENCE | BETWEEN_3_5 | 2024 | 1944 | 5 | 0.763 | 1.732 | 3.373 | 2.022 |
| PRIMARY | SEQUENCE | BETWEEN_GT5 | ALL | 12920 | 10 | 1.065 | 2.38 | 4.172 | 2.487 |
| PRIMARY | SEQUENCE | BETWEEN_GT5 | 2023 | 6413 | 5 | 1.05 | 2.384 | 4.181 | 2.403 |
| PRIMARY | SEQUENCE | BETWEEN_GT5 | 2024 | 6507 | 5 | 1.08 | 2.378 | 4.162 | 2.571 |
| PRIMARY | SEQUENCE | NO_INTERVENING | ALL | 7115 | 10 | 0.62 | 1.423 | 2.78 | 1.512 |
| PRIMARY | SEQUENCE | NO_INTERVENING | 2023 | 3537 | 5 | 0.68 | 1.494 | 2.868 | 1.533 |
| PRIMARY | SEQUENCE | NO_INTERVENING | 2024 | 3578 | 5 | 0.576 | 1.362 | 2.676 | 1.491 |
| PRIMARY | TIMESTAMP_CARBLOCK_SEP | <=5s | ALL | 2706 | 10 | 0.518 | 1.25 | 2.521 | 1.483 |
| PRIMARY | TIMESTAMP_CARBLOCK_SEP | <=5s | 2023 | 1224 | 5 | 0.537 | 1.34 | 2.829 | 1.345 |
| PRIMARY | TIMESTAMP_CARBLOCK_SEP | <=5s | 2024 | 1482 | 5 | 0.513 | 1.202 | 2.35 | 1.738 |
| PRIMARY | TIMESTAMP_CARBLOCK_SEP | 5-15s | ALL | 2003 | 10 | 0.788 | 2.014 | 3.52 | 2.031 |
| PRIMARY | TIMESTAMP_CARBLOCK_SEP | 5-15s | 2023 | 970 | 5 | 0.788 | 2.017 | 3.544 | 2.082 |
| PRIMARY | TIMESTAMP_CARBLOCK_SEP | 5-15s | 2024 | 1033 | 5 | 0.795 | 2.007 | 3.517 | 1.98 |
| PRIMARY | TIMESTAMP_CARBLOCK_SEP | 15-60s | ALL | 8705 | 10 | 0.758 | 1.731 | 3.283 | 1.859 |
| PRIMARY | TIMESTAMP_CARBLOCK_SEP | 15-60s | 2023 | 4326 | 5 | 0.787 | 1.767 | 3.288 | 1.89 |
| PRIMARY | TIMESTAMP_CARBLOCK_SEP | 15-60s | 2024 | 4379 | 5 | 0.719 | 1.698 | 3.277 | 1.828 |
| PRIMARY | TIMESTAMP_CARBLOCK_SEP | 60-300s | ALL | 13023 | 10 | 1.024 | 2.272 | 4.068 | 2.334 |
| PRIMARY | TIMESTAMP_CARBLOCK_SEP | 60-300s | 2023 | 6567 | 5 | 1.015 | 2.276 | 4.051 | 2.446 |
| PRIMARY | TIMESTAMP_CARBLOCK_SEP | 60-300s | 2024 | 6456 | 5 | 1.029 | 2.27 | 4.095 | 2.037 |
| ERA_C_SECONDARY | SEQUENCE | SAME_UPDATE | ALL | 826 | 5 | 0.668 | 1.637 | 3.29 | 1.628 |
| ERA_C_SECONDARY | SEQUENCE | SAME_UPDATE | 2025 | 826 | 5 | 0.668 | 1.637 | 3.29 | 1.628 |
| ERA_C_SECONDARY | SEQUENCE | CONSECUTIVE | ALL | 1795 | 7 | 0.795 | 1.96 | 3.575 | 1.968 |
| ERA_C_SECONDARY | SEQUENCE | CONSECUTIVE | 2025 | 1795 | 7 | 0.795 | 1.96 | 3.575 | 1.968 |
| ERA_C_SECONDARY | SEQUENCE | BETWEEN_1_2 | ALL | 917 | 6 | 1.074 | 2.231 | 3.963 | 2.217 |
| ERA_C_SECONDARY | SEQUENCE | BETWEEN_1_2 | 2025 | 917 | 6 | 1.074 | 2.231 | 3.963 | 2.217 |
| ERA_C_SECONDARY | SEQUENCE | BETWEEN_3_5 | ALL | 1257 | 5 | 1.067 | 2.33 | 4.106 | 2.387 |
| ERA_C_SECONDARY | SEQUENCE | BETWEEN_3_5 | 2025 | 1257 | 5 | 1.067 | 2.33 | 4.106 | 2.387 |
| ERA_C_SECONDARY | SEQUENCE | BETWEEN_GT5 | ALL | 4261 | 7 | 1.247 | 2.672 | 4.775 | 2.603 |
| ERA_C_SECONDARY | SEQUENCE | BETWEEN_GT5 | 2025 | 4261 | 7 | 1.247 | 2.672 | 4.775 | 2.603 |
| ERA_C_SECONDARY | SEQUENCE | NO_INTERVENING | ALL | 2621 | 7 | 0.75 | 1.859 | 3.455 | 1.96 |
| ERA_C_SECONDARY | SEQUENCE | NO_INTERVENING | 2025 | 2621 | 7 | 0.75 | 1.859 | 3.455 | 1.96 |
| ERA_C_SECONDARY | TIMESTAMP_CARBLOCK_SEP | <=5s | ALL | 997 | 5 | 0.647 | 1.664 | 3.262 | 1.526 |
| ERA_C_SECONDARY | TIMESTAMP_CARBLOCK_SEP | <=5s | 2025 | 997 | 5 | 0.647 | 1.664 | 3.262 | 1.526 |
| ERA_C_SECONDARY | TIMESTAMP_CARBLOCK_SEP | 5-15s | ALL | 731 | 6 | 1.045 | 2.063 | 3.803 | 2.102 |
| ERA_C_SECONDARY | TIMESTAMP_CARBLOCK_SEP | 5-15s | 2025 | 731 | 6 | 1.045 | 2.063 | 3.803 | 2.102 |
| ERA_C_SECONDARY | TIMESTAMP_CARBLOCK_SEP | 15-60s | ALL | 2938 | 7 | 0.992 | 2.279 | 4.074 | 2.13 |
| ERA_C_SECONDARY | TIMESTAMP_CARBLOCK_SEP | 15-60s | 2025 | 2938 | 7 | 0.992 | 2.279 | 4.074 | 2.13 |
| ERA_C_SECONDARY | TIMESTAMP_CARBLOCK_SEP | 60-300s | ALL | 4390 | 7 | 1.151 | 2.535 | 4.49 | 2.434 |
| ERA_C_SECONDARY | TIMESTAMP_CARBLOCK_SEP | 60-300s | 2025 | 4390 | 7 | 1.151 | 2.535 | 4.49 | 2.434 |

**Within-target paired diagnostic** (median D(>5 between) − median D(no intervening), per target, holding the block and target fixed):

| role | scope | n_pairs | n_sessions | D_median | D_session_balanced_median | share_positive |
|---|---|---|---|---|---|---|
| PRIMARY | ALL | 1748 | 10 | 0.777 | 0.695 | 0.731 |
| PRIMARY | 2023 | 939 | 5 | 0.715 | 0.674 | 0.705 |
| PRIMARY | 2024 | 809 | 5 | 0.827 | 0.715 | 0.761 |
| ERA_C_SECONDARY | ALL | 660 | 6 | 0.808 | 0.801 | 0.695 |
| ERA_C_SECONDARY | 2025 | 660 | 6 | 0.808 | 0.801 | 0.695 |

**Per-session contrast** (primary and 2025):

| role | session | n_no_intervening | n_gt5 | D_gt5_minus_D_no_intervening | eligible_for_S2_session_rule |
|---|---|---|---|---|---|
| PRIMARY | 6198 | 950 | 1969 | 1.245 | True |
| PRIMARY | 6199 | 768 | 1035 | 0.827 | True |
| PRIMARY | 6200 | 6 | 10 | 1.073 | True |
| PRIMARY | 6207 | 728 | 1207 | 0.615 | True |
| PRIMARY | 6208 | 1085 | 2192 | 0.887 | True |
| PRIMARY | 6375 | 16 | 62 | -0.028 | True |
| PRIMARY | 6378 | 766 | 1603 | 1.071 | True |
| PRIMARY | 6380 | 6 | 22 | -0.118 | True |
| PRIMARY | 6387 | 1367 | 2325 | 1.08 | True |
| PRIMARY | 6388 | 1423 | 2495 | 1.005 | True |
| ERA_C_SECONDARY | 6651 | 223 | 289 | 1.118 | True |
| ERA_C_SECONDARY | 6653 | 126 | 341 | 0.754 | True |
| ERA_C_SECONDARY | 6654 | 462 | 361 | 1.032 | True |
| ERA_C_SECONDARY | 6655 | 1 | 1 | -0.05 | False |
| ERA_C_SECONDARY | 6657 | 5 | 12 | 0.132 | True |
| ERA_C_SECONDARY | 6662 | 869 | 1768 | 0.75 | True |
| ERA_C_SECONDARY | 6663 | 935 | 1489 | 0.629 | True |

**Readings:**
- **Primary, session-balanced median D:** same update 1.348, consecutive 1.605, 1–2 between 1.776, 3–5 between 1.953, >5 between 2.487 mph.
- **Different-team cars that are timing-adjacent are more similar** in observed local performance than less-adjacent ones:
  - Δ_S2 = 0.975 mph;
  - positive in 2023 (0.869) and 2024 (1.080);
  - positive in 0.800 of eligible sessions; the two exceptions are small sessions, 2024 Practice 1 and Fast Friday;
  - positive within target (0.695);
  - also present in 2025 (0.643).
- **The timestamp-bin gradient** (car-block median time, the Phase 4F bins) **is not monotone:** ≤5 s is lowest, but 5–15 s is higher than 15–60 s. Car-block median-time separation is a coarser proxy than lap-level sequence adjacency.

## Direction of dependence is not identified

- **One direction:** timing adjacency may reflect shared local on-track context that makes speeds similar.
- **The reverse direction:** two cars can only **stay** near-consecutive across several laps if their lap times are similar. Sustained adjacency is partly a *consequence* of similar speed.
- **Either way,** choosing the control by nearest car-block time conditions on a variable that is associated with the outcome D. That is the concrete control-selection property identified here.

## Observed vs not observed (4G.13)

**OBSERVED:** two cars' lap records appeared in the same Timing71 feed update, or with few intervening records. That means they crossed the timing line close together in time and order, at about 1.7 s feed resolution.

**NOT OBSERVED:**
- whether one car was physically towing another;
- the exact physical gap;
- the order within a feed update;
- the traffic configuration around the full lap;
- aerodynamic interaction;
- run purpose.

Timing-sequence adjacency is consistent with shared local on-track context but does not identify tow.
