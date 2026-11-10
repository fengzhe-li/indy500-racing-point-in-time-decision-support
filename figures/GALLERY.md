# Figure gallery

Repository figure names are semantic. Manuscript numbering is kept only in the paper and legacy publication assets. The curated set below is generated or copied by `scripts/generate_portfolio_figures.py`.

| Preview | Purpose | Source analysis | Scientific status |
|---|---|---|---|
| [![Identifiability](portfolio/identifiability-system-boundary.svg)](portfolio/identifiability-system-boundary.svg) | Identifiability-driven scope and human decision boundary | Historical reconnaissance + FINAL_V2 specification | System architecture |
| [![Pipeline](portfolio/evidence-engineering-pipeline.svg)](portfolio/evidence-engineering-pipeline.svg) | End-to-end evidence and model pipeline | Canonical pipeline through FINAL_V2 | System architecture |
| [![Evidence products](portfolio/evidence-products-and-attrition.svg)](portfolio/evidence-products-and-attrition.svg) | Verified products and distinct observation units | R5.2, V2-A, V2-B, 2025 evaluation | Evidence summary |
| [![Hierarchy](portfolio/evidence-hierarchy.svg)](portfolio/evidence-hierarchy.svg) | Evidence authority and quarantine | Canonical eligibility rules | Evidence summary |
| [![Same car](portfolio/same-car-transition-design.svg)](portfolio/same-car-transition-design.svg) | Same-car differencing design | Frozen response core | Methodology |
| [![Physical response](portfolio/frozen-physical-response.svg)](portfolio/frozen-physical-response.svg) | Frozen zero-intercept response and coefficients | R5.2 FINAL_V2 | Frozen model |
| [![Physical-state examples](portfolio/physical-state-transition-examples.png)](portfolio/physical-state-transition-examples.png) | Measured physical-state transition examples | R5.2 response core | Paper-aligned result |
| [![Observed versus predicted](portfolio/observed-vs-frozen-physical-prediction.png)](portfolio/observed-vs-frozen-physical-prediction.png) | Observed total change versus frozen physical contribution | R5.2 response core | Paper-aligned result |
| [![Future state](portfolio/future-track-state-model.svg)](portfolio/future-track-state-model.svg) | Separate future track-state layer | V2-A | Frozen model |
| [![Model selection](portfolio/future-track-model-selection.png)](portfolio/future-track-model-selection.png) | Out-of-year future-state candidate comparison | V2-A | Paper-aligned result |
| [![Conformal calibration](portfolio/future-track-conformal-calibration.png)](portfolio/future-track-conformal-calibration.png) | Future-state interval calibration | V2-A | Paper-aligned result |
| [![Uncertainty architecture](portfolio/three-source-uncertainty.svg)](portfolio/three-source-uncertainty.svg) | Three propagated sources | FINAL_V2 | System architecture |
| [![Ablation](portfolio/uncertainty-source-ablation.png)](portfolio/uncertainty-source-ablation.png) | Predictive-width sensitivity | V2-D | Frozen diagnostic |
| [![LOYO track coefficient](portfolio/loyo-track-coefficient-stability.png)](portfolio/loyo-track-coefficient-stability.png) | Track-coefficient out-of-year stability | R5.2 response core | Supplementary diagnostic |
| [![LOYO ambient coefficient](portfolio/loyo-ambient-coefficient-stability.png)](portfolio/loyo-ambient-coefficient-stability.png) | Ambient-coefficient out-of-year stability | R5.2 response core | Supplementary diagnostic |
| [![Horizon boundary](portfolio/calibrated-horizon-boundary.svg)](portfolio/calibrated-horizon-boundary.svg) | Calibration versus interpolation | OPERATIONAL_CURVE_V2 | Operational semantics |
| [![Sections](portfolio/section-mechanism-coherence.png)](portfolio/section-mechanism-coherence.png) | Spatial coherence without sample inflation | V2-B | Frozen diagnostic |
| [![Wind](portfolio/wind-residual-diagnostic.png)](portfolio/wind-residual-diagnostic.png) | Rejected wind extension | V2-C | Frozen diagnostic |
| [![Stress test](portfolio/scenario-stress-test-120min.png)](portfolio/scenario-stress-test-120min.png) | 120-minute physical-state scenario surface | V2-E | Frozen stress test |
| [![Probability range](portfolio/scenario-probability-range-by-horizon.png)](portfolio/scenario-probability-range-by-horizon.png) | Scenario P(improvement) range by horizon | V2-E | Supplementary frozen diagnostic |
| [![Performance envelope](portfolio/scenario-performance-envelope-by-horizon.png)](portfolio/scenario-performance-envelope-by-horizon.png) | Expected-performance scenario envelope | V2-E | Supplementary frozen diagnostic |
| [![External validation](portfolio/external-validation-2025.png)](portfolio/external-validation-2025.png) | All 15 external cases and support boundary | R6 external evaluation v2 | External validation |
| [![Supported external subset](portfolio/external-validation-2025-supported.png)](portfolio/external-validation-2025-supported.png) | Four cases within production horizon | R6 external evaluation v2 | External validation subset |
| [![Regime timeline](portfolio/technical-regime-timeline.svg)](portfolio/technical-regime-timeline.svg) | Technical and format boundaries | R6 frozen extension | Transfer/applicability |
| [![Regime coefficients](portfolio/regime-coefficient-comparison.png)](portfolio/regime-coefficient-comparison.png) | Coefficient estimates and 90% intervals | R6 regime comparison | Supporting transfer analysis |
| [![Operational curve](portfolio/operational-performance-outlook.png)](portfolio/operational-performance-outlook.png) | Expected speed and predictive bands | OPERATIONAL_CURVE_V2 | Operational presentation |
| [![Operational probability](portfolio/operational-probability-outlook.png)](portfolio/operational-probability-outlook.png) | Conditional P(improvement) curve | OPERATIONAL_CURVE_V2 | Operational presentation |
| [![Opportunity performance overlay](portfolio/external-opportunity-window-performance-overlay.png)](portfolio/external-opportunity-window-performance-overlay.png) | Externally supplied opportunity window over the performance curve | OPERATIONAL_CURVE_V2 | Operational illustration |
| [![Opportunity probability overlay](portfolio/external-opportunity-window-probability-overlay.png)](portfolio/external-opportunity-window-probability-overlay.png) | Externally supplied opportunity window over P(improvement) | OPERATIONAL_CURVE_V2 | Operational illustration |
| [![Freeze](portfolio/freeze-and-reproducibility.svg)](portfolio/freeze-and-reproducibility.svg) | Versioning and external-evidence separation | Freeze manifests | Reproducibility architecture |

The SVG diagrams are explanatory views. Numerical plots are generated from or copied byte-for-byte from frozen outputs. None of the gallery assets refits a scientific model.

## Manuscript-aligned and supplementary source assets

These legacy names retain the numbering used during paper production. They remain evidence-grounded source assets; GitHub-facing references use the semantic names above.

| Asset group | Purpose | Source analysis | Scientific status |
|---|---|---|---|
| [`figure3a_physical_state_transitions`](figure3a_physical_state_transitions.png), [`figure3b_observed_vs_frozen_prediction`](figure3b_observed_vs_frozen_prediction.png) | Physical-state examples and frozen response comparison | R5.2 response core | Paper-aligned |
| [`figure4_future_track_model_selection`](figure4_future_track_model_selection.png) | Candidate future-state comparison | V2-A | Paper-aligned; curated semantic copy used above |
| [`figure5_conformal_calibration`](figure5_conformal_calibration.png) | Future track-state interval calibration | V2-A | Paper-aligned |
| [`figure6_uncertainty_ablation`](figure6_uncertainty_ablation.png) | Uncertainty-source sensitivity | V2-D | Paper-aligned; curated semantic copy used above |
| [`figure7_v2e_120min_stress_test`](figure7_v2e_120min_stress_test.png) | 120-minute scenario matrix | V2-E | Paper-aligned; curated semantic copy used above |
| [`figure8_external_2025_validation`](figure8_external_2025_validation.png), [`supported subset`](figure8_external_2025_supported_120min.png) | 2025 external evaluation | R6 evaluation v2 | Paper-aligned; semantic copies used above |
| [`appendix_external_2025_beyond_120min`](appendix_external_2025_beyond_120min.png) | Cases beyond production boundary | R6 evaluation v2 | Extended retrospective diagnostic |
| [`figure9a_operational_performance_curve`](figure9a_operational_performance_curve.png), [`figure9b_probability_improvement_curve`](figure9b_probability_improvement_curve.png) | Continuous presentation from frozen anchors | OPERATIONAL_CURVE_V2 | Paper-aligned; semantic copies used above |
| [`figure10a_scenario_probability_range`](figure10a_scenario_probability_range.png), [`figure10b_scenario_performance_envelope`](figure10b_scenario_performance_envelope.png) | Horizon-wise stress-test envelope | V2-E | Supplementary frozen diagnostic |
| [`figure11a_loyo_beta_track`](figure11a_loyo_beta_track.png), [`figure11b_loyo_beta_ambient`](figure11b_loyo_beta_ambient.png) | Leave-one-year-out coefficient stability | R5.2 response core | Supplementary diagnostic |
| [`figure12a_queue_context_performance_overlay`](figure12a_queue_context_performance_overlay.png), [`figure12b_queue_context_probability_overlay`](figure12b_queue_context_probability_overlay.png) | Externally supplied opportunity-window overlay | OPERATIONAL_CURVE_V2 | Operational illustration; not a queue prediction |

Matching PDF versions preserve publication-quality export, and adjacent plotting-data CSV files retain auditable figure inputs. The obsolete duplicate with a non-semantic `_副本` suffix and the superseded standalone root architecture export were removed during the consistency audit.

## V4 — Team-normalized evidence extension (frozen, additive)

`V4_TEAM_NORMALIZED_FINAL` is an additive evidence extension. It leaves FINAL_V2/V3 and the paper unchanged.

- **Main README visuals:** the summary graphic below and the Phase 4H run-state figure.
- **Everything else:** the other V4 figures stay in their phase folders and are linked here.
- **Excluded:** the Phase 4F and 4G diagnostic figures are superseded intermediate diagnostics and are intentionally not featured.

| Preview | Purpose | Source analysis | Scientific status |
|---|---|---|---|
| [![V4 summary](portfolio/v4-control-evidence-summary.png)](portfolio/v4-control-evidence-summary.png) | Final teammate-control result. C1 (same team − same car) is robust; C2 (different team − same team) is not; the full hierarchy is not established | Phase 4J frozen outputs (drawn by `scripts/generate_v4_summary_figure.py`; nothing recomputed) | Final (presentation rendering) |
| [![Run-state composition](../v4_team_normalized/output/phase4h/figures/fig06_run_state_by_session_category.png)](../v4_team_normalized/output/phase4h/figures/fig06_run_state_by_session_category.png) | A valid timed practice lap is not automatically a comparable performance observation | Phase 4H | Final (measurement validity) |
| [![Tier 1 vs Tier 2](../v4_team_normalized/output/phase4j/figures/fig06_tier1_vs_tier2.png)](../v4_team_normalized/output/phase4j/figures/fig06_tier1_vs_tier2.png) | Contrasts under strict (A↔A) and extended (A/B) validity tiers | Phase 4J | Final; Tier 2 is a sensitivity analysis only |
| [![2023–24 vs 2025](../v4_team_normalized/output/phase4j/figures/fig07_2023_24_vs_2025.png)](../v4_team_normalized/output/phase4j/figures/fig07_2023_24_vs_2025.png) | Primary 2023–24 vs separate 2025 replication | Phase 4J | Final; 2025 not pooled |
| [![Leave-one-out](../v4_team_normalized/output/phase4j/figures/fig05_leave_one_out.png)](../v4_team_normalized/output/phase4j/figures/fig05_leave_one_out.png) | Leave-one-session and leave-one-team stability | Phase 4J | Final robustness diagnostic |
| [![Common support](../v4_team_normalized/output/phase4i/figures/fig04_common_support_by_session.png)](../v4_team_normalized/output/phase4i/figures/fig04_common_support_by_session.png) | Three-layer support after validity filtering | Phase 4I | Final support audit |
| [![Prediction attrition](../v4_team_normalized/output/phase4k/figures/fig01_attrition.png)](../v4_team_normalized/output/phase4k/figures/fig01_attrition.png) | Teammate-prediction feasibility attrition (113 → 8 strict events) | Phase 4K | Final feasibility audit; teammate value not prospectively identifiable, not zero |

**Authoritative text:** [`phase4l_final_scientific_synthesis.md`](../v4_team_normalized/output/phase4l/phase4l_final_scientific_synthesis.md).
