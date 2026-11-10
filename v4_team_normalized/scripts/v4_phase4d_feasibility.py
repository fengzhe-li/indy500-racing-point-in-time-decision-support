"""V4 Phase 4D: latent team-state / residual-attribution FEASIBILITY (no latent model is fitted).

Implements output/phase4d/phase4d_identifiability_spec.md (committed before any computation).
Frozen artefacts and Phase 4C are read-only. Frozen coefficients are only *applied* to teammate
previous-attempt changes (spec §2); nothing is refitted.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4d"
WINDOWS = [15, 30, 45, 60, "INTERVAL"]
PRIMARY_W = 30
SEED, NPERM = 20260928, 2000
ERA_B = [2020, 2021, 2022, 2023, 2024]
FROZEN_LINKED = {"RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE", "FROZEN_CORE_ENDPOINT"}


def ts(s):
    return pd.to_datetime(s, utc=True, format="mixed", errors="coerce")


def car_key(c):
    s = str(c)
    return (int(s) if s.isdigit() else 999, s)


# ------------------------------------------------------------------ inputs
def load():
    core = pd.read_csv(REPO / "r5_2/manual/r5_2_repeat_analysis_set_v1.csv", dtype={"car_number": str})
    core = core.dropna(subset=["delta_four_lap_average_speed_mph", "delta_track_temp_c", "delta_air_temp_c"]).reset_index(drop=True)
    lo = pd.read_csv(REPO / "r5_2/manual/probabilistic_physics_loyo_residuals_v1.csv", dtype={"car_number": str})
    bt = pd.read_csv(REPO / "r5_2/manual/probabilistic_physics_historical_backtest_v1.csv", dtype={"car_number": str})
    for other in (lo, bt):
        assert (other.year.values == core.year.values).all() and (other.car_number.values == core.car_number.values).all()
    assert np.allclose(lo.residual_loyo_raw, core.delta_four_lap_average_speed_mph - lo.predicted_physical_delta_mph_loyo)
    anch = pd.read_csv(V4 / "output/phase4a/frozen_transition_anchors.csv", dtype={"target_car": str})
    assert list(anch.transition_id) == list(core.transition_id)
    a = anch[["transition_id", "year", "canonical_engineering_team", "target_team_in_primary_layer", "target_driver", "target_car",
              "before_attempt_id", "after_attempt_id", "t1", "t2", "t1_source", "t2_source", "speed_t1", "speed_t2", "observed_delta_speed",
              "track_temp_t1", "track_temp_t2", "ambient_temp_t1", "ambient_temp_t2"]].copy()
    a["frozen_expected_delta_loyo"] = lo.predicted_physical_delta_mph_loyo.values
    a["target_residual"] = lo.residual_loyo_raw.values
    a["frozen_residual_loyo_centered"] = lo.residual_loyo_centered.values
    a["secondary_backtest_predicted_median"] = bt.predicted_median_mph.values
    for c in ["physical_link_quality", "analysis_source", "before_time_class", "after_time_class", "hrrr_pair_available",
              "ptsc_pair_available", "full_environment_pair_available", "exclusion_reason", "in_frozen_39",
              "delta_track_temp_c", "delta_air_temp_c"]:
        a[f"frozen_{c}"] = core[c].values
    a["t1"], a["t2"] = ts(a.t1), ts(a.t2)
    a["t_mid"] = a.t1 + (a.t2 - a.t1) / 2
    j = pd.read_csv(V4 / "output/phase4b/team_timeline_long.csv", dtype={"car_number": str, "registry_car_number": str}, low_memory=False)
    for b in ["primary_teammate_layer", "on_performance_timeline", "on_timeline", "complete_four_lap", "is_frozen_core_attempt"]:
        j[b] = j[b].astype(str).eq("True")
    j["attempt_timestamp_utc"] = ts(j.attempt_timestamp_utc)
    beta = json.loads((REPO / "r5_2/manual/probabilistic_physics_core_v1.json").read_text())["mean_core"]["full_data_huber_coefficients"]
    frozen_ep = set(core.before_attempt_id) | set(core.after_attempt_id)
    frozen_pairs = {(b, c): t for b, c, t in zip(core.before_attempt_id, core.after_attempt_id, core.transition_id)}
    return a, j, beta, frozen_ep, frozen_pairs


# ------------------------------------------------------------------ observations (spec §2)
def build_moves(j, years, beta, frozen_ep, frozen_pairs, physics=True):
    rows = []
    prim = j[j.year.isin(years) & j.primary_teammate_layer]
    for (y, car), g in prim.groupby(["year", "registry_car_number"]):
        perf = g[g.on_performance_timeline].sort_values(["attempt_timestamp_utc", "attempt_id"]).reset_index(drop=True)
        has_untimed = bool((~g.on_timeline).any())
        timed_incomplete = g[g.on_timeline & ~g.complete_four_lap]
        for k in range(1, len(perf)):
            p, c = perf.iloc[k - 1], perf.iloc[k]
            between = ((timed_incomplete.attempt_timestamp_utc > p.attempt_timestamp_utc) & (timed_incomplete.attempt_timestamp_utc < c.attempt_timestamp_utc)).any()
            dtr = c.track_temp_c - p.track_temp_c
            dam = c.ambient_temp_c - p.ambient_temp_c
            d = c.four_lap_average_speed_mph - p.four_lap_average_speed_mph
            adj = d - (beta["delta_track_temp_c"] * dtr + beta["delta_air_temp_c"] * dam) if physics else d
            rows.append(dict(obs_id=f"MOVE|{p.attempt_id}|{c.attempt_id}", obs_type="MOVE", year=y, canonical_engineering_team=c.canonical_engineering_team,
                             car=car, driver=c.registry_driver, attempt_prev=p.attempt_id, attempt_curr=c.attempt_id,
                             t_prev=p.attempt_timestamp_utc, t_curr=c.attempt_timestamp_utc,
                             previous_attempt_delta=d, delta_time_min=(c.attempt_timestamp_utc - p.attempt_timestamp_utc).total_seconds() / 60,
                             delta_track_c=dtr, delta_ambient_c=dam, physics_adjusted_move=adj if pd.notna(adj) else np.nan,
                             seq_prev=p.car_timeline_order, seq_curr=c.car_timeline_order, speed_prev=p.four_lap_average_speed_mph,
                             speed_curr=c.four_lap_average_speed_mph, time_class_prev=p.time_class, time_class_curr=c.time_class,
                             link_uncertain=bool(has_untimed or between),
                             is_frozen_pair=(p.attempt_id, c.attempt_id) in frozen_pairs,
                             frozen_pair_transition=frozen_pairs.get((p.attempt_id, c.attempt_id), ""),
                             touches_frozen_endpoint=(p.attempt_id in frozen_ep) or (c.attempt_id in frozen_ep)))
    return pd.DataFrame(rows)


def build_levels(j, years, frozen_ep):
    p = j[j.year.isin(years) & j.primary_teammate_layer & j.on_performance_timeline]
    return pd.DataFrame(dict(obs_id="LEVEL|" + p.attempt_id, obs_type="LEVEL", year=p.year, canonical_engineering_team=p.canonical_engineering_team,
                             car=p.registry_car_number, driver=p.registry_driver, attempt_curr=p.attempt_id, t_curr=p.attempt_timestamp_utc,
                             speed_curr=p.four_lap_average_speed_mph, speed_minus_car_mean=p.speed_minus_car_mean,
                             speed_minus_car_median=p.speed_minus_car_median, car_n_timeline=p.car_n_timeline,
                             track_c=p.track_temp_c, ambient_c=p.ambient_temp_c, time_class_curr=p.time_class,
                             track_basis=p.track_basis, ambient_basis=p.ambient_basis,
                             touches_frozen_endpoint=p.attempt_id.isin(frozen_ep))).reset_index(drop=True)


def base_label(o):
    if o.obs_type == "MOVE" and o.is_frozen_pair:
        return "RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE"
    if o.touches_frozen_endpoint:
        return "FROZEN_CORE_ENDPOINT"
    pt = "APPROX_POINT_RECORDER_CAPTURE"
    if o.obs_type == "MOVE" and (o.link_uncertain or o.time_class_prev != pt or o.time_class_curr != pt):
        return "UNKNOWN_DEPENDENCE"
    if o.obs_type == "LEVEL" and o.time_class_curr != pt:
        return "UNKNOWN_DEPENDENCE"
    return None  # INDEPENDENT or OTHER_DEPENDENT_REUSE, decided after reuse is known


# ------------------------------------------------------------------ context (spec §4)
def span(a, w):
    if w == "INTERVAL":
        return a.t1, a.t2
    return a.t1 - pd.Timedelta(minutes=w), a.t2 + pd.Timedelta(minutes=w)


def context_rows(anchors, moves, levels):
    rows = []
    for a in anchors.itertuples(index=False):
        if not a.target_team_in_primary_layer or pd.isna(a.t1) or pd.isna(a.t2):
            continue
        sel = lambda df: df[(df.year == a.year) & (df.canonical_engineering_team == a.canonical_engineering_team) & (df.car != a.target_car)]
        for o in pd.concat([sel(moves), sel(levels)], ignore_index=True).itertuples(index=False):
            start = o.t_prev if o.obs_type == "MOVE" else o.t_curr
            r = dict(transition_id=a.transition_id, obs_id=o.obs_id, obs_type=o.obs_type,
                     offset_t1_start_min=(start - a.t1).total_seconds() / 60, offset_t1_end_min=(o.t_curr - a.t1).total_seconds() / 60,
                     offset_t2_start_min=(start - a.t2).total_seconds() / 60, offset_t2_end_min=(o.t_curr - a.t2).total_seconds() / 60,
                     region=("BEFORE_T1" if o.t_curr < a.t1 else "AFTER_T2" if start > a.t2 else
                             "BETWEEN_T1_T2" if start >= a.t1 and o.t_curr <= a.t2 else "STRADDLES_ENDPOINT"))
            for w in WINDOWS:
                lo_, hi_ = span(a, w)
                r[f"in_window_{w}"] = bool(start >= lo_ and o.t_curr <= hi_)
                if w != "INTERVAL":
                    wd = pd.Timedelta(minutes=w)
                    r[f"near_t1_{w}"] = bool(o.t_curr >= a.t1 - wd and start <= a.t1 + wd)
                    r[f"near_t2_{w}"] = bool(o.t_curr >= a.t2 - wd and start <= a.t2 + wd)
            rows.append(r)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ structure (spec §5)
def structure(anchors, ctx, obs):
    ob = obs.set_index("obs_id")
    rows = []
    for a in anchors.itertuples(index=False):
        for w in WINDOWS:
            base = dict(transition_id=a.transition_id, year=a.year, canonical_engineering_team=a.canonical_engineering_team,
                        target_car=a.target_car, target_driver=a.target_driver, window=str(w))
            if not a.target_team_in_primary_layer or pd.isna(a.t1) or pd.isna(a.t2):
                rows.append(dict(base, category="D", reason="target outside primary layer or endpoint untimed"))
                continue
            c = ctx[(ctx.transition_id == a.transition_id) & ctx[f"in_window_{w}"]]
            mv = ob.loc[c[c.obs_type == "MOVE"].obs_id] if len(c) else ob.iloc[0:0]
            lv = ob.loc[c[c.obs_type == "LEVEL"].obs_id] if len(c) else ob.iloc[0:0]
            mc = set(mv.car)
            imv = int(mv.frozen_independent.sum()) if len(mv) else 0
            if w == "INTERVAL":
                both = bool(len(mv) and (mv.t_prev <= a.t_mid).any() and (mv.t_curr >= a.t_mid).any())
            else:
                cm = c[c.obs_type == "MOVE"]
                both = bool(len(cm) and cm[f"near_t1_{w}"].any() and cm[f"near_t2_{w}"].any())
            if not len(mv) and not len(lv):
                cat, why = "D", "no in-window teammate observation"
            elif len(mc) >= 2 and imv >= 1 and both:
                cat, why = "A", "multi-car MOVE, >=1 frozen-independent MOVE, both-sides coverage"
            elif len(mc) >= 1 and (len(mc) >= 2 or imv >= 1):
                cat, why = "B", "MOVE context with multiple cars or independent MOVE, but A not met"
            else:
                cat, why = "C", "only LEVEL observations or single-car frozen-linked MOVEs"
            allt = pd.concat([mv.t_prev, mv.t_curr, lv.t_curr]) if len(mv) or len(lv) else pd.Series(dtype="datetime64[ns, UTC]")
            wx_tr = pd.concat([lv.track_c]).dropna()
            ints = sorted(zip(mv.t_prev, mv.t_curr, mv.car))
            overlap = any(i[2] != k[2] and i[0] < k[1] and k[0] < i[1] for n, i in enumerate(ints) for k in ints[n + 1:])
            rows.append(dict(base, category=cat, reason=why, n_level=len(lv), n_move=len(mv), unique_teammate_cars=len(set(mv.car) | set(lv.car)),
                             move_cars=len(mc), cars_with_repeats=len(mc), frozen_independent_moves=imv,
                             fully_independent_moves=int((mv.independence_label == "INDEPENDENT_OF_FROZEN_CORE").sum()) if len(mv) else 0,
                             frozen_overlapping_moves=int(mv.independence_label.isin(FROZEN_LINKED).sum()) if len(mv) else 0,
                             frozen_independent_levels=int((~lv.independence_label.isin(FROZEN_LINKED)).sum()) if len(lv) else 0,
                             dominated_by_frozen_reuse=bool(len(mv) and mv.independence_label.isin(FROZEN_LINKED).all()),
                             temporal_span_min=(allt.max() - allt.min()).total_seconds() / 60 if len(allt) >= 2 else 0.0,
                             track_span_c=(wx_tr.max() - wx_tr.min()) if len(wx_tr) >= 2 else np.nan,
                             both_sides_coverage=both,
                             obs_both_sides_of_midpoint=bool(len(allt) and (allt <= a.t_mid).any() and (allt >= a.t_mid).any()),
                             multi_car_overlapping_move_coverage=overlap))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ summaries (spec §6) and alignment (spec §7)
def summaries(anchors, ctx, obs, struct):
    ob = obs.set_index("obs_id")
    srows, arows = [], []
    for a in anchors.itertuples(index=False):
        for w in WINDOWS:
            st = struct[(struct.transition_id == a.transition_id) & (struct.window == str(w))].iloc[0]
            base = dict(transition_id=a.transition_id, year=a.year, canonical_engineering_team=a.canonical_engineering_team,
                        target_car=a.target_car, window=str(w), category=st.category, target_residual=a.target_residual,
                        target_delta_time_min=(a.t2 - a.t1).total_seconds() / 60 if pd.notna(a.t1) and pd.notna(a.t2) else np.nan)
            s = dict(base)
            c = ctx[(ctx.transition_id == a.transition_id)] if st.category != "D" else ctx.iloc[0:0]
            cw = c[c[f"in_window_{w}"]] if len(c) else c
            mv = ob.loc[cw[cw.obs_type == "MOVE"].obs_id].dropna(subset=["physics_adjusted_move"]) if len(cw) else ob.iloc[0:0]
            lv_ids = lambda mask: ob.loc[c[mask & (c.obs_type == "LEVEL")].obs_id] if len(c) else ob.iloc[0:0]
            if w != "INTERVAL" and len(c):
                s["S1_centered_near_t1"] = lv_ids(c[f"near_t1_{w}"]).speed_minus_car_mean.median()
                s["S2_centered_near_t2"] = lv_ids(c[f"near_t2_{w}"]).speed_minus_car_mean.median()
                n1, n2 = lv_ids(c[f"near_t1_{w}"]), lv_ids(c[f"near_t2_{w}"])
                common = sorted(set(n1.car) & set(n2.car), key=car_key)
                s["S8_common_car_centered_change"] = np.mean([n2[n2.car == k].speed_minus_car_mean.median() - n1[n1.car == k].speed_minus_car_mean.median()
                                                             for k in common]) if common else np.nan
                s["S8_common_cars"] = "|".join(common)
            if len(c):
                s["S3_centered_between"] = lv_ids(c.region.eq("BETWEEN_T1_T2")).speed_minus_car_mean.median()
            if len(mv):
                mid = mv.t_prev + (mv.t_curr - mv.t_prev) / 2
                k = (mid - a.t_mid).abs().idxmin()
                s.update(S4_nearest_move_raw=mv.loc[k, "previous_attempt_delta"], S4_nearest_move_adj=mv.loc[k, "physics_adjusted_move"],
                         S4_nearest_move_dt_min=mv.loc[k, "delta_time_min"], S4_nearest_move_car=mv.loc[k, "car"])
                s["S5_median_adj_move"] = mv.physics_adjusted_move.median()
                s["S5_largest_car_share"] = mv.car.value_counts(normalize=True).max()
                per_car = mv.groupby("car").physics_adjusted_move.median()
                s["S6_car_balanced_median_adj_move"] = per_car.median()
                s["S6_cars"] = len(per_car)
                s["move_dt_min_median"] = mv.delta_time_min.median()
                ind = mv[mv.frozen_independent]
                if len(ind):
                    s["S5_IND"] = ind.physics_adjusted_move.median()
                    s["S6_IND"] = ind.groupby("car").physics_adjusted_move.median().median()
                    s["S6_IND_cars"] = ind.car.nunique()
            srows.append(s)
            # alignment (spec §7)
            for variant, src in [("S6", mv), ("S6_IND", mv[mv.frozen_independent] if len(mv) else mv), ("S4", mv)]:
                row = dict(base, variant=variant)
                r = a.target_residual
                if st.category in ("C", "D") or not len(src):
                    row.update(label="INSUFFICIENT_TEAM_CONTEXT", contributing_cars=0)
                else:
                    if variant == "S4":
                        mc = pd.Series({s["S4_nearest_move_car"]: s["S4_nearest_move_adj"]})
                    else:
                        mc = src.groupby("car").physics_adjusted_move.median()
                    sg = np.sign(mc.values)
                    if (sg == np.sign(r)).all() and r != 0:
                        lab = "TEAM_CONTEXT_CONSISTENT"
                    elif (sg == -np.sign(r)).all() and r != 0:
                        lab = "TARGET_CAR_ISOLATED"
                    else:
                        lab = "MIXED_TEAM_CONTEXT"
                    S = float(np.median(mc.values))
                    row.update(label=lab, contributing_cars=len(mc), single_car_label=len(mc) == 1, team_context_value=S,
                               abs_residual=abs(r), abs_team_context=abs(S), ratio_S_over_r=S / r if abs(r) >= 0.001 else np.nan,
                               abs_diff=abs(S - r), sign_agree=bool(np.sign(S) == np.sign(r)))
                arows.append(row)
    return pd.DataFrame(srows), pd.DataFrame(arows)


# ------------------------------------------------------------------ placebo (spec §8)
def placebo(anchors, struct, moves):
    rows = []
    prim = struct[(struct.window == str(PRIMARY_W)) & struct.category.isin(["A", "B"])]
    for a in anchors[anchors.transition_id.isin(prim.transition_id)].itertuples(index=False):
        lo_, hi_ = span(a, PRIMARY_W)
        yr = moves[(moves.year == a.year) & (moves.t_prev >= lo_) & (moves.t_curr <= hi_) & (moves.car != a.target_car)].dropna(subset=["physics_adjusted_move"])
        teams = {}
        for team, g in yr.groupby("canonical_engineering_team"):
            for scope, gg in [("ALL", g), ("IND", g[g.frozen_independent])]:
                if len(gg):
                    teams[(team, scope)] = gg.groupby("car").physics_adjusted_move.median()
        for scope in ["ALL", "IND"]:
            same = teams.get((a.canonical_engineering_team, scope))
            others = {t: v for (t, sc), v in teams.items() if sc == scope and t != a.canonical_engineering_team}
            pooled = pd.concat(list(others.values())) if others else pd.Series(dtype=float)
            allS = {t: float(v.median()) for t, v in others.items()}
            if same is not None:
                allS[a.canonical_engineering_team] = float(same.median())
            rank = (sorted(allS, key=lambda t: abs(allS[t] - a.target_residual)).index(a.canonical_engineering_team) + 1) if same is not None else np.nan
            rows.append(dict(transition_id=a.transition_id, year=a.year, canonical_engineering_team=a.canonical_engineering_team, scope=scope,
                             target_residual=a.target_residual, same_team_S6=float(same.median()) if same is not None else np.nan,
                             same_team_cars=len(same) if same is not None else 0,
                             unrelated_pooled_S6=float(pooled.median()) if len(pooled) else np.nan, unrelated_teams=len(others),
                             unrelated_cars=len(pooled), same_team_rank_by_abs_diff=rank, teams_ranked=len(allS),
                             identifiable=same is not None and len(pooled) > 0,
                             per_other_team_S6="; ".join(f"{t}={v:+.3f}" for t, v in sorted(allS.items()) if t != a.canonical_engineering_team)))
    cols = ["transition_id", "year", "canonical_engineering_team", "scope", "target_residual", "same_team_S6", "same_team_cars",
            "unrelated_pooled_S6", "unrelated_teams", "unrelated_cars", "same_team_rank_by_abs_diff", "teams_ranked", "identifiable", "per_other_team_S6"]
    return pd.DataFrame(rows, columns=cols)


# ------------------------------------------------------------------ permutation (spec §9)
def permutation(anchors, moves, levels):
    elig = anchors[anchors.target_team_in_primary_layer & anchors.t1.notna() & anchors.t2.notna()].reset_index(drop=True)
    cars = levels[levels.year.isin(ERA_B)][["year", "car", "canonical_engineering_team"]].drop_duplicates()
    # per transition x car: car median of in-window (±30) physics-adjusted MOVEs
    med = {}
    for a in elig.itertuples(index=False):
        lo_, hi_ = span(a, PRIMARY_W)
        m = moves[(moves.year == a.year) & (moves.t_prev >= lo_) & (moves.t_curr <= hi_) & (moves.car != a.target_car)].dropna(subset=["physics_adjusted_move"])
        med[a.transition_id] = m.groupby("car").physics_adjusted_move.median().to_dict()

    def stats(team_of):
        S, R = [], []
        for a in elig.itertuples(index=False):
            tm = team_of[a.year].get(a.target_car)
            vals = [v for c, v in med[a.transition_id].items() if team_of[a.year].get(c) == tm]
            if vals:
                S.append(np.median(vals)); R.append(a.target_residual)
        S, R = np.array(S), np.array(R)
        if len(S) == 0:
            return np.nan, np.nan, 0
        return float(np.mean(np.sign(S) == np.sign(R))), float(np.median(np.abs(S - R))), len(S)

    real = {y: dict(zip(g.car, g.canonical_engineering_team)) for y, g in cars.groupby("year")}
    obs = stats(real)
    rng = np.random.default_rng(SEED)
    draws = []
    for _ in range(NPERM):
        sh = {}
        for y, g in cars.groupby("year"):
            labels = np.array(g.canonical_engineering_team.tolist(), dtype=object)
            rng.shuffle(labels)
            sh[y] = dict(zip(g.car, labels))
        draws.append(stats(sh))
    d = pd.DataFrame(draws, columns=["T1_sign_agree", "T2_median_abs_diff", "T3_n_defined"])
    meaningful = obs[2] >= 5
    pct = lambda col, v, lower_better=False: float((d[col] <= v).mean() * 100) if not lower_better else float((d[col] >= v).mean() * 100)
    summ = pd.DataFrame([
        dict(statistic="T1_sign_agree", observed=obs[0], perm_median=d.T1_sign_agree.median(), perm_p05=d.T1_sign_agree.quantile(.05),
             perm_p95=d.T1_sign_agree.quantile(.95), observed_percentile=pct("T1_sign_agree", obs[0]), meaningful=meaningful,
             note="percentile = % of shuffles with T1 <= observed (higher = stronger same-team agreement)"),
        dict(statistic="T2_median_abs_diff", observed=obs[1], perm_median=d.T2_median_abs_diff.median(), perm_p05=d.T2_median_abs_diff.quantile(.05),
             perm_p95=d.T2_median_abs_diff.quantile(.95), observed_percentile=pct("T2_median_abs_diff", obs[1], lower_better=True), meaningful=meaningful,
             note="percentile = % of shuffles with T2 >= observed (higher = same-team closer than shuffled)"),
        dict(statistic="T3_n_defined", observed=obs[2], perm_median=d.T3_n_defined.median(), perm_p05=d.T3_n_defined.quantile(.05),
             perm_p95=d.T3_n_defined.quantile(.95), observed_percentile=np.nan, meaningful=meaningful, note="transitions with defined S6"),
    ])
    summ["n_permutations"], summ["seed"], summ["eligible_transitions"] = NPERM, SEED, len(elig)
    return summ, d


# ------------------------------------------------------------------ feasibility case (spec §12)
def feasibility_case(struct, align, plc, perm):
    p = struct[struct.window == str(PRIMARY_W)]
    nA = int((p.category == "A").sum())
    with_move = p[p.n_move.fillna(0) > 0]
    dom = int(with_move.dominated_by_frozen_reuse.sum())
    crit = []
    c_hit = nA < 5 or (len(with_move) and dom > len(with_move) / 2)
    crit.append(dict(case="C", satisfied=bool(c_hit), detail=f"category A at ±30 = {nA}; dominated by frozen reuse = {dom}/{len(with_move)}"))
    pa = plc[(plc.scope == "ALL") & plc.identifiable]
    if len(pa):
        same_rate = float((np.sign(pa.same_team_S6) == np.sign(pa.target_residual)).mean())
        unrel_rate = float((np.sign(pa.unrelated_pooled_S6) == np.sign(pa.target_residual)).mean())
        same_md = float((pa.same_team_S6 - pa.target_residual).abs().median())
        unrel_md = float((pa.unrelated_pooled_S6 - pa.target_residual).abs().median())
        d_hit = (not c_hit) and (same_rate <= unrel_rate or same_md >= unrel_md)
        det = f"n={len(pa)}; sign agree same {same_rate:.2f} vs unrelated {unrel_rate:.2f}; median|S-r| same {same_md:.3f} vs unrelated {unrel_md:.3f}"
    else:
        d_hit, det = False, "placebo not identifiable (no transition with both same-team and unrelated context)"
    crit.append(dict(case="D", satisfied=bool(d_hit), detail=det))
    t1p = perm[perm.statistic == "T1_sign_agree"].observed_percentile.iloc[0]
    b_hit = (not c_hit) and (not d_hit) and (nA < 10 or not (t1p >= 90))
    crit.append(dict(case="B", satisfied=bool(b_hit), detail=f"category A = {nA}; permutation T1 percentile = {t1p:.1f}"))
    crit.append(dict(case="A", satisfied=bool(not (c_hit or d_hit or b_hit)), detail="all A conditions met" if not (c_hit or d_hit or b_hit) else "not met"))
    head = next((c["case"] for c in sorted(crit, key=lambda c: "CDBA".index(c["case"])) if c["satisfied"]), "NONE")
    out = pd.DataFrame(crit)
    out["headline_by_precedence_C_D_B_A"] = head
    return out


# ------------------------------------------------------------------ 2025 extension (spec §11)
def extension_2025(j):
    empty = set()
    mv = build_moves(j, [2025], None, empty, {}, physics=False)
    lv = build_levels(j, [2025], empty)
    anchors = mv.rename(columns={"car": "target_car", "driver": "target_driver", "t_prev": "t1", "t_curr": "t2"})
    anchors = anchors.assign(transition_id="2025|" + anchors.attempt_prev + "->" + anchors.attempt_curr, target_residual=anchors.previous_attempt_delta,
                             target_team_in_primary_layer=True, t_mid=anchors.t1 + (anchors.t2 - anchors.t1) / 2)
    anchor_pairs = set(zip(mv.attempt_prev, mv.attempt_curr))
    mv["is_frozen_pair"] = False
    mv["touches_frozen_endpoint"] = False
    obs = pd.concat([mv, lv], ignore_index=True)
    obs["physics_adjusted_move"] = obs.previous_attempt_delta
    obs["base_label"] = [base_label(o) for o in obs.itertuples(index=False)]
    ctx = context_rows(anchors, mv.assign(physics_adjusted_move=mv.previous_attempt_delta), lv)
    reuse = ctx[ctx[f"in_window_{PRIMARY_W}"]].groupby("obs_id").transition_id.nunique()
    obs["reuse_count_pw"] = obs.obs_id.map(reuse).fillna(0).astype(int)
    # every 2025 teammate MOVE is itself another 2025 anchor -> reciprocal by construction
    obs["independence_label"] = [("RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE" if o.obs_type == "MOVE" and (o.attempt_prev, o.attempt_curr) in anchor_pairs
                                  else o.base_label if isinstance(o.base_label, str) else "OTHER_DEPENDENT_REUSE" if o.reuse_count_pw >= 2 else "INDEPENDENT_OF_FROZEN_CORE")
                                 for o in obs.itertuples(index=False)]
    obs["frozen_independent"] = ~obs.independence_label.isin(FROZEN_LINKED)
    st = structure(anchors, ctx, obs)
    _, al = summaries(anchors, ctx, obs, st)
    st["scope"], al["scope"] = "2025_EXTENSION_RAW_DELTAS_NOT_POOLED", "2025_EXTENSION_RAW_DELTAS_NOT_POOLED"
    return st, al, anchors


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    anchors, j, beta, frozen_ep, frozen_pairs = load()
    moves = build_moves(j, ERA_B, beta, frozen_ep, frozen_pairs)
    levels = build_levels(j, ERA_B, frozen_ep)
    obs = pd.concat([moves, levels], ignore_index=True)
    obs["base_label"] = [base_label(o) for o in obs.itertuples(index=False)]
    ctx = context_rows(anchors, moves, levels)
    reuse = ctx[ctx[f"in_window_{PRIMARY_W}"]].groupby("obs_id").transition_id.nunique()
    reuse_any = ctx.groupby("obs_id").transition_id.nunique()
    obs["reuse_count_primary_window"] = obs.obs_id.map(reuse).fillna(0).astype(int)
    obs["context_of_n_transitions_any"] = obs.obs_id.map(reuse_any).fillna(0).astype(int)
    # base_label is None/NaN when not frozen-linked or unknown (pd.concat turns None into NaN, which is truthy)
    obs["independence_label"] = [o.base_label if isinstance(o.base_label, str) else
                                 ("OTHER_DEPENDENT_REUSE" if o.reuse_count_primary_window >= 2 else "INDEPENDENT_OF_FROZEN_CORE")
                                 for o in obs.itertuples(index=False)]
    obs["frozen_independent"] = ~obs.independence_label.isin(FROZEN_LINKED)
    obs["used_elsewhere_in_analysis"] = obs.context_of_n_transitions_any >= 2
    moves = moves.merge(obs[["obs_id", "independence_label", "frozen_independent"]], on="obs_id")

    struct = structure(anchors, ctx, obs)
    summ, align = summaries(anchors, ctx, obs, struct)
    plc = placebo(anchors, struct, moves)
    perm, perm_draws = permutation(anchors, moves, levels)
    case = feasibility_case(struct, align, plc, perm)

    # team_context_observations: one row per transition x observation
    tco = ctx.merge(obs.drop(columns=["base_label"]), on=["obs_id", "obs_type"], how="left")
    tco.to_csv(OUT / "team_context_observations.csv", index=False)
    obs.drop(columns=["base_label"]).to_csv(OUT / "evidence_independence_audit.csv", index=False)
    struct.to_csv(OUT / "identifiability_by_transition.csv", index=False)
    summ.to_csv(OUT / "team_context_summary.csv", index=False)
    align.to_csv(OUT / "residual_context_alignment.csv", index=False)
    plc.to_csv(OUT / "unrelated_team_placebo.csv", index=False)
    perm.to_csv(OUT / "permutation_diagnostic.csv", index=False)
    perm_draws.to_csv(OUT / "permutation_draws.csv", index=False)
    case.to_csv(OUT / "feasibility_case_evaluation.csv", index=False)
    # transition-level table: anchors + primary-window structure + primary alignment
    pw = struct[struct.window == str(PRIMARY_W)].drop(columns=["year", "canonical_engineering_team", "target_car", "target_driver", "window"])
    pa = align[(align.window == str(PRIMARY_W)) & (align.variant == "S6")][["transition_id", "label", "contributing_cars", "team_context_value"]]
    pi = align[(align.window == str(PRIMARY_W)) & (align.variant == "S6_IND")][["transition_id", "label"]].rename(columns={"label": "label_IND"})
    tt = anchors.merge(pw, on="transition_id", how="left").merge(pa, on="transition_id", how="left").merge(pi, on="transition_id", how="left")
    tt["abs_target_residual_rank"] = tt.target_residual.abs().rank(ascending=False, method="first").astype(int)
    tt.to_csv(OUT / "transition_team_context.csv", index=False)
    big = tt.nsmallest(8, "abs_target_residual_rank")
    big.to_csv(OUT / "large_residual_case_summary.csv", index=False)
    st25, al25, anch25 = extension_2025(j)
    st25.to_csv(OUT / "extension_2025_identifiability.csv", index=False)
    al25.to_csv(OUT / "extension_2025_alignment.csv", index=False)
    print(struct[struct.window == str(PRIMARY_W)].category.value_counts().to_dict())
    print(case.to_string())


if __name__ == "__main__":
    main()
