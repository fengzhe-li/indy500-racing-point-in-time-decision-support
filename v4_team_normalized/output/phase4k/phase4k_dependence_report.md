# V4 Phase 4K — Dependence Report

| population | level | total_events | unique_future_target_outcomes | unique_target_cars | unique_teams | unique_sessions | unique_teammate_cars | unique_target_teammate_pairs | events_sharing_same_target_outcome | unique_teammate_movements | max_teammate_movement_reuse | median_teammate_movement_reuse | events_sharing_a_teammate_movement | unique_placebo_movements | max_placebo_movement_reuse | max_events_per_car_session_trajectory | median_events_per_car_session_trajectory | events_within_same_stint | mean_teammate_signals_per_event | mean_comparable_pairs_per_event |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PRIMARY_TIER1_2023_2024 | F3 | 44 | 44 | 31 | 10 | 6 | 27 | 46 | 0 | 35 | 6 | 1 | 34 | 23 | 6 | 6 | 1 | 32 | 1.364 | 1.091 |
| PRIMARY_TIER1_2023_2024 | F4 | 22 | 22 | 21 | 9 | 5 | 19 | 36 | 0 | 26 | 3 | 1 | 13 | 23 | 6 | 1 | 1 | 17 | 1.727 | 2.182 |
| PRIMARY_TIER1_2023_2024 | F5 | 8 | 8 | 8 | 6 | 5 | 12 | 13 | 0 | 13 | 1 | 1 | 0 | 12 | 2 | 1 | 1 | 3 | 1.625 | 1.75 |
| TIER2_2023_2024_EXTENDED | F3 | 129 | 129 | 56 | 11 | 9 | 56 | 104 | 0 | 94 | 8 | 2 | 108 | 56 | 6 | 8 | 1 | 70 | 1.488 | 1.31 |
| TIER2_2023_2024_EXTENDED | F4 | 66 | 66 | 38 | 11 | 8 | 41 | 74 | 0 | 63 | 5 | 2 | 52 | 56 | 6 | 3 | 1 | 33 | 1.727 | 2.561 |
| TIER2_2023_2024_EXTENDED | F5 | 36 | 36 | 27 | 9 | 8 | 29 | 52 | 0 | 44 | 4 | 1 | 22 | 41 | 4 | 2 | 1 | 4 | 1.722 | 2.5 |
| TIER1_2025_SECONDARY | F3 | 35 | 35 | 21 | 11 | 6 | 20 | 26 | 0 | 27 | 2 | 1 | 20 | 14 | 2 | 2 | 1 | 28 | 1.057 | 0.486 |
| TIER1_2025_SECONDARY | F4 | 12 | 12 | 9 | 5 | 4 | 8 | 11 | 0 | 11 | 2 | 1 | 4 | 14 | 2 | 2 | 1 | 11 | 1.083 | 1.417 |
| TIER1_2025_SECONDARY | F5 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 0 | 3 | 1 | 1 | 0 | 4 | 1 | 1 | 1 | 2 | 1 | 1.333 |

**Readings:**
- One canonical event per future target outcome, by construction; no outcome is shared.
- Teammate-movement reuse is up to 6 at F3, falls to 1 at F5, and placebo reuse is at most 2.
- The dependence problem is less reuse than **scarcity**: 8 primary F5 events, with up to 37.5% from one session.

## Coverage (coverage only; not a ranking)

| population | level | key | F0 | F3 | F4 | F5 | share_of_F5 |
|---|---|---|---|---|---|---|---|
| PRIMARY_TIER1_2023_2024 | YEAR | 2023 | 58 | 22 | 9 | 3 | 0.375 |
| PRIMARY_TIER1_2023_2024 | YEAR | 2024 | 55 | 22 | 13 | 5 | 0.625 |
| PRIMARY_TIER1_2023_2024 | SESSION | 6199 | 29 | 16 | 3 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | SESSION | 6207 | 11 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | SESSION | 6208 | 18 | 6 | 6 | 2 | 0.25 |
| PRIMARY_TIER1_2023_2024 | SESSION | 6375 | 2 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | SESSION | 6378 | 14 | 5 | 3 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | SESSION | 6380 | 7 | 3 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | SESSION | 6387 | 22 | 10 | 8 | 3 | 0.375 |
| PRIMARY_TIER1_2023_2024 | SESSION | 6388 | 10 | 4 | 2 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | CATEGORY | CARB_DAY | 28 | 10 | 8 | 3 | 0.375 |
| PRIMARY_TIER1_2023_2024 | CATEGORY | FAST_FRIDAY | 7 | 3 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | CATEGORY | POST_QUALIFYING_PRACTICE | 33 | 10 | 8 | 3 | 0.375 |
| PRIMARY_TIER1_2023_2024 | CATEGORY | PRACTICE | 45 | 21 | 6 | 2 | 0.25 |
| PRIMARY_TIER1_2023_2024 | TARGET_TEAM_ALPHABETICAL | ABEL_MOTORSPORTS | 4 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_TEAM_ALPHABETICAL | AJ_FOYT | 3 | 1 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_TEAM_ALPHABETICAL | ANDRETTI | 11 | 4 | 4 | 2 | 0.25 |
| PRIMARY_TIER1_2023_2024 | TARGET_TEAM_ALPHABETICAL | ARROW_MCLAREN_SPM | 18 | 10 | 4 | 2 | 0.25 |
| PRIMARY_TIER1_2023_2024 | TARGET_TEAM_ALPHABETICAL | CHIP_GANASSI_RACING | 13 | 6 | 2 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | TARGET_TEAM_ALPHABETICAL | DALE_COYNE_RACING | 5 | 1 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_TEAM_ALPHABETICAL | DREYER_REINBOLD_RACING | 5 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_TEAM_ALPHABETICAL | ED_CARPENTER_RACING | 8 | 5 | 1 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | TARGET_TEAM_ALPHABETICAL | JUNCOS_HOLLINGER_RACING | 7 | 1 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_TEAM_ALPHABETICAL | MEYER_SHANK_RACING | 11 | 4 | 3 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_TEAM_ALPHABETICAL | RAHAL_LETTERMAN_LANIGAN | 14 | 6 | 4 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | TARGET_TEAM_ALPHABETICAL | TEAM_PENSKE | 14 | 6 | 2 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|10 | 3 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|11 | 1 | 1 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|12 | 2 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|18 | 1 | 1 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|2 | 2 | 1 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|20 | 3 | 3 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|23 | 1 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|24 | 2 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|26 | 2 | 1 | 1 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|27 | 3 | 1 | 1 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|28 | 1 | 1 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|29 | 1 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|3 | 3 | 2 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|30 | 1 | 1 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|33 | 1 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|45 | 4 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|5 | 1 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|50 | 4 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|51 | 1 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|55 | 1 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|6 | 2 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|60 | 2 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|7 | 7 | 6 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|77 | 4 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|78 | 1 | 1 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|8 | 2 | 2 | 1 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|9 | 1 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2023|98 | 1 | 1 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|06 | 4 | 1 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|11 | 1 | 1 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|12 | 2 | 1 | 1 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|14 | 1 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|15 | 1 | 1 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|17 | 4 | 1 | 1 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|18 | 2 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|2 | 3 | 2 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|20 | 2 | 1 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|21 | 1 | 1 | 1 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|24 | 2 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|27 | 1 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|28 | 2 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|3 | 2 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|30 | 5 | 1 | 1 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|33 | 1 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|41 | 1 | 1 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|45 | 2 | 2 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|5 | 1 | 1 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|51 | 1 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|6 | 1 | 1 | 1 | 1 | 0.125 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|60 | 3 | 1 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|66 | 2 | 2 | 2 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|7 | 2 | 1 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|75 | 1 | 1 | 1 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|77 | 1 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|78 | 1 | 0 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|8 | 4 | 2 | 0 | 0 | 0 |
| PRIMARY_TIER1_2023_2024 | TARGET_CAR | 2024|9 | 1 | 0 | 0 | 0 | 0 |
