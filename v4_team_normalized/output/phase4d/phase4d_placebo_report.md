# V4 Phase 4D — Placebo / Negative-Control Report

## Pre-declared unrelated-team placebo (spec §8)

- **Scope:** defined only for transitions in category A/B at ±30. There are **none**, so the placebo is **not identifiable**, and `unrelated_team_placebo.csv` contains no rows.
- **This is itself a finding:** no transition has structurally adequate same-team context to compare against unrelated teams.

## Permutation diagnostic (spec §9)

- **Shuffle:** within each year, team labels are reassigned to cars, preserving team sizes. 2000 draws, seed 20260928.
- **Statistics:** computed on transitions whose (pseudo-)team S6 at ±30 is defined, whatever their category.

| statistic | observed | perm_median | perm_p05 | perm_p95 | observed_percentile | meaningful | note |
|---|---|---|---|---|---|---|---|
| T1_sign_agree | 0.5 | 0.538 | 0.2 | 0.833 | 48.95 | True | percentile = % of shuffles with T1 <= observed (higher = stronger same-team agreement) |
| T2_median_abs_diff | 0.332 | 0.542 | 0.199 | 1.318 | 79.3 | True | percentile = % of shuffles with T2 >= observed (higher = same-team closer than shuffled) |
| T3_n_defined | 12 | 9 | 5 | 14 |  | True | transitions with defined S6 |

## Reading

- **Sign alignment:** the real team is no better than a random team (T1 at the 49th percentile).
- **Magnitude:** T2 at the 79th percentile means the same-team |S6 − r| is smaller than most shuffles. The observed same-team S6 values are other frozen transitions' physics-adjusted deltas, so any closeness partly reflects frozen transitions from the same team and session sharing environment, and the frozen model's residual structure. It does not reflect independent team-state evidence.
- **Not tested:** no unrelated-team signal was tested beyond this. CASE D (session-wide rather than team-specific structure) could not be evaluated, because the placebo is not identifiable.
- **Caveats:** transitions are dependent (shared teammates, reciprocity), and no p-value is claimed.

Figure: `figures/placebo/fig4_same_team_vs_shuffled_permutation.png`.
