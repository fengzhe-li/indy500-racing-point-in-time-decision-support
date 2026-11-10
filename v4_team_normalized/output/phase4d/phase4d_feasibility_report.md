# V4 Phase 4D — Latent Team-State / Residual-Attribution Feasibility Report

**Specification:** `phase4d_identifiability_spec.md`, committed as `7a817ae` before any context, category or alignment was computed. The rules were not changed afterwards.

**Scope:**
- No latent, state-space, Gaussian-process, factor or HMM model was fitted, and no coefficient was refitted.
- Phase 4C, FINAL_V2, V3 and the paper are untouched.
- The frozen full-data coefficients are only *applied* to teammate previous-attempt changes (spec §2).

**Anchors:** the 41 frozen 2020–2024 transitions. The target residual is the frozen `residual_loyo_raw` (= observed − frozen LOYO expected Δ). No in-sample full-model expected value is stored per transition in the frozen manifest; that is reported, not reconstructed. The frozen backtest median is carried as secondary context.

## 1–3. Coverage

| Level | Transitions |
|---|---|
| Frozen transitions | 41 |
| Target in primary layer with timed endpoints | 40 |
| Any timed teammate attempt anywhere in the session | **35** |
| Any frozen-independent teammate attempt (LEVEL) | **32** |
| Any teammate previous-attempt move (repeated teammate-car information) | **27** |
| Any frozen-independent teammate move | **1** |

- **Why moves are almost all frozen evidence:** across 2020–2024, the teammate previous-attempt moves available are 42 in total. Of these, **40 are themselves frozen transitions**. The remaining ones are 1 `UNKNOWN_DEPENDENCE` (2024 Ilott, link-uncertain) and 1 without weather (2024 Rossi, not physics-adjustable).
- **Consequence:** repeated teammate-car information in the reference era *is* the frozen core, seen from another car.

## 4–5. Structural categories by window (pre-declared rules)

| window | A | B | C | D |
|---|---|---|---|---|
| 15 | 0 | 0 | 32 | 9 |
| 30 | 0 | 0 | 33 | 8 |
| 45 | 0 | 2 | 31 | 8 |
| 60 | 0 | 3 | 30 | 8 |
| INTERVAL | 0 | 0 | 28 | 13 |

Transitions with move context, and how many of them are dominated by frozen-core reuse:

| window | with_move_context | dominated_by_frozen_reuse |
|---|---|---|
| 15 | 8 | 8 |
| 30 | 12 | 12 |
| 45 | 14 | 14 |
| 60 | 18 | 18 |
| INTERVAL | 2 | 2 |

**Category A: none at any window.** B appears only at ±45 (2) and ±60 (3), always from frozen-reciprocal moves of ≥2 cars.

## 6–7. Team-context movement estimates

- **At ±30:** S6 (car-balanced median physics-adjusted teammate move) is *defined* for 12 transitions, but every one rests on single-car, frozen-reciprocal moves (category C). **0 transitions** support a structurally identifiable team-context movement estimate at ±30.
- **Dominated by frozen-core reuse:** every transition with move context, at every window (table above).

## 8. Target-residual distribution (all 41; frozen LOYO residuals)

| n | mean | sd | min | q25 | median | q75 | max | abs_median |
|---|---|---|---|---|---|---|---|---|
| 41 | 0.317 | 1.025 | -1.193 | -0.18 | 0.08 | 0.472 | 4.697 | 0.293 |

## 9. Team-context summaries at ±30 (descriptive; where defined)

| summary | n_defined | median | abs_median | min | max |
|---|---|---|---|---|---|
| S1_centered_near_t1 | 22 | 0 | 0 | -0.231 | 0.204 |
| S2_centered_near_t2 | 17 | 0.123 | 0.123 | -0.077 | 0.543 |
| S3_centered_between | 28 | 0 | 0.039 | -0.709 | 0.321 |
| S4_nearest_move_adj | 12 | 0.02 | 0.185 | -0.456 | 0.565 |
| S5_median_adj_move | 12 | 0.067 | 0.225 | -0.456 | 0.565 |
| S6_car_balanced_median_adj_move | 12 | 0.067 | 0.225 | -0.456 | 0.565 |
| S6_IND | 0 |  |  |  |  |
| S8_common_car_centered_change | 7 | -0.002 | 0.154 | -0.154 | 0.901 |

## 10–12. Alignment (pre-declared labels)

| window | variant | INSUFFICIENT_TEAM_CONTEXT | MIXED_TEAM_CONTEXT | TARGET_CAR_ISOLATED | TEAM_CONTEXT_CONSISTENT |
|---|---|---|---|---|---|
| 15 | S4 | 41 | 0 | 0 | 0 |
| 15 | S6 | 41 | 0 | 0 | 0 |
| 15 | S6_IND | 41 | 0 | 0 | 0 |
| 30 | S4 | 41 | 0 | 0 | 0 |
| 30 | S6 | 41 | 0 | 0 | 0 |
| 30 | S6_IND | 41 | 0 | 0 | 0 |
| 45 | S4 | 39 | 0 | 1 | 1 |
| 45 | S6 | 39 | 2 | 0 | 0 |
| 45 | S6_IND | 41 | 0 | 0 | 0 |
| 60 | S4 | 38 | 0 | 1 | 2 |
| 60 | S6 | 38 | 2 | 0 | 1 |
| 60 | S6_IND | 41 | 0 | 0 | 0 |
| INTERVAL | S4 | 41 | 0 | 0 | 0 |
| INTERVAL | S6 | 41 | 0 | 0 | 0 |
| INTERVAL | S6_IND | 41 | 0 | 0 | 0 |

- **Primary (S6, ±30):** all 41 transitions are `INSUFFICIENT_TEAM_CONTEXT`.
- **Wider windows:** at ±45/±60, the handful of labels come from category-B cases built entirely from frozen-reciprocal moves. They carry no evidence independent of the frozen core.
- **Independent-evidence-only (S6_IND):** `INSUFFICIENT_TEAM_CONTEXT` for all 41 transitions at every window.

**Descriptive S6 vs residual wherever S6 is defined** (including category C; not a label):

| window | n_S6_defined | sign_agree | median_abs_diff | median_abs_S6 | median_abs_residual_same_transitions |
|---|---|---|---|---|---|
| 15 | 8 | 0.625 | 0.242 | 0.28 | 0.144 |
| 30 | 12 | 0.5 | 0.332 | 0.225 | 0.241 |
| 45 | 14 | 0.357 | 0.333 | 0.225 | 0.241 |
| 60 | 18 | 0.333 | 0.366 | 0.252 | 0.241 |
| INTERVAL | 2 | 1 | 0.254 | 0.245 | 0.499 |

**Magnitude:**
- **The rows in the table above** (sign agreement, median |S6 − r|): at ±30, sign agreement is about a coin flip, 0.50.
- **Scale:** the typical |S6| is a fraction of the typical |residual|.
- **Where labels exist**, the ratio and absolute difference are listed per transition below. No magnitude threshold was declared, and none is inferred.

| window | variant | transition_id | category | label | contributing_cars | target_residual | team_context_value | abs_residual | abs_team_context | ratio_S_over_r | abs_diff |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 60 | S6 | 09935cc4-f542-569f-b50c-7460e0663860__TO__8ac7badc-828c-5c70-bbf4-d92f136c2564 | B | MIXED_TEAM_CONTEXT | 2 | 0.08 | -0.498 | 0.08 | 0.498 | -6.259 | 0.578 |
| 60 | S4 | 09935cc4-f542-569f-b50c-7460e0663860__TO__8ac7badc-828c-5c70-bbf4-d92f136c2564 | B | TEAM_CONTEXT_CONSISTENT | 1 | 0.08 | 0.199 | 0.08 | 0.199 | 2.504 | 0.12 |
| 45 | S6 | b671a083-ccd6-5511-a882-53e7bf202c19__TO__cb6ab391-510a-562a-a1bc-a173959477a0 | B | MIXED_TEAM_CONTEXT | 2 | 0.198 | -0.558 | 0.198 | 0.558 | -2.813 | 0.756 |
| 45 | S4 | b671a083-ccd6-5511-a882-53e7bf202c19__TO__cb6ab391-510a-562a-a1bc-a173959477a0 | B | TEAM_CONTEXT_CONSISTENT | 1 | 0.198 | 0.08 | 0.198 | 0.08 | 0.404 | 0.118 |
| 60 | S6 | b671a083-ccd6-5511-a882-53e7bf202c19__TO__cb6ab391-510a-562a-a1bc-a173959477a0 | B | MIXED_TEAM_CONTEXT | 2 | 0.198 | -0.558 | 0.198 | 0.558 | -2.813 | 0.756 |
| 60 | S4 | b671a083-ccd6-5511-a882-53e7bf202c19__TO__cb6ab391-510a-562a-a1bc-a173959477a0 | B | TEAM_CONTEXT_CONSISTENT | 1 | 0.198 | 0.08 | 0.198 | 0.08 | 0.404 | 0.118 |
| 45 | S6 | ad6c40ac-4389-5426-b8e5-1d130ac9da81__TO__3a0bcd66-fa08-5944-bf0b-5ec6c5a10f91 | B | MIXED_TEAM_CONTEXT | 2 | 0.307 | -0.003 | 0.307 | 0.003 | -0.008 | 0.31 |
| 45 | S4 | ad6c40ac-4389-5426-b8e5-1d130ac9da81__TO__3a0bcd66-fa08-5944-bf0b-5ec6c5a10f91 | B | TARGET_CAR_ISOLATED | 1 | 0.307 | -0.456 | 0.307 | 0.456 | -1.483 | 0.763 |
| 60 | S6 | ad6c40ac-4389-5426-b8e5-1d130ac9da81__TO__3a0bcd66-fa08-5944-bf0b-5ec6c5a10f91 | B | TEAM_CONTEXT_CONSISTENT | 2 | 0.307 | 0.253 | 0.307 | 0.253 | 0.822 | 0.055 |
| 60 | S4 | ad6c40ac-4389-5426-b8e5-1d130ac9da81__TO__3a0bcd66-fa08-5944-bf0b-5ec6c5a10f91 | B | TARGET_CAR_ISOLATED | 1 | 0.307 | -0.456 | 0.307 | 0.456 | -1.483 | 0.763 |

## 13. Same-team vs unrelated-team placebo

- **At ±30:** no transition is category A/B, so the pre-declared placebo is **not identifiable** (`unrelated_team_placebo.csv` is empty by rule).
- **Descriptive substitute:** the permutation below compares same-team with shuffled-team context on all transitions where S6 is defined. See `phase4d_placebo_report.md`.

## 14. Permutation (within-year team-label shuffle, 2000 draws)

| statistic | observed | perm_median | perm_p05 | perm_p95 | observed_percentile | meaningful |
|---|---|---|---|---|---|---|
| T1_sign_agree | 0.5 | 0.538 | 0.2 | 0.833 | 48.95 | True |
| T2_median_abs_diff | 0.332 | 0.542 | 0.199 | 1.318 | 79.3 | True |
| T3_n_defined | 12 | 9 | 5 | 14 |  | True |

- **Sign agreement:** same-team context is no better than shuffled-team context (49th percentile).
- **Magnitude:** same-team |S6 − r| is somewhat smaller than typical shuffles (79th percentile). But every same-team S6 here is another frozen transition's physics-adjusted change, so this is **not** independent team-state evidence.
- **Meaningfulness:** the diagnostic is formally meaningful (≥5 transitions defined) but substantively uninformative.

## 15. Large-residual case studies (the 8 largest |residual|; selection only)

| year | canonical_engineering_team | target_driver | observed_delta_speed | frozen_expected_delta_loyo | target_residual | category | n_level | n_move | label |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | MEYER_SHANK_RACING | Jack Harvey | 4.695 | -0.002 | 4.697 | D | 0 | 0 | INSUFFICIENT_TEAM_CONTEXT |
| 2023 | JUNCOS_HOLLINGER_RACING | Callum Ilott | 3.462 | -0.01 | 3.472 | D | 0 | 0 | INSUFFICIENT_TEAM_CONTEXT |
| 2020 | DRAGONSPEED | Ben Hanley | 1.971 | 0.312 | 1.659 | D | 0 | 0 | INSUFFICIENT_TEAM_CONTEXT |
| 2020 | CARLIN | Max Chilton | 1.484 | 0.234 | 1.25 | D | 0 | 0 | INSUFFICIENT_TEAM_CONTEXT |
| 2021 | ANDRETTI | Colton Herta | -1.419 | -0.226 | -1.193 | C | 3 | 0 | INSUFFICIENT_TEAM_CONTEXT |
| 2024 | ED_CARPENTER_RACING | Rinus VeeKay | 1.253 | 0.1 | 1.153 | D | 0 | 0 | INSUFFICIENT_TEAM_CONTEXT |
| 2021 | AJ_FOYT | Dalton Kellett | -0.927 | -0.052 | -0.875 | C | 3 | 0 | INSUFFICIENT_TEAM_CONTEXT |
| 2023 | ARROW_MCLAREN_SPM | Tony Kanaan | 0.727 | -0.121 | 0.848 | C | 1 | 0 | INSUFFICIENT_TEAM_CONTEXT |

- **Largest cases:** the five largest residuals (Harvey 2021 +4.70, Ilott 2023 +3.47, Hanley 2020, Chilton 2020, VeeKay 2024) have **no timed teammate attempt at all** (category D). Their unexplained movement cannot be attributed to shared or isolated anything.
- **The next three:** Herta 2021, Kellett 2021 and Kanaan 2023 have teammate LEVEL observations only (category C), so they are also unidentifiable.
- **Figures:** `figures/large_residual_cases/`.

## 16. 2021 Andretti (dense QA case; not representative)

| target_driver | target_car | observed_delta_speed | frozen_expected_delta_loyo | target_residual | category | n_level | n_move | move_cars | frozen_independent_moves | label |
|---|---|---|---|---|---|---|---|---|---|---|
| Stefan Wilson | 25 | -0.02 | 0.27 | -0.29 | C | 6 | 1 | 1 | 0 | INSUFFICIENT_TEAM_CONTEXT |
| Stefan Wilson | 25 | -0.062 | -0.142 | 0.08 | C | 3 | 1 | 1 | 0 | INSUFFICIENT_TEAM_CONTEXT |
| Colton Herta | 26 | -1.419 | -0.226 | -1.193 | C | 3 | 0 | 0 | 0 | INSUFFICIENT_TEAM_CONTEXT |
| Marco Andretti | 98 | 0.611 | 0.532 | 0.079 | C | 6 | 1 | 1 | 0 | INSUFFICIENT_TEAM_CONTEXT |
| Marco Andretti | 98 | -0.002 | -0.2 | 0.198 | C | 3 | 1 | 1 | 0 | INSUFFICIENT_TEAM_CONTEXT |

Andretti 2021 teammate moves:

| car | driver | previous_attempt_delta | delta_time_min | delta_track_c | physics_adjusted_move | independence_label | frozen_pair_transition |
|---|---|---|---|---|---|---|---|
| 25 | Stefan Wilson | -0.02 | 156.667 | 8.333 | -0.309 | RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE | 8c31470a-6324-527c-bfc3-fe19d8c1dc4d__TO__09935cc4-f542-569f-b50c-7460e0663860 |
| 25 | Stefan Wilson | -0.062 | 125.833 | 4.444 | 0.08 | RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE | 09935cc4-f542-569f-b50c-7460e0663860__TO__8ac7badc-828c-5c70-bbf4-d92f136c2564 |
| 26 | Colton Herta | -1.419 | 132.817 | 10.556 | -1.195 | RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE | e9da8645-6367-51bf-8601-3670e9e76c5e__TO__90108456-7f40-5313-a9ff-43273b65d2f0 |
| 98 | Marco Andretti | 0.611 | 169.15 | 5 | 0.053 | RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE | c2deab22-d3a0-5601-80f8-4cbf631c8f88__TO__b671a083-ccd6-5511-a882-53e7bf202c19 |
| 98 | Marco Andretti | -0.002 | 150.583 | 6.111 | 0.199 | RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE | b671a083-ccd6-5511-a882-53e7bf202c19__TO__cb6ab391-510a-562a-a1bc-a173959477a0 |

- **Every move is frozen evidence.** All 5 Andretti 2021 previous-attempt moves are themselves frozen transitions (Wilson ×2, Herta ×1, Marco Andretti ×2). Rossi, Hunter-Reay and Hinchcliffe contribute only single attempts.
- **Why the movements appear to conflict:**
  - *Different car baselines* (raw speeds span ≈2 mph).
  - *Different temporal positions* (local time):
    - Herta: ≈14:12 → 16:25.
    - Marco: ≈12:06 → 14:55 → 17:25.
    - Wilson: ≈12:30 → 15:07 → 17:12.
  - *Different repeated-run trajectories:*
    - Herta −1.42 mph.
    - Marco +0.61, then −0.00.
    - Wilson −0.02, then −0.06.
  - These moves overlap in time yet disagree, so a "team state" moving everyone together is not supported. Each move is a frozen transition, so it is not independent evidence either way.
- **Verdict:** a common team state is **not identifiable**. The only repeated-car information is frozen, and single-attempt cars carry no within-car movement. Figures: `figures/2021_andretti/`.

## 17–18. Interpretation and feasibility case

- **Attribution:** the apparent residual structure is **mostly unidentified**. Where context exists, it is frozen-core evidence re-seen. There is no transition where team-shared vs car-specific movement can be distinguished with independent evidence.

Mechanical case evaluation (precedence C → D → B → A):

| case | satisfied | detail |
|---|---|---|
| C | True | category A at ±30 = 0; dominated by frozen reuse = 12/12 |
| D | False | placebo not identifiable (no transition with both same-team and unrelated context) |
| B | False | category A = 0; permutation T1 percentile = 48.9 |
| A | False | not met |

**Headline: CASE C, NOT IDENTIFIED.**

## 19–21. Is a latent team-state model justified?

**No.**
- In the 2020–2024 reference era, the "repeated multi-car local information" a latent team state would need is almost exactly the frozen same-car transitions themselves.
- Independent teammate information consists of single attempts, which carry no within-car movement.
- A state-space, Gaussian-process or factor model would produce smooth latent curves that the data do not identify.

**What team context is still useful for:**
- (i) *Case-level qualitative context* around individual transitions: who else ran, when, and under what state (`figures/context_timelines/`).
- (ii) *Flagging* transitions whose residuals have no teammate context at all. These include the five largest residuals.
- (iii) *A documented negative result* for the paper's limitations: teammate data cannot separate team-shared from car-specific unexplained movement in this historical design.
- (iv) *A starting point:* if future sessions provide many independent repeated runs per car, the same structural audit can be re-run before any latent model is considered.

**2025 extension** (separate; raw deltas; never pooled):

| window | A | B | C | D |
|---|---|---|---|---|
| 15 | 0 | 2 | 17 | 5 |
| 30 | 0 | 3 | 18 | 3 |
| 45 | 0 | 4 | 18 | 2 |
| 60 | 0 | 5 | 18 | 1 |
| INTERVAL | 0 | 1 | 16 | 7 |

| variant | label | n |
|---|---|---|
| S4 | INSUFFICIENT_TEAM_CONTEXT | 21 |
| S4 | TEAM_CONTEXT_CONSISTENT | 3 |
| S6 | INSUFFICIENT_TEAM_CONTEXT | 21 |
| S6 | MIXED_TEAM_CONTEXT | 1 |
| S6 | TEAM_CONTEXT_CONSISTENT | 2 |
| S6_IND | INSUFFICIENT_TEAM_CONTEXT | 24 |

In 2025, every teammate move is itself another 2025 anchor (reciprocal by construction), so `S6_IND` is insufficient everywhere. The few category-B labels are self-referential and give no independent attribution.

## 22. Outputs

See `phase4d_checks_log.txt` and the file list in `README`.
