# V4 Phase 4H — Run-State Report (Phase 4F/4G population audit)

## Evidence tiers

| Tier | Contents |
|---|---|
| **Directly observed** | lap flag; pit exit/entry feed messages (practice stint starts matched 71.1%; ends 75.5%; qualifying stints 0.0%, i.e. not pit-bounded); lap time; feed-update timestamp |
| **Inferred proxy** | out/in-laps at unmatched stint boundaries; build, pre-in and restart laps; capture gaps; steady-state windows; level vs the car's own best |
| **Unknown** | fuel, tyres, setup, boost within session, run purpose, tow/traffic, driver intent |

## Phase 4F car-blocks and comparison populations (4H.9)

The class of each Phase 4F comparable-layer car-block is its modal lap class.

| role | car_blocks | carblock_share_A | carblock_share_B | carblock_share_C | carblock_share_D | carblock_share_E |
|---|---|---|---|---|---|---|
| PRIMARY | 2890 | 0.098 | 0.035 | 0.749 | 0 | 0.118 |
| ERA_C_SECONDARY | 1323 | 0.13 | 0.036 | 0.698 | 0 | 0.136 |

| role | population | n_pairs | share_matched | share_mismatched | share_both_A | share_both_AB | share_involves_C_ambiguous | share_involves_D_or_E | target_share_A | comparator_share_A |
|---|---|---|---|---|---|---|---|---|---|---|
| ERA_C_SECONDARY | A_PRIMARY_CONTROL | 762 | 0.686 | 0.314 | 0.029 | 0.055 | 0.903 | 0.14 | 0.096 | 0.125 |
| ERA_C_SECONDARY | B_ELIGIBLE_CANDIDATES | 9056 | 0.656 | 0.344 | 0.014 | 0.028 | 0.94 | 0.154 | 0.091 | 0.094 |
| ERA_C_SECONDARY | C1_TEAMMATE_OF_TARGET | 762 | 0.678 | 0.322 | 0.018 | 0.035 | 0.937 | 0.139 | 0.096 | 0.092 |
| ERA_C_SECONDARY | C2_ALL_TEAMMATES | 1086 | 0.691 | 0.309 | 0.018 | 0.033 | 0.941 | 0.129 | 0.091 | 0.091 |
| PRIMARY | A_PRIMARY_CONTROL | 1937 | 0.693 | 0.307 | 0.014 | 0.022 | 0.933 | 0.16 | 0.081 | 0.081 |
| PRIMARY | B_ELIGIBLE_CANDIDATES | 26437 | 0.685 | 0.315 | 0.013 | 0.021 | 0.948 | 0.151 | 0.079 | 0.081 |
| PRIMARY | C1_TEAMMATE_OF_TARGET | 1937 | 0.696 | 0.304 | 0.017 | 0.026 | 0.925 | 0.162 | 0.081 | 0.082 |
| PRIMARY | C2_ALL_TEAMMATES | 3278 | 0.703 | 0.297 | 0.014 | 0.024 | 0.931 | 0.157 | 0.076 | 0.076 |
| PRIMARY | TEAM_BALANCED_DIFF | 17411 | 0.65 | 0.35 | 0.014 | 0.021 | 0.936 | 0.193 | 0.086 | 0.086 |

**Readings:**
- About 93.3% of the Phase 4F primary target–control pairs involve at least one run-state-ambiguous car-block.
- Only 1.4% are A on both sides, and 2.2% are A/B on both sides.
- "Same class" (69.3%) is mostly C = C, which is uninformative because C is the residual category.
- Teammate, pool and team-balanced populations look the same.
- **Most of the observed dispersion in Phases 4F/4G is therefore measured on car-blocks whose run state cannot be established.**

## Timing adjacency vs run state (4H.8)

| role | stratum | n_pairs | share_matched | share_both_A | share_both_AB | share_involves_C | D_sb_median_ALL | D_sb_median_RUNSTATE_MATCHED | n_RUNSTATE_MATCHED | D_sb_median_RUNSTATE_MISMATCHED | D_sb_median_BOTH_A | n_BOTH_A |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PRIMARY | SAME_UPDATE | 2280 | 0.796 | 0.008 | 0.014 | 0.972 | 1.348 | 1.224 | 1816 | 1.826 | 0.885 | 18 |
| PRIMARY | CONSECUTIVE | 4835 | 0.763 | 0.009 | 0.016 | 0.968 | 1.605 | 1.533 | 3690 | 1.821 | 1.012 | 44 |
| PRIMARY | BETWEEN_1_2 | 2556 | 0.672 | 0.016 | 0.029 | 0.946 | 1.776 | 1.752 | 1717 | 2.088 | 1.42 | 40 |
| PRIMARY | BETWEEN_3_5 | 3846 | 0.699 | 0.012 | 0.02 | 0.957 | 1.953 | 1.935 | 2687 | 2.126 | 1.542 | 48 |
| PRIMARY | BETWEEN_GT5 | 12920 | 0.635 | 0.014 | 0.023 | 0.935 | 2.487 | 2.44 | 8205 | 2.709 | 1.355 | 184 |
| PRIMARY | NO_INTERVENING | 7115 | 0.774 | 0.009 | 0.016 | 0.97 | 1.512 | 1.461 | 5506 | 1.771 | 0.833 | 62 |
| ERA_C_SECONDARY | SAME_UPDATE | 826 | 0.781 | 0.019 | 0.031 | 0.955 | 1.628 | 1.603 | 645 | 1.745 | 1.063 | 16 |
| ERA_C_SECONDARY | CONSECUTIVE | 1795 | 0.753 | 0.012 | 0.029 | 0.958 | 1.968 | 1.993 | 1351 | 1.807 | 1.017 | 22 |
| ERA_C_SECONDARY | BETWEEN_1_2 | 917 | 0.632 | 0.021 | 0.038 | 0.915 | 2.217 | 2.398 | 580 | 1.947 | 1.227 | 19 |
| ERA_C_SECONDARY | BETWEEN_3_5 | 1257 | 0.686 | 0.014 | 0.03 | 0.954 | 2.387 | 2.491 | 862 | 2.261 | 2.358 | 17 |
| ERA_C_SECONDARY | BETWEEN_GT5 | 4261 | 0.587 | 0.012 | 0.024 | 0.931 | 2.603 | 2.949 | 2502 | 2.368 | 2.146 | 50 |
| ERA_C_SECONDARY | NO_INTERVENING | 2621 | 0.762 | 0.014 | 0.03 | 0.957 | 1.96 | 1.969 | 1996 | 1.807 | 1.269 | 38 |

**Adjacency gradient** (D(>5 between) − D(no intervening)) within run-state subsets:

| role | stratum | n_pairs | n_no_intervening | n_gt5 | D_sb_no_intervening | D_sb_gt5 | gradient_gt5_minus_no_intervening |
|---|---|---|---|---|---|---|---|
| PRIMARY | ALL|ALL | 26437 | 7115 | 12920 | 1.512 | 2.487 | 0.975 |
| PRIMARY | ALL|2023 | 13087 | 3537 | 6413 | 1.533 | 2.403 | 0.869 |
| PRIMARY | ALL|2024 | 13350 | 3578 | 6507 | 1.491 | 2.571 | 1.08 |
| PRIMARY | BOTH_A|ALL | 334 | 62 | 184 | 0.833 | 1.355 | 0.522 |
| PRIMARY | BOTH_A|2023 | 78 | 12 | 48 | 0.816 | 1.465 | 0.649 |
| PRIMARY | BOTH_A|2024 | 256 | 50 | 136 | 0.85 | 1.355 | 0.505 |
| PRIMARY | RUNSTATE_MATCHED|ALL | 18115 | 5506 | 8205 | 1.461 | 2.44 | 0.979 |
| PRIMARY | RUNSTATE_MATCHED|2023 | 8850 | 2765 | 3995 | 1.424 | 2.428 | 1.004 |
| PRIMARY | RUNSTATE_MATCHED|2024 | 9265 | 2741 | 4210 | 1.467 | 2.451 | 0.984 |
| PRIMARY | RUNSTATE_MISMATCHED|ALL | 8322 | 1609 | 4715 | 1.771 | 2.709 | 0.938 |
| PRIMARY | RUNSTATE_MISMATCHED|2023 | 4237 | 772 | 2418 | 2.006 | 2.874 | 0.869 |
| PRIMARY | RUNSTATE_MISMATCHED|2024 | 4085 | 837 | 2297 | 1.61 | 2.295 | 0.685 |
| ERA_C_SECONDARY | ALL|ALL | 9056 | 2621 | 4261 | 1.96 | 2.603 | 0.643 |
| ERA_C_SECONDARY | ALL|2025 | 9056 | 2621 | 4261 | 1.96 | 2.603 | 0.643 |
| ERA_C_SECONDARY | BOTH_A|ALL | 124 | 38 | 50 | 1.269 | 2.146 | 0.876 |
| ERA_C_SECONDARY | BOTH_A|2025 | 124 | 38 | 50 | 1.269 | 2.146 | 0.876 |
| ERA_C_SECONDARY | RUNSTATE_MATCHED|ALL | 5940 | 1996 | 2502 | 1.969 | 2.949 | 0.98 |
| ERA_C_SECONDARY | RUNSTATE_MATCHED|2025 | 5940 | 1996 | 2502 | 1.969 | 2.949 | 0.98 |
| ERA_C_SECONDARY | RUNSTATE_MISMATCHED|ALL | 3116 | 625 | 1759 | 1.807 | 2.368 | 0.561 |
| ERA_C_SECONDARY | RUNSTATE_MISMATCHED|2025 | 3116 | 625 | 1759 | 1.807 | 2.368 | 0.561 |

**Readings** (descriptive; no mediation claimed):
- **Adjacent pairs share a run-state class more often:** in 2023–24, 79.6% for same-update pairs vs 63.5% for pairs more than 5 records apart. So *adjacency → similar run state → lower D* is plausible as part of the picture.
- **The Phase 4G gradient does not disappear when the coarse class is held equal:**
  - within matched pairs: 0.979 mph;
  - within mismatched pairs: 0.938 mph;
  - within both-A pairs: 0.522 mph (n = 334 pairs; small).
- **But the classifier leaves about 75% of car-blocks in the residual C class.** Holding "C = C" equal does not hold run state equal.
- **Conclusion:** the data cannot separate a pure adjacency phenomenon from run-state matching. The Phase 4G association is **materially compatible** with run-state composition and is not identified as a pure adjacency effect.

## Qualifying negative control (4H.10)

| role | n_pairs | n_no_intervening | n_gt5 | qualifying_carblocks | blocks_with_2plus_cars | identifiable | note |
|---|---|---|---|---|---|---|---|
| 2023_2024 | 10 | 0 | 0 | 142 | 13 | False | NOT IDENTIFIABLE (<30 pairs in a stratum); single-car qualifying structure |
| 2025 | 23 | 0 | 0 | 103 | 24 | False | NOT IDENTIFIABLE (<30 pairs in a stratum); single-car qualifying structure |

**NOT IDENTIFIABLE.** Indianapolis qualifying is run one car at a time, so different-team cars almost never share a 5-min block with laps in either adjacency stratum. No comparison was manufactured.
