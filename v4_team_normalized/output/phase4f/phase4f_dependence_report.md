# V4 Phase 4F — Dependence Report

| item | count |
|---|---|
| primary laps (comparable layer) | 10665 |
| car-block observations | 3032 |
| unique cars | 68 |
| unique canonical teams | 12 |
| unique sessions (independent clusters) | 15 |
| unique session-blocks | 454 |
| eligible within-block contrast blocks | 209 |
| comparisons DIFF_TEAM | 1937 |
| comparisons SAME_CAR | 1356 |
| comparisons SAME_TEAM | 1648 |
| comparisons TEAMMATE_OF_TARGET | 1937 |
| max appearances of one car across comparisons | 415 |
| median appearances per car | 203.5 |
| Phase 4E raw same-team lap pairs ±5 min in these sessions | 92893 |
| car-block reuse: max comparisons involving one car-block | 13 |

- **Clusters:** there are only 15 primary sessions (independent clusters). The session bootstrap resamples those; intervals are wide and fragile.
- **Reuse:** a single car appears in up to 415 comparisons, and a single car-block in up to 13.
- **Sample size:** none of the 92,893 raw same-team lap pairs is an independent observation. The effective sample is the session (15), then the block (209 eligible contrast blocks), then the car-block.
- **Not done:** no pair-level bootstrap and no p-values.
