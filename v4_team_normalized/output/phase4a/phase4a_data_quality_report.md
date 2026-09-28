# V4 Phase 4A — Data-Quality Report

Inputs:
- Phase 3 `team_attempt_join.csv`, core tier only (all Phase 3 quality flags carried forward).
- The frozen repeat set and frozen LOYO residual file, both read-only.

| issue | count | handling |
|---|---|---|
| Endpoint time source | 6 of 82 endpoints use Phase 3 rescue times | labelled in t1_source/t2_source; frozen timestamp columns preserved (NaN) |
| Teammate time class not a recorder point | 12 of 276 eligible teammate attempts | any_non_point_time flag per control |
| Mixed temperature measurement basis (teammate vs endpoint) | 59 of 276 eligible candidate rows | any_mixed_basis flag per control |
| 15-min PTSC quantisation: teammate shares the endpoint's PTSC track observation | 6 of 276 | any_same_ptsc_obs flag; identical track values are resolution, not identical state |
| Missing teammate weather | 2 track / 0 ambient missing among eligible | speed controls still computed; env-fidelity metrics use available values |
| 2020 recorder data gap crossed between endpoint and teammate | 19 | any_crosses_data_gap flag (data note, not a track interruption) |
| Session state | no interruption record for 2020/2021/2023/2024 (no frozen 2022 transitions) | SAME_DAY1_SESSION_NO_INTERRUPTION_RECORD; absence of record ≠ uninterrupted |
| PIT ordering within timestamp resolution | 6 prior-only candidate rows (|offset| < 2 min or non-point time) | pit_order_fragile / any_pit_fragile flags |
| R6 wind units unverified | R6 excluded from Phase 4A | not used |
| Technical-partnership target | 1 transition (2021 Paretta #16) | no teammates by decision; kept in anchors |
| Incomplete or untimed teammate attempts | 130 of 406 candidate rows | retained in candidates, eligible_control = False |

## Endpoint-level candidate coverage

- Endpoints with ≥1 eligible teammate attempt anywhere in the session: 70 of 82.
- Eligible candidate rows: 276 (complete four-lap and timed), out of 406 candidate rows.
- **Precision:** temperatures are carried at source precision, and no interpolation beyond the Phase 3 rules was added. Differences below one PTSC step (≈0.5 °C at the published °F resolution) or between observations in the same 15-minute bin should not be read as physical differences.
