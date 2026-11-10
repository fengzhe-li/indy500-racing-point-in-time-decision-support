"""V4 Phase 4F: empirical performance-control hierarchy (implements phase4f_prespecified_design.md).

Lap data = Timing71 archived recordings of the INDYCAR live timing feed (third-party). Official INDYCAR
session-detail records are used only as a cross-check. Phase 4E is imported read-only (pure functions only).
Descriptive only: no regression / variance / latent model, no weather coefficients, no team ranking.
"""
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
P4E = V4 / "output" / "phase4e"
OUT = V4 / "output" / "phase4f"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4e_audit as A  # noqa: E402  (read-only use of pure functions)

SOURCE_LABEL = "TIMING71_ARCHIVED_LIVE_FEED (third-party recording of INDYCAR live timing)"
OFFICIAL_LABEL = "INDYCAR_OFFICIAL_SESSION_DETAILS"
WIDTHS = [1, 2, 5, 10]
SEED, B = 20261001, 2000
LINKS = [("PRACTICE", "FAST_FRIDAY"), ("FAST_FRIDAY", "QUALIFYING_DAY1"), ("QUALIFYING_DAY1", "POST_QUALIFYING_PRACTICE"),
         ("QUALIFYING_DAY1", "CARB_DAY"), ("PRACTICE", "CARB_DAY"), ("POST_QUALIFYING_PRACTICE", "CARB_DAY")]


# ------------------------------------------------------------------ population (spec §1)
def population():
    e = pd.read_csv(P4E / "evidence_hierarchy_feasibility.csv")
    ab = e[e.quality_tier.isin(["A", "B"]) & e.hier_all_three & (e.normalized_category != "RACE")]
    prim = ab[ab.era == "ERA_B_REFERENCE"].assign(role="PRIMARY")
    sec = ab[ab.era == "ERA_C_HYBRID"].assign(role="ERA_C_SECONDARY_NOT_DESIGN1_FEASIBLE")
    race = e[(e.normalized_category == "RACE") & (e.timestamp_basis == "OBSERVED_LAP_TIMESTAMPS")].assign(role="RACE_APPENDIX_STRUCTURAL_ONLY")
    return pd.concat([prim, sec, race], ignore_index=True)[["session_key", "year", "era", "normalized_category", "quality_tier", "official_segments", "role"]]


# ------------------------------------------------------------------ laps (Phase 4E functions, no writes)
def laps_for(keys):
    reg = A.registry()
    sessions, off_recs = A.official_sessions()
    files, laps = A.build_laps(reg, sessions)
    fmap = A.map_files(files, sessions)
    laps = laps.merge(fmap, on="source_id", how="left")
    laps = laps[laps.session_key.isin(keys)].copy()
    jc = {(y, c): A.join_car(reg, y, c, g.driver.mode().iloc[0] if g.driver.notna().any() else "") for (y, c), g in laps.groupby(["year", "car"])}
    J = pd.DataFrame([dict(year=y, car=c, **v) for (y, c), v in jc.items()])
    laps = laps.merge(J, on=["year", "car"], how="left")
    laps["car_id"] = laps.year.astype(str) + "|" + laps.car.astype(str)
    laps["_k"] = laps.ts.round(0).astype("Int64").astype(str) + "|" + laps.laptime.round(4).astype(str)
    laps = laps.sort_values("source_id").drop_duplicates(["session_key", "car", "_k"])
    lo, hi = A.AT_SPEED
    laps["broad"] = laps.flag.astype(str).str.lower().isin(["green", "none"]) & ~laps.is_out_lap & ~laps.is_in_lap & laps.laptime.between(lo, hi)
    # stint endTime (pit entry) from the retrieved modern Timing71 files
    ends = {}
    man = pd.read_csv(V4 / "evidence/phase4e/retrieval_manifest.csv")
    for r in man[man.source_id.isin(laps.source_id.unique())].itertuples(index=False):
        d = json.load(open(REPO / r.local_path))
        cars = d["cars"]["cars"] if "cars" in d.get("cars", {}) else d.get("cars", {})
        for car, c in cars.items():
            for si, st in enumerate(c.get("stints", [])):
                ends[(r.source_id, car, si)] = st.get("endTime") is not None
    laps["stint_has_end"] = [ends.get((s, c, i), False) for s, c, i in zip(laps.source_id, laps.car, laps.stint)]
    laps = laps.sort_values(["session_key", "car", "stint", "lap_in_stint"]).reset_index(drop=True)
    g = laps.groupby(["session_key", "car", "stint"])
    prev_flag = g.flag.shift(1)
    prev_ts = g.ts.shift(1)
    coherent = ((laps.ts - prev_ts - laps.laptime).abs() <= 2.0)
    last = laps.lap_in_stint == laps.laps_in_stint - 1
    penult = laps.lap_in_stint == laps.laps_in_stint - 2
    laps["comparable"] = (laps.broad & (laps.flag.astype(str).str.lower() == "green") & (prev_flag.astype(str).str.lower() == "green")
                          & (laps.lap_in_stint != 1) & ~(laps.stint_has_end & (last | penult)) & coherent.fillna(False))
    laps["speed_mph"] = 2.5 * 3600 / laps.laptime
    laps["evidence_source"] = SOURCE_LABEL
    return reg, sessions, off_recs, laps


# ------------------------------------------------------------------ car-blocks and comparisons (spec §4-§7)
def car_blocks(L, layer, width, min_laps=1, drop_team=None):
    x = L[L[layer] & (L.join_status == "MATCHED") & ~L.technical_partnership_only.fillna(False).astype(bool)].copy()
    if drop_team:
        x = x[x.canonical_engineering_team != drop_team]
    x["block"] = np.floor(x.ts / (width * 60)).astype(int)
    cb = x.groupby(["session_key", "block", "car_id"]).agg(
        year=("year", "first"), car=("registry_car", "first"), team=("canonical_engineering_team", "first"), primary_layer=("primary_layer", "first"),
        v=("speed_mph", "median"), n_laps=("speed_mph", "size"), v_min=("speed_mph", "min"), v_max=("speed_mph", "max"),
        t=("ts", "median"), stint_positions=("lap_in_stint", lambda s: "|".join(map(str, sorted(s)))),
        pit_adjacent_laps=("comparable", lambda s: int((~s).sum()) if layer == "broad" else 0)).reset_index()
    cb["spread"] = cb.v_max - cb.v_min
    cb = cb[cb.n_laps >= min_laps]
    cb["team_key"] = np.where(cb.primary_layer.fillna(False).astype(bool), cb.team, "SOLO:" + cb.car_id)
    return cb


def comparisons(cb):
    rows, blk = [], []
    # SAME_CAR: adjacent blocks
    nxt = cb[["session_key", "block", "car_id", "v", "t"]].assign(block=lambda d: d.block - 1)
    sc = cb.merge(nxt, on=["session_key", "block", "car_id"], suffixes=("", "_b"))
    for r in sc.itertuples(index=False):
        rows.append(("SAME_CAR", r.session_key, r.year, r.block, r.car_id, r.car_id, r.team, r.team, abs(r.v - r.v_b), abs(r.t_b - r.t) / 60, 1.0))
    for (sk, b), g in cb.groupby(["session_key", "block"]):
        g = g.reset_index(drop=True)
        teams = g.team_key.values
        t, v, cid, tm = g.t.values, g.v.values, g.car_id.values, g.team.values
        # SAME_TEAM unordered pairs, weight 1/(pairs in block-team)
        for tk, gg in g[~g.team_key.str.startswith("SOLO:")].groupby("team_key"):
            pr = list(itertools.combinations(gg.index, 2))
            for i, j in pr:
                rows.append(("SAME_TEAM", sk, g.year.iloc[0], b, cid[i], cid[j], tm[i], tm[j], abs(v[i] - v[j]), abs(t[i] - t[j]) / 60, 1.0 / len(pr)))
        # target-matched teammate vs different-team control
        dst, ddt = [], []
        for i in range(len(g)):
            if teams[i].startswith("SOLO:"):
                continue
            mates = [k for k in range(len(g)) if k != i and teams[k] == teams[i]]
            if not mates:
                continue
            others = [k for k in range(len(g)) if tm[k] != tm[i]]
            if not others:
                continue
            key = lambda k: (abs(t[k] - t[i]), A.car_key if False else (int(str(g.car.iloc[k])) if str(g.car.iloc[k]).isdigit() else 999), str(g.car.iloc[k]))
            m = min(mates, key=key)
            o = min(others, key=key)
            rows.append(("TEAMMATE_OF_TARGET", sk, g.year.iloc[0], b, cid[i], cid[m], tm[i], tm[m], abs(v[i] - v[m]), abs(t[i] - t[m]) / 60, np.nan))
            rows.append(("DIFF_TEAM", sk, g.year.iloc[0], b, cid[i], cid[o], tm[i], tm[o], abs(v[i] - v[o]), abs(t[i] - t[o]) / 60, 1.0))
            dst.append(abs(v[i] - v[m]))
            ddt.append(abs(v[i] - v[o]))
        if dst:
            # team-balanced different-team sensitivity: equal weight per team pair
            tp = []
            ut = sorted(set(tm))
            for a_, b_ in itertools.combinations(ut, 2):
                ia, ib = np.where(tm == a_)[0], np.where(tm == b_)[0]
                tp.append(np.median([abs(v[x_] - v[y_]) for x_ in ia for y_ in ib]))
            st_pairs = [abs(v[x_] - v[y_]) for tk in set(teams) if not tk.startswith("SOLO:") for x_, y_ in itertools.combinations(np.where(teams == tk)[0], 2)]
            blk.append(dict(session_key=sk, year=g.year.iloc[0], block=b, targets=len(dst), cars=len(g), teams=len(set(tm)),
                            teams_with_2plus=int(sum(1 for tk in set(teams) if not tk.startswith("SOLO:") and (teams == tk).sum() >= 2)),
                            median_D_same_team_target=float(np.median(dst)), median_D_diff_team_target=float(np.median(ddt)),
                            delta_block=float(np.median(ddt) - np.median(dst)),
                            team_balanced_D_diff=float(np.median(tp)) if tp else np.nan, median_D_same_team_pairs=float(np.median(st_pairs)),
                            delta_block_team_balanced=(float(np.median(tp)) - float(np.median(st_pairs))) if tp else np.nan))
    cols = ["class", "session_key", "year", "block", "car_a", "car_b", "team_a", "team_b", "D_mph", "time_sep_min", "weight"]
    return pd.DataFrame(rows, columns=cols), pd.DataFrame(blk)


def adjacent_fairness(cb):
    """Spec §8(i): all three classes across adjacent blocks (k -> k+1)."""
    rows = []
    for sk, g in cb.groupby("session_key"):
        byb = {b: gg.reset_index(drop=True) for b, gg in g.groupby("block")}
        for b, gk in byb.items():
            g1 = byb.get(b + 1)
            if g1 is None:
                continue
            for r in gk.itertuples(index=False):
                if r.team_key.startswith("SOLO:"):
                    continue
                same = g1[g1.car_id == r.car_id]
                mates = g1[(g1.team_key == r.team_key) & (g1.car_id != r.car_id)]
                others = g1[g1.team != r.team]
                if same.empty or mates.empty or others.empty:
                    continue
                m = mates.iloc[(mates.t - r.t).abs().argsort().iloc[0]]
                o = others.iloc[(others.t - r.t).abs().argsort().iloc[0]]
                s = same.iloc[0]
                for cls, x in [("SAME_CAR_ADJ", s), ("SAME_TEAM_ADJ", m), ("DIFF_TEAM_ADJ", o)]:
                    rows.append(dict(class_=cls, session_key=sk, year=r.year, block=b, car_a=r.car_id, car_b=x.car_id, D_mph=abs(r.v - x.v), time_sep_min=abs(x.t - r.t) / 60))
    return pd.DataFrame(rows).rename(columns={"class_": "class"})


def wmedian(x, w):
    x, w = np.asarray(x, float), np.asarray(w, float)
    if len(x) == 0:
        return np.nan
    o = np.argsort(x)
    cw = np.cumsum(w[o])
    return float(x[o][np.searchsorted(cw, cw[-1] / 2)])


def session_balanced(blk, col="delta_block"):
    s = blk.groupby("session_key")[col].median().dropna()
    return (float(s.median()) if len(s) else np.nan), s


def boot(sess_vals):
    rng = np.random.default_rng(SEED)
    v = sess_vals.values
    if len(v) < 2:
        return np.nan, np.nan
    d = [np.median(rng.choice(v, len(v), replace=True)) for _ in range(B)]
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def dist_summary(cmp, scope):
    out = []
    for cls, g in cmp[cmp["class"].isin(["SAME_CAR", "SAME_TEAM", "DIFF_TEAM"])].groupby("class"):
        w = g.weight.values
        blockmed = g.groupby(["session_key", "block"]).D_mph.median()
        sessmed = g.groupby("session_key").apply(lambda h: wmedian(h.D_mph, h.weight), include_groups=False)
        out.append(dict(scope=scope, **{"class": cls}, n_raw_comparisons=len(g), n_unique_cars=len(set(g.car_a) | set(g.car_b)),
                        n_unique_teams=len(set(g.team_a) | set(g.team_b)), n_unique_sessions=g.session_key.nunique(),
                        n_unique_blocks=g[["session_key", "block"]].drop_duplicates().shape[0], weighted_median=wmedian(g.D_mph, w),
                        mean=float(np.average(g.D_mph, weights=w)), sd=float(g.D_mph.std()), p10=g.D_mph.quantile(.1), p25=g.D_mph.quantile(.25),
                        median_unweighted=g.D_mph.median(), p75=g.D_mph.quantile(.75), p90=g.D_mph.quantile(.9),
                        iqr=g.D_mph.quantile(.75) - g.D_mph.quantile(.25), block_balanced_median=float(blockmed.median()),
                        session_balanced_median=float(sessmed.median()), time_sep_median_min=g.time_sep_min.median()))
    return pd.DataFrame(out)


def run(L, keys, layer="comparable", width=5, min_laps=1, drop_team=None):
    cb = car_blocks(L[L.session_key.isin(keys)], layer, width, min_laps, drop_team)
    cmp, blk = comparisons(cb)
    return cb, cmp, blk


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pop = population()
    reg, sessions, off_recs, L = laps_for(set(pop.session_key))
    L = L.merge(pop[["session_key", "role", "normalized_category", "era"]], on="session_key", how="left", suffixes=("", "_pop"))
    prim = list(pop[pop.role == "PRIMARY"].session_key)
    sec = list(pop[pop.role.str.startswith("ERA_C")].session_key)
    race = list(pop[pop.role.str.startswith("RACE")].session_key)
    cat = dict(zip(pop.session_key, pop.normalized_category))
    res = {}

    # analysis population
    ap = []
    for r in pop.itertuples(index=False):
        g = L[L.session_key == r.session_key]
        ap.append(dict(**r._asdict(), evidence_source=SOURCE_LABEL, raw_laps=len(g), broad_laps=int(g.broad.sum()), comparable_laps=int(g.comparable.sum()),
                       cars=g.car_id.nunique(), teams=g.canonical_engineering_team.nunique(),
                       technical_partnership_cars=int(g[g.technical_partnership_only.fillna(False).astype(bool)].car_id.nunique()),
                       unmatched_cars=int(g[g.join_status != "MATCHED"].car_id.nunique())))
    pd.DataFrame(ap).to_csv(OUT / "analysis_population.csv", index=False)

    # ---- car-block validity check (addendum 3) + car-block observations (5 min, both layers, primary + secondary)
    cbs = []
    for role, keys in [("PRIMARY", prim), ("ERA_C_SECONDARY", sec)]:
        for layer in ["broad", "comparable"]:
            cb = car_blocks(L[L.session_key.isin(keys)], layer, 5)
            cbs.append(cb.assign(role=role, layer=layer, width_min=5, category=cb.session_key.map(cat), wide_spread_flag=cb.spread > 3.0,
                                 evidence_source=SOURCE_LABEL))
    CB = pd.concat(cbs, ignore_index=True)
    CB.to_csv(OUT / "car_block_observations.csv", index=False)
    validity = CB.groupby(["role", "layer", "category"]).agg(car_blocks=("v", "size"), laps_median=("n_laps", "median"), laps_p90=("n_laps", lambda s: s.quantile(.9)),
                                                             single_lap_share=("n_laps", lambda s: (s == 1).mean()), spread_median=("spread", "median"),
                                                             spread_p90=("spread", lambda s: s.quantile(.9)), wide_spread_share=("wide_spread_flag", "mean"),
                                                             with_pit_adjacent_laps_share=("pit_adjacent_laps", lambda s: (s > 0).mean())).reset_index()
    validity.to_csv(OUT / "car_block_validity.csv", index=False)

    # ---- primary + sensitivities
    allcmp, allblk, sb_rows = [], [], []
    for role, keys in [("PRIMARY", prim), ("ERA_C_SECONDARY", sec)]:
        for layer in ["comparable", "broad"]:
            for width in WIDTHS:
                for min_laps in ([1, 2] if width == 5 else [1]):
                    cb, cmp, blk = run(L, keys, layer, width, min_laps)
                    tag = dict(role=role, layer=layer, width_min=width, min_laps=min_laps)
                    if width == 5 and min_laps == 1:
                        allcmp.append(cmp.assign(**tag))
                        allblk.append(blk.assign(**tag))
                    med, sv = session_balanced(blk)
                    lo, hi = boot(sv)
                    medtb, svtb = session_balanced(blk, "delta_block_team_balanced")
                    ds = dist_summary(cmp, "x").set_index("class")
                    sb_rows.append(dict(**tag, sessions_with_eligible_blocks=len(sv), eligible_blocks=len(blk),
                                        session_balanced_delta=med, boot_session_lo=lo, boot_session_hi=hi,
                                        share_sessions_positive=float((sv > 0).mean()) if len(sv) else np.nan,
                                        session_balanced_delta_team_balanced=medtb,
                                        sb_D_same_car=ds.session_balanced_median.get("SAME_CAR", np.nan), sb_D_same_team=ds.session_balanced_median.get("SAME_TEAM", np.nan),
                                        sb_D_diff_team=ds.session_balanced_median.get("DIFF_TEAM", np.nan)))
    CMP = pd.concat(allcmp, ignore_index=True)
    BLK = pd.concat(allblk, ignore_index=True)
    CMP.to_csv(OUT / "comparison_pairs.csv", index=False)
    BLK.assign(category=BLK.session_key.map(cat)).to_csv(OUT / "block_level_contrasts.csv", index=False)
    SB = pd.DataFrame(sb_rows)
    # per-session results (primary tag) + session-balanced table
    ps = []
    for (role, layer), g in BLK.groupby(["role", "layer"]):
        for sk, h in g.groupby("session_key"):
            c = CMP[(CMP.role == role) & (CMP.layer == layer) & (CMP.session_key == sk)]
            dsum = {cls: wmedian(cc.D_mph, cc.weight) for cls, cc in c[c["class"].isin(["SAME_CAR", "SAME_TEAM", "DIFF_TEAM"])].groupby("class")}
            ps.append(dict(level="SESSION", role=role, layer=layer, width_min=5, session_key=sk, year=h.year.iloc[0], category=cat[sk], eligible_blocks=len(h),
                           session_median_delta=h.delta_block.median(), share_blocks_positive=float((h.delta_block > 0).mean()),
                           D_same_car=dsum.get("SAME_CAR"), D_same_team=dsum.get("SAME_TEAM"), D_diff_team=dsum.get("DIFF_TEAM")))
    PS = pd.DataFrame(ps)
    pd.concat([PS, SB.assign(level="SESSION_BALANCED")], ignore_index=True).to_csv(OUT / "session_balanced_results.csv", index=False)

    # distribution summary (primary tag, 5 min)
    ds = []
    for (role, layer), g in CMP.groupby(["role", "layer"]):
        ds.append(dist_summary(g, f"{role}|{layer}|5min"))
    DS = pd.concat(ds, ignore_index=True)
    DS.to_csv(OUT / "comparison_distribution_summary.csv", index=False)

    # year / session-type sensitivity (primary role, both layers)
    yr, ct = [], []
    for layer in ["comparable", "broad"]:
        pb = BLK[(BLK.role == "PRIMARY") & (BLK.layer == layer)]
        for y, g in pb.groupby("year"):
            m, sv = session_balanced(g)
            yr.append(dict(role="PRIMARY", layer=layer, year=y, sessions=len(sv), session_balanced_delta=m, share_sessions_positive=float((sv > 0).mean()), blocks=len(g)))
        for c, g in pb.assign(category=pb.session_key.map(cat)).groupby("category"):
            m, sv = session_balanced(g)
            ct.append(dict(role="PRIMARY", layer=layer, category=c, sessions=len(sv), session_balanced_delta=m, share_sessions_positive=float((sv > 0).mean()),
                           blocks=len(g), pooled_block_median_delta=g.delta_block.median()))
        sb = BLK[(BLK.role.str.startswith("ERA_C")) & (BLK.layer == layer)]
        m, sv = session_balanced(sb)
        yr.append(dict(role="ERA_C_SECONDARY", layer=layer, year=2025, sessions=len(sv), session_balanced_delta=m, share_sessions_positive=float((sv > 0).mean()), blocks=len(sb)))
    pd.DataFrame(yr).to_csv(OUT / "year_sensitivity.csv", index=False)
    pd.DataFrame(ct).to_csv(OUT / "session_type_sensitivity.csv", index=False)

    # leave-one-team-out (primary tag)
    teams = sorted(L[L.session_key.isin(prim) & L.primary_layer.fillna(False).astype(bool)].canonical_engineering_team.dropna().unique())
    lt = []
    for tname in teams:
        _, _, blk = run(L, prim, "comparable", 5, 1, drop_team=tname)
        m, sv = session_balanced(blk)
        lt.append(dict(dropped_team=tname, sessions=len(sv), blocks=len(blk), session_balanced_delta=m, share_sessions_positive=float((sv > 0).mean())))
    LT = pd.DataFrame(lt)
    LT.to_csv(OUT / "leave_one_team_out.csv", index=False)

    # same-car fairness (primary)
    fair = []
    for layer in ["comparable", "broad"]:
        cb = car_blocks(L[L.session_key.isin(prim)], layer, 5)
        adj = adjacent_fairness(cb)
        for cls, g in adj.groupby("class"):
            sm = g.groupby("session_key").D_mph.median()
            fair.append(dict(construction="ADJACENT_BLOCK_ALL_CLASSES", layer=layer, **{"class": cls}, n=len(g), sessions=g.session_key.nunique(),
                             session_balanced_median=float(sm.median()), pooled_median=g.D_mph.median(), time_sep_median_min=g.time_sep_min.median()))
        c = CMP[(CMP.role == "PRIMARY") & (CMP.layer == layer)]
        sc = c[c["class"] == "SAME_CAR"]
        bins = np.arange(0, 11, 1)
        h_sc = np.histogram(sc.time_sep_min.clip(upper=9.999), bins=bins)[0] / max(len(sc), 1)
        for cls in ["SAME_TEAM", "DIFF_TEAM"]:
            g = c[c["class"] == cls]
            hb = np.histogram(g.time_sep_min.clip(upper=9.999), bins=bins)[0] / max(len(g), 1)
            idx = np.clip(np.digitize(g.time_sep_min.clip(upper=9.999), bins) - 1, 0, 9)
            w = np.where(hb[idx] > 0, h_sc[idx] / np.where(hb[idx] > 0, hb[idx], 1), 0) * g.weight.values
            cover = float(h_sc[hb > 0].sum())
            fair.append(dict(construction="TIME_SEPARATION_REWEIGHTED_TO_SAME_CAR", layer=layer, **{"class": cls}, n=len(g), sessions=g.session_key.nunique(),
                             session_balanced_median=float(pd.Series([wmedian(h.D_mph, w[g.session_key.values == s]) for s, h in g.groupby("session_key")]).median()),
                             pooled_median=wmedian(g.D_mph, w), time_sep_median_min=g.time_sep_min.median(), same_car_separation_mass_covered=cover))
        fair.append(dict(construction="TIME_SEPARATION_REWEIGHTED_TO_SAME_CAR", layer=layer, **{"class": "SAME_CAR"}, n=len(sc), sessions=sc.session_key.nunique(),
                         session_balanced_median=float(sc.groupby("session_key").D_mph.median().median()), pooled_median=sc.D_mph.median(),
                         time_sep_median_min=sc.time_sep_min.median(), same_car_separation_mass_covered=1.0))
    FA = pd.DataFrame(fair)
    FA.to_csv(OUT / "same_car_fairness.csv", index=False)

    # leave-one-out team-relative deviations (5 min, both roles, comparable)
    dev = []
    for role, keys in [("PRIMARY", prim), ("ERA_C_SECONDARY", sec)]:
        cb = car_blocks(L[L.session_key.isin(keys)], "comparable", 5)
        for (sk, b, tk), g in cb[~cb.team_key.str.startswith("SOLO:")].groupby(["session_key", "block", "team_key"]):
            if len(g) < 2:
                continue
            for r in g.itertuples(index=False):
                ref = g[g.car_id != r.car_id].v.median()
                dev.append(dict(role=role, session_key=sk, year=r.year, category=cat[sk], block=b, team=r.team, car_id=r.car_id, v=r.v,
                                team_reference_minus_i=ref, n_other_cars=len(g) - 1, team_relative_deviation=r.v - ref, abs_deviation=abs(r.v - ref)))
    DV = pd.DataFrame(dev)
    DV.to_csv(OUT / "team_relative_deviations.csv", index=False)

    # cross-session persistence (exploratory)
    per = DV.groupby(["role", "year", "category", "session_key", "car_id"]).team_relative_deviation.median().reset_index()
    per = per.groupby(["role", "year", "category", "car_id"]).team_relative_deviation.median().reset_index()
    cp = []
    for role in ["PRIMARY", "ERA_C_SECONDARY"]:
        for y in sorted(per[per.role == role].year.unique()):
            p = per[(per.role == role) & (per.year == y)]
            for a_, b_ in LINKS:
                m = p[p.category == a_].merge(p[p.category == b_], on="car_id", suffixes=("_a", "_b"))
                n = len(m)
                cp.append(dict(role=role, year=y, from_category=a_, to_category=b_, linked_cars=n,
                               spearman=m.team_relative_deviation_a.corr(m.team_relative_deviation_b, method="spearman") if n >= 8 else np.nan,
                               sign_persistence=float((np.sign(m.team_relative_deviation_a) == np.sign(m.team_relative_deviation_b)).mean()) if n >= 8 else np.nan,
                               note="shown only for >=8 linked cars (spec §9)" if n < 8 else ""))
    pd.DataFrame(cp).to_csv(OUT / "cross_session_persistence.csv", index=False)

    # dependence audit
    c = CMP[(CMP.role == "PRIMARY") & (CMP.layer == "comparable")]
    use = pd.concat([c.car_a, c.car_b]).value_counts()
    cbp = CB[(CB.role == "PRIMARY") & (CB.layer == "comparable")]
    ll = L[L.session_key.isin(prim) & L.comparable]
    dep = [dict(item="primary laps (comparable layer)", count=len(ll)), dict(item="car-block observations", count=len(cbp)),
           dict(item="unique cars", count=cbp.car_id.nunique()), dict(item="unique canonical teams", count=cbp.team.nunique()),
           dict(item="unique sessions (independent clusters)", count=cbp.session_key.nunique()),
           dict(item="unique session-blocks", count=cbp[["session_key", "block"]].drop_duplicates().shape[0]),
           dict(item="eligible within-block contrast blocks", count=int(((BLK.role == "PRIMARY") & (BLK.layer == "comparable")).sum()))]
    for cls, g in c.groupby("class"):
        dep.append(dict(item=f"comparisons {cls}", count=len(g)))
    dep += [dict(item="max appearances of one car across comparisons", count=int(use.max())), dict(item="median appearances per car", count=float(use.median())),
            dict(item="Phase 4E raw same-team lap pairs ±5 min in these sessions", count=int(pd.read_csv(P4E / "same_team_opportunities.csv").set_index("session_key").loc[prim].same_team_pairs_le5.sum())),
            dict(item="car-block reuse: max comparisons involving one car-block", count=int(pd.concat([c[["session_key", "block", "car_a"]].rename(columns={"car_a": "c"}),
                                                                                                      c[["session_key", "block", "car_b"]].rename(columns={"car_b": "c"})]).value_counts().max()))]
    pd.DataFrame(dep).to_csv(OUT / "dependence_audit.csv", index=False)

    # weather diagnostic (PTSC, read-only from Phase 4E extraction)
    wx = pd.read_csv(P4E / "inputs/ptsc_event_observations_extracted.csv")
    wx["ts_s"] = (pd.to_datetime(wx.local_ts, utc=True, format="mixed") - pd.Timestamp("1970-01-01", tz="UTC")) / pd.Timedelta(seconds=1)
    bl = BLK[(BLK.role == "PRIMARY") & (BLK.layer == "comparable")][["session_key", "block"]].drop_duplicates()
    wrows = []
    for r in bl.itertuples(index=False):
        s0, s1 = r.block * 300, r.block * 300 + 300
        w = wx[(wx.ts_s >= s0 - 900) & (wx.ts_s <= s1)]
        wrows.append(dict(session_key=r.session_key, block=r.block, ptsc_readings=len(w), track_range_c=(w.track_c.max() - w.track_c.min()) if len(w) else np.nan,
                          ambient_range_c=(w.ambient_c.max() - w.ambient_c.min()) if len(w) else np.nan))
    pd.DataFrame(wrows).to_csv(OUT / "weather_block_diagnostic.csv", index=False)

    # official cross-check (distinct sources)
    offmap = {}
    for r in sessions.itertuples(index=False):
        if pd.notna(r.official_session_id):
            offmap[str(int(r.official_session_id))] = int(r.official_session_id)
    ox = []
    for sk in prim + sec:
        ids = [int(x) for x in (sk.split("|")[-1].split("+") if "|" in sk else [sk])]
        orec = off_recs[off_recs.official_session_id.isin(ids)]
        g = L[L.session_key == sk]
        t71best = g.groupby("car").laptime.min().pipe(lambda s: 2.5 * 3600 / s)
        ob = orec.assign(car=orec.car_number.astype(str)).groupby("car").best_speed.max()
        both = t71best.to_frame("t71").join(ob.to_frame("official"), how="inner").dropna()
        ox.append(dict(session_key=sk, timing71_cars=g.car.nunique(), official_cars=orec.car_number.nunique(),
                       timing71_cars_in_official=int(sum(c in set(ob.index) for c in g.car.unique())),
                       best_speed_compared=len(both), best_speed_agree_within_0p01mph=int(((both.t71 - both.official).abs() <= 0.01).sum()),
                       lap_source=SOURCE_LABEL, crosscheck_source=OFFICIAL_LABEL))
    pd.DataFrame(ox).to_csv(OUT / "official_crosscheck.csv", index=False)

    # race appendix (structural only)
    ra = []
    for sk in race:
        cb = car_blocks(L[L.session_key == sk], "comparable", 5)
        per_b = cb.groupby("block").apply(lambda g: pd.Series({"cars": len(g), "teams_2plus": int((g[~g.team_key.str.startswith("SOLO:")].team_key.value_counts() >= 2).sum())}), include_groups=False)
        ra.append(dict(session_key=sk, year=int(cb.year.iloc[0]) if len(cb) else np.nan, car_blocks=len(cb), blocks=len(per_b),
                       blocks_with_same_team_pair=int((per_b.teams_2plus > 0).sum()) if len(per_b) else 0, note="structural counts only; no race D values (spec §9)"))
    pd.DataFrame(ra).to_csv(OUT / "race_appendix_structural.csv", index=False)

    # case evaluation (spec §10)
    sbp = SB[(SB.role == "PRIMARY") & (SB.layer == "comparable") & (SB.width_min == 5) & (SB.min_laps == 1)].iloc[0]
    sbb = SB[(SB.role == "PRIMARY") & (SB.layer == "broad") & (SB.width_min == 5) & (SB.min_laps == 1)].iloc[0]
    oth = SB[(SB.role == "PRIMARY") & (SB.layer == "comparable") & (SB.width_min.isin([1, 2, 10]))]
    yrs = pd.read_csv(OUT / "year_sensitivity.csv")
    yp = yrs[(yrs.role == "PRIMARY") & (yrs.layer == "comparable")]
    fa = FA[(FA.construction == "ADJACENT_BLOCK_ALL_CLASSES") & (FA.layer == "comparable")].set_index("class").session_balanced_median
    crit = dict(delta_positive=sbp.session_balanced_delta > 0, share_ge_075=sbp.share_sessions_positive >= 0.75,
                both_years_positive=bool((yp.session_balanced_delta > 0).all()) and len(yp) == 2, loto_all_positive=bool((LT.session_balanced_delta > 0).all()),
                broad_positive=sbb.session_balanced_delta > 0, windows_ge2_positive=int((oth.session_balanced_delta > 0).sum()) >= 2)
    consistent = all(crit.values())
    same_car_est = fa.get("SAME_CAR_ADJ", np.nan) < fa.get("SAME_TEAM_ADJ", np.nan) < fa.get("DIFF_TEAM_ADJ", np.nan)
    if (sbp.session_balanced_delta <= 0) or (sbp.share_sessions_positive <= 0.5):
        case = "D"
    elif consistent and same_car_est:
        case = "A"
    elif consistent:
        case = "B"
    else:
        case = "C"
    pd.DataFrame([dict(criterion=k, value=bool(v)) for k, v in crit.items()] + [dict(criterion="team_advantage_consistent", value=consistent),
                                                                                 dict(criterion="same_car_ordering_established", value=bool(same_car_est)),
                                                                                 dict(criterion="CASE", value=case)]).to_csv(OUT / "case_evaluation.csv", index=False)
    print(SB[(SB.min_laps == 1)].to_string())
    print(pd.read_csv(OUT / "case_evaluation.csv").to_string())


if __name__ == "__main__":
    main()
