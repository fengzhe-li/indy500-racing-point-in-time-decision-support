# V4 Phase 4J — Limitations Report

1. **Restricted population.** 2023–2024 practice-type sessions only, the frozen Phase 4H class-A car-blocks only (a small minority of raw practice), and 6 evaluable sessions. The result does not generalise to raw practice, other years, qualifying, or the race.
2. **Small, session-clustered evidence.**
   - 53 common-support contexts from 26 teammate pairs and 9 teams.
   - Concentration: up to 38% from one session and 36% from one team.
   - Bootstrap intervals over 6 sessions are wide and only descriptive.
3. **Layer structure differs.**
   - Same-car pairs compare consecutive 5-min blocks (about 82 s apart).
   - Same-team and different-team comparisons are within one block (about 104 s apart).
   - The time scales are comparable but not identical.
4. **Unobserved variables.** Run purpose, fuel, tyres, tow and traffic are unobserved even in class A. Timing adjacency was balanced as a design variable, not modelled.
5. **Adjacency support.** Exact-stratum common support removes all same-update contexts and most close-adjacency contexts. The primary therefore mostly reflects the >5-intervening stratum.
6. **C2 construction.** C2 is paired within context (the same target, block and stratum). The difference of layer medians has the opposite sign. This instability is part of the result.
7. **Oriented contexts.** Each unordered teammate pair contributes two oriented contexts with the same D_same-team, as pre-specified, while the different-team candidates are matched to each target separately. Session medians therefore weight a pair twice when both orientations are in support.
8. **Not claimed:** team effects, rankings, causal decomposition.
9. **Finality.** No Phase 4K and no redesign. The classifier, block width, adjacency rule, aggregation and weighting are frozen as specified in `28af221`.
