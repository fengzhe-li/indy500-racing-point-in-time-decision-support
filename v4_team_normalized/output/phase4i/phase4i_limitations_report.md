# V4 Phase 4I — Limitations Report

## Era coverage (4I.12)

| period | source | temporal_resolution | phase4e_tier | phase4h_classifier_applied | lap_level_hierarchy_support | contributes | tier | eligible_laps | eligible_carblocks | sessions | cars | teams | same_team_pairs | diff_team_pairs | sessions_all_three_block_scale |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2018-2021 | Timing71 legacy analysis files | stint-level timestamps only; lap times; derived lap timestamps inconsistent | D (all sessions) | False | NONE (not lap-level comparable; classifier not projected backwards) | registry / team identity; longitudinal context; session-level indicative summaries only |  |  |  |  |  |  |  |  |  |
| 2022 | official INDYCAR session records only (no Timing71 lap data retrieved) | session-level only | D | False | NONE | registry / team identity; session-level results context |  |  |  |  |  |  |  |  |  |
| 2023 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | lap-level; feed-update timestamps (~1.67 s) | A/B sessions only | True | PRIMARY (2023-2024) |  | TIER1_STRICT | 688 | 219 | 6 | 34 | 12 | 23 | 164 | 3 |
| 2024 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | lap-level; feed-update timestamps (~1.67 s) | A/B sessions only | True | PRIMARY (2023-2024) |  | TIER1_STRICT | 484 | 155 | 5 | 34 | 11 | 23 | 258 | 5 |
| 2025 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | lap-level; feed-update timestamps (~1.67 s) | A/B sessions only | True | SECONDARY (separate; not Design-1 feasible in Phase 4E) |  | TIER1_STRICT | 695 | 243 | 8 | 33 | 12 | 20 | 224 | 6 |
| 2023 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | lap-level; feed-update timestamps (~1.67 s) | A/B sessions only | True | PRIMARY (2023-2024) |  | TIER2_EXTENDED | 970 | 302 | 6 | 34 | 12 | 34 | 343 | 5 |
| 2024 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | lap-level; feed-update timestamps (~1.67 s) | A/B sessions only | True | PRIMARY (2023-2024) |  | TIER2_EXTENDED | 713 | 225 | 5 | 34 | 11 | 50 | 480 | 5 |
| 2025 | TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing) | lap-level; feed-update timestamps (~1.67 s) | A/B sessions only | True | SECONDARY (separate; not Design-1 feasible in Phase 4E) |  | TIER2_EXTENDED | 952 | 317 | 8 | 34 | 12 | 38 | 420 | 6 |

**What the eras contribute:**
- **2018–2022:** the eight-year registry and longitudinal team identity. These years provide **no lap-level eligible evidence**: 2018–2021 have stint-level timestamps only, 2022 has session-level records only, and the Phase 4H classifier is not projected backwards.
- **2023–2025:** all hierarchy-relevant support. 2023–2024 is primary; 2025 is secondary and separate.

## Measurement scale (4I.13; descriptive)

| reference | scope | n_units | median_sd_mph | median_range_mph | p90_range_mph | median_speed_mph | median_sd_pct | median_range_pct | median_abs_delta_mph | p90_abs_delta_mph | median_abs_delta_pct | p90_sd_mph | note | median_sd_laptime_equiv_s_at_225 | median_range_laptime_equiv_s_at_225 | median_abs_delta_laptime_equiv_s_at_225 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| QUALIFYING_OFFICIAL_WITHIN_ATTEMPT | 2023 | 43 | 0.586 | 1.326 | 2.183 | 232.868 | 0.251 | 0.57 |  |  |  |  |  | 0.104 | 0.236 |  |
| QUALIFYING_OFFICIAL_WITHIN_ATTEMPT | 2024 | 24 | 0.373 | 0.845 | 1.716 | 232.333 | 0.16 | 0.364 |  |  |  |  |  | 0.066 | 0.15 |  |
| SAME_CAR_A_WITHIN_CARBLOCK | 2023_2024_PRIMARY | 319 | 0.579 | 1.255 | 1.944 | 221.372 | 0.262 | 0.567 |  |  |  |  |  | 0.103 | 0.223 |  |
| SAME_CAR_A_CONSECUTIVE_LAP_ABS_DELTA | 2023_2024_PRIMARY | 904 |  |  |  | 221.372 |  |  | 0.509 | 1.487 | 0.23 |  |  |  |  | 0.09 |
| SAME_CAR_A_CROSS_SESSION_SD_OF_SESSION_MEDIANS | 2023_2024_PRIMARY | 67 | 2.701 |  |  | 221.372 | 1.22 |  |  |  |  | 6.006 |  | 0.48 |  |  |
| SAME_CAR_A_WITHIN_CARBLOCK | 2025_SECONDARY | 182 | 0.52 | 1.111 | 1.894 | 219.589 | 0.237 | 0.506 |  |  |  |  |  | 0.093 | 0.197 |  |
| SAME_CAR_A_CONSECUTIVE_LAP_ABS_DELTA | 2025_SECONDARY | 530 |  |  |  | 219.589 |  |  | 0.457 | 1.428 | 0.208 |  |  |  |  | 0.081 |
| SAME_CAR_A_CROSS_SESSION_SD_OF_SESSION_MEDIANS | 2025_SECONDARY | 32 | 5.279 |  |  | 219.589 | 2.404 |  |  |  |  | 6.839 |  | 0.938 |  |  |
| LAPTIME_PRECISION | 1e-4 s recorded precision |  | 0.001 |  |  | 225 |  |  |  |  |  |  | speed change for a 0.0001 s lap-time change at 225 mph | 0 |  |  |
| TIMESTAMP_RESOLUTION | Timing71 feed update |  |  |  |  |  |  |  |  |  |  |  | ~1.67 s feed-update cycle (Phase 4G); lap times themselves are not affected |  |  |  |

**Readings:**
- **Qualifying within-attempt SD:** about 0.4–0.6 mph (0.16–0.25%).
- **Class-A same-car within-car-block SD:** about 0.5–0.6 mph.
- **Consecutive-lap |Δ|:** median about 0.5 mph (about 0.09 s of lap time).
- **Same-car cross-session SD of session medians:** 2.7 mph (2023–24) and 5.3 mph (2025). Session conditions and run programmes change more than local repeat noise.
- **Recorded precision** (0.0006 mph) is not limiting.
- No minimum meaningful difference and no power calculation.

## Limitations

1. **Tier 1 is strict by construction.** Phase 4H class A is narrow and was not loosened, so absolute support is small, especially for same-team pairs.
2. **Tier 2 is lower quality.** It mixes A and B; about two-thirds of its pairs involve B or mixed car-blocks.
3. **Adjacency.** Common support within the closest adjacency strata (same update / consecutive) is sparse. A future adjacency-balanced design would lose most of those strata.
4. **Unobserved variables.** Run purpose, fuel, tyres, tow and traffic remain unobserved even for class A.
5. **Session clusters.** There are only 11 primary sessions (8 in 2025), so between-session dependence dominates.
6. **Scope.** Support counts do not imply a detectable or meaningful hierarchy effect, and no outcome was examined.
