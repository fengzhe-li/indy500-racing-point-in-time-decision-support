# V4 Phase 4E — Future Design Feasibility Report

Labels are mechanical (spec §8). No design was run.

- **DESIGN_1_evidence_hierarchy (ERA_B_REFERENCE): FEASIBLE NOW.** Tier A/B sessions with all_three: 15 over 2 year(s); 2023-2024 only (2020-2021 need replay ZIPs; 2022 needs official PDFs)
- **DESIGN_2_within_team_relative (ERA_B_REFERENCE): FEASIBLE NOW.** Tier A/B sessions with >=50% multi-car-team laps having a LOO team reference within ±5 min: 10; 2023-2024 only (2020-2021 need replay ZIPs; 2022 needs official PDFs)
- **DESIGN_3_cross_session_persistence (ERA_B_REFERENCE): FEASIBLE WITH ADDITIONAL DATA.** share of primary-layer cars with valid laps in >=3 categories (Tier A/B/C sessions only): 0.40; official-record linkage >=3 categories: 0.98
- **DESIGN_4_within_team_dispersion (ERA_B_REFERENCE): FEASIBLE NOW.** Tier A/B sessions with >=3 multi-car teams: 15; 2023-2024 only (2020-2021 need replay ZIPs; 2022 needs official PDFs)
- **DESIGN_5_race_teammate_pace (ERA_B_REFERENCE): WEAK / HIGH-CONFOUNDING.** lap-level race sessions: 4 (tiers: C/D; race is at best Tier C by rule; fuel/tyre/traffic unobserved)
- **DESIGN_1_evidence_hierarchy (ERA_C_HYBRID): FEASIBLE WITH ADDITIONAL DATA.** Tier A/B sessions with all_three: 10 over 1 year(s); only one in-scope year of this regime (2026 same-regime sessions exist in the Timing71 listing, outside Phase 4E scope)
- **DESIGN_2_within_team_relative (ERA_C_HYBRID): FEASIBLE WITH ADDITIONAL DATA.** Tier A/B sessions with >=50% multi-car-team laps having a LOO team reference within ±5 min: 5; only one in-scope year of this regime (2026 same-regime sessions exist in the Timing71 listing, outside Phase 4E scope)
- **DESIGN_3_cross_session_persistence (ERA_C_HYBRID): FEASIBLE NOW.** share of primary-layer cars with valid laps in >=3 categories (Tier A/B/C sessions only): 1.00; official-record linkage >=3 categories: 0.97
- **DESIGN_4_within_team_dispersion (ERA_C_HYBRID): FEASIBLE NOW.** Tier A/B sessions with >=3 multi-car teams: 10; only one in-scope year of this regime (2026 same-regime sessions exist in the Timing71 listing, outside Phase 4E scope)
- **DESIGN_5_race_teammate_pace (ERA_C_HYBRID): WEAK / HIGH-CONFOUNDING.** lap-level race sessions: 1 (tiers: C; race is at best Tier C by rule; fuel/tyre/traffic unobserved)
- **DESIGN_1_evidence_hierarchy (ERA_A_PRE_AEROSCREEN): FEASIBLE WITH ADDITIONAL DATA.** Tier A/B sessions with all_three: 0 over 0 year(s); 2018-2019 sessions are Tier D (no observed lap timestamps) - replay ZIPs would supply them
- **DESIGN_2_within_team_relative (ERA_A_PRE_AEROSCREEN): FEASIBLE WITH ADDITIONAL DATA.** Tier A/B sessions with >=50% multi-car-team laps having a LOO team reference within ±5 min: 0; 2018-2019 sessions are Tier D (no observed lap timestamps) - replay ZIPs would supply them
- **DESIGN_3_cross_session_persistence (ERA_A_PRE_AEROSCREEN): FEASIBLE WITH ADDITIONAL DATA.** share of primary-layer cars with valid laps in >=3 categories (Tier A/B/C sessions only): 0.00; official-record linkage >=3 categories: 0.94
- **DESIGN_4_within_team_dispersion (ERA_A_PRE_AEROSCREEN): FEASIBLE WITH ADDITIONAL DATA.** Tier A/B sessions with >=3 multi-car teams: 0; 2018-2019 sessions are Tier D (no observed lap timestamps) - replay ZIPs would supply them
- **DESIGN_5_race_teammate_pace (ERA_A_PRE_AEROSCREEN): WEAK / HIGH-CONFOUNDING.** lap-level race sessions: 2 (tiers: D; race is at best Tier C by rule; fuel/tyre/traffic unobserved)

## Structural support for each design (counts only)

- **Design 1:** `evidence_hierarchy_feasibility.csv` gives A/B/C coexistence per lap-level session.
- **Design 2:** `team_reference_feasibility.csv` gives, per window, how many valid laps have a nearest or leave-one-car-out team reference (≥1 other car) and a leave-one-out median (≥2 other cars). The target is never in its own reference.
- **Design 3:** `cross_session_identity.csv`.
- **Design 4:** multi-car team counts per Tier A/B session.
- **Design 5:** race sessions have per-lap flags and stint boundaries. Traffic (gap), fuel and tyre state are not observable from the retrieved sources, so any race teammate comparison is high-confounding.

## What would change the labels

Exact lap timestamps for 2018–2021 (replay ZIPs) and 2022 lap data (official PDFs) would move Designs 1, 2 and 4 in Eras A and B (2018–2022) from "additional data" toward "feasible now". Nothing retrievable here removes the race's fuel/tyre/traffic confounding.
