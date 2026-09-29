# V4 Limitations (consolidated)

1. **Restricted final population.** Phase 4J covers 2023–24 practice-type sessions, class-A car-blocks only and 6 evaluable sessions. It does not generalise to raw practice, other years, qualifying or the race.
2. **Session-level replication.** Bootstrap and leave-one-out analyses over few sessions are descriptive, and there are no p-values.
3. **Provenance.** Lap data are a third-party archived recording of the INDYCAR live timing feed. Timestamps are feed-update times (about 1.67 s), so order within an update is unobserved.
4. **Era resolution.** 2018–2021 have stint-level timestamps only and 2022 has session-level records only. The classifier was not projected backwards.
5. **Retrospective labels.** The Phase 4H class labels are retrospective. This limits point-in-time use (4K).
6. **Unobserved variables.** Run purpose, fuel, tyres, setup, tow and traffic are unobserved. Timing adjacency is a proxy for local contemporaneous context only.
7. **Environment.** 15-min PTSC resolution and no forecast vintages. The frozen qualifying β is not validated for practice.
8. **2025.** Its Timing71 structure differs and it has no official qualifying anchor. It is always analysed separately.
9. **No causal claims.** No team effects, driver or team rankings, variance decomposition or latent-state model.
10. **Evidential status.** Phases 4F, 4G, 4H and 4K contain negative, partial or non-identifiable results. They are preserved as evidence, not overwritten.
