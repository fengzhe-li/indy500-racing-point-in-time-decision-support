"""V4 Phase 4A: teammate-control matching design anchored on the 41 frozen same-car transitions.

Descriptive design only:
  * no coefficient is fitted or refitted, no weight assigned, no final rule chosen;
  * the frozen 41 transitions are read, never modified; teammate observations are not
    added to the training sample;
  * no p-values (endpoint matches are not independent).

Conventions
-----------
offset_min = teammate_timestamp - endpoint_timestamp (negative = teammate ran BEFORE the endpoint).
Direction  ANY:    |offset| <= w
           PRIOR:  -w <= offset <= 0   (teammate_timestamp <= endpoint: information available at t)
           FUTURE: 0 < offset <= w     (retrospective only; not available in real time)
delta_team_control  = team_control_t2 - team_control_t1
delta_target        = frozen after_speed - before_speed (frozen value, unaltered)
team_adjusted_delta = delta_target - delta_team_control     (diagnostic, not a causal driver effect)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
P3 = V4 / "output" / "phase3"
OUT = V4 / "output" / "phase4a"

WINDOWS = [5, 10, 15, 20, 30, 45, 60]
DIRECTIONS = ["ANY", "PRIOR", "FUTURE"]
STRATEGIES = ["NEAREST", "MUTUAL_NEAREST", "WINDOW_MEDIAN", "WINDOW_MEAN", "CAR_BALANCED_MEAN", "CAR_BALANCED_COMMON_CARS"]
PIT_FRAGILE_MARGIN_MIN = 2.0  # |offset| below this: ordering is within approximate-timestamp resolution
KNOWN_INTERRUPTION_YEARS = {2022}
DATA_GAPS = {2020: ("2020-08-15T18:35:15Z", "2020-08-15T18:42:30Z")}


def ts(s):
    return pd.to_datetime(s, utc=True, format="mixed", errors="coerce")


def car_sort_key(c):
    s = str(c)
    return (int(s) if s.isdigit() else 999, s)


# ------------------------------------------------------------------ anchors
def load_frozen(j):
    r = pd.read_csv(REPO / "r5_2/manual/r5_2_repeat_analysis_set_v1.csv", dtype={"car_number": str})
    core = r.dropna(subset=["delta_four_lap_average_speed_mph", "delta_track_temp_c", "delta_air_temp_c"]).reset_index(drop=True)
    assert len(core) == 41
    # existing frozen LOYO predictions/residuals (same row order as build_probabilistic_physics_core_v1.py)
    lo = pd.read_csv(REPO / "r5_2/manual/probabilistic_physics_loyo_residuals_v1.csv", dtype={"car_number": str})
    assert len(lo) == 41
    link_ok = ((lo.year.values == core.year.values) & (lo.car_number.values == core.car_number.values)
               & (lo.driver_name.values == core.driver_name.values)
               & np.isclose(lo.delta_four_lap_average_speed_mph.values, core.delta_four_lap_average_speed_mph.values)
               & np.isclose(lo.delta_track_temp_c.values, core.delta_track_temp_c.values)
               & np.isclose(lo.delta_air_temp_c.values, core.delta_air_temp_c.values))
    assert link_ok.all(), "LOYO residual file does not align with the frozen 41"
    model = json.loads((REPO / "r5_2/manual/probabilistic_physics_core_v1.json").read_text())
    beta = model["mean_core"]["full_data_huber_coefficients"]

    team = {(y, c): t for y, c, t in zip(j.year, j.registry_car_number, j.canonical_engineering_team)}
    prim = {(y, c): p for y, c, p in zip(j.year, j.registry_car_number, j.primary_teammate_layer)}
    jt = j.set_index("attempt_id")
    rows = []
    for i, x in core.iterrows():
        t1f, t2f = ts(x.before_time_utc), ts(x.after_time_utc)
        t1p, t2p = jt.attempt_timestamp_utc.get(x.before_attempt_id), jt.attempt_timestamp_utc.get(x.after_attempt_id)
        rows.append(dict(
            transition_id=x.transition_id, year=x.year,
            canonical_engineering_team=team.get((x.year, x.car_number), ""),
            target_team_in_primary_layer=bool(prim.get((x.year, x.car_number), False)),
            target_driver=x.driver_name, target_car=x.car_number,
            before_attempt_id=x.before_attempt_id, after_attempt_id=x.after_attempt_id,
            frozen_t1_utc=x.before_time_utc, frozen_t2_utc=x.after_time_utc,
            frozen_t1_time_class=x.before_time_class, frozen_t2_time_class=x.after_time_class,
            t1=t1f if pd.notna(t1f) else t1p, t2=t2f if pd.notna(t2f) else t2p,
            t1_source="FROZEN_REPEAT_SET" if pd.notna(t1f) else ("PHASE3_" + jt.time_class.get(x.before_attempt_id, "MISSING")),
            t2_source="FROZEN_REPEAT_SET" if pd.notna(t2f) else ("PHASE3_" + jt.time_class.get(x.after_attempt_id, "MISSING")),
            speed_t1=x.before_four_lap_average_speed_mph, speed_t2=x.after_four_lap_average_speed_mph,
            observed_delta_speed=x.delta_four_lap_average_speed_mph,
            track_temp_t1=x.previous_track_temp_c, track_temp_t2=x.next_track_temp_c,
            ambient_temp_t1=x.previous_air_temp_c, ambient_temp_t2=x.next_air_temp_c,
            frozen_delta_track_temp_c=x.delta_track_temp_c, frozen_delta_air_temp_c=x.delta_air_temp_c,
            frozen_loyo_predicted_delta_mph=lo.predicted_physical_delta_mph_loyo[i],
            frozen_loyo_residual_raw_mph=lo.residual_loyo_raw[i], frozen_loyo_residual_centered_mph=lo.residual_loyo_centered[i],
            derived_full_data_frozen_prediction_mph=beta["delta_track_temp_c"] * x.delta_track_temp_c + beta["delta_air_temp_c"] * x.delta_air_temp_c,
            frozen_analysis_source=x.analysis_source, frozen_physical_link_quality=x.physical_link_quality,
            track_basis_t1=jt.track_basis.get(x.before_attempt_id, ""), track_basis_t2=jt.track_basis.get(x.after_attempt_id, ""),
            ambient_basis_t1=jt.ambient_basis.get(x.before_attempt_id, ""), ambient_basis_t2=jt.ambient_basis.get(x.after_attempt_id, ""),
            track_obs_t1=jt.track_obs_time_utc.get(x.before_attempt_id, ""), track_obs_t2=jt.track_obs_time_utc.get(x.after_attempt_id, ""),
        ))
    a = pd.DataFrame(rows)
    a["t1"] = pd.to_datetime(a.t1, utc=True)
    a["t2"] = pd.to_datetime(a.t2, utc=True)
    return a


# ------------------------------------------------------------------ teammate candidates
def teammate_candidates(anchors, j):
    rows = []
    for a in anchors.itertuples(index=False):
        if not a.target_team_in_primary_layer:
            continue
        pool = j[(j.year == a.year) & (j.canonical_engineering_team == a.canonical_engineering_team)
                 & (j.primary_teammate_layer == True) & (j.registry_car_number != a.target_car)]
        for ep, t, basis_t, basis_a, obs in [("T1", a.t1, a.track_basis_t1, a.ambient_basis_t1, a.track_obs_t1),
                                             ("T2", a.t2, a.track_basis_t2, a.ambient_basis_t2, a.track_obs_t2)]:
            for x in pool.itertuples(index=False):
                off = (x.attempt_timestamp_utc - t).total_seconds() / 60 if pd.notna(x.attempt_timestamp_utc) and pd.notna(t) else np.nan
                gap_crossed = False
                if a.year in DATA_GAPS and not np.isnan(off):
                    g0, g1 = ts(DATA_GAPS[a.year][0]), ts(DATA_GAPS[a.year][1])
                    lo_, hi_ = sorted([t, x.attempt_timestamp_utc])
                    gap_crossed = bool(lo_ < g0 and hi_ > g1)
                rows.append(dict(
                    transition_id=a.transition_id, year=a.year, canonical_engineering_team=a.canonical_engineering_team,
                    target_car=a.target_car, target_driver=a.target_driver, endpoint=ep, endpoint_time_utc=t,
                    teammate_driver=x.registry_driver, teammate_car=x.registry_car_number, teammate_raw_car=x.car_number,
                    teammate_attempt=x.attempt_id, teammate_timestamp=x.attempt_timestamp_utc,
                    signed_offset_min=off, abs_offset_min=abs(off) if not np.isnan(off) else np.nan,
                    direction=("PRIOR" if off <= 0 else "FUTURE") if not np.isnan(off) else "UNTIMED",
                    teammate_speed=x.four_lap_average_speed_mph, teammate_complete_four_lap=bool(x.complete_four_lap),
                    teammate_result_status=x.result_status, teammate_attempt_class=x.attempt_class,
                    teammate_track_temp_c=x.track_temp_c, teammate_ambient_temp_c=x.ambient_temp_c,
                    teammate_time_class=x.time_class, teammate_time_half_width_min=x.time_half_width_min,
                    teammate_track_basis=x.track_basis, teammate_ambient_basis=x.ambient_basis,
                    teammate_track_obs_time_utc=x.track_obs_time_utc,
                    eligible_control=bool(x.complete_four_lap) and pd.notna(x.attempt_timestamp_utc),
                    env_basis_matches_endpoint=(x.track_basis == basis_t and x.ambient_basis == basis_a) if x.track_basis and basis_t else pd.NA,
                    same_ptsc_track_observation_as_endpoint=(str(x.track_obs_time_utc) == str(obs)) if isinstance(obs, str) and obs else pd.NA,
                    crosses_2020_data_gap=gap_crossed,
                    session_state=("KNOWN_INTERRUPTION_YEAR" if a.year in KNOWN_INTERRUPTION_YEARS else "SAME_DAY1_SESSION_NO_INTERRUPTION_RECORD"),
                    pit_available=(off <= 0) if not np.isnan(off) else False,
                    pit_order_fragile=(not np.isnan(off)) and off <= 0 and (abs(off) < PIT_FRAGILE_MARGIN_MIN
                                                                            or x.time_class != "APPROX_POINT_RECORDER_CAPTURE"),
                ))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ controls
def select(pool, w, direction):
    p = pool[pool.eligible_control]
    if direction == "ANY":
        p = p[p.abs_offset_min <= w]
    elif direction == "PRIOR":
        p = p[(p.signed_offset_min <= 0) & (p.signed_offset_min >= -w)]
    else:
        p = p[(p.signed_offset_min > 0) & (p.signed_offset_min <= w)]
    return p


def nearest_row(p):
    # ties: smaller |offset|, then prior before future, then car sort key
    k = p.assign(_f=(p.signed_offset_min > 0).astype(int), _c=p.teammate_car.map(car_sort_key))
    return k.sort_values(["abs_offset_min", "_f", "_c"], kind="stable").iloc[0]


def endpoint_control(pool, target_attempts, endpoint_attempt, strategy, w, direction, other_cars=None):
    p = select(pool, w, direction)
    if p.empty:
        return None
    if strategy in ("NEAREST", "MUTUAL_NEAREST"):
        r = nearest_row(p)
        if strategy == "MUTUAL_NEAREST":
            d = (target_attempts.attempt_timestamp_utc - r.teammate_timestamp).abs()
            if target_attempts.empty or target_attempts.loc[d.idxmin(), "attempt_id"] != endpoint_attempt:
                return None
        used = p[p.teammate_attempt == r.teammate_attempt]
        value = r.teammate_speed
    elif strategy == "WINDOW_MEDIAN":
        used, value = p, p.teammate_speed.median()
    elif strategy == "WINDOW_MEAN":
        used, value = p, p.teammate_speed.mean()
    elif strategy == "CAR_BALANCED_MEAN":
        used, value = p, p.groupby("teammate_car").teammate_speed.mean().mean()
    elif strategy == "CAR_BALANCED_COMMON_CARS":
        used = p[p.teammate_car.isin(other_cars)] if other_cars is not None else p
        if used.empty:
            return None
        value = used.groupby("teammate_car").teammate_speed.mean().mean()
    return dict(value=value, n_attempts=len(used), n_cars=used.teammate_car.nunique(),
                cars="|".join(sorted(used.teammate_car.unique(), key=car_sort_key)),
                attempts="|".join(used.teammate_attempt), min_abs_offset=used.abs_offset_min.min(),
                max_abs_offset=used.abs_offset_min.max(), mean_signed_offset=used.signed_offset_min.mean(),
                mean_track=used.teammate_track_temp_c.mean(), mean_ambient=used.teammate_ambient_temp_c.mean(),
                any_mixed_basis=bool((used.env_basis_matches_endpoint.astype(str) == "False").any()),
                any_non_point_time=bool((used.teammate_time_class != "APPROX_POINT_RECORDER_CAPTURE").any()),
                any_pit_fragile=bool(used.pit_order_fragile.any()),
                any_same_ptsc_obs=bool((used.same_ptsc_track_observation_as_endpoint.astype(str) == "True").any()),
                any_crosses_data_gap=bool(used.crosses_2020_data_gap.any()))


def build_controls(anchors, cand, j):
    rows = []
    windows = WINDOWS + [np.inf]
    for a in anchors.itertuples(index=False):
        tgt = j[(j.year == a.year) & (j.registry_car_number == a.target_car) & j.complete_four_lap & j.attempt_timestamp_utc.notna()]
        c1 = cand[(cand.transition_id == a.transition_id) & (cand.endpoint == "T1")]
        c2 = cand[(cand.transition_id == a.transition_id) & (cand.endpoint == "T2")]
        for strategy in STRATEGIES:
            for w in windows:
                if np.isinf(w) and strategy not in ("NEAREST", "MUTUAL_NEAREST"):
                    continue
                for direction in DIRECTIONS:
                    common = None
                    if strategy == "CAR_BALANCED_COMMON_CARS":
                        s1, s2 = select(c1, w, direction), select(c2, w, direction)
                        common = sorted(set(s1.teammate_car) & set(s2.teammate_car))
                    e1 = endpoint_control(c1, tgt, a.before_attempt_id, strategy, w, direction, common) if len(c1) else None
                    e2 = endpoint_control(c2, tgt, a.after_attempt_id, strategy, w, direction, common) if len(c2) else None
                    row = dict(transition_id=a.transition_id, year=a.year, canonical_engineering_team=a.canonical_engineering_team,
                               target_car=a.target_car, target_driver=a.target_driver, strategy=strategy,
                               window_min=("UNBOUNDED" if np.isinf(w) else int(w)), direction=direction,
                               view=("PIT_COMPATIBLE" if direction == "PRIOR" else "RETROSPECTIVE"),
                               target_team_in_primary_layer=a.target_team_in_primary_layer,
                               supported_t1=e1 is not None, supported_t2=e2 is not None,
                               supported_both=e1 is not None and e2 is not None,
                               delta_target=a.observed_delta_speed,
                               frozen_loyo_predicted_delta_mph=a.frozen_loyo_predicted_delta_mph,
                               frozen_loyo_residual_raw_mph=a.frozen_loyo_residual_raw_mph)
                    for tag, e in (("t1", e1), ("t2", e2)):
                        for k in ["value", "n_attempts", "n_cars", "cars", "attempts", "min_abs_offset", "max_abs_offset",
                                  "mean_signed_offset", "mean_track", "mean_ambient", "any_mixed_basis", "any_non_point_time",
                                  "any_pit_fragile", "any_same_ptsc_obs", "any_crosses_data_gap"]:
                            row[f"{k if k != 'value' else 'team_control'}_{tag}"] = e[k] if e else np.nan
                    if row["supported_both"]:
                        dc = e2["value"] - e1["value"]
                        row["delta_team_control"] = dc
                        row["team_adjusted_delta"] = a.observed_delta_speed - dc
                        st, sc = np.sign(a.observed_delta_speed), np.sign(dc)
                        row["same_direction"] = (st == sc) if st != 0 and sc != 0 else pd.NA
                        s1, s2 = set(e1["cars"].split("|")), set(e2["cars"].split("|"))
                        row["same_teammate_car_set_both_endpoints"] = s1 == s2
                        row["shared_teammate_attempts_between_endpoints"] = len(set(e1["attempts"].split("|")) & set(e2["attempts"].split("|")))
                        row["degenerate_identical_control"] = e1["attempts"] == e2["attempts"]
                        row["teammate_delta_track_c"] = e2["mean_track"] - e1["mean_track"]
                        row["teammate_delta_ambient_c"] = e2["mean_ambient"] - e1["mean_ambient"]
                    rows.append(row)
    ctrl = pd.DataFrame(rows)
    # Is the control change itself another frozen same-car transition? (circularity / double counting)
    frozen_ep = {(a.before_attempt_id, a.after_attempt_id): a.transition_id for a in anchors.itertuples(index=False)}
    other, recip = [], []
    for r in ctrl.itertuples(index=False):
        hit = ""
        if r.supported_both and isinstance(r.attempts_t1, str) and "|" not in r.attempts_t1 and "|" not in r.attempts_t2:
            hit = frozen_ep.get((r.attempts_t1, r.attempts_t2), "")
        other.append(hit)
    ctrl["control_equals_other_frozen_transition"] = other
    key = {(r.strategy, r.window_min, r.direction, r.transition_id): r.control_equals_other_frozen_transition for r in ctrl.itertuples(index=False)}
    ctrl["reciprocal_frozen_pair"] = [bool(o) and key.get((r.strategy, r.window_min, r.direction, o)) == r.transition_id
                                      for r, o in zip(ctrl.itertuples(index=False), other)]
    tr = anchors.set_index("transition_id")
    ctrl["frozen_delta_track_temp_c"] = ctrl.transition_id.map(tr.frozen_delta_track_temp_c)
    ctrl["frozen_delta_air_temp_c"] = ctrl.transition_id.map(tr.frozen_delta_air_temp_c)
    ctrl["transition_elapsed_min"] = ctrl.transition_id.map((tr.t2 - tr.t1).dt.total_seconds() / 60)
    return ctrl


# ------------------------------------------------------------------ summaries
def support_table(ctrl, anchors):
    base = ctrl[(ctrl.strategy == "WINDOW_MEAN") & (ctrl.window_min != "UNBOUNDED")]
    out = []
    for (w, d), g in base.groupby(["window_min", "direction"]):
        for scope, gg in [("ALL", g)] + [(f"YEAR={y}", h) for y, h in g.groupby("year")] + \
                         [(f"TEAM={t}", h) for t, h in g.groupby("canonical_engineering_team")]:
            out.append(dict(window_min=w, direction=d, view=("PIT_COMPATIBLE" if d == "PRIOR" else "RETROSPECTIVE"), scope=scope,
                            frozen_transitions=len(gg), support_t1=int(gg.supported_t1.sum()), support_t2=int(gg.supported_t2.sum()),
                            support_both=int(gg.supported_both.sum()),
                            multi_car_t1=int((gg.n_cars_t1 >= 2).sum()), multi_car_t2=int((gg.n_cars_t2 >= 2).sum()),
                            multi_car_both=int(((gg.n_cars_t1 >= 2) & (gg.n_cars_t2 >= 2)).sum())))
    return pd.DataFrame(out)


def strategy_summary(ctrl):
    out = []
    for (s, w, d), g in ctrl.groupby(["strategy", "window_min", "direction"], sort=False):
        b = g[g.supported_both]
        nd = b[~b.degenerate_identical_control.astype(bool)] if len(b) else b
        sd = nd.same_direction.dropna().astype(bool) if len(nd) else pd.Series(dtype=bool)
        r = dict(strategy=s, window_min=w, direction=d, view=("PIT_COMPATIBLE" if d == "PRIOR" else "RETROSPECTIVE"),
                 n_supported_both=len(b), n_degenerate_identical_control=int(b.degenerate_identical_control.sum()) if len(b) else 0,
                 n_nondegenerate=len(nd), n_same_teammate_car_set=int(nd.same_teammate_car_set_both_endpoints.sum()) if len(nd) else 0,
                 same_direction_n=len(sd), same_direction_fraction=sd.mean() if len(sd) else np.nan)
        if len(nd) >= 3:
            x, y = nd.delta_team_control.astype(float), nd.delta_target.astype(float)
            r.update(pearson_r=x.corr(y), spearman_rho=x.corr(y, method="spearman"),
                     median_delta_team_control=x.median(), median_team_adjusted=nd.team_adjusted_delta.median(),
                     iqr_team_adjusted=nd.team_adjusted_delta.quantile(.75) - nd.team_adjusted_delta.quantile(.25),
                     sd_delta_target=y.std(), sd_team_adjusted=nd.team_adjusted_delta.std(),
                     sd_frozen_loyo_residual_same_subset=nd.frozen_loyo_residual_raw_mph.std(),
                     pearson_team_control_vs_frozen_prediction=x.corr(nd.frozen_loyo_predicted_delta_mph),
                     env_fidelity_corr_delta_track=nd.teammate_delta_track_c.corr(nd.frozen_delta_track_temp_c),
                     env_fidelity_median_abs_diff_delta_track_c=(nd.teammate_delta_track_c - nd.frozen_delta_track_temp_c).abs().median(),
                     env_fidelity_corr_delta_ambient=nd.teammate_delta_ambient_c.corr(nd.frozen_delta_air_temp_c),
                     env_fidelity_median_abs_diff_delta_ambient_c=(nd.teammate_delta_ambient_c - nd.frozen_delta_air_temp_c).abs().median())
        r["n_control_equals_other_frozen_transition"] = int((nd.control_equals_other_frozen_transition.fillna("") != "").sum()) if len(nd) else 0
        r["n_reciprocal_frozen_pairs"] = int(nd.reciprocal_frozen_pair.sum() // 2) if len(nd) else 0
        r["n_independent_of_frozen_transitions"] = r["n_nondegenerate"] - r["n_control_equals_other_frozen_transition"]
        out.append(r)
    return pd.DataFrame(out)


def dependence(ctrl):
    out = []
    for (s, w, d), g in ctrl.groupby(["strategy", "window_min", "direction"], sort=False):
        b = g[g.supported_both]
        uses = []
        rel = set()
        for r in b.itertuples(index=False):
            for tag in ("t1", "t2"):
                att = getattr(r, f"attempts_{tag}").split("|")
                uses += att
                for car in getattr(r, f"cars_{tag}").split("|"):
                    rel.add((r.year, r.target_car, car))
        u = pd.Series(uses).value_counts() if uses else pd.Series(dtype=int)
        out.append(dict(strategy=s, window_min=w, direction=d, view=("PIT_COMPATIBLE" if d == "PRIOR" else "RETROSPECTIVE"),
                        unique_frozen_transitions=b.transition_id.nunique(),
                        unique_target_cars=b[["year", "target_car"]].drop_duplicates().shape[0],
                        unique_teammate_cars=len({(y, c) for y, _, c in rel}), unique_teammate_relationships=len(rel),
                        unique_teams=b[["year", "canonical_engineering_team"]].drop_duplicates().shape[0],
                        unique_canonical_teams=b.canonical_engineering_team.nunique(), unique_years=b.year.nunique(),
                        teammate_attempt_uses=len(uses), unique_teammate_attempts_used=len(u),
                        teammate_attempts_reused=int((u > 1).sum()) if len(u) else 0,
                        max_reuse_of_one_teammate_attempt=int(u.max()) if len(u) else 0,
                        share_of_uses_that_are_reused=float(u[u > 1].sum() / len(uses)) if uses else np.nan,
                        controls_equal_to_another_frozen_transition=int((b.control_equals_other_frozen_transition.fillna("") != "").sum()),
                        reciprocal_frozen_transition_pairs=int(b.reciprocal_frozen_pair.sum() // 2),
                        transitions_sharing_attempt_across_own_endpoints=int((b.shared_teammate_attempts_between_endpoints > 0).sum()) if len(b) else 0))
    return pd.DataFrame(out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    j = pd.read_csv(P3 / "team_attempt_join.csv", dtype={"car_number": str, "registry_car_number": str}, low_memory=False)
    j = j[j.tier == "CORE_2020_2024"].copy()  # frozen 41 are 2020-2024; R6 kept out of the reference analysis
    j["attempt_timestamp_utc"] = ts(j.attempt_timestamp_utc)
    for col in ["track_basis", "ambient_basis", "track_obs_time_utc", "time_class"]:
        j[col] = j[col].fillna("")
    anchors = load_frozen(j)
    anchors.to_csv(OUT / "frozen_transition_anchors.csv", index=False)
    cand = teammate_candidates(anchors, j)
    cand.to_csv(OUT / "frozen_transition_teammate_candidates.csv", index=False)
    ctrl = build_controls(anchors, cand, j)
    ctrl.to_csv(OUT / "all_matched_controls.csv", index=False)
    ctrl[ctrl.strategy.isin(["NEAREST", "MUTUAL_NEAREST"])].to_csv(OUT / "matched_controls_nearest.csv", index=False)
    ctrl[ctrl.strategy == "WINDOW_MEDIAN"].to_csv(OUT / "matched_controls_window_median.csv", index=False)
    ctrl[ctrl.strategy == "WINDOW_MEAN"].to_csv(OUT / "matched_controls_window_mean.csv", index=False)
    ctrl[ctrl.strategy.str.startswith("CAR_BALANCED")].to_csv(OUT / "matched_controls_car_balanced.csv", index=False)
    ctrl[ctrl.direction == "PRIOR"].to_csv(OUT / "pit_prior_only_controls.csv", index=False)
    support_table(ctrl, anchors).to_csv(OUT / "endpoint_support_by_window.csv", index=False)
    strategy_summary(ctrl).to_csv(OUT / "strategy_summary.csv", index=False)
    dependence(ctrl).to_csv(OUT / "dependence_audit.csv", index=False)
    return anchors, cand, ctrl


if __name__ == "__main__":
    anchors, cand, ctrl = main()
    print(anchors.groupby(["year", "target_team_in_primary_layer"]).size().to_string())
    print(anchors[["t1_source", "t2_source"]].value_counts().to_string())
    print("candidates", len(cand), "eligible", int(cand.eligible_control.sum()), "controls rows", len(ctrl))
