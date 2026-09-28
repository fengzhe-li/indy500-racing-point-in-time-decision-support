"""V4 Phase 4E: required output tables, figures and reports from the audit cache (descriptive only)."""
import pickle
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4e"
FIG = OUT / "figures"
WINDOWS = [1, 2, 5, 10, 15, 30]
CATS = ["PRACTICE", "FAST_FRIDAY", "QUALIFYING_WEEKEND_PRACTICE", "QUALIFYING_DAY1", "QUALIFYING_OTHER", "POST_QUALIFYING_PRACTICE", "CARB_DAY", "RACE", "AGGREGATE_RESULT"]
IDENT_CATS = ["PRACTICE", "FAST_FRIDAY", "QUALIFYING_DAY1", "QUALIFYING_OTHER", "POST_QUALIFYING_PRACTICE", "CARB_DAY", "RACE"]
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
TIERC = {"A": "#0f3f7a", "B": "#2a78d6", "C": "#9dc3f0", "D": "#e4e3df"}
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 9, "legend.frameon": False})
DIAG = "Phase 4E data-opportunity audit · counts only · no model · race never pooled with other sessions · eras separate."


def md(df, index=False):
    d = df.reset_index() if index else df
    f = lambda v: "" if (isinstance(v, float) and np.isnan(v)) else (f"{v:,.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))
    return "\n".join(["| " + " | ".join(map(str, d.columns)) + " |", "|" + "|".join("---" for _ in d.columns) + "|"]
                     + ["| " + " | ".join(f(v) for v in r) + " |" for r in d.itertuples(index=False)])


def save(fig, name, top=0.92):
    fig.tight_layout(rect=(0, 0.05, 1, top))
    fig.text(0.01, 0.01, DIAG, fontsize=6.5, color=INK2)
    fig.savefig(FIG / name, dpi=140, bbox_inches="tight")
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    cache = OUT / "inputs" / "_audit_cache.pkl"   # intermediate, not committed; regenerated from committed sources when absent
    if not cache.exists():
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import v4_phase4e_audit as A
        pickle.dump(A.main(), open(cache, "wb"))
    reg, sessions, off_recs, files, laps, S, wx = pickle.load(open(cache, "rb"))
    sessions = sessions.copy()
    sessions["official_session_id"] = sessions.official_session_id.astype("Int64")
    cat_of_key = {}
    for r in sessions.itertuples(index=False):
        if r.lap_level_session_key:
            cat_of_key[r.lap_level_session_key] = (r.normalized_category, r.quality_tier, r.era, r.year)
    U = S.copy()   # one row per lap-level session key (totals never double-count shared segments)
    U["normalized_category"] = U.session_key.map(lambda k: cat_of_key.get(k, (None,))[0])
    U["quality_tier"] = U.session_key.map(lambda k: cat_of_key.get(k, (None, None))[1])
    U["official_segments"] = U.session_key.map(sessions.groupby("lap_level_session_key").official_session_name.apply(lambda s: " | ".join(s)))

    # ---- source inventory (post-retrieval update; pre-retrieval version is in git history, commit d2d65e4)
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import v4_phase4e_source_inventory as SI   # rebuild the pre-retrieval inventory deterministically, then add retrieval status
    SI.main(str(OUT / "inputs" / "timing71_indy500_candidates_head_probe.csv"))
    inv = pd.read_csv(OUT / "source_inventory.csv", low_memory=False)
    man = pd.read_csv(V4 / "evidence/phase4e/retrieval_manifest.csv")
    inv = inv.merge(man[["source_id", "local_path", "bytes", "sha256", "retrieved_utc", "http_status"]].rename(columns={"local_path": "retrieved_path"}), on="source_id", how="left")
    inv["retrieval_date"] = np.where(inv.retrieved_utc.notna(), "retrieved " + inv.retrieved_utc.astype(str), inv.retrieval_date)
    inv["local"] = inv.local.astype(str).eq("True") | inv.retrieved_path.notna()
    fstat = files.set_index("source_id")[["map_status", "content_description", "format"]]
    inv = inv.join(fstat, on="source_id")
    inv.to_csv(OUT / "source_inventory.csv", index=False)

    # ---- session inventory
    si = sessions.assign(scheduled_start_end="not in retrieved sources", actual_timing_span_min=sessions.timing_span_min.round(1),
                         technical_era=sessions.era, weather_availability=np.where(sessions.weather_observed_in_span, "PTSC_OBSERVED", "MISSING"),
                         canonical_team_mapping=np.where(sessions.identity_match_share.fillna(-1) >= 0.95, "V4_REGISTRY_EXACT_CAR_JOIN",
                                                         np.where(sessions.lap_level_session_key != "", "PARTIAL", "OFFICIAL_RECORDS_ONLY (join possible, not lap-level)")),
                         analysis_potential=sessions.quality_tier)[
        ["year", "event", "official_session_id", "official_session_name", "normalized_category", "subtype", "session_date", "scheduled_start_end",
         "timing_span_start_utc", "actual_timing_span_min", "technical_era", "source_availability", "timing_resolution", "weather_availability",
         "canonical_team_mapping", "analysis_potential", "lap_level_session_key", "lap_data_shared_by_n_official_segments", "official_records", "official_reports"]]
    si.to_csv(OUT / "session_inventory.csv", index=False)

    # ---- observation granularity
    gran = []
    for r in sessions.itertuples(index=False):
        modern = isinstance(r.formats, str) and "MODERN" in r.formats
        legacy = isinstance(r.formats, str) and "LEGACY" in r.formats
        lap = modern or legacy
        q = r.normalized_category in ("QUALIFYING_DAY1", "QUALIFYING_OTHER")
        gran.append(dict(year=r.year, official_session_name=r.official_session_name, normalized_category=r.normalized_category,
                         finest_unit=("lap (observed timestamp)" if modern else "lap (stint-level timestamps; lap times derived)" if legacy
                                      else "session-level best lap per car" if r.official_json else "none"),
                         car_number=True, driver=True, canonical_team="via V4 registry (exact car join)", lap_number=modern, lap_time=lap,
                         lap_speed="derived from lap time (2.5 mi)" if lap else False,
                         four_lap_average=("official results + accepted Phase 3 layer (Day 1)" if r.normalized_category == "QUALIFYING_DAY1" else
                                           "official results" if q else False),
                         timestamp="OBSERVED" if modern else "STINT_START_END_ONLY" if legacy else False, session_elapsed_time="derivable from timestamp" if lap else False,
                         run_attempt_identifier="stint index" if lap else False, pit_status="stint boundaries" if lap else False,
                         in_out_lap="derived (first/last lap of stint)" if lap else False, stint_identifier=lap,
                         position="final only (official); race lap chart PDF not ingested" if r.normalized_category == "RACE" else "final only",
                         track_status_caution="per-lap flag" if lap else False, traffic=False, weather="PTSC 15-min (Firestone archive)" if r.weather_observed_in_span else False,
                         tyre="not identified (feed column present, not populated reliably)", fuel=False))
    pd.DataFrame(gran).to_csv(OUT / "observation_granularity.csv", index=False)

    # ---- team join coverage
    carj = laps.drop_duplicates(["year", "car"])[["year", "car", "driver", "team_raw", "join_status", "join_method", "canonical_engineering_team", "raw_entry_name",
                                                 "relationship_type", "primary_layer", "technical_partnership_only", "registry_car", "registry_driver", "driver_matches_registry"]]
    carj = carj.assign(engineering_preparation_entity=carj.canonical_engineering_team, level="CAR")
    sess_j = U[["session_key", "cars", "identity_match_share", "unmatched_cars", "technical_partnership_valid_laps"]].assign(level="SESSION")
    pd.concat([sess_j, carj], ignore_index=True).to_csv(OUT / "team_join_coverage.csv", index=False)

    U["timestamp_basis"] = np.where(U.observed_lap_timestamp_share >= 0.8, "OBSERVED_LAP_TIMESTAMPS",
                                    "DERIVED_FROM_STINTS (indicative only; fails spec criterion T)")
    base = ["session_key", "year", "era", "normalized_category", "quality_tier", "timestamp_basis", "official_segments", "valid_laps", "cars", "drivers",
            "canonical_teams", "multi_car_teams", "teams_3plus", "valid_laps_multi_car_teams"]
    st = U[base + [f"same_team_pairs_le{w}" for w in WINDOWS] + ["distinct_same_team_car_pairs_le5", "distinct_team_5min_cells_2plus_cars", "teams_with_same_team_overlap_le5"]]
    st.to_csv(OUT / "same_team_opportunities.csv", index=False)
    dtm = U[base + [f"diff_team_pairs_le{w}" for w in WINDOWS]]
    dtm.to_csv(OUT / "different_team_opportunities.csv", index=False)
    sc = U[base + ["cars_ge2", "cars_ge3", "cars_ge5", "cars_ge10", "same_car_gap_min_p10", "same_car_gap_min_median", "same_car_gap_min_p90"]
           + [f"same_car_pairs_le{w}" for w in WINDOWS]].assign(
        autocorrelation_flag=np.where(U.normalized_category.isin(["PRACTICE", "FAST_FRIDAY", "POST_QUALIFYING_PRACTICE", "CARB_DAY", "QUALIFYING_WEEKEND_PRACTICE", "RACE"]),
                                      "consecutive laps within a stint are serially dependent (fuel/tyre/traffic state)", "laps within a 4-lap run are dependent; runs are the unit"))
    sc.to_csv(OUT / "same_car_opportunities.csv", index=False)
    tcols = [c for c in U.columns if c.startswith(("nearest_teammate_min_", "teammate_abs_dtrack_c_", "teammate_abs_dambient_c_"))]
    U[base + tcols].to_csv(OUT / "temporal_overlap_summary.csv", index=False)
    rcols = [c for c in U.columns if c.startswith("ref_")] + ["valid_laps_in_multi_car_team_timed"]
    tr = U[base + rcols].copy()
    tr["share_with_loo_mean_le5"] = tr.ref_nearest_or_loo_mean_le5 / tr.valid_laps_in_multi_car_team_timed.replace(0, np.nan)
    tr.to_csv(OUT / "team_reference_feasibility.csv", index=False)
    U[base + ["hier_A_same_car", "hier_B_same_team", "hier_C_diff_team", "hier_all_three"]].to_csv(OUT / "evidence_hierarchy_feasibility.csv", index=False)

    # ---- cross-session identity (lap-level valid laps, and official session records incl. 2022)
    vl = laps[laps.valid_lap & (laps.join_status == "MATCHED")]
    abc_keys = set(U[U.quality_tier.isin(["A", "B", "C"])].session_key)
    vl_abc = vl[vl.session_key.isin(abc_keys)]
    lapcat = vl_abc.groupby(["year", "registry_car"]).normalized_category.apply(lambda s: set(s) & set(IDENT_CATS))   # spec §8: Tier A/B/C sessions only
    orec = off_recs.merge(sessions[["official_session_id", "normalized_category"]].dropna(subset=["official_session_id"]).astype({"official_session_id": int}),
                          on="official_session_id", how="left")
    orec = orec[orec.normalized_category.isin(IDENT_CATS) & (orec.laps_complete.fillna(0) > 0)]
    offcat = orec.groupby(["year", "car_number"]).normalized_category.apply(set)
    prim = reg[reg.primary]
    ci = []
    for r in prim.itertuples(index=False):
        a = lapcat.get((r.year, r.car_number), set())
        b = offcat.get((r.year, r.car_number), set())
        avail_lap = set(U[(U.year == r.year) & U.session_key.isin(abc_keys)].normalized_category) & set(IDENT_CATS)
        ci.append(dict(year=r.year, era=sessions[sessions.year == r.year].era.iloc[0], car_number=r.car_number, driver=r.driver,
                       canonical_engineering_team=r.canonical_engineering_team, lap_level_categories="|".join(sorted(a)), n_lap_level_categories=len(a),
                       lap_level_categories_available_in_year=len(avail_lap), official_record_categories="|".join(sorted(b)), n_official_categories=len(b)))
    ci = pd.DataFrame(ci)
    ci.to_csv(OUT / "cross_session_identity.csv", index=False)

    # ---- cross-year team coverage (per era; counts only)
    ctr = []
    for (era, team), g in ci.groupby(["era", "canonical_engineering_team"]):
        vv = vl[(vl.canonical_engineering_team == team) & vl.year.isin(g.year.unique())]
        ctr.append(dict(era=era, canonical_engineering_team=team, years="|".join(map(str, sorted(g.year.unique()))), n_years=g.year.nunique(),
                        lap_level_sessions=vv.session_key.nunique(), cars=len(g), drivers=g.driver.nunique(), valid_laps_non_race=int((vv.normalized_category != "RACE").sum()),
                        valid_laps_race=int((vv.normalized_category == "RACE").sum()),
                        official_session_records=int(off_recs[off_recs.year.isin(g.year.unique()) & off_recs.car_number.isin(g.car_number)].shape[0])))
    ctr = pd.DataFrame(ctr)
    # same-team pair opportunities per team require per-team recount: count distinct team-5min cells from laps
    cells = vl[vl.primary_layer.fillna(False).astype(bool)].assign(b=lambda d: (d.ts // 300)).groupby(["canonical_engineering_team", "session_key", "b"]).registry_car.nunique()
    cells = cells[cells >= 2].reset_index().merge(U[["session_key", "normalized_category", "era"]], on="session_key")
    cc = cells.groupby(["era", "canonical_engineering_team", cells.normalized_category == "RACE"]).size().unstack(fill_value=0).rename(columns={False: "same_team_5min_cells_non_race", True: "same_team_5min_cells_race"}).reset_index()
    ctr = ctr.merge(cc, on=["era", "canonical_engineering_team"], how="left").fillna({"same_team_5min_cells_non_race": 0, "same_team_5min_cells_race": 0})
    ctr.to_csv(OUT / "cross_year_team_coverage.csv", index=False)

    # ---- weather coverage (per official session; no imputation)
    hrrr_day1 = {(y, "QUALIFYING_DAY1") for y in range(2020, 2025)}
    wc = sessions[["year", "official_session_name", "normalized_category", "session_date", "ptsc_obs_in_span", "weather_observed_in_span", "weather_ptsc_on_date"]].copy()
    obs = np.where(wc.weather_observed_in_span, "OBSERVED", "MISSING")
    wc["ambient_temperature"], wc["track_temperature"], wc["humidity"], wc["pressure"] = obs, obs, obs, obs
    wc["wind"] = np.where(wc.weather_observed_in_span, "OBSERVED_UNIT_UNVERIFIED", "MISSING")
    fc = [("FORECAST (HRRR, issue-gated; local)" if (y, c) in hrrr_day1 else "MISSING (HRRR recoverable externally; not retrieved)") for y, c in zip(wc.year, wc.normalized_category)]
    wc["solar_radiation"], wc["cloud"], wc["forecast_vintage"] = fc, fc, fc
    wc["note"] = "PTSC extracted from Firestone archive for all event days (validated vs R6 canonical 2019/2025 Day 1)"
    wc.to_csv(OUT / "weather_coverage.csv", index=False)

    # ---- sampling / dependence
    sd = U[base + ["raw_laps_all", "non_at_speed_laps", "valid_laps_per_car_median", "stints_with_valid_laps", "valid_laps_per_stint_median",
                   "within_stint_lag1_autocorr_median", "stints_for_autocorr", "distinct_same_team_car_pairs_le5", "distinct_team_5min_cells_2plus_cars",
                   "same_team_pairs_le5"]].copy()
    sd["raw_observation_count"] = sd.raw_laps_all
    sd["effective_information_proxy"] = sd.distinct_team_5min_cells_2plus_cars
    sd["raw_to_effective_ratio"] = sd.same_team_pairs_le5 / sd.distinct_team_5min_cells_2plus_cars.replace(0, np.nan)
    sd["note"] = "raw lap/pair counts are NOT independent observations; effective proxy = distinct (team, 5-min) cells with >=2 same-team cars at speed"
    sd.to_csv(OUT / "sampling_dependence_audit.csv", index=False)

    # ---- tiers
    tiers = sessions[["year", "era", "official_session_id", "official_session_name", "normalized_category", "state_class", "lap_level_session_key", "T_lap_timestamps",
                      "identity_match_share", "multi_car_teams", "same_team_pairs_le5", "teams_with_same_team_overlap_le5", "weather_observed_in_span",
                      "P_provenance", "quality_tier", "tier_reason", "lap_data_shared_by_n_official_segments"]]
    tiers.to_csv(OUT / "session_quality_tiers.csv", index=False)

    # ---- future design feasibility (spec §8, mechanical)
    AB = U[U.quality_tier.isin(["A", "B"])]
    fd = []
    for era, g in [("ERA_B_REFERENCE", AB[AB.era == "ERA_B_REFERENCE"]), ("ERA_C_HYBRID", AB[AB.era == "ERA_C_HYBRID"]), ("ERA_A_PRE_AEROSCREEN", AB[AB.era == "ERA_A_PRE_AEROSCREEN"])]:
        n3 = g[g.hier_all_three]
        d1 = "FEASIBLE NOW" if len(n3) >= 10 and n3.year.nunique() >= 2 else ("FEASIBLE WITH ADDITIONAL DATA" if len(n3) >= 1 or era != "ERA_C_HYBRID" else "NOT IDENTIFIED")
        tr_e = tr[tr.session_key.isin(g.session_key)]
        d2n = int((tr_e.share_with_loo_mean_le5 >= 0.5).sum())
        d2 = "FEASIBLE NOW" if d2n >= 10 else ("FEASIBLE WITH ADDITIONAL DATA" if era != "ERA_C_HYBRID" or d2n > 0 else "NOT IDENTIFIED")
        cie = ci[ci.era == era]
        share3 = float((cie.n_lap_level_categories >= 3).mean()) if len(cie) else 0.0
        d3 = "FEASIBLE NOW" if share3 >= 0.5 else ("FEASIBLE WITH ADDITIONAL DATA" if (cie.n_official_categories >= 3).mean() >= 0.5 else "NOT IDENTIFIED")
        d4n = int((g.multi_car_teams >= 3).sum())
        d4 = "FEASIBLE NOW" if d4n >= 10 else ("FEASIBLE WITH ADDITIONAL DATA" if era != "ERA_C_HYBRID" or d4n > 0 else "NOT IDENTIFIED")
        race = U[(U.era == era) & (U.normalized_category == "RACE")]
        d5 = "WEAK / HIGH-CONFOUNDING" if len(race) else "NOT IDENTIFIED (no lap-level race data retrieved)"
        note = ("; only one in-scope year of this regime (2026 same-regime sessions exist in the Timing71 listing, outside Phase 4E scope)" if era == "ERA_C_HYBRID"
                else "; 2018-2019 sessions are Tier D (no observed lap timestamps) - replay ZIPs would supply them" if era == "ERA_A_PRE_AEROSCREEN"
                else "; 2023-2024 only (2020-2021 need replay ZIPs; 2022 needs official PDFs)")
        for d, lab, det in [("DESIGN_1_evidence_hierarchy", d1, f"Tier A/B sessions with all_three: {len(n3)} over {n3.year.nunique()} year(s)" + note),
                            ("DESIGN_2_within_team_relative", d2, f"Tier A/B sessions with >=50% multi-car-team laps having a LOO team reference within ±5 min: {d2n}" + note),
                            ("DESIGN_3_cross_session_persistence", d3, f"share of primary-layer cars with valid laps in >=3 categories (Tier A/B/C sessions only): {share3:.2f}; "
                             f"official-record linkage >=3 categories: {(cie.n_official_categories >= 3).mean():.2f}"),
                            ("DESIGN_4_within_team_dispersion", d4, f"Tier A/B sessions with >=3 multi-car teams: {d4n}" + note),
                            ("DESIGN_5_race_teammate_pace", d5, f"lap-level race sessions: {len(race)} (tiers: {'/'.join(sorted(race.quality_tier.dropna().unique()))}; race is at best Tier C by rule; fuel/tyre/traffic unobserved)")]:
            fd.append(dict(era=era, design=d, feasibility=lab, evidence=det))
    fdd = pd.DataFrame(fd)
    fdd.to_csv(OUT / "future_design_feasibility.csv", index=False)

    # ---- opportunity matrix (year x category)
    om = []
    for (y, c), g in sessions.groupby(["year", "normalized_category"]):
        keys = [k for k in g.lap_level_session_key.unique() if k]
        u = U[U.session_key.isin(keys)]
        om.append(dict(year=y, era=g.era.iloc[0], normalized_category=c, official_sessions=len(g), source_available=bool(len(g)),
                       machine_readable=bool((g.official_json != "").any()), lap_run_level=bool(keys),
                       timestamp_available="OBSERVED" if g.T_lap_timestamps.any() else ("STINT_ONLY" if keys else "NONE"),
                       canonical_team_join=bool(keys) and bool((u.identity_match_share >= 0.95).all()),
                       same_car_repeats=int(u.cars_ge2.sum()) if len(u) else 0, same_team_overlap_pairs_le5=int(u.same_team_pairs_le5.sum()) if len(u) else 0,
                       same_team_5min_cells=int(u.distinct_team_5min_cells_2plus_cars.sum()) if len(u) else 0,
                       different_team_controls_le5=int(u.diff_team_pairs_le5.sum()) if len(u) else 0,
                       weather="PTSC_OBSERVED" if g.weather_observed_in_span.all() else ("PARTIAL" if g.weather_observed_in_span.any() else "MISSING"),
                       race_or_state_confounders=g.state_class.iloc[0], quality_tier="/".join(sorted(g.quality_tier.unique()))))
    omd = pd.DataFrame(om)
    omd.to_csv(OUT / "opportunity_matrix.csv", index=False)
    figures(sessions, U, ci, ctr, fdd, tr, wc)
    reports(reg, sessions, U, files, laps, ci, ctr, fdd, tr, wc, omd, inv, sd)


def figures(sessions, U, ci, ctr, fdd, tr, wc):
    years = list(range(2018, 2026))
    cats = [c for c in CATS if c != "AGGREGATE_RESULT"]
    # 1 availability heatmap (tier)
    M = np.full((len(cats), len(years)), -1.0)
    lab = np.full((len(cats), len(years)), "", dtype=object)
    tv = {"D": 0, "C": 1, "B": 2, "A": 3}
    for (y, c), g in sessions[sessions.normalized_category.isin(cats)].groupby(["year", "normalized_category"]):
        best = max(g.quality_tier, key=lambda t: tv[t])
        M[cats.index(c), years.index(y)] = tv[best]
        lab[cats.index(c), years.index(y)] = f"{best} ({len(g)})"
    fig, ax = plt.subplots(figsize=(10, 4.2))
    cmap = matplotlib.colors.ListedColormap([SURFACE, TIERC["D"], TIERC["C"], TIERC["B"], TIERC["A"]])
    ax.imshow(M + 1, cmap=cmap, vmin=0, vmax=4, aspect="auto")
    for (i, k), v in np.ndenumerate(lab):
        ax.text(k, i, v, ha="center", va="center", fontsize=7.5, color="white" if M[i, k] >= 2 else INK)
    ax.set_xticks(range(len(years)), years)
    ax.set_yticks(range(len(cats)), cats, fontsize=7.5)
    ax.grid(False)
    ax.set_xlabel("cell = best tier among official sessions of that category (n sessions); blank = no such session that year")
    ax.set_title("1. 2018–2025 year × session availability and data-quality tier", loc="left", fontsize=10.5)
    save(fig, "fig01_availability_tier_heatmap.png", top=0.97)
    # 2/3/4 use only sessions with OBSERVED lap timestamps (2023-2025), faceted by era (never pooled)
    O = U[U.timestamp_basis == "OBSERVED_LAP_TIMESTAMPS"]
    eras = [("ERA_B_REFERENCE", "2023–2024 (Era B)"), ("ERA_C_HYBRID", "2025 (Era C)")]
    present = [c for c in cats if c in set(O.normalized_category)]
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.9), sharey=True)
    for ax, (era, ttl) in zip(axes, eras):
        for k, c in enumerate(present):
            g = O[(O.era == era) & (O.normalized_category == c)]
            if len(g):
                ax.plot(WINDOWS, [max(g[f"same_team_pairs_le{w}"].sum(), 0.8) for w in WINDOWS], "-o", color=CAT[k % 8], label=c, ms=4)
        ax.set_yscale("log"); ax.set_xticks(WINDOWS); ax.set_xlabel("window (± min)"); ax.set_title(ttl, fontsize=9)
    axes[0].set_ylabel("same-team different-car valid-lap pairs (raw)")
    axes[1].legend(fontsize=6.5, loc="lower right")
    fig.suptitle("2. Same-team opportunities by session type and window (observed-timestamp sessions only; eras separate; race is its own line)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig02_same_team_opportunities_by_session_type.png")
    fig, axes = plt.subplots(1, 2, figsize=(13, 4), sharey=True)
    wdt = 0.27
    for ax, (era, ttl) in zip(axes, eras):
        for j, (col, lab_, cc) in enumerate([("same_car_pairs_le5", "same car", CAT[0]), ("same_team_pairs_le5", "same team, different car", CAT[1]), ("diff_team_pairs_le5", "different team", CAT[2])]):
            ax.bar(np.arange(len(present)) + (j - 1) * wdt, [max(O[(O.era == era) & (O.normalized_category == c)][col].sum(), 0.8) for c in present], width=wdt, color=cc, label=lab_)
        ax.set_yscale("log"); ax.set_xticks(range(len(present)), present, rotation=35, ha="right", fontsize=7); ax.set_title(ttl, fontsize=9)
    axes[0].set_ylabel("valid-lap pairs within ±5 min (raw, log)")
    axes[1].legend(fontsize=7.5)
    fig.suptitle("3. Same-car vs same-team vs different-team close-time opportunities (raw pairs; not independent; eras separate)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig03_samecar_sameteam_diffteam_counts.png")
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.9), sharey=True)
    for ax, (era, ttl) in zip(axes, eras):
        for k, c in enumerate(present):
            g = O[(O.era == era) & (O.normalized_category == c)]
            if not len(g):
                continue
            ax.scatter([k] * len(g), g.nearest_teammate_min_p050, s=16, color=CAT[k % 8])
            ax.vlines(k, g.nearest_teammate_min_p025.min(), g.nearest_teammate_min_p075.max(), color=CAT[k % 8], lw=2, alpha=0.6)
        ax.set_yscale("log"); ax.set_xticks(range(len(present)), present, rotation=35, ha="right", fontsize=7); ax.set_title(ttl, fontsize=9)
    axes[0].set_ylabel("nearest same-team other-car valid lap (min)")
    fig.suptitle("4. Teammate temporal gap by session type (dots = session medians; line = range of session IQRs)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig04_teammate_gap_by_session_type.png")
    # 5 weather coverage heatmap
    W = np.full((len(cats), len(years)), np.nan)
    for (y, c), g in wc[wc.normalized_category.isin(cats)].groupby(["year", "normalized_category"]):
        W[cats.index(c), years.index(y)] = g.weather_ptsc_on_date.mean()
    fig, ax = plt.subplots(figsize=(10, 4))
    cm = matplotlib.colors.LinearSegmentedColormap.from_list("s", ["#eef4fc", CAT[0]])
    cm.set_bad(SURFACE)
    ax.imshow(np.ma.masked_invalid(W), cmap=cm, vmin=0, vmax=1, aspect="auto")
    for (i, k), v in np.ndenumerate(W):
        if not np.isnan(v):
            ax.text(k, i, f"{v:.0%}", ha="center", va="center", fontsize=7.5, color="white" if v > 0.6 else INK)
    ax.set_xticks(range(len(years)), years)
    ax.set_yticks(range(len(cats)), cats, fontsize=7.5)
    ax.grid(False)
    ax.set_xlabel("share of official sessions whose date has PTSC observations (ambient, track, humidity, pressure; wind unit-unverified). Solar/cloud: HRRR Day 1 2020–24 only")
    ax.set_title("5. Observed weather (PTSC) coverage by year × session type", loc="left", fontsize=10.5)
    save(fig, "fig05_weather_coverage.png", top=0.97)
    # 6 cross-session identity
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6), sharey=True)
    for ax, col, ttl in [(axes[0], "n_lap_level_categories", "lap-level (valid laps)"), (axes[1], "n_official_categories", "official session records")]:
        for k, era in enumerate(["ERA_A_PRE_AEROSCREEN", "ERA_B_REFERENCE", "ERA_C_HYBRID"]):
            g = ci[ci.era == era]
            vals = [(g[col] >= n).mean() for n in [1, 2, 3, 4, 5, 6, 7]]
            ax.plot([1, 2, 3, 4, 5, 6, 7], vals, "-o", color=CAT[k], ms=4, label=era)
        ax.set_xlabel("linked across ≥ n session categories")
        ax.set_title(ttl, fontsize=9)
    axes[0].set_ylabel("share of primary-layer cars")
    axes[1].legend(fontsize=7)
    fig.suptitle("6. Cross-session identity coverage (same car/driver/team within a year)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig06_cross_session_identity.png")
    # 7 raw vs effective
    fig, ax = plt.subplots(figsize=(8, 4))
    O = U[U.timestamp_basis == "OBSERVED_LAP_TIMESTAMPS"]
    present = [c for c in cats if c in set(O.normalized_category)]
    for k, c in enumerate(present):
        for era, mk in [("ERA_B_REFERENCE", "o"), ("ERA_C_HYBRID", "^")]:
            g = O[(O.normalized_category == c) & (O.era == era)]
            ax.scatter(g.same_team_pairs_le5.clip(lower=0.8), g.distinct_team_5min_cells_2plus_cars.clip(lower=0.8), s=28, marker=mk, color=CAT[k % 8],
                       label=c if era == "ERA_B_REFERENCE" else None)
    ax.scatter([], [], marker="o", color=INK2, label="circle = 2023–24"); ax.scatter([], [], marker="^", color=INK2, label="triangle = 2025")
    ax.set_xscale("log")
    ax.set_yscale("log")
    lim = [0.8, 1e5]
    ax.plot(lim, lim, color=GRID)
    ax.set_xlabel("raw same-team lap pairs within ±5 min")
    ax.set_ylabel("effective proxy: distinct (team, 5-min) cells")
    ax.legend(fontsize=6.5)
    ax.set_title("7. Raw observations vs effective-information proxy (observed-timestamp sessions)", loc="left", fontsize=10.5)
    save(fig, "fig07_raw_vs_effective_information.png", top=0.97)
    # 8 tier distribution
    tab = sessions.groupby(["year", "quality_tier"]).size().unstack(fill_value=0).reindex(columns=["A", "B", "C", "D"], fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 3.6))
    bottom = np.zeros(len(tab))
    for t in ["A", "B", "C", "D"]:
        ax.bar(tab.index.astype(str), tab[t], bottom=bottom, color=TIERC[t], edgecolor=SURFACE, linewidth=1.5, label=f"Tier {t}")
        bottom += tab[t].values
    ax.set_ylabel("official sessions")
    ax.legend(fontsize=7.5, ncol=4)
    ax.set_title("8. Data-quality tier distribution by year (pre-declared rules)", loc="left", fontsize=10.5)
    save(fig, "fig08_quality_tier_distribution.png", top=0.97)
    # 9 canonical team longitudinal coverage
    teams = ctr.groupby("canonical_engineering_team").n_years.sum().sort_values(ascending=False).index.tolist()
    P = np.zeros((len(teams), len(years)))
    for r in ci.itertuples(index=False):
        P[teams.index(r.canonical_engineering_team), years.index(r.year)] = max(P[teams.index(r.canonical_engineering_team), years.index(r.year)], r.n_lap_level_categories)
    cars_n = ci.groupby(["canonical_engineering_team", "year"]).size()
    fig, ax = plt.subplots(figsize=(9, 0.33 * len(teams) + 1.4))
    cm = matplotlib.colors.LinearSegmentedColormap.from_list("s", ["#eef4fc", CAT[0], "#0f3f7a"])
    ax.imshow(P, cmap=cm, vmin=0, vmax=7, aspect="auto")
    for (i, k), v in np.ndenumerate(P):
        n = cars_n.get((teams[i], years[k]), 0)
        if n:
            ax.text(k, i, f"{n}c/{int(v)}", ha="center", va="center", fontsize=6.5, color="white" if v > 4 else INK)
    ax.set_xticks(range(len(years)), years)
    ax.set_yticks(range(len(teams)), teams, fontsize=7)
    ax.grid(False)
    ax.set_xlabel("cell = primary-layer cars / max lap-level session categories linked (0 where no lap-level data)")
    ax.set_title("9. Canonical-team longitudinal coverage", loc="left", fontsize=10.5)
    save(fig, "fig09_team_longitudinal_coverage.png", top=0.97)
    # 10 design feasibility
    order = ["FEASIBLE NOW", "FEASIBLE WITH ADDITIONAL DATA", "WEAK / HIGH-CONFOUNDING", "NOT IDENTIFIED (no lap-level race data retrieved)", "NOT IDENTIFIED"]
    col = {order[0]: TIERC["A"], order[1]: TIERC["B"], order[2]: TIERC["C"], order[3]: TIERC["D"], order[4]: TIERC["D"]}
    designs = fdd.design.unique().tolist()
    eras = ["ERA_A_PRE_AEROSCREEN", "ERA_B_REFERENCE", "ERA_C_HYBRID"]
    fig, ax = plt.subplots(figsize=(11, 3.6))
    for i, d in enumerate(designs):
        for k, e in enumerate(eras):
            r = fdd[(fdd.design == d) & (fdd.era == e)].iloc[0]
            ax.add_patch(plt.Rectangle((k, i), 0.96, 0.9, color=col[r.feasibility]))
            ax.text(k + 0.48, i + 0.45, r.feasibility.replace(" (no lap-level race data retrieved)", "*"), ha="center", va="center", fontsize=7,
                    color="white" if r.feasibility == "FEASIBLE NOW" else INK)
    ax.set_xlim(0, 3)
    ax.set_ylim(0, len(designs))
    ax.set_xticks([0.48, 1.48, 2.48], eras)
    ax.set_yticks([i + 0.45 for i in range(len(designs))], designs, fontsize=7.5)
    ax.invert_yaxis()
    ax.grid(False)
    ax.set_title("10. Future-design feasibility (mechanical, spec §8; designs not run)", loc="left", fontsize=10.5)
    save(fig, "fig10_future_design_feasibility.png", top=0.97)


def reports(reg, sessions, U, files, laps, ci, ctr, fdd, tr, wc, omd, inv, sd):
    y_cat = sessions.groupby(["year", "normalized_category"]).size().unstack(fill_value=0)
    loc_ext = inv.assign(kind=inv.source_id.str.extract(r"^([A-Z0-9]+_[A-Z]+)")[0]).groupby(["authority", "local"]).size().reset_index(name="sources")
    fstat = files.groupby(["year", "map_status"]).size().unstack(fill_value=0)
    gran = pd.read_csv(OUT / "observation_granularity.csv").groupby(["normalized_category", "finest_unit"]).size().rename("sessions").reset_index()
    rawobs = U.groupby(["era", "timestamp_basis", "normalized_category"]).agg(sessions=("session_key", "size"), raw_laps=("raw_laps_all", "sum"), valid_laps=("valid_laps", "sum")).reset_index()
    ids = pd.DataFrame([dict(era=e, cars=len(g), drivers=g.driver.nunique(), teams=g.canonical_engineering_team.nunique(),
                             team_years=g[["year", "canonical_engineering_team"]].drop_duplicates().shape[0]) for e, g in ci.groupby("era")])
    win = U.groupby(["era", "timestamp_basis", "normalized_category"])[[f"same_car_pairs_le{w}" for w in WINDOWS] + [f"same_team_pairs_le{w}" for w in WINDOWS] + [f"diff_team_pairs_le{w}" for w in WINDOWS]].sum().reset_index()
    eff = U.groupby(["era", "timestamp_basis", "normalized_category"])[["distinct_same_team_car_pairs_le5", "distinct_team_5min_cells_2plus_cars", "cars_ge2", "cars_ge10"]].sum().reset_index()
    gapq = U.groupby("normalized_category")[["nearest_teammate_min_p010", "nearest_teammate_min_p025", "nearest_teammate_min_p050", "nearest_teammate_min_p075",
                                             "nearest_teammate_min_p090", "nearest_teammate_min_p100", "teammate_abs_dtrack_c_p050", "teammate_abs_dambient_c_p050"]].median().round(2).reset_index()
    tiers = sessions.groupby(["era", "quality_tier"]).size().unstack(fill_value=0).reset_index()
    tier_list = sessions[sessions.quality_tier.isin(["A", "B"])][["year", "official_session_name", "normalized_category", "quality_tier", "tier_reason"]]
    xs = ci.groupby("era").apply(lambda g: pd.Series({f"lap_level_ge{n}": int((g.n_lap_level_categories >= n).sum()) for n in [2, 3, 4]} |
                                                   {"lap_level_all_available": int((g.n_lap_level_categories >= g.lap_level_categories_available_in_year).sum() if (g.lap_level_categories_available_in_year > 0).any() else 0)} |
                                                   {f"official_ge{n}": int((g.n_official_categories >= n).sum()) for n in [2, 3, 4]} | {"cars": len(g)}), include_groups=False).reset_index()
    topteams = ctr.sort_values(["n_years", "same_team_5min_cells_non_race"], ascending=False).head(10)[["era", "canonical_engineering_team", "years", "cars", "drivers",
                                                                                                         "valid_laps_non_race", "valid_laps_race", "same_team_5min_cells_non_race"]]
    day1 = U[U.normalized_category == "QUALIFYING_DAY1"][["year", "valid_laps", "same_team_pairs_le5", "distinct_same_team_car_pairs_le5", "distinct_team_5min_cells_2plus_cars", "quality_tier"]]
    prac = U[U.normalized_category.isin(["PRACTICE", "POST_QUALIFYING_PRACTICE", "CARB_DAY", "FAST_FRIDAY"])].groupby("year")[["valid_laps", "same_team_pairs_le5", "distinct_same_team_car_pairs_le5", "distinct_team_5min_cells_2plus_cars"]].sum().reset_index()
    p3 = pd.read_csv(V4 / "output/phase3/comparability_window_counts.csv")
    fe = fdd.pivot(index="design", columns="era", values="feasibility").reset_index()
    t71_uncertain = files[files.format == "LEGACY"]

    rep = f"""# V4 Phase 4E — 2018–2025 Multi-Session Team-Comparison Data-Opportunity Audit

**Scope:** audit only.
- No model was fitted, no coefficient estimated, no team-reference metric chosen, and no performance hypothesis tested.
- No team or driver was ranked.
- Race is never pooled with other sessions, and eras are never pooled.

**Specification:** `phase4e_quality_tier_spec.md` was committed with the pre-retrieval `source_inventory.csv` (`d2d65e4`) before any retrieval or counting. Implementation clarifications made during coding are listed in `phase4e_limitations_report.md` §Implementation notes; none changes a tier rule.

**Retrieval (documented, small):**
- 101 Timing71 lap-level analysis JSONs (11.0 MB);
- 60 official INDYCAR session-detail JSONs for 2020–2024 (1.3 MB).

Every file is listed with its SHA-256 in `v4_team_normalized/evidence/phase4e/retrieval_manifest.csv`. Timing71 replay ZIPs and official lap-level PDFs were **not** ingested (documented as recoverable).

## 1. Session data by year (official session list; normalized categories)

{md(y_cat, index=True)}

## 2. Local vs requiring retrieval

{md(loc_ext)}

Timing71 file-to-session mapping outcome:

{md(fstat, index=True)}

- **Excluded as not Indy 500 IndyCar content:** the archive listing mislabelled an Indy Lights open-test practice and the Freedom 100 (2019).
- **Empty captures:** four analysis files.
- **No lap-level capture:** 2022 has no Timing71 capture; its lap-level data exist only as official PDFs.
- **Other missing captures:** 2024 Practice 4 and Last Chance, and 2025 Top-12.

## 3. Finest reliable observation unit

{md(gran)}

- **2023–2025:** lap-level with **observed** timestamps (±~1 s feed latency; median |Δtimestamp − laptime| = 0.78 s).
- **2018–2021:** the Timing71 legacy format stores stint-level start/end times plus lap times. Lap times reconstructed from stints are consistent within 15 s for only about 25% of stints, so those years do **not** meet the pre-declared "observed lap timestamp" criterion.
- **Exact legacy lap times:** would require the replay ZIPs (not retrieved).

## 4–5. Raw observations and identity

{md(rawobs)}

{md(ids)}

Identity joins to the V4 registry (exact car number, no fuzzy matching) match 100% of cars in every lap-level session.

## 6–9. Opportunity counts by window (raw valid-lap pairs; NOT independent)

{md(win)}

**Effective-information companions (±5 min):**

{md(eff)}

## 10–11. Strongest coverage

- **Contemporaneous teammate coverage:** strongest in open practice (Practice 3/4, Post-Qualifying Practice 8, Carb Day) and the race.
  - In practice, thousands of raw same-team pairs per session fall within ±5 min, spread over every multi-car team.
  - Qualifying (Day 1 and other segments) has tens.
- **Same-car repeat coverage:** strongest in practice and the race (every car has dozens of valid laps). In qualifying, laps come in 4-lap runs.

**Teammate time-gap quantiles** (session medians by category; minutes; weather differences are |Δ| of the most recent PTSC reading, 15-min resolution):

{md(gapq)}

## 12–13. Weather and state confounding

- **Observed PTSC weather:** ambient, track, humidity and pressure; wind is unit-unverified.
  - Present for essentially every event day 2018–2025 in the local Firestone archive. It is now extracted for all event days and validated against the R6 canonical 2019/2025 Day 1 values (exact match).
  - Its resolution is 15 minutes, so nearly all close-time teammates share the same reading (median |Δtrack| = 0).
- **HRRR solar/cloud forecasts:** local only for Day 1, 2020–2024.
- **Major state confounding:** the race (traffic, fuel, tyres, cautions) is always Tier C.
- **One important limitation:** every practice-type session (unobserved run plan, tow, fuel, boost).

## 14. Cross-session linkage (primary-layer cars)

{md(xs)}

## 15. Longitudinal team coverage (top 10 by years × non-race same-team 5-min cells)

{md(topteams)}

## 16. Quality tiers

{md(tiers)}

**Tier A/B sessions:**

{md(tier_list)}

## 17. Does the broader dataset improve on Day 1 qualifying?

Day 1 qualifying at lap level:

{md(day1)}

Practice-type sessions (practice, Fast Friday, post-qualifying, Carb Day) at lap level:

{md(prac)}

**Materially, yes, for contemporaneous same-team coverage, and only in 2023–2025.**
- **Scale:** practice-type sessions give ≈50–250× more distinct same-team 5-minute cells than Day 1 qualifying (2023: 616 vs 12; 2024: 421 vs 3; 2025: 491 vs 2), across all multi-car teams, with simultaneous same-car, same-team and different-team comparisons.
- **The price:** unobserved run plan, tow and fuel state (Tier B at best).
- **Dependence, measured:** the within-stint lag-1 autocorrelation of valid lap times is low in practice (session medians ≈0.0–0.1) but high in the race (≈0.5) and in 4-lap qualifying runs (≈0.8). Practice dependence comes mainly from shared run state (fuel, tyre, traffic, run plan) and from repeated car pairs, not lap-to-lap correlation; the raw-to-effective ratios (same-team pairs per distinct team × 5-min cell ≈ 60–90 in practice, ≈250 in the race) show how much raw counts overstate information.
- **2018–2022:** no improvement without additional data (exact legacy lap timestamps; 2022 lap data).
- **Accepted Day 1 attempt layer (Phase 3):** unchanged; its 2020–2024 counts are in `output/phase3/`.

## 18–22. Future designs (mechanical, spec §8; not run)

{md(fe)}

{md(fdd)}

- **Design 1 (evidence hierarchy):** feasible now for 2023–2024 (Era B) and 2025 (Era C, which has only one year and so fails the ≥2-year rule). Limited to the lap-level Tier A/B sessions.
- **Design 2 (leave-one-out team reference):** structurally supported in the same sessions.
- **Design 3 (cross-session persistence):** counted in Tier A/B/C sessions only. Linkage is strong in 2023–2025; 2018–2022 linkage exists only in official session-level records.
- **Design 4 (within-team dispersion):** feasible in 2023–2025 Tier A/B sessions.
- **Design 5 (race-only teammate pace):** weak / high-confounding by construction (fuel, tyre and traffic are not observed).

## 23. Most valuable additional data (for the strongest currently infeasible design: the hierarchy in 2018–2022)

1. **Timing71 replay ZIPs for 2018–2021** (already listed in the archive): exact lap timestamps would lift those sessions from D to B, adding four more years to Design 1 and 2 in Eras A and B.
2. **Official Section Results PDFs for 2022** (all sessions, primary source): the only lap-level route for 2022.
3. **HRRR for non-Day-1 event days:** solar/cloud context. Observed PTSC is already local.
4. **Run-plan context** (no-tow speed column, boost/fuel annotations) from the Timing71 feed columns, to narrow practice state confounding.

## 24. Recommended next scientific phase

A **pre-registered Design 1 descriptive comparison in 2023–2024 practice-type Tier A/B sessions** (Era B), with 2025 as a separate replication:
- **Question:** under matched close-time windows, how large are |Δ lap time| distances for same car vs same team/different car vs different team?
- **Units and dependence:** run-level units (stints), not laps, with cluster-aware summaries by car and team.
- **Scope:** qualifying (Day 1, Tier A) as a separate small-n stratum; race excluded or run only as a separately labelled, high-confounding sensitivity.
- **What it tests:** whether engineering-team identity removes variance beyond session matching, before any physics or latent modelling.

## 25–27

See the final summary and `phase4e_checks_log.txt`.
"""
    (OUT / "phase4e_data_opportunity_report.md").write_text(rep)

    cov = sessions[["year", "official_session_name", "normalized_category", "session_date", "source_availability", "timing_resolution", "quality_tier", "tier_reason",
                    "valid_laps", "cars", "multi_car_teams", "weather_observed_in_span", "lap_data_shared_by_n_official_segments"]].sort_values(["year", "session_date"])
    (OUT / "phase4e_session_coverage_report.md").write_text(f"""# V4 Phase 4E — Session Coverage Report

Every official 2018–2025 Indianapolis 500 session, plus Timing71-only captures, with source, timing resolution, weather and tier. Official names are preserved; categories follow spec §1.

- **Shared captures:** `lap_data_shared_by_n_official_segments > 1` means one Timing71 capture spans several official qualifying segments (e.g. Top-12 / Last Chance / Fast 6). Their lap data are identical, and totals count them once.
- **Qualifying regimes stay separate:** Day 1 vs Fast 9 / Positions 10-33 / 31-33 / Top-12 / Fast 12 / Last Chance / Fast 6 keep their official names in `subtype`, and no qualifying regimes are mixed.

{md(cov)}
""")
    fd_text = "\n".join(f"- **{r.design} ({r.era}): {r.feasibility}.** {r.evidence}" for r in fdd.itertuples(index=False))
    (OUT / "phase4e_future_design_report.md").write_text(f"""# V4 Phase 4E — Future Design Feasibility Report

Labels are mechanical (spec §8). No design was run.

{fd_text}

## Structural support for each design (counts only)

- **Design 1:** `evidence_hierarchy_feasibility.csv` gives A/B/C coexistence per lap-level session.
- **Design 2:** `team_reference_feasibility.csv` gives, per window, how many valid laps have a nearest or leave-one-car-out team reference (≥1 other car) and a leave-one-out median (≥2 other cars). The target is never in its own reference.
- **Design 3:** `cross_session_identity.csv`.
- **Design 4:** multi-car team counts per Tier A/B session.
- **Design 5:** race sessions have per-lap flags and stint boundaries. Traffic (gap), fuel and tyre state are not observable from the retrieved sources, so any race teammate comparison is high-confounding.

## What would change the labels

Exact lap timestamps for 2018–2021 (replay ZIPs) and 2022 lap data (official PDFs) would move Designs 1, 2 and 4 in Eras A and B (2018–2022) from "additional data" toward "feasible now". Nothing retrievable here removes the race's fuel/tyre/traffic confounding.
""")
    (OUT / "phase4e_limitations_report.md").write_text(f"""# V4 Phase 4E — Limitations Report

1. **Legacy timing (2018–2021).**
   - Timing71 legacy analysis files carry stint start/end timestamps and lap times, but no per-lap timestamps.
   - Reconstructing lap times from stint boundaries is consistent within 15 s for only about 25% of stints.
   - Per the pre-declared criterion (T: observed lap timestamps on ≥80% of valid laps), every 2018–2021 session is Tier D.
   - Derived timestamps are retained in the lap-level cache, labelled, and excluded from tiering.
2. **2022** has no Timing71 capture. Only session-level official records are machine-readable; lap-level data exist as official PDFs (not ingested).
3. **Secondary timing source.** Timing71 is a third-party capture of the INDYCAR feed. Captures can skip laps: about 10% of consecutive in-stint entries skip ≥1 lap. Four archive files were empty, and two archive entries were mislabelled (other series). Content was verified per file (≥80% of cars in the V4 registry and no other-series keywords).
4. **Weather.**
   - PTSC is 15-minute, so close-time teammates almost always share a reading.
   - Wind units are unverified.
   - Solar/cloud are HRRR Day 1 2020–2024 only.
   - Nothing was imputed.
5. **State confounding.**
   - Practice: run plan, tow/traffic, fuel, tyre age and boost are not observed.
   - Race: plus cautions and strategy.
   - The per-lap flag is observed; traffic is not.
6. **Pseudoreplication.**
   - Lap and pair counts are raw. They are dominated by repeated use of the same car pairs and shared run state. Within-stint lag-1 lap-time autocorrelation is low in practice (≈0.0–0.1) but high in the race (≈0.5) and qualifying runs (≈0.8); see `sampling_dependence_audit.csv`.
   - The effective-information proxies (distinct car-pairs, distinct team × 5-min cells) are orders of magnitude smaller.
7. **Validity filter.** The at-speed plausibility band (37–45 s) and the out/in-lap exclusion are declared data-quality filters. Their counts are reported (`non_at_speed_laps`); they were not tuned.

## Implementation notes (clarifications; no tier rule changed)

1. **Fast Friday name.** The spec's "Fast" qualifying keyword was intended for Fast 9 / 12 / 6 / Six segments. Official names containing "Fast Friday" (2020 "Practice 3 (Fast Friday)") are treated as practice; otherwise an official practice would have been labelled qualifying. This affects 2020 categories only, which are Tier D regardless (legacy timing).
2. **File-to-session dates.** Timing71 files are mapped by the modal local date of their laps; one 2020 capture begins with stale data from an earlier day.
3. **Timing71-only sessions.** Captures absent from the official session list (2023 Practice 1) are kept as separate inventory rows with the provenance criterion failed.
4. **Empty files.** Empty analysis files are labelled `EMPTY_ANALYSIS`, not "excluded content".
5. **Shared qualifying captures.** Where one capture spans several official qualifying segments, totals count its laps once (`lap_data_shared_by_n_official_segments`).
6. **Epoch conversion.** A weather-join timestamp conversion bug (microsecond epochs) was fixed before any tier was interpreted.
""")


if __name__ == "__main__":
    main()
