# V4 Phase 4F — Cross-Session Persistence (exploratory)

- **Measure:** the per-car median leave-one-out team-relative deviation (comparable layer, 5 min), linked across session categories within the same year.
- **Coverage:** only pairs with ≥8 linked cars are summarised.
- **Interpretation limit:** this is not driver skill and not a car effect.

| role | year | from_category | to_category | linked_cars | spearman | sign_persistence | note |
|---|---|---|---|---|---|---|---|
| PRIMARY | 2023 | PRACTICE | FAST_FRIDAY | 10 | 0.564 | 0.8 |  |
| PRIMARY | 2023 | FAST_FRIDAY | QUALIFYING_DAY1 | 0 |  |  | shown only for >=8 linked cars (spec §9) |
| PRIMARY | 2023 | QUALIFYING_DAY1 | POST_QUALIFYING_PRACTICE | 2 |  |  | shown only for >=8 linked cars (spec §9) |
| PRIMARY | 2023 | QUALIFYING_DAY1 | CARB_DAY | 2 |  |  | shown only for >=8 linked cars (spec §9) |
| PRIMARY | 2023 | PRACTICE | CARB_DAY | 32 | 0.167 | 0.562 |  |
| PRIMARY | 2023 | POST_QUALIFYING_PRACTICE | CARB_DAY | 31 | 0.225 | 0.677 |  |
| PRIMARY | 2024 | PRACTICE | FAST_FRIDAY | 8 | 0.238 | 0.625 |  |
| PRIMARY | 2024 | FAST_FRIDAY | QUALIFYING_DAY1 | 1 |  |  | shown only for >=8 linked cars (spec §9) |
| PRIMARY | 2024 | QUALIFYING_DAY1 | POST_QUALIFYING_PRACTICE | 3 |  |  | shown only for >=8 linked cars (spec §9) |
| PRIMARY | 2024 | QUALIFYING_DAY1 | CARB_DAY | 3 |  |  | shown only for >=8 linked cars (spec §9) |
| PRIMARY | 2024 | PRACTICE | CARB_DAY | 32 | -0.032 | 0.5 |  |
| PRIMARY | 2024 | POST_QUALIFYING_PRACTICE | CARB_DAY | 32 | 0.475 | 0.594 |  |
| ERA_C_SECONDARY | 2025 | PRACTICE | FAST_FRIDAY | 6 |  |  | shown only for >=8 linked cars (spec §9) |
| ERA_C_SECONDARY | 2025 | FAST_FRIDAY | QUALIFYING_DAY1 | 2 |  |  | shown only for >=8 linked cars (spec §9) |
| ERA_C_SECONDARY | 2025 | QUALIFYING_DAY1 | POST_QUALIFYING_PRACTICE | 2 |  |  | shown only for >=8 linked cars (spec §9) |
| ERA_C_SECONDARY | 2025 | QUALIFYING_DAY1 | CARB_DAY | 2 |  |  | shown only for >=8 linked cars (spec §9) |
| ERA_C_SECONDARY | 2025 | PRACTICE | CARB_DAY | 29 | -0.372 | 0.448 |  |
| ERA_C_SECONDARY | 2025 | POST_QUALIFYING_PRACTICE | CARB_DAY | 30 | 0.436 | 0.7 |  |

## Reading

- **Links through qualifying are impossible:** they have ≤3 linked cars, because teammates rarely share a 5-minute block in qualifying.
- **Practice → Carb Day and post-qualifying → Carb Day** (≈30 cars each):
  - post-qualifying → Carb Day is positive in all three years (ρ 0.23, 0.48, 0.44);
  - practice → Carb Day is inconsistent (0.17, −0.03, −0.37).
- **Practice → Fast Friday** is positive in 2023 (ρ 0.56, n = 10) and weak in 2024 (0.24, n = 8).
- **Overall:** at most weak-to-moderate, inconsistent persistence. No stable car or driver relative-to-team signal is established.

## Race

| session_key | year | car_blocks | blocks | blocks_with_same_team_pair | note |
|---|---|---|---|---|---|
| 6135 |  | 0 | 0 | 0 | structural counts only; no race D values (spec §9) |
| 6309 | 2024 | 512 | 24 | 24 | structural counts only; no race D values (spec §9) |
| 6460 | 2025 | 639 | 24 | 24 | structural counts only; no race D values (spec §9) |

The race is structural only; no D values were computed. The 2023 race has no comparable-layer car-blocks (none of its 647 broad-layer laps passed the comparable-layer filters). The reason was not diagnosed in this phase.
