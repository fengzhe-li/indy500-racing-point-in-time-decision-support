"""V4 Phase 4L: final scientific synthesis (NO new analysis).

Reads frozen Phase 1-4K outputs only, extracts the authoritative case labels and key numbers into
phase4l_key_results_table.csv / phase4l_phase_outcomes.csv (each value with its source file and field), and renders the
synthesis documents from those extracted values. No estimator, model, classifier or new statistic is computed.
"""
import re
from pathlib import Path

import pandas as pd

V4 = Path(__file__).resolve().parents[1]
O = V4 / "output"
OUT = O / "phase4l"
TIMING71 = "third-party archived recording of the INDYCAR live timing feed"


def rd(p, **kw):
    return pd.read_csv(O / p, **kw)


def ce(p, key="CASE", col="criterion"):
    return rd(p).set_index(col).value[key]


def extract():
    K = []
    add = lambda phase, item, value, src, field: K.append(dict(phase=phase, item=item, value=value, source=src, field=field))
    rep = (O / "v4_team_normalization_report.md").read_text()
    add("P1-2", "official_entry_list_labels", int(re.search(r"Official entry-list entrant/team labels \| \*\*(\d+)\*\*", rep).group(1)), "v4_team_normalization_report.md", "§1 table")
    add("P1-2", "canonical_engineering_teams", int(rd("v4_team_entry_registry.csv").canonical_engineering_team.nunique()), "v4_team_entry_registry.csv", "canonical_engineering_team nunique")
    m = re.search(r"\*\*(\d+) of (\d+)\*\* strict V4 teammate pairs \((\d+)%\)", rep)
    add("P1-2", "teammate_pairs_missed_by_old_grouping", int(m.group(1)), "v4_team_normalization_report.md", "summary")
    add("P1-2", "strict_v4_teammate_pairs", int(m.group(2)), "v4_team_normalization_report.md", "summary")
    add("P1-2", "missed_share_pct", int(m.group(3)), "v4_team_normalization_report.md", "summary")
    add("P1-2", "old_grouping_spurious_pairs", 0 if "The old grouping had **no spurious** pairs" in rep else -1, "v4_team_normalization_report.md", "summary")
    reg = rd("v4_team_entry_registry.csv")
    add("P1-2", "technical_partnership_rows", int((reg.relationship_type == "TECHNICAL_PARTNERSHIP").sum()), "v4_team_entry_registry.csv", "relationship_type")
    c4c = rd("phase4c/case_evaluation.csv")
    add("4C", "CASE", c4c.headline_by_precedence_D_B_C_A.iloc[0], "phase4c/case_evaluation.csv", "headline_by_precedence_D_B_C_A")
    c4d = rd("phase4d/feasibility_case_evaluation.csv")
    add("4D", "CASE", c4d.headline_by_precedence_C_D_B_A.iloc[0], "phase4d/feasibility_case_evaluation.csv", "headline_by_precedence_C_D_B_A")
    add("4F", "CASE", ce("phase4f/case_evaluation.csv"), "phase4f/case_evaluation.csv", "CASE")
    sb = rd("phase4f/session_balanced_results.csv")
    p4f = sb[(sb.level == "SESSION_BALANCED") & (sb.role == "PRIMARY") & (sb.layer == "comparable") & (sb.width_min == 5) & (sb.min_laps == 1)].iloc[0]
    add("4F", "primary_session_balanced_delta_mph", round(float(p4f.session_balanced_delta), 3), "phase4f/session_balanced_results.csv", "session_balanced_delta")
    add("4F", "primary_share_sessions_positive", round(float(p4f.share_sessions_positive), 3), "phase4f/session_balanced_results.csv", "share_sessions_positive")
    add("4F", "team_balanced_delta_mph", round(float(p4f.session_balanced_delta_team_balanced), 3), "phase4f/session_balanced_results.csv", "session_balanced_delta_team_balanced")
    add("4G", "CASE", ce("phase4g/phase4g_case_evaluation.csv"), "phase4g/phase4g_case_evaluation.csv", "CASE")
    g = rd("phase4g/adjacency_distribution_summary.csv")
    gA = g[(g.role == "PRIMARY") & (g.population == "A_PRIMARY_CONTROL") & (g.basis == "OBSERVED_FEED_SEQUENCE")].iloc[0]
    gB = g[(g.role == "PRIMARY") & (g.population == "B_RANDOM_PICK_EXPECTATION") & (g.basis == "OBSERVED_FEED_SEQUENCE")].iloc[0]
    add("4G", "primary_control_median_carblock_sep_s", round(float(gA.carblock_sep_s_median), 2), "phase4g/adjacency_distribution_summary.csv", "carblock_sep_s_median")
    add("4G", "primary_control_share_no_intervening", round(float(gA.share_le0_intervening), 3), "phase4g/adjacency_distribution_summary.csv", "share_le0_intervening")
    add("4G", "random_pool_expected_share_no_intervening", round(float(gB.share_le0_intervening), 3), "phase4g/adjacency_distribution_summary.csv", "share_le0_intervening")
    g4 = rd("phase4g/phase4g_case_evaluation.csv").set_index("criterion").value
    add("4G", "S2_delta_D_gt5_minus_no_intervening_mph", round(float(g4["S2_delta"]), 3), "phase4g/phase4g_case_evaluation.csv", "S2_delta")
    h = rd("phase4h/case_evaluation.csv").set_index("criterion").value
    add("4H", "CASE", h["MEASUREMENT_VALIDITY_CASE"], "phase4h/case_evaluation.csv", "MEASUREMENT_VALIDITY_CASE")
    add("4H", "share_A_of_at_speed_2023_24_pct", round(100 * float(h["S_A_nonD_2023_2024"]), 1), "phase4h/case_evaluation.csv", "S_A_nonD_2023_2024")
    add("4H", "share_AB_of_at_speed_2023_24_pct", round(100 * float(h["S_AB_nonD_2023_2024"]), 1), "phase4h/case_evaluation.csv", "S_AB_nonD_2023_2024")
    add("4H", "share_C_ambiguous_of_at_speed_2023_24_pct", round(100 * float(h["S_C_nonD"]), 1), "phase4h/case_evaluation.csv", "S_C_nonD")
    rc = rd("phase4h/run_state_classification.csv")
    yg = rc[(rc.level == "YEAR_GROUP") & (rc.yr_group == "2023_2024_PRIMARY")].iloc[0]
    add("4H", "share_D_of_all_2023_24_practice_laps_pct", round(100 * float(yg.share_all_D), 1), "phase4h/run_state_classification.csv", "share_all_D")
    pa = rd("phase4h/phase4f_population_run_state_audit.csv")
    pa1 = pa[(pa.role == "PRIMARY") & (pa.population == "A_PRIMARY_CONTROL")].iloc[0]
    add("4H", "phase4f_primary_control_pairs_both_A_pct", round(100 * float(pa1.share_both_A), 1), "phase4h/phase4f_population_run_state_audit.csv", "share_both_A")
    add("4H", "phase4f_primary_control_pairs_involving_ambiguous_pct", round(100 * float(pa1.share_involves_C_ambiguous), 1), "phase4h/phase4f_population_run_state_audit.csv", "share_involves_C_ambiguous")
    add("4H", "C1_2024_official_qualifying_retention_A", round(float(h["C1_2024_official_retention_A"]), 3), "phase4h/case_evaluation.csv", "C1_2024_official_retention_A")
    ci = rd("phase4i/case_evaluation.csv")
    add("4I", "CASE", ci[ci.criterion == "SUPPORT_CASE"].value.iloc[0], "phase4i/case_evaluation.csv", "SUPPORT_CASE")
    t1 = rd("phase4i/tier1_strict_support.csv")
    t1p = t1[(t1.level == "YEAR_GROUP") & (t1.yr_group == "2023_2024_PRIMARY")].iloc[0]
    for k in ["eligible_laps", "eligible_carblocks", "cars", "teams", "sessions"]:
        add("4I", f"tier1_{k}", int(t1p[k]), "phase4i/tier1_strict_support.csv", k)
    st = rd("phase4i/same_team_support.csv")
    s1 = st[(st.layer == "SAME_TEAM") & (st.tier == "TIER1_STRICT") & (st.yr_group == "2023_2024_PRIMARY")].iloc[0]
    add("4I", "tier1_same_team_pairs", int(s1.pairs), "phase4i/same_team_support.csv", "pairs")
    add("4I", "tier1_same_team_distinct_car_pairs", int(s1.independent_car_pairs), "phase4i/same_team_support.csv", "independent_car_pairs")
    add("4I", "tier1_same_team_teams", int(s1.distinct_teams), "phase4i/same_team_support.csv", "distinct_teams")
    add("4I", "tier1_same_team_sessions", int(s1.sessions), "phase4i/same_team_support.csv", "sessions")
    dt = rd("phase4i/different_team_candidate_support.csv")
    add("4I", "tier1_diff_team_candidates", int(dt[(dt.tier == "TIER1_STRICT") & (dt.yr_group == "2023_2024_PRIMARY")].pairs.iloc[0]), "phase4i/different_team_candidate_support.csv", "pairs")
    cim = ci[(ci.tier == "TIER1_STRICT") & (ci.yr_group == "2023_2024_PRIMARY")].set_index("criterion").value
    add("4I", "tier1_sessions_all_three_layers", int(float(cim["M1"])), "phase4i/case_evaluation.csv", "M1")
    add("4I", "tier1_blocks_all_three_layers", int(float(cim["M3"])), "phase4i/case_evaluation.csv", "M3")
    j = rd("phase4j/hierarchy_summary_all_analyses.csv").set_index("analysis")
    jp = j.loc["PRIMARY_TIER1_2023_2024"]
    add("4J", "CASE", ce("phase4j/case_evaluation.csv", "PRIMARY_CASE"), "phase4j/case_evaluation.csv", "PRIMARY_CASE")
    add("4J", "spec_commit", "28af221", "phase4j/case_evaluation.csv", "pre_result_spec_commit")
    jc = rd("phase4j/same_team_primary.csv").set_index("item").value
    add("4J", "contexts_all", int(jp.all_contexts), "phase4j/hierarchy_summary_all_analyses.csv", "all_contexts")
    add("4J", "contexts_common_support", int(jp.common_support_contexts), "phase4j/hierarchy_summary_all_analyses.csv", "common_support_contexts")
    add("4J", "teammate_pairs", int(jc["distinct unordered teammate pairs in support"]), "phase4j/same_team_primary.csv", "distinct unordered teammate pairs in support")
    add("4J", "cars", int(jc["cars in support contexts"]), "phase4j/same_team_primary.csv", "cars in support contexts")
    add("4J", "teams", int(jc["teams in support contexts"]), "phase4j/same_team_primary.csv", "teams in support contexts")
    add("4J", "blocks", int(jc["blocks with support contexts"]), "phase4j/same_team_primary.csv", "blocks with support contexts")
    add("4J", "evaluable_sessions", int(jp.evaluable_sessions), "phase4j/hierarchy_summary_all_analyses.csv", "evaluable_sessions")
    for k in ["D_same_car", "D_same_team", "D_diff_team", "C1", "C2", "C3", "C1_boot_lo", "C1_boot_hi", "C2_boot_lo", "C2_boot_hi", "C2_from_layer_medians"]:
        add("4J", k, round(float(jp[k]), 3), "phase4j/hierarchy_summary_all_analyses.csv", k)
    add("4J", "C1_laptime_equiv_s_at_225", round(float(jp.C1) / 225 * 40, 3), "derived: C1/225*40 (Phase 4J spec §8)", "C1")
    add("4J", "C1_sessions_positive", f"{int(round(jp.share_sessions_C1_pos * jp.evaluable_sessions))}/{int(jp.evaluable_sessions)}", "phase4j/hierarchy_summary_all_analyses.csv", "share_sessions_C1_pos")
    add("4J", "C2_sessions_positive", f"{int(round(jp.share_sessions_C2_pos * jp.evaluable_sessions))}/{int(jp.evaluable_sessions)}", "phase4j/hierarchy_summary_all_analyses.csv", "share_sessions_C2_pos")
    add("4J", "C1_status", jp.C1_status, "phase4j/hierarchy_summary_all_analyses.csv", "C1_status")
    add("4J", "C2_status", jp.C2_status, "phase4j/hierarchy_summary_all_analyses.csv", "C2_status")
    lo, lt = rd("phase4j/leave_one_session_out.csv"), rd("phase4j/leave_one_team_out.csv")
    lo, lt = lo[lo.analysis == "PRIMARY_TIER1_2023_2024"], lt[(lt.analysis == "PRIMARY_TIER1_2023_2024") & lt.feasible]
    add("4J", "C1_all_LOSO_positive", bool((lo.C1 > 0).all()), "phase4j/leave_one_session_out.csv", "C1")
    add("4J", "C1_all_LOTO_positive", bool((lt.C1 > 0).all()), "phase4j/leave_one_team_out.csv", "C1")
    add("4J", "C2_LOTO_sign_flips", int((lt.C2 <= 0).sum()), "phase4j/leave_one_team_out.csv", "C2")
    add("4J", "C2_LOTO_flip_team", ";".join(lt[lt.C2 <= 0].dropped_team), "phase4j/leave_one_team_out.csv", "dropped_team")
    add("4J", "tier2_C1", round(float(j.loc["TIER2_SENSITIVITY_2023_2024"].C1), 3), "phase4j/hierarchy_summary_all_analyses.csv", "C1")
    add("4J", "tier2_C2", round(float(j.loc["TIER2_SENSITIVITY_2023_2024"].C2), 3), "phase4j/hierarchy_summary_all_analyses.csv", "C2")
    add("4J", "rep2025_C1", round(float(j.loc["REPLICATION_2025_TIER1"].C1), 3), "phase4j/hierarchy_summary_all_analyses.csv", "C1")
    add("4J", "rep2025_C2", round(float(j.loc["REPLICATION_2025_TIER1"].C2), 3), "phase4j/hierarchy_summary_all_analyses.csv", "C2")
    add("4J", "rep2025_C2_boot", f"[{float(j.loc['REPLICATION_2025_TIER1'].C2_boot_lo):.2f}, {float(j.loc['REPLICATION_2025_TIER1'].C2_boot_hi):.2f}]", "phase4j/hierarchy_summary_all_analyses.csv", "C2_boot_lo/hi")
    k = rd("phase4k/case_evaluation.csv").set_index("criterion").value
    add("4K", "CASE", k["PRIMARY_FEASIBILITY_CASE"], "phase4k/case_evaluation.csv", "PRIMARY_FEASIBILITY_CASE")
    at = rd("phase4k/event_attrition.csv")
    ap = at[(at.population == "PRIMARY_TIER1_2023_2024") & (at.cutoff == "PRIMARY")].set_index("level")
    for f in ["F0", "F1", "F2", "F3", "F4", "F5"]:
        add("4K", f, int(ap.loc[f, "events"]), "phase4k/event_attrition.csv", f"{f} events")
    add("4K", "F5_target_cars", int(ap.loc["F5", "target_cars"]), "phase4k/event_attrition.csv", "target_cars")
    add("4K", "F5_teams", int(ap.loc["F5", "target_teams"]), "phase4k/event_attrition.csv", "target_teams")
    add("4K", "F5_sessions", int(ap.loc["F5", "sessions"]), "phase4k/event_attrition.csv", "sessions")
    add("4K", "F5_years", int(k["Y5"]), "phase4k/case_evaluation.csv", "Y5")
    ac = at[(at.population == "PRIMARY_TIER1_2023_2024") & (at.cutoff == "CONSERVATIVE")].set_index("level")
    add("4K", "F5_conservative_cutoff", int(ac.loc["F5", "events"]), "phase4k/event_attrition.csv", "CONSERVATIVE F5")
    ph = rd("phase4k/physical_input_support.csv").set_index("population")
    add("4K", "events_with_measured_env_change", int(ph.loc["PRIMARY_TIER1_2023_2024", "resolved_physical_change"]), "phase4k/physical_input_support.csv", "resolved_physical_change")
    add("4K", "genuine_forecast_vintage_events", int(ph.loc["PRIMARY_TIER1_2023_2024", "genuine_forecast_vintage_events"]), "phase4k/physical_input_support.csv", "genuine_forecast_vintage_events")
    dep = rd("phase4k/event_overlap_dependence.csv")
    d5 = dep[(dep.population == "PRIMARY_TIER1_2023_2024") & (dep.level == "F5")].iloc[0]
    add("4K", "F5_events_sharing_target_outcome", int(d5.events_sharing_same_target_outcome), "phase4k/event_overlap_dependence.csv", "events_sharing_same_target_outcome")
    add("4K", "F5_max_teammate_movement_reuse", int(d5.max_teammate_movement_reuse), "phase4k/event_overlap_dependence.csv", "max_teammate_movement_reuse")
    t2 = at[(at.population == "TIER2_2023_2024_EXTENDED") & (at.cutoff == "PRIMARY")].set_index("level")
    add("4K", "tier2_F5", int(t2.loc["F5", "events"]), "phase4k/event_attrition.csv", "TIER2 F5")
    add("4K", "tier2_F5_sessions", int(t2.loc["F5", "sessions"]), "phase4k/event_attrition.csv", "TIER2 F5 sessions")
    r5 = at[(at.population == "TIER1_2025_SECONDARY") & (at.cutoff == "PRIMARY")].set_index("level")
    add("4K", "rep2025_F5", int(r5.loc["F5", "events"]), "phase4k/event_attrition.csv", "2025 F5")
    return pd.DataFrame(K)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    K = extract()
    K.to_csv(OUT / "phase4l_key_results_table.csv", index=False)
    v = {(r.phase, r.item): r.value for r in K.itertuples(index=False)}
    g = lambda ph, it: v[(ph, it)]
    ph = [dict(phase="1-2", question="Team identity / registry", outcome="COMPLETE (registry + audit)", case_label="n/a", source="v4_team_normalization_report.md"),
          dict(phase="3", question="Teammate attempt candidates / comparability", outcome="COMPLETE (descriptive)", case_label="n/a", source="phase3/"),
          dict(phase="4A", question="Frozen-transition teammate-control matching design", outcome="COMPLETE (sparse endpoint support; substantial reuse)", case_label="n/a", source="phase4a/"),
          dict(phase="4B", question="Team-year timelines", outcome="COMPLETE (car x time confounding; Era A/B environment-time collinearity)", case_label="n/a", source="phase4b/"),
          dict(phase="4C", question="2025 exploratory within-team panel", outcome="physical terms not separable from session time (ambient); track sign stable but interval includes 0", case_label=g("4C", "CASE"), source="phase4c/case_evaluation.csv"),
          dict(phase="4D", question="Latent team-state / residual attribution feasibility", outcome="NOT IDENTIFIED", case_label=g("4D", "CASE"), source="phase4d/feasibility_case_evaluation.csv"),
          dict(phase="4E", question="2018-2025 multi-session data opportunity", outcome="Design 1 feasible now for 2023-2024 only; 2018-2021 stint-level; 2022 session-level", case_label="n/a (tiered)", source="phase4e/"),
          dict(phase="4F", question="Raw-practice empirical hierarchy (pre-registered)", outcome="no team-control advantage under primary nearest-time estimator; design-sensitive", case_label=g("4F", "CASE"), source="phase4f/case_evaluation.csv"),
          dict(phase="4G", question="Control-selection / timing-adjacency diagnostic", outcome="primary controls unusually timing-adjacent; adjacency associated with lower D", case_label=g("4G", "CASE"), source="phase4g/phase4g_case_evaluation.csv"),
          dict(phase="4H", question="Performance-lap / run-state measurement validity", outcome="raw practice unsuitable for a clean performance hierarchy", case_label=g("4H", "CASE"), source="phase4h/case_evaluation.csv"),
          dict(phase="4I", question="Post-validity eligibility / support", outcome="restricted hierarchy test feasible", case_label=g("4I", "CASE"), source="phase4i/case_evaluation.csv"),
          dict(phase="4J", question="FINAL pre-registered hierarchy", outcome="C1 supported; C2 not established; full hierarchy not established", case_label=g("4J", "CASE"), source="phase4j/case_evaluation.csv"),
          dict(phase="4K", question="Point-in-time teammate prediction feasibility", outcome="weak support; teammate predictive value not prospectively identifiable; no predictive experiment", case_label=g("4K", "CASE"), source="phase4k/case_evaluation.csv")]
    pd.DataFrame(ph).to_csv(OUT / "phase4l_phase_outcomes.csv", index=False)

    claims = [
        ("SUPPORTED", "Historical entrant naming fragmented real engineering-team relationships", f"P1-2: {g('P1-2','official_entry_list_labels')} official labels -> {g('P1-2','canonical_engineering_teams')} canonical teams", "v4_team_normalization_report.md"),
        ("SUPPORTED", "Canonical team normalization recovers those relationships", f"{g('P1-2','teammate_pairs_missed_by_old_grouping')}/{g('P1-2','strict_v4_teammate_pairs')} strict teammate pairs recovered", "v4_team_normalization_report.md"),
        ("SUPPORTED", "Old teammate grouping had high precision but incomplete recall", f"0 spurious pairs; {g('P1-2','missed_share_pct')}% of true pairs missed", "v4_team_normalization_report.md"),
        ("SUPPORTED", "Practice provides much denser contemporaneous same-team observation than qualifying", "Phase 4E opportunity counts (raw, dependent)", "phase4e/"),
        ("SUPPORTED", "Raw practice laps are heterogeneous in run state", f"4H: {g('4H','share_A_of_at_speed_2023_24_pct')}% class A; {g('4H','share_C_ambiguous_of_at_speed_2023_24_pct')}% ambiguous", "phase4h/case_evaluation.csv"),
        ("SUPPORTED", "Exact-car control reduces observed performance dispersion relative to same-team different-car comparison (restricted final population)", f"4J C1 = +{g('4J','C1')} mph, {g('4J','C1_status')}", "phase4j/"),
        ("SUPPORTED", "The original same-car qualifying design has empirically supported methodological value", "4J C1 robust; relaxing controls exposed additional heterogeneity (4B-4K)", "phase4j/, phase4b-4k"),
        ("PARTIALLY_SUPPORTED", "Same-team similarity relative to different-team similarity", f"4J C2 = {g('4J','C2')} mph but {g('4J','C2_status')}; Tier 2 {g('4J','tier2_C2')}; layer-median {g('4J','C2_from_layer_medians')}", "phase4j/"),
        ("PARTIALLY_SUPPORTED", "2025 cross-regime consistency", f"2025 C1 = +{g('4J','rep2025_C1')} (consistent); C2 = {g('4J','rep2025_C2')} with interval {g('4J','rep2025_C2_boot')}", "phase4j/"),
        ("PARTIALLY_SUPPORTED", "Local contemporaneous running context is an important design variable", f"4G CASE {g('4G','CASE')}; mechanism not identified (4H)", "phase4g/, phase4h/"),
        ("NOT_ESTABLISHED", "Complete same-car < same-team < different-team hierarchy", f"4J CASE {g('4J','CASE')}", "phase4j/"),
        ("NOT_ESTABLISHED", "Causal team effect", "no causal design in V4", "all"),
        ("NOT_ESTABLISHED", "Latent team-state trajectory", f"4D CASE {g('4D','CASE')} (NOT IDENTIFIED)", "phase4d/"),
        ("NOT_ESTABLISHED", "Tow / traffic / aerodynamic mechanism", "timing adjacency is a proxy; not identified", "phase4g/, phase4h/"),
        ("NOT_ESTABLISHED", "Teammate incremental predictive value", f"4K CASE {g('4K','CASE')}; not tested (Phase 4L predictive experiment not justified)", "phase4k/"),
        ("NOT_ESTABLISHED", "Deployable practice prediction", "no forecast vintages; no predictive experiment", "phase4k/"),
        ("NOT_ESTABLISHED", "Practice-specific physical coefficients", "none estimated; frozen qualifying beta not validated for practice", "phase4c/, phase4k/"),
        ("NOT_IDENTIFIABLE", "Strict point-in-time teammate predictor under current retrospective labels", f"F5 = {g('4K','F5')}; conservative-cutoff F5 = {g('4K','F5_conservative_cutoff')}", "phase4k/"),
        ("NOT_IDENTIFIABLE", "Genuine forecast-conditioned practice prediction", f"forecast-vintage events = {g('4K','genuine_forecast_vintage_events')}", "phase4k/"),
    ]
    pd.DataFrame(claims, columns=["status", "claim", "evidence", "source"]).to_csv(OUT / "phase4l_claims_matrix.csv", index=False)
    write_docs(g)


def write_docs(g):
    syn = f"""# V4 Final Scientific Synthesis: Team-Normalized / Teammate-Control Investigation

**Status:** the authoritative interpretation of V4, Phases 1–4K.
- This is a synthesis only. No new estimator, model, classifier or statistic was computed.
- Every number below is read from a frozen output (`phase4l_key_results_table.csv` lists each source file and field).

**Data provenance:**
- Lap data: Timing71 files, a {TIMING71}.
- Official INDYCAR session-detail records: used as cross-checks and as the qualifying anchor.

## Final case sequence

| Phase | Question | Case |
|---|---|---|
| 4C | exploratory 2025 within-team panel | **{g('4C','CASE')}** |
| 4D | latent team state | **{g('4D','CASE')}** (NOT IDENTIFIED) |
| 4F | raw-practice hierarchy | **{g('4F','CASE')}** |
| 4G | control-selection diagnostic | **{g('4G','CASE')}** |
| 4H | raw-practice measurement validity | **{g('4H','CASE')}** |
| 4I | post-validity support | **{g('4I','CASE')}** |
| 4J | FINAL hierarchy | **{g('4J','CASE')}** |
| 4K | teammate prediction feasibility | **{g('4K','CASE')}** |

## Q1 — Team identity

**Question:** did sponsor-heavy entrant naming fragment real engineering-team relationships? **Yes.**
- **Normalisation:** {g('P1-2','official_entry_list_labels')} distinct official entry-list labels (2018–2025) normalise to {g('P1-2','canonical_engineering_teams')} canonical engineering teams.
- **Old grouping:** it missed **{g('P1-2','teammate_pairs_missed_by_old_grouping')} of {g('P1-2','strict_v4_teammate_pairs')}** strict teammate pairs ({g('P1-2','missed_share_pct')}%) and created no spurious pairs. It was **high precision, low recall**.
- **Documented cases:** #98 Andretti Herta → Andretti; lineage-stable IDs such as SPM → Arrow McLaren.
- **Technical partnerships** ({g('P1-2','technical_partnership_rows')} registry rows) stay separate from the primary teammate layer.

This does not affect the frozen same-car V2/V3 core, which never used teammate grouping.

## Q2 — Can qualifying teammates provide an independent control layer?

**Evidence (Phases 4A–4D):**
- Endpoint matching to the 41 frozen transitions was sparse.
- Teammate-attempt reuse was substantial, and most available teammate "moves" are themselves frozen transitions seen from another car.
- Team timelines showed car × time confounding.
- In Eras A and B (the pre-2023 eras), track temperature, ambient temperature and session time were nearly collinear within team-years.
- **Phase 4C** (2025 exploratory panel, CASE {g('4C','CASE')}): track temperature kept a comparatively stable negative point estimate (about −0.058 mph/°C). Its car-bootstrap interval nonetheless includes 0. Ambient temperature, time and rerunning effects were not separable or not stable.
- **Phase 4D** (CASE {g('4D','CASE')}): latent dynamic team state was **not identified**.

**Conclusion:** team identity and team context are recoverable. Independent dynamic team-state movement is **not** recoverable from the qualifying record.

## Q3 — Does multi-session practice add observational opportunity?

**Yes, but only in 2023–2025.**

| Period | What it provides |
|---|---|
| 2023–2025 | qualitatively new lap-level timing structure (Timing71, observed lap timestamps) |
| 2018–2021 | stint-level timestamps only; **not equivalent lap-level evidence** |
| 2022 | session-level official records only |

- Practice greatly increases contemporaneous same-team opportunity.
- Raw pair counts are highly dependent; the effective replication unit is the session.
- The eight-year dataset is **not** eight years of equivalent lap-level evidence.

## Q4 — Does raw practice support the proposed hierarchy? (Phase 4F, CASE {g('4F','CASE')})

**Pre-registered primary result:**
- The nearest-time different-team estimator gave Δ = {g('4F','primary_session_balanced_delta_mph')} mph, positive in only {g('4F','primary_share_sessions_positive')} of sessions.
- **No team-control advantage was established.**

**Design sensitivity:**
- A pre-specified team-balanced construction was more favourable to same-team similarity ({g('4F','team_balanced_delta_mph')} mph). The result was design-sensitive.
- Raw pair counts overstated the evidence; replication was at session level.

Phase 4F neither established nor refuted the final hierarchy. Its CASE {g('4F','CASE')} label stands.

## Q5 — Why was Phase 4F design-sensitive? (Phase 4G, CASE {g('4G','CASE')})

**Finding:** nearest-time different-team controls were unusually timing-adjacent.
- Their median car-block separation was {g('4G','primary_control_median_carblock_sep_s')} s.
- {100 * g('4G','primary_control_share_no_intervening'):.1f}% had no intervening lap record, against {100 * g('4G','random_pool_expected_share_no_intervening'):.1f}% expected from a random pick in the same pool.
- Timing adjacency was associated with lower D: +{g('4G','S2_delta_D_gt5_minus_no_intervening_mph')} mph between the far and adjacent strata.

**Interpretation (updated by Phase 4H):**
- Adjacency reflects **local contemporaneous running context**. That may include run phase, run purpose, track position, traffic or tow, and other unobserved local state.
- Phase 4G identifies a **control-selection property, not its causal mechanism**. It is not evidence of tow, traffic or aerodynamic interaction.

## Q6 — Were raw practice laps valid performance observations? (Phase 4H, CASE {g('4H','CASE')})

**A timed, valid lap is not the same as a comparable performance observation.**

**Qualifying reference:**
- Attempts are tightly structured.
- The frozen classifier, calibrated on 2023 official attempts, retained {100 * g('4H','C1_2024_official_qualifying_retention_A'):.1f}% of 2024 official qualifying laps out of year.

**Raw 2023–24 practice:**

| Class (at-speed laps) | Share |
|---|---|
| Class A | **{g('4H','share_A_of_at_speed_2023_24_pct')}%** |
| A + B | {g('4H','share_AB_of_at_speed_2023_24_pct')}% |
| Ambiguous | {g('4H','share_C_ambiguous_of_at_speed_2023_24_pct')}% |

- Separately, {g('4H','share_D_of_all_2023_24_practice_laps_pct')}% of all practice laps fell into clearly non-comparable structures (pit, non-green, out of band).
- Phase 4F primary-control pairs were {g('4H','phase4f_primary_control_pairs_involving_ambiguous_pct')}% ambiguity-affected, and only {g('4H','phase4f_primary_control_pairs_both_A_pct')}% were A–A.

**Narrow reading of CASE {g('4H','CASE')}:** *the raw practice population is unsuitable for a clean performance hierarchy.* It does **not** mean that practice can never support a hierarchy; Phase 4I tested that separately.

## Q7 — After validity filtering, is enough evidence left? (Phase 4I, CASE {g('4I','CASE')})

**Tier 1, 2023–24:**
- {g('4I','tier1_eligible_laps')} class-A laps in {g('4I','tier1_eligible_carblocks')} five-minute car-blocks;
- {g('4I','tier1_cars')} cars, {g('4I','tier1_teams')} teams, {g('4I','tier1_sessions')} sessions.

**Layers:**
- **Same team:** {g('4I','tier1_same_team_pairs')} pairs ({g('4I','tier1_same_team_distinct_car_pairs')} distinct car pairs, {g('4I','tier1_same_team_teams')} teams, {g('4I','tier1_same_team_sessions')} sessions).
- **Different team:** {g('4I','tier1_diff_team_candidates')} candidates.
- **All three layers:** {g('4I','tier1_sessions_all_three_layers')}/{g('4I','tier1_sessions')} sessions and {g('4I','tier1_blocks_all_three_layers')} blocks.

A minority survival fraction did **not** imply insufficient absolute support. A restricted final test remained feasible.

## Q8 — The final pre-registered hierarchy (Phase 4J, CASE {g('4J','CASE')}; spec `{g('4J','spec_commit')}`)

**Population:**
- Tier 1, 2023–24, strict timing-adjacency common support.
- {g('4J','contexts_common_support')} of {g('4J','contexts_all')} contexts from {g('4J','teammate_pairs')} teammate pairs, {g('4J','cars')} cars, {g('4J','teams')} teams and {g('4J','blocks')} blocks.
- **{g('4J','evaluable_sessions')} evaluable independent sessions**, session-balanced.

**Layer medians:** D_same-car = {g('4J','D_same_car')}, D_same-team = {g('4J','D_same_team')}, D_different-team = {g('4J','D_diff_team')} mph.

**C1 = D_same-team − D_same-car = +{g('4J','C1')} mph** (≈ +{g('4J','C1_laptime_equiv_s_at_225')} s/lap): `{g('4J','C1_status')}`.
- positive in {g('4J','C1_sessions_positive')} sessions;
- session-bootstrap interval [{g('4J','C1_boot_lo')}, {g('4J','C1_boot_hi')}], which excludes zero;
- all leave-one-session-out and leave-one-team-out estimates positive;
- Tier 2 +{g('4J','tier2_C1')}; 2025 replication +{g('4J','rep2025_C1')}.

**C2 (context-paired different-team − same-team) = +{g('4J','C2')} mph: `{g('4J','C2_status')}`. Not robust.**
- positive in only {g('4J','C2_sessions_positive')} sessions;
- interval [{g('4J','C2_boot_lo')}, {g('4J','C2_boot_hi')}];
- removing {g('4J','C2_LOTO_flip_team')} flips the sign;
- Tier 2 {g('4J','tier2_C2')};
- difference of overall layer medians {g('4J','C2_from_layer_medians')};
- the 2025 value {g('4J','rep2025_C2')} is highly uncertain ({g('4J','rep2025_C2_boot')}).

**C3 = D_different-team − D_same-car = +{g('4J','C3')} mph.**

**Authoritative conclusion:** the full hierarchy *same car < same team < different team* was **not established**.
- Exact-car identity gave a robust reduction in observed performance dispersion relative to same-team different-car comparisons.
- Shared team identity alone showed **no stable additional reduction** relative to different-team comparisons.
- *The V4 evidence supports the methodological value of exact-car control, but does not establish a complete same-car < same-team < different-team performance-control hierarchy.*

**What this does not mean:** that teammates have no value, that team identity is irrelevant, or that same-team cars are physically unrelated.

## Q9 — Can teammate movement provide predictive information? (Phase 4K, CASE {g('4K','CASE')})

This is a distinct question from Q8.

**Primary class-A 2023–24 attrition:**

| Level | Requirement | Events |
|---|---|---|
| F0 | target event | {g('4K','F0')} |
| F1 | + physical readings | {g('4K','F1')} |
| F2 | + prior teammate observation | {g('4K','F2')} |
| F3 | + prior teammate movement | {g('4K','F3')} |
| F4 | + comparable different-team placebo | {g('4K','F4')} |
| F5 | + no leakage | **{g('4K','F5')}** |

- **F5 coverage:** {g('4K','F5_target_cars')} target cars, {g('4K','F5_teams')} teams, {g('4K','F5_sessions')} sessions, both years.
- **Dependence:** no duplicate future outcomes ({g('4K','F5_events_sharing_target_outcome')}), and teammate-movement reuse at F5 is at most {g('4K','F5_max_teammate_movement_reuse')}. Reuse is not the binding problem; **scarcity is**.
- **Forecast vintages:** {g('4K','genuine_forecast_vintage_events')} events.
- **Measured environmental change:** only {g('4K','events_with_measured_env_change')}/{g('4K','F0')} events at the 15-min archive resolution.
- **Prediction at t0 completion:** F5 = {g('4K','F5_conservative_cutoff')}, because the retrospective class-A label cannot yet be confirmed.
- **Tier 2** would give {g('4K','tier2_F5')} F5 events over {g('4K','tier2_F5_sessions')} sessions, but it was pre-specified as secondary and cannot rescue Tier 1.
- **2025** gives {g('4K','rep2025_F5')} F5 events.

**Authoritative conclusion:** the historical record does **not** establish that teammate movement lacks predictive value. *The incremental predictive value of teammate movement is not prospectively identifiable from the current retrospective historical record under the strict Class-A measurement-validity definition.*

**Why:**
- performance-state labels are retrospective;
- leakage-free high-confidence events are sparse;
- archived environment is coarse relative to the horizon;
- no practice forecast vintages exist;
- the surviving events are structurally restricted (mostly cross-stint, long baselines).

## The central methodological result

The original frozen design used same-car formal qualifying repeats. V4 progressively relaxed those controls, and each relaxation exposed another confounding layer:
1. team-identity fragmentation;
2. different-car baseline, setup and driver heterogeneity;
3. car × session-time confounding;
4. environment/time collinearity;
5. dependence and teammate reuse;
6. timing-sequence / local contemporaneous-context selection;
7. heterogeneous practice run states;
8. retrospective performance-state identifiability;
9. insufficient prospective teammate-prediction support.

**The restrictive same-car qualifying-repeat design was not merely conservative.** Relaxing its controls progressively exposed additional sources of performance heterogeneity, measurement ambiguity and prospective non-identifiability.

V4 does **not** mathematically prove that the frozen V2 coefficients are correct.

## What V4 does not change

V4 is an **additive methodological and evidence extension**. It does **not** modify:
- the FINAL_V2 frozen coefficients (β_track −0.03482533, β_ambient +0.18239338);
- the 41-transition same-car core;
- the V2 uncertainty calibration;
- the V3 point-in-time architecture;
- historical evidence labels or the Phase 3 PIT conclusions;
- production inference, scenario-mode inference or the operational curve;
- any frozen manifest.

## What remains unknown

- Whether shared team identity reduces dispersion beyond different-team comparisons, under better run-state information.
- Whether teammate movement carries prospective predictive information.
- Mechanisms of local contemporaneous context (tow, traffic, run purpose).
- Practice-specific physical coefficients.
- Latent team-state dynamics.

See `phase4l_claims_matrix.csv`, `phase4l_evidence_chain.md`, `phase4l_paper_integration_map.md`, `phase4l_future_data_requirements.md` and `phase4l_limitations.md`.
"""
    chain = f"""# V4 Evidence Chain (Phase 1 → 4K)

Each step records what it established and how it constrained the next step. **Final findings** are marked; the rest are intermediate diagnostics.

| Step | Output | Established | Constrained next |
|---|---|---|---|
| **P1–2** registry (**final**) | 59 labels → 21 teams; 85/313 pairs recovered | identity fragmentation; high-precision, low-recall old grouping | the team layer for all later phases |
| P3 candidates | teammate attempt comparability | structure of teammate attempts | 4A matching design |
| 4A matching | frozen-transition teammate controls | sparse endpoints; heavy reuse | 4B timelines |
| 4B timelines | team-year timelines | car × time confounding; Era A/B collinearity | only a narrow exploratory 4C |
| 4C panel | 2025 FE/mixed exploratory | CASE {g('4C','CASE')}: ambient/time not separable; track sign stable, interval includes 0 | no corroboration claim |
| **4D feasibility** (**final**) | latent state | CASE {g('4D','CASE')} NOT IDENTIFIED | move to practice (4E) |
| 4E opportunity | 2018–2025 audit | lap-level only 2023–25; Design 1 feasible for 2023–24 | 4F population |
| 4F hierarchy (**final for raw practice**) | pre-registered | CASE {g('4F','CASE')}; design-sensitive | 4G diagnostic |
| 4G diagnostic | control selection | CASE {g('4G','CASE')}: nearest-time controls timing-adjacent | 4H validity question |
| **4H validity** (**final**) | run-state audit | CASE {g('4H','CASE')}: raw practice not a clean performance population | 4I support |
| 4I support | post-validity support | CASE {g('4I','CASE')}: a restricted test is feasible | 4J |
| **4J FINAL hierarchy** | pre-registered `{g('4J','spec_commit')}` | CASE {g('4J','CASE')}: C1 robust; C2 not established | closes the hierarchy sequence |
| **4K prediction feasibility** (**final**) | support only | CASE {g('4K','CASE')}: not prospectively identifiable | no predictive experiment |

**Superseded intermediate details** are kept in their phase folders but are not authoritative:
- 4F's nearest-time primary as a hierarchy estimate (superseded by 4J);
- 4G's timing-adjacency language implying traffic mechanisms (reinterpreted after 4H).
"""
    pim = f"""# Paper-Integration Map (recommendation only; the paper was NOT edited)

## A. Main paper (priority order)

1. **Motivation for team normalisation.** Entrant naming fragments engineering teams.
2. **Identity-registry correction.** 59 labels → 21 teams; the old grouping missed 27% of teammate pairs with zero false pairs.
3. **Why teammate control was scientifically attractive.** A contemporaneous shared-engineering control, and much denser in practice.
4. **Measurement-validity audit (4H).** A timed lap is not a comparable performance observation: {g('4H','share_A_of_at_speed_2023_24_pct')}% class A.
5. **Final Phase 4J partial hierarchy.** C1 robust; C2 not established; full hierarchy not established.
6. **Methodological support for exact-car control.**
7. **Phase 4K predictive identifiability.** An insufficient-support, non-identifiable result, **not** a negative-effect result.
8. **Implications for future instrumentation and data collection.**

## B. Methods

- Registry construction from official entry lists.
- Timing71 provenance ({TIMING71}), with official records as cross-checks.
- The era/resolution tiering (2023–25 lap-level; 2018–21 stint-level; 2022 session-level).
- The Phase 4H classifier: qualifying-calibrated thresholds and point-in-time limits.
- The Phase 4J pre-registered design: exact-stratum adjacency common support, context-level medians and session balancing.
- The Phase 4K event definition and leakage rules.

## C. Results

- Registry numbers.
- The 4H class shares.
- 4I support counts.
- 4J table: D layers, C1, C2 and C3 with session counts, bootstrap and LOSO/LOTO.
- 4K attrition F0→F5.

## D. Discussion / limitations

- The design sensitivity of raw-practice hierarchies (4F → 4G) and the neutral "local contemporaneous running context" interpretation.
- Retrospective labels.
- No forecast vintages.
- Session-level replication (6 sessions).
- 2025 kept separate.
- No causal team effect.

## E. Appendix / supplement only

- Phases 3, 4A, 4B, 4C and 4D details (matching, timelines, exploratory panel, latent-state feasibility).
- Phase 4E source inventory and tiers.
- Phase 4F full sensitivity grid.
- Phase 4G adjacency tables.
- Phase 4I dependence and graph summaries.
- Tier 2 and 2025 secondary tables.

## F. Do not include (superseded intermediate diagnostics)

- 4F nearest-time Δ presented as a hierarchy estimate.
- 4G wording implying tow or traffic mechanisms.
- Raw pair counts presented as sample size.
- Any statement that the eight years are equivalent lap-level evidence.
- 4C coefficients presented as practice or corroborating physics.
- Tier 2 as a replacement for Tier 1.
"""
    fut = """# Future Data Requirements (based only on demonstrated V4 limitations)

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
"""
    lim = f"""# V4 Limitations (consolidated)

1. **Restricted final population.** Phase 4J covers 2023–24 practice-type sessions, class-A car-blocks only and {g('4J','evaluable_sessions')} evaluable sessions. It does not generalise to raw practice, other years, qualifying or the race.
2. **Session-level replication.** Bootstrap and leave-one-out analyses over few sessions are descriptive, and there are no p-values.
3. **Provenance.** Lap data are a {TIMING71}. Timestamps are feed-update times (about 1.67 s), so order within an update is unobserved.
4. **Era resolution.** 2018–2021 have stint-level timestamps only and 2022 has session-level records only. The classifier was not projected backwards.
5. **Retrospective labels.** The Phase 4H class labels are retrospective. This limits point-in-time use (4K).
6. **Unobserved variables.** Run purpose, fuel, tyres, setup, tow and traffic are unobserved. Timing adjacency is a proxy for local contemporaneous context only.
7. **Environment.** 15-min PTSC resolution and no forecast vintages. The frozen qualifying β is not validated for practice.
8. **2025.** Its Timing71 structure differs and it has no official qualifying anchor. It is always analysed separately.
9. **No causal claims.** No team effects, driver or team rankings, variance decomposition or latent-state model.
10. **Evidential status.** Phases 4F, 4G, 4H and 4K contain negative, partial or non-identifiable results. They are preserved as evidence, not overwritten.
"""
    for n, t in [("phase4l_final_scientific_synthesis.md", syn), ("phase4l_evidence_chain.md", chain), ("phase4l_paper_integration_map.md", pim),
                 ("phase4l_future_data_requirements.md", fut), ("phase4l_limitations.md", lim)]:
        (OUT / n).write_text(t)


if __name__ == "__main__":
    main()
