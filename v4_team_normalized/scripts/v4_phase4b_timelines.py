"""V4 Phase 4B: team-year chronological qualifying timelines (exploratory, descriptive only).

No regression, fixed-effects, mixed-effects or other statistical model is fitted. The only
use of the frozen model is *applying* its published coefficients to observed state changes
as a descriptive reference sign (never re-estimated). Source files are read-only.

Eras are never pooled:
  ERA_A_PRE_AEROSCREEN_EXT   2018, 2019   (R6 extension tier)
  ERA_B_FROZEN_REFERENCE     2020-2024    (core tier)
  ERA_C_HYBRID_EXTERNAL      2025         (R6 extension tier)

Performance timeline = primary-teammate-layer attempts that are complete over four laps AND timed.
Centered quantities are within-car location shifts computed on that performance timeline only.
"""
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
P3 = V4 / "output" / "phase3"
OUT = V4 / "output" / "phase4b"
LOCAL_TZ = "America/Indiana/Indianapolis"

ERA = {2018: "ERA_A_PRE_AEROSCREEN_EXT", 2019: "ERA_A_PRE_AEROSCREEN_EXT", 2020: "ERA_B_FROZEN_REFERENCE",
       2021: "ERA_B_FROZEN_REFERENCE", 2022: "ERA_B_FROZEN_REFERENCE", 2023: "ERA_B_FROZEN_REFERENCE",
       2024: "ERA_B_FROZEN_REFERENCE", 2025: "ERA_C_HYBRID_EXTERNAL"}
KNOWN_INTERRUPTIONS = {2022: [("2022-05-21T18:14:00Z", "2022-05-21T19:34:00Z"), ("2022-05-21T20:00:00Z", "2022-05-21T20:50:00Z")]}
DATA_GAPS = {2020: [("2020-08-15T18:35:15Z", "2020-08-15T18:42:30Z")]}
# Descriptive triage labels only (not inferential thresholds)
CONFOUND_LABELS = [(0.5, "SEVERE"), (0.25, "MODERATE"), (0.0, "LOW")]


def ts(s):
    return pd.to_datetime(s, utc=True, format="mixed", errors="coerce")


def car_sort_key(c):
    s = str(c)
    return (int(s) if s.isdigit() else 999, s)


def uniq(df):
    """Cluster counts that must accompany every major summary (4B.14)."""
    return dict(unique_years=df.year.nunique(), unique_team_years=df[["year", "canonical_engineering_team"]].drop_duplicates().shape[0],
                unique_teams=df.canonical_engineering_team.nunique(), unique_cars=df[["year", "registry_car_number"]].drop_duplicates().shape[0],
                unique_drivers=df.registry_driver.nunique(), unique_attempts=df.attempt_id.nunique())


def frozen_endpoints():
    r = pd.read_csv(REPO / "r5_2/manual/r5_2_repeat_analysis_set_v1.csv", dtype={"car_number": str})
    core = r.dropna(subset=["delta_four_lap_average_speed_mph", "delta_track_temp_c", "delta_air_temp_c"]).reset_index(drop=True)
    assert len(core) == 41
    role = {}
    for x in core.itertuples(index=False):
        role.setdefault(x.before_attempt_id, []).append(f"T1:{x.transition_id}")
        role.setdefault(x.after_attempt_id, []).append(f"T2:{x.transition_id}")
    beta = json.loads((REPO / "r5_2/manual/probabilistic_physics_core_v1.json").read_text())["mean_core"]["full_data_huber_coefficients"]
    return core, role, beta


# ------------------------------------------------------------------ 4B.1 / 4B.4 long timeline
def build_long():
    j = pd.read_csv(P3 / "team_attempt_join.csv", dtype={"car_number": str, "registry_car_number": str}, low_memory=False)
    j = j[j.year.between(2018, 2025) & (j.primary_teammate_layer == True)].copy()
    j["attempt_timestamp_utc"] = ts(j.attempt_timestamp_utc)
    j["era"] = j.year.map(ERA)
    j["timestamp_local"] = j.attempt_timestamp_utc.dt.tz_convert(LOCAL_TZ)
    j["timestamp_quality"] = j.time_class
    j["on_timeline"] = j.attempt_timestamp_utc.notna()
    j["on_performance_timeline"] = j.on_timeline & j.complete_four_lap.astype(bool)
    j["timeline_exclusion_reason"] = np.select(
        [~j.on_timeline & ~j.complete_four_lap.astype(bool), ~j.on_timeline, ~j.complete_four_lap.astype(bool)],
        ["UNTIMED_AND_INCOMPLETE", "UNTIMED", "INCOMPLETE_FOUR_LAP"], "")
    first = j[j.on_timeline].groupby("session_id").attempt_timestamp_utc.min()
    j["session_elapsed_min"] = (j.attempt_timestamp_utc - j.session_id.map(first)).dt.total_seconds() / 60
    j = j.sort_values(["year", "canonical_engineering_team", "attempt_timestamp_utc", "registry_car_number", "attempt_id"],
                      key=lambda s: s.map(car_sort_key) if s.name == "registry_car_number" else s, na_position="last").reset_index(drop=True)
    j["team_timeline_order"] = j[j.on_timeline].groupby(["year", "canonical_engineering_team"]).cumcount() + 1
    j["car_timeline_order"] = j[j.on_timeline].groupby(["year", "registry_car_number"]).cumcount() + 1
    j["attempt_sequence"] = j.car_attempt_index
    j["weather_timestamp"] = j.track_obs_time_utc.fillna("").astype(str)
    j["weather_method"] = j.track_basis.fillna("") + " / " + j.ambient_basis.fillna("")
    j["interruption_record"] = np.where(j.year.isin(list(KNOWN_INTERRUPTIONS)), "KNOWN_2022_WEATHER_STOPS",
                                        "NO_INTERRUPTION_RECORD_IN_RECONSTRUCTION")
    core, role, _ = frozen_endpoints()
    j["frozen_core_role"] = j.attempt_id.map(lambda a: "|".join(role.get(a, [])))
    j["is_frozen_core_attempt"] = j.frozen_core_role != ""

    # 4B.3 within-car centering on the performance timeline (descriptive location shifts)
    pt = j[j.on_performance_timeline]
    g = pt.groupby(["year", "registry_car_number"]).four_lap_average_speed_mph
    j["car_mean_timeline"] = [g.mean().get((y, c), np.nan) for y, c in zip(j.year, j.registry_car_number)]
    j["car_median_timeline"] = [g.median().get((y, c), np.nan) for y, c in zip(j.year, j.registry_car_number)]
    j["car_n_timeline"] = [g.size().get((y, c), 0) for y, c in zip(j.year, j.registry_car_number)]
    perf = j.on_performance_timeline
    j["speed_minus_car_mean"] = np.where(perf, j.four_lap_average_speed_mph - j.car_mean_timeline, np.nan)
    j["speed_minus_car_median"] = np.where(perf, j.four_lap_average_speed_mph - j.car_median_timeline, np.nan)
    j["centering_informative"] = perf & (j.car_n_timeline >= 2)  # a single observation centers to 0 by construction
    return j, core


def car_baselines(j):
    rows = []
    for (y, team, car), g in j.groupby(["year", "canonical_engineering_team", "registry_car_number"]):
        comp = g[g.complete_four_lap.astype(bool)]
        perf = g[g.on_performance_timeline]
        first = comp.sort_values(["attempt_timestamp_utc", "car_attempt_index"], na_position="last").iloc[0] if len(comp) else None
        rows.append(dict(
            era=ERA[y], tier=g.tier.iloc[0], year=y, canonical_engineering_team=team, car_number=car,
            driver=g.registry_driver.iloc[0], raw_entry_name=g.raw_entry_name.iloc[0],
            attempts_total=len(g), attempts_complete=len(comp), attempts_timed=int(g.on_timeline.sum()),
            attempts_on_performance_timeline=len(perf),
            mean_speed_all_complete=comp.four_lap_average_speed_mph.mean(),
            median_speed_all_complete=comp.four_lap_average_speed_mph.median(),
            first_attempt_speed=first.four_lap_average_speed_mph if first is not None else np.nan,
            first_attempt_basis=("EARLIEST_TIMESTAMP" if first is not None and pd.notna(first.attempt_timestamp_utc) else
                                 "LOWEST_SOURCE_ATTEMPT_INDEX" if first is not None else ""),
            best_speed=comp.four_lap_average_speed_mph.max(),
            sd_speed_all_complete=comp.four_lap_average_speed_mph.std() if len(comp) >= 2 else np.nan,
            mean_speed_timeline=perf.four_lap_average_speed_mph.mean(), median_speed_timeline=perf.four_lap_average_speed_mph.median(),
            sd_speed_timeline=perf.four_lap_average_speed_mph.std() if len(perf) >= 2 else np.nan,
            timeline_vs_all_mean_gap=perf.four_lap_average_speed_mph.mean() - comp.four_lap_average_speed_mph.mean(),
            centering_informative=len(perf) >= 2,
            frozen_core_attempts=int(g.is_frozen_core_attempt.sum())))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ 4B.8 sampling
def sampling_summary(j):
    rows = []
    for (y, team), g in j.groupby(["year", "canonical_engineering_team"]):
        p = g[g.on_performance_timeline].sort_values("attempt_timestamp_utc")
        gaps = p.attempt_timestamp_utc.diff().dt.total_seconds().div(60).dropna()
        cars = p.registry_car_number.values
        same = int(sum(a == b for a, b in zip(cars[:-1], cars[1:])))
        rows.append(dict(
            era=ERA[y], year=y, canonical_engineering_team=team,
            cars_entered=g.registry_car_number.nunique(), attempts_total=len(g), attempts_timed=int(g.on_timeline.sum()),
            attempts_on_performance_timeline=len(p), cars_on_performance_timeline=p.registry_car_number.nunique(),
            cars_with_2plus_timeline_attempts=int((p.groupby("registry_car_number").size() >= 2).sum()),
            timestamp_coverage=g.on_timeline.mean(),
            first_attempt_local=p.timestamp_local.min() if len(p) else pd.NaT, last_attempt_local=p.timestamp_local.max() if len(p) else pd.NaT,
            timeline_span_min=(p.attempt_timestamp_utc.max() - p.attempt_timestamp_utc.min()).total_seconds() / 60 if len(p) >= 2 else 0.0,
            median_gap_min=gaps.median() if len(gaps) else np.nan, max_gap_min=gaps.max() if len(gaps) else np.nan,
            consecutive_same_car=same, consecutive_car_switch=max(len(p) - 1, 0) - same,
            frozen_core_attempts_on_timeline=int(p.is_frozen_core_attempt.sum()),
            panel_eligible=(p.registry_car_number.nunique() >= 2) and (int((p.groupby("registry_car_number").size() >= 2).sum()) >= 2)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ 4B.9 consecutive observations
def consecutive(j, beta):
    rows = []
    for (y, team), g in j[j.on_performance_timeline].groupby(["year", "canonical_engineering_team"]):
        p = g.sort_values(["attempt_timestamp_utc", "attempt_id"]).reset_index(drop=True)
        for k in range(1, len(p)):
            a, b = p.iloc[k - 1], p.iloc[k]
            dtr = b.track_temp_c - a.track_temp_c if pd.notna(a.track_temp_c) and pd.notna(b.track_temp_c) else np.nan
            dam = b.ambient_temp_c - a.ambient_temp_c if pd.notna(a.ambient_temp_c) and pd.notna(b.ambient_temp_c) else np.nan
            crosses = False
            for lo, hi in KNOWN_INTERRUPTIONS.get(y, []):
                if a.attempt_timestamp_utc < ts(hi) and b.attempt_timestamp_utc > ts(lo):
                    crosses = True
            gap = any(a.attempt_timestamp_utc < ts(lo) and b.attempt_timestamp_utc > ts(hi) for lo, hi in DATA_GAPS.get(y, []))
            ref = beta["delta_track_temp_c"] * dtr + beta["delta_air_temp_c"] * dam if not (np.isnan(dtr) or np.isnan(dam)) else np.nan
            rows.append(dict(
                era=ERA[y], tier=a.tier, year=y, canonical_engineering_team=team, pair_index=k,
                attempt_prev=a.attempt_id, attempt_next=b.attempt_id, car_prev=a.registry_car_number, car_next=b.registry_car_number,
                driver_prev=a.registry_driver, driver_next=b.registry_driver,
                pair_type="SAME_CAR" if a.registry_car_number == b.registry_car_number else "DIFFERENT_CAR",
                delta_time_min=(b.attempt_timestamp_utc - a.attempt_timestamp_utc).total_seconds() / 60,
                delta_raw_speed=b.four_lap_average_speed_mph - a.four_lap_average_speed_mph,
                delta_centered_mean=b.speed_minus_car_mean - a.speed_minus_car_mean,
                delta_centered_median=b.speed_minus_car_median - a.speed_minus_car_median,
                both_centering_informative=bool(a.centering_informative and b.centering_informative),
                delta_track_temp_c=dtr, delta_ambient_temp_c=dam,
                env_method_consistent=(a.track_basis == b.track_basis and a.ambient_basis == b.ambient_basis),
                same_track_observation=(str(a.track_obs_time_utc) == str(b.track_obs_time_utc)) if pd.notna(a.track_obs_time_utc) and a.track_obs_time_utc != "" else pd.NA,
                crosses_known_interruption=crosses, crosses_data_gap=gap,
                frozen_reference_sign_mph=ref,  # frozen coefficients APPLIED (not refitted); descriptive reference only
                involves_frozen_core_attempt=bool(a.is_frozen_core_attempt or b.is_frozen_core_attempt)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ 4B.11 car/time confounding
def confounding(j):
    rows = []
    for (y, team), g in j[j.on_performance_timeline].groupby(["year", "canonical_engineering_team"]):
        cars = g.registry_car_number.nunique()
        t = g.session_elapsed_min
        if cars < 2 or len(g) < 3:
            rows.append(dict(era=ERA[y], year=y, canonical_engineering_team=team, cars=cars, attempts=len(g),
                             confounding_severity="NOT_ASSESSABLE", reason="fewer than 2 cars or 3 timed complete attempts"))
            continue
        grand = t.mean()
        ss_between = sum(len(h) * (h.session_elapsed_min.mean() - grand) ** 2 for _, h in g.groupby("registry_car_number"))
        ss_total = ((t - grand) ** 2).sum()
        eta2 = ss_between / ss_total if ss_total > 0 else np.nan
        tert = pd.qcut(t.rank(method="first"), 3, labels=["EARLY", "MID", "LATE"]) if len(g) >= 3 else None
        early = g[tert == "EARLY"].registry_car_number.value_counts(normalize=True)
        late = g[tert == "LATE"].registry_car_number.value_counts(normalize=True)
        ranges = {c: (h.session_elapsed_min.min(), h.session_elapsed_min.max()) for c, h in g.groupby("registry_car_number")}
        pairs = list(itertools.combinations(ranges, 2))
        overlap = [min(ranges[a][1], ranges[b][1]) > max(ranges[a][0], ranges[b][0]) for a, b in pairs]
        per_car = "; ".join(f"#{c}: n={len(h)}, t={h.session_elapsed_min.min():.0f}–{h.session_elapsed_min.max():.0f} min, "
                            f"median {h.session_elapsed_min.median():.0f}"
                            for c, h in sorted(g.groupby("registry_car_number"), key=lambda kv: car_sort_key(kv[0])))
        label = next(l for thr, l in CONFOUND_LABELS if (eta2 if not np.isnan(eta2) else 0) >= thr)
        if overlap and not any(overlap):
            label = "SEVERE"
        rows.append(dict(era=ERA[y], year=y, canonical_engineering_team=team, cars=cars, attempts=len(g),
                         eta2_time_explained_by_car=eta2, car_pairs=len(pairs),
                         car_pairs_with_overlapping_time_ranges=int(sum(overlap)),
                         early_tertile_dominant_car=early.idxmax(), early_tertile_dominant_share=early.max(),
                         late_tertile_dominant_car=late.idxmax(), late_tertile_dominant_share=late.max(),
                         max_attempt_share_one_car=g.registry_car_number.value_counts(normalize=True).max(),
                         per_car_time_distribution=per_car, confounding_severity=label,
                         reason=("no pair of cars has overlapping time ranges" if overlap and not any(overlap) else
                                 f"eta2={eta2:.2f} (descriptive triage label)")))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ 4B.12 weather identifiability
def weather(j):
    rows = []
    for (y, team), g in j.groupby(["year", "canonical_engineering_team"]):
        p = g[g.on_performance_timeline]
        tr, am = p.track_temp_c.dropna(), p.ambient_temp_c.dropna()
        obs = p.track_obs_time_utc.dropna().astype(str)
        obs = obs[obs != ""]
        methods_t = sorted(set(p.track_basis.dropna()) - {""})
        methods_a = sorted(set(p.ambient_basis.dropna()) - {""})
        flags = []
        if any(m.startswith("PTSC_PAST_SAFE") for m in methods_t):
            flags.append("TRACK_15MIN_PAST_SAFE_QUANTISATION")
        if any("LINEAR_INTERPOLATION" in m or "INTERPOLATED" in m for m in methods_t):
            flags.append("TRACK_INTERPOLATED_BETWEEN_15MIN_OBS")
        if len(methods_t) > 1 or len(methods_a) > 1:
            flags.append("MIXED_MEASUREMENT_METHODS")
        if len(p) and (tr.size < len(p) or am.size < len(p)):
            flags.append("MISSING_WEATHER")
        if len(p) and tr.size == 0:
            flags.append("NO_TRACK_TEMPERATURE")
        flags.append("KNOWN_INTERRUPTIONS_2022" if y in KNOWN_INTERRUPTIONS else "INTERRUPTIONS_UNRECONSTRUCTED")
        if g.tier.iloc[0] == "REGIME_EXT_R6":
            flags += ["R6_WIND_UNITS_UNVERIFIED", "NO_SOLAR"]
        if y == 2018:
            flags.append("NO_PTSC_ARCHIVE_2018")
        tt = p.dropna(subset=["track_temp_c"])
        rows.append(dict(
            era=ERA[y], year=y, canonical_engineering_team=team, attempts_on_performance_timeline=len(p),
            track_min_c=tr.min() if len(tr) else np.nan, track_max_c=tr.max() if len(tr) else np.nan,
            track_range_c=tr.max() - tr.min() if len(tr) else np.nan,
            ambient_min_c=am.min() if len(am) else np.nan, ambient_max_c=am.max() if len(am) else np.nan,
            ambient_range_c=am.max() - am.min() if len(am) else np.nan,
            distinct_track_values=tr.round(3).nunique(), distinct_ambient_values=am.round(3).nunique(),
            distinct_track_observation_times=obs.nunique(),
            track_resolution=("15-min past-safe PTSC steps" if "TRACK_15MIN_PAST_SAFE_QUANTISATION" in flags else
                              "linear interpolation between 15-min PTSC obs" if "TRACK_INTERPOLATED_BETWEEN_15MIN_OBS" in flags else
                              "none" if not len(tr) else "mixed/other"),
            track_methods="|".join(methods_t), ambient_methods="|".join(methods_a),
            method_consistent=len(methods_t) <= 1 and len(methods_a) <= 1,
            missing_track_fraction=1 - tr.size / len(p) if len(p) else np.nan,
            missing_ambient_fraction=1 - am.size / len(p) if len(p) else np.nan,
            corr_track_ambient=tt.track_temp_c.corr(tt.ambient_temp_c) if len(tt) >= 3 and tt.ambient_temp_c.notna().sum() >= 3 else np.nan,
            corr_track_session_time=tt.track_temp_c.corr(tt.session_elapsed_min) if len(tt) >= 3 else np.nan,
            flags="|".join(flags)))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ 4B.13 frozen core context
def frozen_context(j, core):
    rows = []
    jt = j.set_index("attempt_id")
    for x in core.itertuples(index=False):
        a1, a2 = x.before_attempt_id, x.after_attempt_id
        if a1 not in jt.index:
            rows.append(dict(transition_id=x.transition_id, year=x.year, target_car=x.car_number, target_driver=x.driver_name,
                             canonical_engineering_team="", on_team_timeline=False, note="target outside primary teammate layer"))
            continue
        team = jt.at[a1, "canonical_engineering_team"]
        t1, t2 = jt.at[a1, "attempt_timestamp_utc"], jt.at[a2, "attempt_timestamp_utc"]
        tl = j[(j.year == x.year) & (j.canonical_engineering_team == team) & j.on_performance_timeline]
        others = tl[tl.registry_car_number != x.car_number]
        inside = others[(others.attempt_timestamp_utc >= t1) & (others.attempt_timestamp_utc <= t2)] if pd.notna(t1) and pd.notna(t2) else others.iloc[0:0]
        rows.append(dict(
            transition_id=x.transition_id, year=x.year, era=ERA[x.year], canonical_engineering_team=team,
            target_car=x.car_number, target_driver=x.driver_name, t1_utc=t1, t2_utc=t2,
            on_team_timeline=bool(pd.notna(t1) and pd.notna(t2)),
            t1_team_timeline_order=jt.at[a1, "team_timeline_order"], t2_team_timeline_order=jt.at[a2, "team_timeline_order"],
            team_timeline_attempts=len(tl), teammate_cars_on_timeline=others.registry_car_number.nunique(),
            teammate_attempts_on_timeline=len(others),
            teammate_attempts_between_t1_t2=len(inside), teammate_cars_between_t1_t2=inside.registry_car_number.nunique(),
            teammate_attempts_before_t1=int((others.attempt_timestamp_utc < t1).sum()) if pd.notna(t1) else np.nan,
            teammate_attempts_after_t2=int((others.attempt_timestamp_utc > t2).sum()) if pd.notna(t2) else np.nan,
            teammate_centered_informative_between=int(inside.centering_informative.sum()),
            context_class=("RICH (>=2 teammate cars between endpoints)" if inside.registry_car_number.nunique() >= 2 else
                           "SOME (1 teammate car between endpoints)" if len(inside) else
                           "OUTSIDE_ONLY (teammates only before/after)" if len(others) else "NONE (no timed teammate attempts)"),
            note=""))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ 4B.10 common movement
def common_movement(j, cons):
    """Exploratory, descriptive summaries only; returned as a long table of named quantities."""
    out = []
    p = j[j.on_performance_timeline & j.centering_informative].copy()
    # (a) within-car time-trend sign agreement across cars of a team-year
    for (y, team), g in p.groupby(["year", "canonical_engineering_team"]):
        signs = {}
        for car, h in g.groupby("registry_car_number"):
            if len(h) >= 2 and h.session_elapsed_min.nunique() >= 2:
                r = h.session_elapsed_min.corr(h.four_lap_average_speed_mph, method="spearman")
                if not np.isnan(r) and r != 0:
                    signs[car] = np.sign(r)
        if len(signs) >= 2:
            vals = list(signs.values())
            out.append(dict(summary="within_car_time_trend_sign", era=ERA[y], year=y, canonical_engineering_team=team,
                            cars=len(signs), n_positive=int(sum(v > 0 for v in vals)), n_negative=int(sum(v < 0 for v in vals)),
                            all_same_sign=len(set(vals)) == 1))
    # (b) session-time tertiles: mean centered speed per tertile, with car composition
    for (y, team), g in p.groupby(["year", "canonical_engineering_team"]):
        if len(g) < 6 or g.registry_car_number.nunique() < 2:
            continue
        g = g.assign(tertile=pd.qcut(g.session_elapsed_min.rank(method="first"), 3, labels=["EARLY", "MID", "LATE"]))
        for tt, h in g.groupby("tertile", observed=True):
            out.append(dict(summary="tertile_centered_mean", era=ERA[y], year=y, canonical_engineering_team=team, tertile=tt,
                            n=len(h), cars=h.registry_car_number.nunique(), mean_centered=h.speed_minus_car_mean.mean(),
                            mean_track=h.track_temp_c.mean(), mean_ambient=h.ambient_temp_c.mean(),
                            dispersion_centered_sd=h.speed_minus_car_mean.std()))
    # (c) centered speed vs physical state within team-year (Spearman; descriptive, clustered data)
    for (y, team), g in p.groupby(["year", "canonical_engineering_team"]):
        g2 = g.dropna(subset=["track_temp_c"])
        if len(g2) >= 5 and g2.registry_car_number.nunique() >= 2 and g2.track_temp_c.nunique() >= 3:
            out.append(dict(summary="centered_vs_state_spearman", era=ERA[y], year=y, canonical_engineering_team=team,
                            n=len(g2), cars=g2.registry_car_number.nunique(),
                            rho_centered_track=g2.speed_minus_car_mean.corr(g2.track_temp_c, method="spearman"),
                            rho_centered_ambient=g2.speed_minus_car_mean.corr(g2.ambient_temp_c, method="spearman"),
                            rho_raw_track=g2.four_lap_average_speed_mph.corr(g2.track_temp_c, method="spearman"),
                            rho_centered_time=g2.speed_minus_car_mean.corr(g2.session_elapsed_min, method="spearman")))
    # (d) consecutive-pair sign agreement with the frozen reference sign (frozen coefficients applied, not refitted)
    c = cons[cons.both_centering_informative & cons.frozen_reference_sign_mph.notna() & (cons.frozen_reference_sign_mph.abs() > 0)]
    for (era, pt), g in c.groupby(["era", "pair_type"]):
        s = np.sign(g.delta_centered_mean) == np.sign(g.frozen_reference_sign_mph)
        out.append(dict(summary="consecutive_sign_vs_frozen_reference", era=era, pair_type=pt, n=len(g),
                        fraction_same_sign=s.mean(), **{k: v for k, v in uniq_pairs(g).items()}))
    return pd.DataFrame(out)


def uniq_pairs(g):
    return dict(unique_years=g.year.nunique(), unique_team_years=g[["year", "canonical_engineering_team"]].drop_duplicates().shape[0],
                unique_teams=g.canonical_engineering_team.nunique(),
                unique_cars=len(set(zip(g.year, g.car_prev)) | set(zip(g.year, g.car_next))),
                unique_attempts=len(set(g.attempt_prev) | set(g.attempt_next)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    j, core = build_long()
    _, _, beta = frozen_endpoints()
    j.to_csv(OUT / "team_timeline_long.csv", index=False)
    car_baselines(j).to_csv(OUT / "car_baseline_summary.csv", index=False)
    samp = sampling_summary(j)
    samp.to_csv(OUT / "team_timeline_sampling_summary.csv", index=False)
    cons = consecutive(j, beta)
    cons.to_csv(OUT / "consecutive_team_observations.csv", index=False)
    confounding(j).to_csv(OUT / "car_time_confounding_audit.csv", index=False)
    weather(j).to_csv(OUT / "weather_identifiability_audit.csv", index=False)
    frozen_context(j, core).to_csv(OUT / "frozen_core_timeline_context.csv", index=False)
    common_movement(j, cons).to_csv(OUT / "common_movement_exploration.csv", index=False)
    cl = pd.DataFrame([dict(scope=s, **uniq(d)) for s, d in [("ALL_PRIMARY_ATTEMPTS", j), ("PERFORMANCE_TIMELINE", j[j.on_performance_timeline])]]
                      + [dict(scope=f"PERFORMANCE_TIMELINE|{e}", **uniq(d)) for e, d in j[j.on_performance_timeline].groupby("era")])
    cl.to_csv(OUT / "cluster_counts.csv", index=False)
    return j, samp, cons


if __name__ == "__main__":
    j, samp, cons = main()
    print(pd.read_csv(OUT / "cluster_counts.csv").to_string())
    print(samp.groupby("era").agg(team_years=("year", "size"), ge2cars=("cars_on_performance_timeline", lambda s: (s >= 2).sum()),
                                  ge3cars=("cars_on_performance_timeline", lambda s: (s >= 3).sum()), panel=("panel_eligible", "sum")).to_string())
    print(cons.groupby(["era", "pair_type"]).size().to_string())
