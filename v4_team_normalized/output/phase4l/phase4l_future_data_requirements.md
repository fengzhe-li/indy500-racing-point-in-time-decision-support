# Future Data Requirements (based only on demonstrated V4 limitations)

A future teammate-assisted real-time predictor would need the items below. Each follows from a specific V4 phase; no predictor is designed here.

| Requirement | Why (V4 evidence) |
|---|---|
| **Real-time run-state classification** (prospectively available performance-state labels) | 4H labels are retrospective; at t0 completion F5 = 0 (4K) |
| Explicit **run-purpose** information where possible | 4H: 74.6% of at-speed laps ambiguous; run purpose unobserved |
| **Pit/stint state** from a synchronised source | 4H: stint boundaries matched feed pit messages for only about 71–75% |
| **Tyre, fuel and setup metadata** where available | unobserved in all phases |
| **Higher-frequency track/environment measurements** | 4K: only 45/113 events show measured change at 15-min resolution |
| **Genuine archived forecast vintages** | 4K: 0 forecast-vintage events |
| **Synchronised live timing** with crossing-level order | 4G: about 1.67 s feed-update ties; order within an update unobserved |
| **Repeated teammate trajectories** | 4K: 44 → 8 events after movement, placebo and leakage requirements |
| Independent **different-team placebo/control trajectories** | 4K: only 22 events with structurally comparable placebo movement |
