"""V4 Phase 3: teammate comparison candidate construction and comparability audit.

Descriptive only. No model is fitted, no threshold is chosen, no weight is assigned,
and nothing outside v4_team_normalized/output/phase3/ is written.

Tiers
-----
CORE_2020_2024     Day-1 attempts from the project's canonical attempt panel
                   (r4/output/r4p1_attempt_four_lap_panel_v1.csv), with the same
                   environment basis as the frozen same-car core:
                   track = past-safe PTSC track temperature, ambient = HRRR 2 m temperature.
REGIME_EXT_R6      2018 / 2019 / 2025 Day-1 attempts from the frozen R6 extension
                   (official results parse + Timing71 lap-matched timestamps +
                   linearly interpolated PTSC). Different technical regimes and a
                   different environment basis: never pooled with CORE in summaries.

Pair sign convention
--------------------
For every candidate, A is the earlier attempt by assembled timestamp (ties: lower car
sort key, then attempt_id). If either timestamp is missing, A is the lower car sort key
(then attempt_id). Every delta is B minus A, so delta_time_minutes >= 0 whenever both
timestamps exist.
"""
import itertools
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase3"
FIG = OUT / "figures"

DAY1_DATE = {2018: "2018-05-19", 2019: "2019-05-18", 2020: "2020-08-15", 2021: "2021-05-22",
             2022: "2022-05-21", 2023: "2023-05-20", 2024: "2024-05-18", 2025: "2025-05-17"}
CORE_YEARS = [2020, 2021, 2022, 2023, 2024]
EXT_YEARS = [2018, 2019, 2025]
WINDOWS = [5, 10, 15, 20, 30, 45, 60, 90, 120]
QUANTS = [0, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 1.0]
PTSC_MAX_BRACKET_MIN = 30.0  # same interpolation limit the core realized-environment layer uses

# Track-state intervals preserved from the existing reconstruction
# (weather/output/chronology_rescue_2022_weather_interruption_windows_v1.csv).
KNOWN_INTERRUPTIONS = {
    2022: [("FIRST_WEATHER_STOP", "2022-05-21T18:14:00Z", "2022-05-21T19:34:00Z"),
           ("SECOND_WEATHER_STOP_TO_SESSION_CALLED", "2022-05-21T20:00:00Z", "2022-05-21T20:50:00Z")],
}
# Recorder data-coverage gaps (NOT track-state interruptions), from data/canonical/v1/chronology_events.csv
DATA_COVERAGE_GAPS = {2020: [("KNOWN_INTERNAL_7M15S_GAP", "2020-08-15T18:35:15Z", "2020-08-15T18:42:30Z")]}

LAP_MILES = 2.5


def ts(s):
    return pd.to_datetime(s, utc=True, format="mixed", errors="coerce")


def surname(name):
    n = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().strip()
    if "," in n:  # R6 official format "Last, First"
        n = n.split(",")[0].strip()
        return n.split()[-1].lower().replace("demelo", "melo")
    n = n.replace("(R)", "").replace("(W)", "").strip()
    return n.split()[-1].lower() if n else ""


def car_sort_key(c):
    s = str(c)
    return (int(s) if s.isdigit() else 999, s)


# ------------------------------------------------------------------ registry
def load_registry():
    r = pd.read_csv(V4 / "output" / "v4_team_entry_registry.csv", dtype={"car_number": str})
    r = r[r.qualifying_participant].copy()
    r["primary_teammate_layer"] = r.strict_teammate_group.notna() & (r.strict_teammate_group != "")
    r["reg_surname"] = r.driver.map(surname)
    r.loc[r.driver == "Zachary Claman De Melo", "reg_surname"] = "melo"
    return r


def map_to_registry(att, reg):
    """Exact (year, car_number) match; 06/6 variant only as fallback with surname agreement."""
    by = {(y, c): row for y, c, row in zip(reg.year, reg.car_number, reg.to_dict("records"))}
    recs = []
    for a in att.itertuples(index=False):
        y, c, sn = a.year, str(a.car_number), surname(a.driver_name)
        cands = []
        if (y, c) in by:
            cands.append(("EXACT_CAR", by[(y, c)]))
        elif c.endswith("T") and (y, c[:-1]) in by and by[(y, c[:-1])]["reg_surname"] == sn:
            # backup ("T") chassis run on the same official entry by the same driver
            cands.append(("BACKUP_T_CAR_TO_SAME_ENTRY_WITH_SURNAME", by[(y, c[:-1])]))
        else:
            for v in {c.lstrip("0") or "0", "0" + c}:
                if (y, v) in by and by[(y, v)]["reg_surname"] == sn:
                    cands.append(("CAR_VARIANT_06_6_WITH_SURNAME", by[(y, v)]))
        if len(cands) == 0:
            recs.append(dict(map_status="UNMAPPED", map_method="", driver_car_consistent=pd.NA))
            continue
        if len(cands) > 1:
            recs.append(dict(map_status="AMBIGUOUS", map_method="|".join(m for m, _ in cands), driver_car_consistent=pd.NA))
            continue
        m, row = cands[0]
        recs.append(dict(map_status="MAPPED", map_method=m, driver_car_consistent=row["reg_surname"] == sn,
                         registry_driver=row["driver"], registry_car_number=row["car_number"],
                         canonical_engineering_team=row["canonical_engineering_team"],
                         raw_entry_name=row["raw_entry_name"], relationship_type=row["relationship_type"],
                         normalization_confidence=row["normalization_confidence"],
                         primary_teammate_layer=row["primary_teammate_layer"],
                         registry_rule_id=row["rule_id"]))
    return pd.concat([att.reset_index(drop=True), pd.DataFrame(recs)], axis=1)


# ------------------------------------------------------------------ core tier
def build_core():
    p = pd.read_csv(REPO / "r4/output/r4p1_attempt_four_lap_panel_v1.csv", dtype={"car_number": str})
    p = p[p.year.isin(CORE_YEARS)].copy()
    out = pd.DataFrame({
        "tier": "CORE_2020_2024", "year": p.year, "session_id": p.session_id, "attempt_id": p.attempt_id,
        "car_number": p.car_number, "driver_name": p.driver_name, "old_team_label": p.team_name,
        "car_attempt_index": p.car_attempt_index, "attempt_class": p.attempt_class,
        "result_status": p.result_status, "result_counted_at_session_end": p.result_counted_at_session_end,
        "lane_action": p.lane_action,
        "four_lap_average_speed_mph": p.four_lap_average_speed_mph,
        "lap1_speed_mph": p.lap1_speed_mph, "lap2_speed_mph": p.lap2_speed_mph,
        "lap3_speed_mph": p.lap3_speed_mph, "lap4_speed_mph": p.lap4_speed_mph,
        "complete_four_lap": p.attempt_class.eq("A_COMPLETE") & p.four_lap_average_speed_mph.notna(),
        "dq_time_evidence_class": p.time_evidence_class, "dq_time_semantic": p.time_semantic,
        "dq_chronology_usable": p.chronology_usable, "dq_environment_alignment_usable": p.environment_alignment_usable,
        "dq_car_attempt_order_quality": p.car_attempt_order_quality,
        "source_attempt_table": "r4/output/r4p1_attempt_four_lap_panel_v1.csv",
    }).reset_index(drop=True)
    tp, lo, hi = ts(p.time_point_utc).values, ts(p.time_lower_utc).values, ts(p.time_upper_utc).values
    src = p.time_source.values

    # R5.2 public-rescue attempt times/environment (no attempt_id: match year+car+speed)
    rs = pd.read_csv(REPO / "r5_2/manual/rescued_attempt_environment_states_v1.csv", dtype={"car_number": str})
    rs["_t"] = ts(rs.time_utc)

    t_utc, t_cls, t_src, t_half, rescue_idx, conflicts = [], [], [], [], [], []
    for i, a in enumerate(out.itertuples(index=False)):
        m = rs[(rs.year == a.year) & (rs.car_number == a.car_number) &
               ((rs.speed_mph - a.four_lap_average_speed_mph).abs() < 0.0005)]
        ri = m.index[0] if len(m) == 1 else None
        rescue_idx.append(ri)
        if not pd.isna(tp[i]):
            t_utc.append(tp[i]); t_cls.append("APPROX_POINT_RECORDER_CAPTURE"); t_src.append(f"r4p1.time_point_utc<-{src[i]}"); t_half.append(0.0)
            if ri is not None:
                conflicts.append((a.attempt_id, (pd.Timestamp(tp[i]) - rs.loc[ri, "_t"]).total_seconds() / 60))
        elif ri is not None and not pd.isna(rs.loc[ri, "_t"]):
            t_utc.append(rs.loc[ri, "_t"].to_datetime64()); t_cls.append(f"RESCUED_PUBLIC_{rs.loc[ri, 'time_quality']}")
            t_src.append(f"r5_2/manual/rescued_attempt_environment_states_v1.csv ({rs.loc[ri, 'source_authority']})"); t_half.append(0.0)
        elif not pd.isna(lo[i]) and not pd.isna(hi[i]):
            mid = pd.Timestamp(lo[i]) + (pd.Timestamp(hi[i]) - pd.Timestamp(lo[i])) / 2
            t_utc.append(mid.to_datetime64()); t_cls.append("BOUNDED_INTERVAL_MIDPOINT")
            t_src.append(f"r4p1.time_lower/upper_utc<-{src[i]}"); t_half.append((pd.Timestamp(hi[i]) - pd.Timestamp(lo[i])).total_seconds() / 120)
        else:
            t_utc.append(pd.NaT); t_cls.append("MISSING"); t_src.append(""); t_half.append(np.nan)
    out["attempt_timestamp_utc"] = pd.to_datetime(pd.Series(t_utc), utc=True)
    out["time_class"] = t_cls
    out["time_source"] = t_src
    out["time_half_width_min"] = t_half
    out["time_lower_utc"] = pd.to_datetime(pd.Series(lo), utc=True)
    out["time_upper_utc"] = pd.to_datetime(pd.Series(hi), utc=True)
    out["time_semantic"] = np.where(out.time_class.eq("MISSING"), "",
                                    "RECORDER_CAPTURE_OR_PUBLIC_TIME_APPROXIMATING_PERFORMANCE_TIME_NOT_RUN_START")

    # environment: core basis (identical to frozen same-car core inputs)
    ph = pd.read_csv(REPO / "r5_1/output/day1_within_run_fade_physics_v1.csv").set_index("attempt_id")
    pcf = pd.read_csv(REPO / "weather/output/performance_context_features.csv").set_index("attempt_id")
    r5b = pd.read_csv(REPO / "r5/output/r5b_solar_physics_features.csv").drop_duplicates("attempt_id").set_index("attempt_id")
    rea = pd.concat([pd.read_csv(REPO / "weather/output/performance_grade_attempt_realized_environment.csv"),
                     pd.read_csv(REPO / "weather/output/performance_grade_attempt_realized_environment_2024_supported.csv")]
                    ).drop_duplicates("attempt_id").set_index("attempt_id")
    env = {k: [] for k in ["track_temp_c", "track_basis", "ambient_temp_c", "ambient_basis", "solar_shortwave_wm2",
                           "wind_speed_ms", "wind_basis", "track_obs_time_utc", "hrrr_valid_before_utc",
                           "hrrr_valid_after_utc", "env_source", "dq_physical_link_quality",
                           "ptsc_interp_track_c", "ptsc_interp_ambient_c", "ptsc_interp_wind_raw", "ptsc_interp_status"]}
    for a, ri in zip(out.itertuples(index=False), rescue_idx):
        aid = a.attempt_id
        e = dict.fromkeys(env, np.nan)
        e["track_basis"] = e["ambient_basis"] = e["wind_basis"] = e["env_source"] = e["dq_physical_link_quality"] = e["ptsc_interp_status"] = ""
        if aid in ph.index and pd.notna(ph.at[aid, "track_temperature_c_assembled"]):
            q = ph.at[aid, "physical_link_quality"]
            e.update(track_temp_c=ph.at[aid, "track_temperature_c_assembled"],
                     track_basis="PTSC_PAST_SAFE" if q.startswith("PAST_SAFE") else "PTSC_REALIZED_INTERPOLATED",
                     env_source="r5_1/output/day1_within_run_fade_physics_v1.csv", dq_physical_link_quality=q)
        if aid in ph.index and pd.notna(ph.at[aid, "forecast_temp_c"]):
            e.update(ambient_temp_c=ph.at[aid, "forecast_temp_c"], ambient_basis="HRRR_2M_ISSUE_GATED",
                     solar_shortwave_wm2=ph.at[aid, "forecast_shortwave_radiation_wm2"],
                     wind_speed_ms=ph.at[aid, "forecast_wind_speed_10m_ms"], wind_basis="HRRR_10M",
                     dq_physical_link_quality=ph.at[aid, "physical_link_quality"],
                     env_source=e["env_source"] or "r5_1/output/day1_within_run_fade_physics_v1.csv")
        elif aid in pcf.index and pd.notna(pcf.at[aid, "forecast_temp_c"]):
            e.update(ambient_temp_c=pcf.at[aid, "forecast_temp_c"], ambient_basis="HRRR_2M_ISSUE_GATED",
                     solar_shortwave_wm2=pcf.at[aid, "forecast_shortwave_radiation_wm2"],
                     wind_speed_ms=pcf.at[aid, "forecast_wind_speed_10m_ms"], wind_basis="HRRR_10M",
                     env_source=(e["env_source"] + "; " if e["env_source"] else "") + "weather/output/performance_context_features.csv")
        if pd.isna(e["track_temp_c"]) and ri is not None and pd.notna(rs.loc[ri, "ptsc_track_c"]):
            e.update(track_temp_c=rs.loc[ri, "ptsc_track_c"], track_basis=f"RESCUE_PTSC_{rs.loc[ri, 'ptsc_match_status']}",
                     track_obs_time_utc=rs.loc[ri, "ptsc_match_time_utc"], env_source="r5_2/manual/rescued_attempt_environment_states_v1.csv",
                     dq_physical_link_quality=rs.loc[ri, "rescue_environment_status"])
        if pd.isna(e["ambient_temp_c"]) and ri is not None and pd.notna(rs.loc[ri, "hrrr_temp_c"]):
            e.update(ambient_temp_c=rs.loc[ri, "hrrr_temp_c"], ambient_basis="HRRR_2M_RESCUE_MATCH",
                     solar_shortwave_wm2=rs.loc[ri, "hrrr_shortwave_radiation_wm2"], wind_speed_ms=rs.loc[ri, "hrrr_wind_speed_10m_ms"],
                     wind_basis="HRRR_10M", hrrr_valid_before_utc=rs.loc[ri, "hrrr_match_time_utc"],
                     env_source="r5_2/manual/rescued_attempt_environment_states_v1.csv")
        if aid in r5b.index:
            e["track_obs_time_utc"] = r5b.at[aid, "track_observation_time_utc"] if pd.isna(e["track_obs_time_utc"]) else e["track_obs_time_utc"]
        if aid in pcf.index:
            e["hrrr_valid_before_utc"] = pcf.at[aid, "before_valid_time_utc"]
            e["hrrr_valid_after_utc"] = pcf.at[aid, "after_valid_time_utc"]
        if aid in rea.index:
            e.update(ptsc_interp_track_c=rea.at[aid, "ptsc_track_c"], ptsc_interp_ambient_c=rea.at[aid, "ptsc_ambient_c"],
                     ptsc_interp_wind_raw=rea.at[aid, "ptsc_wind"], ptsc_interp_status=rea.at[aid, "ptsc_alignment_status"])
        for k in env:
            env[k].append(e[k])
    for k, v in env.items():
        out[k] = v
    return out, conflicts


# ------------------------------------------------------------------ regime extension tier
def build_extension():
    v = pd.read_csv(REPO / "r6_regime_extension/output/regime_attempt_inventory_v3/regime_official_attempt_inventory_v3.csv",
                    dtype={"car_number": str})
    v = v[v.year.isin(EXT_YEARS)].copy()
    L = pd.read_csv(REPO / "r6_regime_extension/output/timing71_legacy_attempt_reconstruction_v5/legacy_official_attempt_matches_global_v5.csv",
                    dtype={"car_number": str})
    L = L.assign(t=L.attempt_mid_utc, tq=L.match_quality + "|" + L.timestamp_quality, tsrc="timing71_legacy_attempt_reconstruction_v5")
    T = pd.read_csv(REPO / "r6_regime_extension/output/timing71_2025_clean_chronology_v1/timing71_2025_global_one_to_one_matches_v1.csv",
                    dtype={"car_number": str})
    T = T.assign(t=T.attempt_anchor_utc, tq=T.match_quality + "|ATTEMPT_MID_ANCHOR", tsrc="timing71_2025_clean_chronology_v1")
    tm = pd.concat([L[["year", "source_rank", "t", "tq", "tsrc"]], T[["year", "source_rank", "t", "tq", "tsrc"]]])
    v = v.merge(tm, on=["year", "source_rank"], how="left", validate="one_to_one")
    accepted = v.tq.fillna("").str.startswith("EXACT_OR_NEAR_EXACT") & ~v.tq.fillna("").str.contains("UNRESOLVED")

    lap_speed = {k: LAP_MILES * 3600 / v[f"lap{k}_s"] for k in range(1, 5)}
    out = pd.DataFrame({
        "tier": "REGIME_EXT_R6", "year": v.year, "session_id": "INDY500_DAY1_" + v.year.astype(str),
        "attempt_id": "R6_" + v.year.astype(str) + "_RANK" + v.source_rank.astype(str),
        "car_number": v.car_number, "driver_name": v.driver_name, "old_team_label": "",
        "car_attempt_index": v.record_index_for_entrant, "attempt_class": np.where(v.complete_four_lap, "COMPLETE_FOUR_LAP", np.where(v.zero_lap, "ZERO_LAP", "PARTIAL")),
        "result_status": v.status, "result_counted_at_session_end": pd.NA, "lane_action": "",
        "four_lap_average_speed_mph": np.where(v.complete_four_lap, v.average_speed_mph, np.nan),
        "lap1_speed_mph": lap_speed[1], "lap2_speed_mph": lap_speed[2], "lap3_speed_mph": lap_speed[3], "lap4_speed_mph": lap_speed[4],
        "complete_four_lap": v.complete_four_lap.astype(bool),
        "dq_time_evidence_class": v.tq.fillna("NO_TIMING71_MATCH"), "dq_time_semantic": v.source_order_semantics,
        "dq_chronology_usable": accepted, "dq_environment_alignment_usable": pd.NA,
        "dq_car_attempt_order_quality": "RESULT_REPORT_ORDER_NOT_VERIFIED_CHRONOLOGY",
        "source_attempt_table": "r6_regime_extension/output/regime_attempt_inventory_v3/regime_official_attempt_inventory_v3.csv",
    }).reset_index(drop=True)
    out["attempt_timestamp_utc"] = pd.to_datetime(np.where(accepted.values, ts(v.t).values, np.datetime64("NaT", "ns")), utc=True)
    out["time_class"] = np.where(accepted.values, "TIMING71_LAP_MATCHED_ATTEMPT_MID",
                                 np.where(v.tq.notna().values, "TIMING71_MATCH_REJECTED_QUALITY", "MISSING"))
    out["time_source"] = np.where(v.tsrc.notna().values, "r6_regime_extension/output/" + v.tsrc.fillna("").values, "")
    out["time_half_width_min"] = np.where(accepted.values, 0.0, np.nan)
    out["time_lower_utc"] = pd.NaT
    out["time_upper_utc"] = pd.NaT
    out["time_semantic"] = np.where(accepted.values, "ATTEMPT_MIDPOINT_FROM_LAP_TIMING", "")
    out["rejected_time_candidate_utc"] = np.where(~accepted.values & v.t.notna().values, v.t.values, "")

    ptsc = pd.read_csv(REPO / "r6_regime_extension/output/r6_ptsc_canonical_v1/r6_ptsc_2019_2025_canonical_v1.csv")
    ptsc["t"] = ts(ptsc.datetime_utc)
    cols = {k: [] for k in ["track_temp_c", "ambient_temp_c", "wind_speed_ms", "track_obs_time_utc", "ptsc_interp_status"]}
    for a in out.itertuples(index=False):
        p = ptsc[ptsc.year == a.year].sort_values("t")
        res = dict(track_temp_c=np.nan, ambient_temp_c=np.nan, wind_speed_ms=np.nan, track_obs_time_utc="", ptsc_interp_status="")
        if pd.isna(a.attempt_timestamp_utc):
            res["ptsc_interp_status"] = "NO_ATTEMPT_TIME"
        elif p.empty:
            res["ptsc_interp_status"] = "NO_PTSC_FOR_YEAR"
        else:
            b = p[p.t <= a.attempt_timestamp_utc].tail(1)
            f = p[p.t >= a.attempt_timestamp_utc].head(1)
            if b.empty or f.empty:
                res["ptsc_interp_status"] = "OUTSIDE_PTSC_RANGE_NOT_EXTRAPOLATED"
            else:
                gap = (f.t.iloc[0] - b.t.iloc[0]).total_seconds() / 60
                if gap > PTSC_MAX_BRACKET_MIN:
                    res["ptsc_interp_status"] = f"BRACKET_{gap:.0f}MIN_EXCEEDS_{PTSC_MAX_BRACKET_MIN:.0f}"
                else:
                    w = 0.0 if gap == 0 else (a.attempt_timestamp_utc - b.t.iloc[0]).total_seconds() / 60 / gap
                    lin = lambda c: b[c].iloc[0] + w * (f[c].iloc[0] - b[c].iloc[0])
                    res.update(track_temp_c=lin("track_c"), ambient_temp_c=lin("ambient_c"), wind_speed_ms=lin("wind_raw"),
                               track_obs_time_utc=f"{b.t.iloc[0].isoformat()}|{f.t.iloc[0].isoformat()}",
                               ptsc_interp_status="LINEAR_INTERPOLATION")
        for k in cols:
            cols[k].append(res[k])
    for k, vals in cols.items():
        out[k] = vals
    ok = out.ptsc_interp_status.eq("LINEAR_INTERPOLATION")
    out["track_basis"] = np.where(ok, "PTSC_LINEAR_INTERPOLATION", "")
    out["ambient_basis"] = np.where(ok, "PTSC_AMBIENT_LINEAR_INTERPOLATION", "")
    out["wind_basis"] = np.where(ok, "PTSC_WIND_RAW_UNITS_AS_PUBLISHED", "")
    out["solar_shortwave_wm2"] = np.nan
    out["hrrr_valid_before_utc"] = out["hrrr_valid_after_utc"] = ""
    out["env_source"] = np.where(ok, "r6_regime_extension/output/r6_ptsc_canonical_v1/r6_ptsc_2019_2025_canonical_v1.csv", "")
    out["dq_physical_link_quality"] = out.ptsc_interp_status
    out["ptsc_interp_track_c"] = out.track_temp_c
    out["ptsc_interp_ambient_c"] = out.ambient_temp_c
    out["ptsc_interp_wind_raw"] = out.wind_speed_ms
    return out


# ------------------------------------------------------------------ session state
def in_interval(t, a, b):
    return ts(a) <= t <= ts(b)


def segment_of(year, t):
    if pd.isna(t) or year not in KNOWN_INTERRUPTIONS:
        return None
    ivs = KNOWN_INTERRUPTIONS[year]
    for name, a, b in ivs:
        if in_interval(t, a, b):
            return f"INSIDE_{name}"
    seg = 0
    for _, a, b in ivs:
        if t > ts(b):
            seg += 1
    return f"SEGMENT_{seg}"


def pair_session_state(r_a, r_b):
    if r_a["session_id"] != r_b["session_id"]:
        return "DIFFERENT_SESSION", ""
    if pd.isna(r_a["attempt_timestamp_utc"]) or pd.isna(r_b["attempt_timestamp_utc"]):
        return "UNAVAILABLE_TIME_MISSING", ""
    y = r_a["year"]
    gap_note = ""
    for name, a, b in DATA_COVERAGE_GAPS.get(y, []):
        lo, hi = sorted([r_a["attempt_timestamp_utc"], r_b["attempt_timestamp_utc"]])
        if lo < ts(a) and hi > ts(b):
            gap_note = f"SPANS_DATA_COVERAGE_GAP:{name}"
    if y in KNOWN_INTERRUPTIONS:
        if (r_a["time_half_width_min"] or 0) > 0 or (r_b["time_half_width_min"] or 0) > 0:
            segs = set()
            for r in (r_a, r_b):
                hw = pd.Timedelta(minutes=r["time_half_width_min"] or 0)
                segs.add((segment_of(y, r["attempt_timestamp_utc"] - hw), segment_of(y, r["attempt_timestamp_utc"] + hw)))
            if any(s[0] != s[1] for s in segs):
                return "UNAVAILABLE_BOUNDED_TIME_STRADDLES_KNOWN_INTERRUPTION", gap_note
        sa, sb = segment_of(y, r_a["attempt_timestamp_utc"]), segment_of(y, r_b["attempt_timestamp_utc"])
        if sa.startswith("INSIDE") or sb.startswith("INSIDE"):
            return "INCONSISTENT_ATTEMPT_TIME_INSIDE_KNOWN_STOP", gap_note
        return ("SAME_SESSION_SAME_KNOWN_SEGMENT" if sa == sb else "SAME_SESSION_CROSSES_KNOWN_INTERRUPTION"), gap_note
    return "SAME_SESSION_NO_INTERRUPTION_RECORD_IN_RECONSTRUCTION", gap_note


# ------------------------------------------------------------------ candidates
DELTA_VARS = [("four_lap_average_speed_mph", "delta_speed_mph"), ("track_temp_c", "delta_track_temp_c"),
              ("ambient_temp_c", "delta_ambient_temp_c"), ("solar_shortwave_wm2", "delta_solar_wm2"),
              ("wind_speed_ms", "delta_wind")]


def order_pair(a, b):
    ta, tb = a["attempt_timestamp_utc"], b["attempt_timestamp_utc"]
    ka = (car_sort_key(a["registry_car_number"]), a["attempt_id"])
    kb = (car_sort_key(b["registry_car_number"]), b["attempt_id"])
    if pd.notna(ta) and pd.notna(tb):
        return (a, b) if (ta, ka) <= (tb, kb) else (b, a)
    return (a, b) if ka <= kb else (b, a)


def build_candidates(j):
    prim = j[(j.map_status == "MAPPED") & (j.primary_teammate_layer == True)]
    rows = []
    for (tier, y, team), g in prim.groupby(["tier", "year", "canonical_engineering_team"]):
        recs = g.to_dict("records")
        for a, b in itertools.combinations(recs, 2):
            if a["registry_car_number"] == b["registry_car_number"]:
                continue  # never an entry against itself (a backup T-car is the same entry)
            assert a["registry_driver"] != b["registry_driver"]
            A, B = order_pair(a, b)
            state, gap_note = pair_session_state(A, B)
            row = dict(tier=tier, year=y, canonical_engineering_team=team,
                       relationship_pair_id=f"{y}|{team}|" + "~".join(sorted([A["registry_car_number"], B["registry_car_number"]], key=car_sort_key)),
                       car_A=A["registry_car_number"], car_B=B["registry_car_number"],
                       raw_car_A=A["car_number"], raw_car_B=B["car_number"],
                       backup_chassis_involved=A["map_method"].startswith("BACKUP") or B["map_method"].startswith("BACKUP"), driver_A=A["registry_driver"], driver_B=B["registry_driver"],
                       attempt_A=A["attempt_id"], attempt_B=B["attempt_id"],
                       car_attempt_index_A=A["car_attempt_index"], car_attempt_index_B=B["car_attempt_index"],
                       timestamp_A=A["attempt_timestamp_utc"], timestamp_B=B["attempt_timestamp_utc"],
                       time_class_A=A["time_class"], time_class_B=B["time_class"],
                       speed_A=A["four_lap_average_speed_mph"], speed_B=B["four_lap_average_speed_mph"],
                       complete_A=A["complete_four_lap"], complete_B=B["complete_four_lap"],
                       track_A=A["track_temp_c"], track_B=B["track_temp_c"], ambient_A=A["ambient_temp_c"], ambient_B=B["ambient_temp_c"],
                       track_basis_A=A["track_basis"], track_basis_B=B["track_basis"],
                       ambient_basis_A=A["ambient_basis"], ambient_basis_B=B["ambient_basis"],
                       session_state=state, data_coverage_note=gap_note)
            dt = (B["attempt_timestamp_utc"] - A["attempt_timestamp_utc"]).total_seconds() / 60 \
                if pd.notna(A["attempt_timestamp_utc"]) and pd.notna(B["attempt_timestamp_utc"]) else np.nan
            row["delta_time_minutes"] = dt
            row["time_uncertainty_min"] = (A["time_half_width_min"] or 0) + (B["time_half_width_min"] or 0) if not np.isnan(dt) else np.nan
            for src, name in DELTA_VARS:
                va, vb = A[src], B[src]
                row[name] = vb - va if pd.notna(va) and pd.notna(vb) else np.nan
            # exact basis equality: past-safe vs interpolated PTSC track values can differ by ~3 C
            row["env_basis_consistent"] = (A["track_basis"] == B["track_basis"] and A["ambient_basis"] == B["ambient_basis"]) \
                if A["track_basis"] and B["track_basis"] else pd.NA
            row["both_complete_four_lap"] = bool(A["complete_four_lap"] and B["complete_four_lap"])
            row["both_timed"] = not np.isnan(dt)
            row["measurable_candidate"] = row["both_complete_four_lap"] and row["both_timed"]
            rows.append(row)
    c = pd.DataFrame(rows)
    return c


def build_nearest(j):
    prim = j[(j.map_status == "MAPPED") & (j.primary_teammate_layer == True) & j.complete_four_lap & j.attempt_timestamp_utc.notna()]
    rows = []
    for (tier, y, team), g in prim.groupby(["tier", "year", "canonical_engineering_team"]):
        for x in g.itertuples(index=False):
            per_car = []
            for car, h in g[g.registry_car_number != x.registry_car_number].groupby("registry_car_number"):
                d = (h.attempt_timestamp_utc - x.attempt_timestamp_utc).dt.total_seconds() / 60
                k = d.abs().sort_values(kind="stable")
                best = h.loc[k.index[0]]
                sd = d.loc[k.index[0]]
                per_car.append(dict(tier=tier, year=y, canonical_engineering_team=team,
                                    attempt_id=x.attempt_id, car_number=x.registry_car_number, raw_car_number=x.car_number, driver=x.registry_driver,
                                    timestamp=x.attempt_timestamp_utc, speed_mph=x.four_lap_average_speed_mph,
                                    teammate_car=car, teammate_driver=best.registry_driver, teammate_attempt_id=best.attempt_id,
                                    teammate_timestamp=best.attempt_timestamp_utc,
                                    signed_time_to_teammate_min=sd, abs_time_separation_min=abs(sd),
                                    abs_track_temp_separation_c=abs(best.track_temp_c - x.track_temp_c) if pd.notna(best.track_temp_c) and pd.notna(x.track_temp_c) else np.nan,
                                    abs_ambient_temp_separation_c=abs(best.ambient_temp_c - x.ambient_temp_c) if pd.notna(best.ambient_temp_c) and pd.notna(x.ambient_temp_c) else np.nan,
                                    abs_solar_separation_wm2=abs(best.solar_shortwave_wm2 - x.solar_shortwave_wm2) if pd.notna(best.solar_shortwave_wm2) and pd.notna(x.solar_shortwave_wm2) else np.nan,
                                    abs_wind_separation=abs(best.wind_speed_ms - x.wind_speed_ms) if pd.notna(best.wind_speed_ms) and pd.notna(x.wind_speed_ms) else np.nan,
                                    teammate_minus_own_speed_mph=best.four_lap_average_speed_mph - x.four_lap_average_speed_mph,
                                    teammate_attempts_available=len(h)))
            if per_car:
                m = min(r["abs_time_separation_min"] for r in per_car)
                first = True
                for r in sorted(per_car, key=lambda r: (r["abs_time_separation_min"], car_sort_key(r["teammate_car"]))):
                    r["is_overall_nearest_teammate"] = first and r["abs_time_separation_min"] == m
                    first = False
                rows.extend(per_car)
    n = pd.DataFrame(rows)
    key = lambda a, b: "~".join(sorted([a, b]))
    n["attempt_pair_key"] = [key(a, b) for a, b in zip(n.attempt_id, n.teammate_attempt_id)]
    ov = n[n.is_overall_nearest_teammate]
    mutual = ov.attempt_pair_key.value_counts()
    n["overall_nearest_is_mutual"] = n.is_overall_nearest_teammate & n.attempt_pair_key.map(mutual).eq(2)
    return n


# ------------------------------------------------------------------ summaries
ABS_COLS = [("delta_time_minutes", "abs_time_min"), ("delta_track_temp_c", "abs_track_temp_c"),
            ("delta_ambient_temp_c", "abs_ambient_temp_c"), ("delta_solar_wm2", "abs_solar_wm2"), ("delta_wind", "abs_wind")]


def quantile_rows(df, group_cols, scope):
    out = []
    groups = [((), df)] if not group_cols else df.groupby(group_cols)
    for key, g in groups:
        key = key if isinstance(key, tuple) else (key,)
        base = dict(zip(group_cols, key))
        for src, name in ABS_COLS:
            x = g[src].abs().dropna()
            r = dict(scope=scope, **base, variable=name, n=len(x))
            for q in QUANTS:
                r[f"q{int(q * 100):03d}"] = x.quantile(q) if len(x) else np.nan
            out.append(r)
    return out


def window_rows(df, group_cols, scope):
    out = []
    groups = [((), df)] if not group_cols else df.groupby(group_cols)
    for key, g in groups:
        key = key if isinstance(key, tuple) else (key,)
        base = dict(zip(group_cols, key))
        adt = g.delta_time_minutes.abs()
        for w in WINDOWS:
            s = g[adt <= w]
            out.append(dict(scope=scope, **base, max_time_separation_min=w, attempt_pair_candidates=len(s),
                            distinct_relationship_pairs=s.relationship_pair_id.nunique(),
                            distinct_attempts_involved=len(set(s.attempt_A) | set(s.attempt_B)),
                            distinct_team_years=s[["year", "canonical_engineering_team"]].drop_duplicates().shape[0]))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(exist_ok=True)
    reg = load_registry()
    core, conflicts = build_core()
    ext = build_extension()
    att = pd.concat([core, ext], ignore_index=True)
    att["date"] = [str(t.tz_convert("America/Indiana/Indianapolis").date()) if pd.notna(t) else DAY1_DATE[y]
                   for t, y in zip(att.attempt_timestamp_utc, att.year)]
    att["date_source"] = np.where(att.attempt_timestamp_utc.notna(), "LOCAL_DATE_OF_ATTEMPT_TIMESTAMP", "DAY1_SESSION_DATE")
    j = map_to_registry(att, reg)
    j["session_order_by_time"] = j.groupby("session_id").attempt_timestamp_utc.rank(method="first")
    j["car_order_by_time"] = j.groupby(["session_id", "car_number"]).attempt_timestamp_utc.rank(method="first")
    j.to_csv(OUT / "team_attempt_join.csv", index=False)

    c = build_candidates(j)
    c.to_csv(OUT / "teammate_attempt_candidates.csv", index=False)
    n = build_nearest(j)
    n.to_csv(OUT / "nearest_teammate_candidates.csv", index=False)

    m = c[c.measurable_candidate]
    summ = []
    for tier, g in m.groupby("tier"):
        summ += quantile_rows(g, [], f"{tier}|ALL_MEASURABLE_ATTEMPT_PAIRS")
        summ += quantile_rows(g[g.time_uncertainty_min.fillna(0) == 0], [], f"{tier}|POINT_TIMES_ONLY")
    for tier, g in n[n.is_overall_nearest_teammate].groupby("tier"):
        g2 = g.rename(columns={"signed_time_to_teammate_min": "delta_time_minutes"}).assign(
            delta_track_temp_c=g.abs_track_temp_separation_c, delta_ambient_temp_c=g.abs_ambient_temp_separation_c,
            delta_solar_wm2=g.abs_solar_separation_wm2, delta_wind=g.abs_wind_separation)
        summ += quantile_rows(g2, [], f"{tier}|OVERALL_NEAREST_TEAMMATE_PER_ATTEMPT")
    wins = []
    for tier, g in m.groupby("tier"):
        wins += window_rows(g, [], f"{tier}|ALL_MEASURABLE_ATTEMPT_PAIRS")
    qs = pd.DataFrame(summ)
    ws = pd.DataFrame(wins)
    qs.assign(table="QUANTILES").to_csv(OUT / "comparability_summary.csv", index=False)
    ws.to_csv(OUT / "comparability_window_counts.csv", index=False)
    by_year = pd.DataFrame(quantile_rows(m, ["tier", "year"], "BY_YEAR"))
    by_year_w = pd.DataFrame(window_rows(m, ["tier", "year"], "BY_YEAR"))
    by_team = pd.DataFrame(quantile_rows(m, ["tier", "canonical_engineering_team"], "BY_TEAM"))
    by_team_w = pd.DataFrame(window_rows(m, ["tier", "canonical_engineering_team"], "BY_TEAM"))
    pd.concat([by_year.assign(table="QUANTILES"), by_year_w.assign(table="WINDOW_COUNTS")]).to_csv(OUT / "comparability_by_year.csv", index=False)
    pd.concat([by_team.assign(table="QUANTILES"), by_team_w.assign(table="WINDOW_COUNTS")]).to_csv(OUT / "comparability_by_team.csv", index=False)
    return reg, j, c, n, qs, ws, by_year_w, by_team_w, conflicts


if __name__ == "__main__":
    reg, j, c, n, qs, ws, byw, btw, conflicts = main()
    print(j.groupby(["tier", "year"]).size().to_string())
    print(j.map_status.value_counts().to_dict())
    print("candidates", len(c), "measurable", int(c.measurable_candidate.sum()), "nearest rows", len(n))
    print("time conflicts (r4p1 point vs rescue, min):", conflicts)
