# V4 Phase 4G — Limitations Report

1. **Proxy only.** Timing-sequence adjacency is an on-track temporal adjacency proxy measured at the timing line. Timing-sequence adjacency is consistent with shared local on-track context but does not identify tow. No tow, traffic-group or aerodynamic label was created.
2. **Feed resolution.**
   - Timing71 timestamps are feed-update times (about 1.67 s cycle), not line-crossing times.
   - Order within an update is unobserved and was not invented.
   - The derived laptime-chain estimate is a labelled sensitivity. It agrees in direction (about 2.8× the pool expectation). On the derived basis, the absolute excess is 0.246 − 0.088 ≈ 0.16, below the "substantial" threshold of 0.20.
3. **Missing captures:** about 1–16% of records in practice-type sessions follow a capture gap, which would understate intervening counts.
4. **Direction of dependence:** adjacency and similar speed are mutually dependent (sustained adjacency requires similar lap times). Phase 4G shows that the primary control selection conditions on this association. It does not show which way the dependence runs.
5. **Mechanical case thresholds:**
   - The spec thresholds (0.20 absolute, ratio ≥ 2, 0.25 mph) were fixed before the results.
   - **2025 secondary:** the ratio is 1.99 (A 0.636 vs E 0.319), just under 2. The absolute excess (about 0.32) and the D association (Δ_S2 0.643) agree in direction. 2025 does not enter the case.
6. **Small effective sample:**
   - The adjacency–D association uses 10 primary sessions with eligible blocks.
   - The two sessions where it is not positive are small (2024 Practice 1, 2024 Fast Friday).
   - Pairs within a block share cars, and controls are reused (about half of targets share a control car-block). None of this is treated as independent.
7. **Year pattern:**
   - The selected control's excess adjacency over its pool is similar in 2023 and 2024.
   - The year ordering of the Phase 4F Δ matches the control-minus-teammate adjacency gap, but that is three points, and the per-session pattern is mixed.
   - No causal explanation of the year differences is claimed.
8. **What this does not do:**
   - no hierarchy retest;
   - no change to the Phase 4F CASE D label;
   - no model;
   - no team effects;
   - no team/driver ranking;
   - no 2025 or race pooling;
   - no new data ingested.
9. **External evidence** (`future_evidence_feasibility.csv`):
   - The Timing71 live-feed column spec includes an interval-to-car-in-front (`Int`) column. Full replay recordings *might* carry it per update, but that is unverified.
   - Official "Section Results" PDFs exist for practice sessions, but whether they carry per-crossing time of day is unverified.
   - Neither was retrieved in Phase 4G.
