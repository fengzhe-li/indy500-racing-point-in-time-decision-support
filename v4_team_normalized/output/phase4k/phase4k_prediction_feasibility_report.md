# V4 Phase 4K — Point-in-Time Teammate Prediction Feasibility Report

**Pre-specification:** `phase4k_prediction_feasibility_spec.md`, committed as **`dae6856`** before any event count. Its rules were applied without change.

**What was not done:**
- no prediction, error, fitting, λ or predictor comparison;
- Δv_target was never computed;
- Phase 4J (FINAL, CASE B) is unchanged and not revisited.

## Headline: primary feasibility CASE C (weak support)

**Phase 4L:** NO Phase 4L.

**Primary population:** Tier 1 (class A), 2023–24, the 8 Phase 4I-supported practice sessions.
- **F0:** 113 canonical target events (one per future target observation), from 57 target cars, 12 teams and 8 sessions.
- **F5** (leakage-free, with a structurally comparable different-team placebo): **8 events**, from 5 sessions, 6 teams and 8 cars.

**Why F5 is small:**
- Of the 22 F4 events, 14 fail because the frozen class-A label of t0 **cannot be confirmed point-in-time**.
- The Phase 4H rule needs 4-lap windows that extend after t0. For same-stint targets those windows run into t1's own laps.
- The F5 survivors are therefore mostly cross-stint events with long baselines: median t0→t1 about 35 min.
- **Under the conservative cutoff** (prediction at t0's completion), F5 = 0 in every population. At t0's completion its own label can never be confirmed.

## Attrition

| population | cutoff | level | events | sessions | target_cars | target_teams | lost_from_previous | retained_share_of_F0 |
|---|---|---|---|---|---|---|---|---|
| PRIMARY_TIER1_2023_2024 | CONSERVATIVE | F0 | 113 | 8 | 57 | 12 | 0 | 1 |
| PRIMARY_TIER1_2023_2024 | CONSERVATIVE | F1 | 113 | 8 | 57 | 12 | 0 | 1 |
| PRIMARY_TIER1_2023_2024 | CONSERVATIVE | F2 | 57 | 7 | 38 | 11 | 56 | 0.504 |
| PRIMARY_TIER1_2023_2024 | CONSERVATIVE | F3 | 36 | 6 | 26 | 9 | 21 | 0.319 |
| PRIMARY_TIER1_2023_2024 | CONSERVATIVE | F4 | 18 | 5 | 17 | 8 | 18 | 0.159 |
| PRIMARY_TIER1_2023_2024 | CONSERVATIVE | F5 | 0 | 0 | 0 | 0 | 18 | 0 |
| PRIMARY_TIER1_2023_2024 | PRIMARY | F0 | 113 | 8 | 57 | 12 | 0 | 1 |
| PRIMARY_TIER1_2023_2024 | PRIMARY | F1 | 113 | 8 | 57 | 12 | 0 | 1 |
| PRIMARY_TIER1_2023_2024 | PRIMARY | F2 | 71 | 7 | 46 | 11 | 42 | 0.628 |
| PRIMARY_TIER1_2023_2024 | PRIMARY | F3 | 44 | 6 | 31 | 10 | 27 | 0.389 |
| PRIMARY_TIER1_2023_2024 | PRIMARY | F4 | 22 | 5 | 21 | 9 | 22 | 0.195 |
| PRIMARY_TIER1_2023_2024 | PRIMARY | F5 | 8 | 5 | 8 | 6 | 14 | 0.071 |
| TIER2_2023_2024_EXTENDED | CONSERVATIVE | F0 | 258 | 10 | 65 | 12 | 0 | 1 |
| TIER2_2023_2024_EXTENDED | CONSERVATIVE | F1 | 258 | 10 | 65 | 12 | 0 | 1 |
| TIER2_2023_2024_EXTENDED | CONSERVATIVE | F2 | 159 | 10 | 59 | 11 | 99 | 0.616 |
| TIER2_2023_2024_EXTENDED | CONSERVATIVE | F3 | 103 | 9 | 51 | 11 | 56 | 0.399 |
| TIER2_2023_2024_EXTENDED | CONSERVATIVE | F4 | 46 | 8 | 31 | 11 | 57 | 0.178 |
| TIER2_2023_2024_EXTENDED | CONSERVATIVE | F5 | 0 | 0 | 0 | 0 | 46 | 0 |
| TIER2_2023_2024_EXTENDED | PRIMARY | F0 | 258 | 10 | 65 | 12 | 0 | 1 |
| TIER2_2023_2024_EXTENDED | PRIMARY | F1 | 258 | 10 | 65 | 12 | 0 | 1 |
| TIER2_2023_2024_EXTENDED | PRIMARY | F2 | 193 | 10 | 60 | 11 | 65 | 0.748 |
| TIER2_2023_2024_EXTENDED | PRIMARY | F3 | 129 | 9 | 56 | 11 | 64 | 0.5 |
| TIER2_2023_2024_EXTENDED | PRIMARY | F4 | 66 | 8 | 38 | 11 | 63 | 0.256 |
| TIER2_2023_2024_EXTENDED | PRIMARY | F5 | 36 | 8 | 27 | 9 | 30 | 0.14 |
| TIER1_2025_SECONDARY | CONSERVATIVE | F0 | 94 | 6 | 31 | 12 | 0 | 1 |
| TIER1_2025_SECONDARY | CONSERVATIVE | F1 | 94 | 6 | 31 | 12 | 0 | 1 |
| TIER1_2025_SECONDARY | CONSERVATIVE | F2 | 48 | 6 | 25 | 11 | 46 | 0.511 |
| TIER1_2025_SECONDARY | CONSERVATIVE | F3 | 29 | 6 | 21 | 11 | 19 | 0.309 |
| TIER1_2025_SECONDARY | CONSERVATIVE | F4 | 12 | 4 | 9 | 5 | 17 | 0.128 |
| TIER1_2025_SECONDARY | CONSERVATIVE | F5 | 0 | 0 | 0 | 0 | 12 | 0 |
| TIER1_2025_SECONDARY | PRIMARY | F0 | 94 | 6 | 31 | 12 | 0 | 1 |
| TIER1_2025_SECONDARY | PRIMARY | F1 | 94 | 6 | 31 | 12 | 0 | 1 |
| TIER1_2025_SECONDARY | PRIMARY | F2 | 55 | 6 | 25 | 11 | 39 | 0.585 |
| TIER1_2025_SECONDARY | PRIMARY | F3 | 35 | 6 | 21 | 11 | 20 | 0.372 |
| TIER1_2025_SECONDARY | PRIMARY | F4 | 12 | 4 | 9 | 5 | 23 | 0.128 |
| TIER1_2025_SECONDARY | PRIMARY | F5 | 3 | 3 | 3 | 3 | 9 | 0.032 |

## Physical inputs and forecast vintages

| population | events_F0 | realized_environment_t0_t1 | t1_reading_point_in_time_known | resolved_physical_change | same_reading_zero_change | frozen_beta_mechanically_applicable | genuine_forecast_vintage_events | note |
|---|---|---|---|---|---|---|---|---|
| PRIMARY_TIER1_2023_2024 | 113 | 113 | 113 | 45 | 68 | 113 | 0 | PTSC 15-min observed readings (latest at/before time, age<=15 min); no forecast vintages in frozen evidence (HRRR not retrieved); wind unit unverified -> unused |
| TIER2_2023_2024_EXTENDED | 258 | 258 | 258 | 133 | 125 | 258 | 0 | PTSC 15-min observed readings (latest at/before time, age<=15 min); no forecast vintages in frozen evidence (HRRR not retrieved); wind unit unverified -> unused |
| TIER1_2025_SECONDARY | 94 | 94 | 94 | 34 | 60 | 94 | 0 | PTSC 15-min observed readings (latest at/before time, age<=15 min); no forecast vintages in frozen evidence (HRRR not retrieved); wind unit unverified -> unused |

**Readings:**
- Every event has realised PTSC track and ambient readings at t0 and t1, so the frozen β is mechanically applicable to all F1 events. It is **not** validated for practice.
- **Resolved change:** only 45 of 113 events have a *measured* physical change (distinct 15-min readings). The rest share one reading, so Δ = 0 at archive resolution.
- **Genuine forecast vintages: 0.** None exist in the frozen evidence. Any later experiment would condition on the **realised** environment and would not be a deployable forecast.

## Model-free support

| population | cutoff | F4 | F4_model_free_exact | F4_model_free_matched | F5 | F5_model_free_exact | F5_model_free_matched | note |
|---|---|---|---|---|---|---|---|---|
| PRIMARY_TIER1_2023_2024 | CONSERVATIVE | 18 | 12 | 5 | 0 | 0 | 0 | EXACT = no measured PTSC change within target, teammate and placebo intervals; MATCHED = identical PTSC reading pairs across all three intervals |
| PRIMARY_TIER1_2023_2024 | PRIMARY | 22 | 13 | 6 | 8 | 3 | 2 | EXACT = no measured PTSC change within target, teammate and placebo intervals; MATCHED = identical PTSC reading pairs across all three intervals |
| TIER2_2023_2024_EXTENDED | CONSERVATIVE | 46 | 20 | 7 | 0 | 0 | 0 | EXACT = no measured PTSC change within target, teammate and placebo intervals; MATCHED = identical PTSC reading pairs across all three intervals |
| TIER2_2023_2024_EXTENDED | PRIMARY | 66 | 20 | 7 | 36 | 4 | 1 | EXACT = no measured PTSC change within target, teammate and placebo intervals; MATCHED = identical PTSC reading pairs across all three intervals |
| TIER1_2025_SECONDARY | CONSERVATIVE | 12 | 7 | 3 | 0 | 0 | 0 | EXACT = no measured PTSC change within target, teammate and placebo intervals; MATCHED = identical PTSC reading pairs across all three intervals |
| TIER1_2025_SECONDARY | PRIMARY | 12 | 7 | 3 | 3 | 1 | 1 | EXACT = no measured PTSC change within target, teammate and placebo intervals; MATCHED = identical PTSC reading pairs across all three intervals |

## Case evaluation

| criterion | value |
|---|---|
| N5 | 8 |
| S5 | 5 |
| K5 | 6 |
| C5 | 8 |
| Y5 | 2 |
| MS | 0.375 |
| MT | 0.25 |
| MP | 0.07692307692307693 |
| PRIMARY_FEASIBILITY_CASE | C |
| spec_commit | dae6856 |
| phase4l_gate | NO Phase 4L |
| TIER2_2023_2024_EXTENDED_label | B [secondary; never changes primary] |
| TIER1_2025_SECONDARY_label | C [secondary; never changes primary] |

## Phase 4L gate

**CASE C:** a Phase 4L predictive experiment is **not justified**. Phase 4L is not run.

The Tier 2 extended population reaches the B thresholds (36 F5 events, 8 sessions). By pre-registration it is secondary and **cannot rescue** the Tier 1 primary.
