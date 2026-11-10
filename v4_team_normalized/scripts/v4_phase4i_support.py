"""V4 Phase 4I: post-validity eligibility / support audit (implements output/phase4i/phase4i_support_audit_spec.md, ccb06c6).

Support structure only. No between-car D is computed for any pair; no hierarchy direction/estimator; no control selection;
no model; no ranking. The only speed dispersions are the pre-declared measurement-scale references (qualifying; same car).
Lap records = Timing71 archived recordings of the INDYCAR live timing feed (third-party). Phase 4E-4H are read-only.
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4i"
P4H = V4 / "output" / "phase4h"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4f_hierarchy as F  # noqa: E402
import v4_phase4g_adjacency as G  # noqa: E402

SOURCE_LABEL = F.SOURCE_LABEL
TIERS = {"TIER1_STRICT": {"A_PERFORMANCE_COMPARABLE"}, "TIER2_EXTENDED": {"A_PERFORMANCE_COMPARABLE", "B_PLAUSIBLY_PERFORMANCE_COMPARABLE"}}
KEY = ["session_key", "source_id", "car", "stint", "lap_in_stint"]


def load():
    P = pd.read_csv(P4H / "practice_lap_inventory.csv", dtype={"session_key": str, "car": str}, low_memory=False)
    pop = F.population()
    reg, sessions, off, L = F.laps_for(set(P.session_key))
    L["car"] = L.car.astype(str)
    ids = L[KEY + ["join_status", "primary_layer", "technical_partnership_only"]]
    P = P.merge(ids, on=KEY, how="left", validate="one_to_one")
    P["yr_group"] = np.where(P.year == 2025, "2025_SECONDARY", "2023_2024_PRIMARY")
    P["block"] = np.floor(P.ts / 300).astype(int)
    P["stint_key"] = P.source_id + "#" + P.stint.astype(str)
    return P, L


def carblocks(E):
    cb = E.groupby(["session_key", "block", "car_id"]).agg(
        year=("year", "first"), yr_group=("yr_group", "first"), category=("category", "first"), team=("canonical_engineering_team", "first"),
        primary_layer=("primary_layer", "first"), tp=("technical_partnership_only", "first"), t=("ts", "median"), n_laps=("ts", "size"),
        n_A=("cls", lambda s: int((s == "A_PERFORMANCE_COMPARABLE").sum())), n_B=("cls", lambda s: int((s == "B_PLAUSIBLY_PERFORMANCE_COMPARABLE").sum())),
        stint_key=("stint_key", "first"), n_stints=("stint_key", "nunique"), stint=("stint", "first")).reset_index()
    cb["composition"] = np.where(cb.n_B == 0, "A_ONLY", np.where(cb.n_A == 0, "B_ONLY", "MIXED_AB"))
    cb["st_eligible"] = cb.primary_layer.fillna(False).astype(bool) & ~cb.tp.fillna(False).astype(bool)
    cb["cb_id"] = cb.session_key + "|" + cb.block.astype(str) + "|" + cb.car_id
    return cb


def within_block_pairs(cb, laps, seqs, wx):
    rows = []
    for (sk, b), g in cb.groupby(["session_key", "block"]):
        g = g.sort_values("car_id").reset_index(drop=True)
        for i, j in itertools.combinations(range(len(g)), 2):
            a, c = g.iloc[i], g.iloc[j]
            if a.team == c.team:
                if not (a.st_eligible and c.st_eligible):
                    continue
                layer = "SAME_TEAM"
            else:
                layer = "DIFF_TEAM"
            m = G.pair_metrics(seqs[sk], laps[(sk, b, a.car_id)], laps[(sk, b, c.car_id)])
            rows.append(dict(layer=layer, session_key=sk, year=int(a.year), yr_group=a.yr_group, category=a.category, block=int(b),
                             cb_a=a.cb_id, cb_b=c.cb_id, car_a=a.car_id, car_b=c.car_id, team_a=a.team, team_b=c.team,
                             comp_a=a.composition, comp_b=c.composition, time_sep_s=abs(a.t - c.t), adjacency_category=m["pair_category"],
                             adjacency_code=m["pair_category_code"], median_intervening=m["median_intervening"], ptsc_readings=wx.get((sk, b), 0)))
    return pd.DataFrame(rows)


def same_car_pairs(cb):
    rows = []
    for car, g in cb.groupby("car_id"):
        g = g.sort_values("t").reset_index(drop=True)
        stint_order = {sk: {s: k for k, s in enumerate(h.sort_values("t").stint_key.unique())} for sk, h in g.groupby("session_key")}
        for i, j in itertools.combinations(range(len(g)), 2):
            a, c = g.iloc[i], g.iloc[j]
            if a.session_key == c.session_key:
                sub = "SAME_CAR_LOCAL_REPEAT" if a.stint_key == c.stint_key else "SAME_CAR_CROSS_RUN"
                stsep = abs(stint_order[a.session_key][a.stint_key] - stint_order[a.session_key][c.stint_key])
            else:
                sub = "SAME_CAR_CROSS_SESSION_SAME_CATEGORY" if a.category == c.category else "SAME_CAR_CROSS_SESSION_DIFF_CATEGORY"
                stsep = np.nan
            rows.append(dict(layer="SAME_CAR", subtype=sub, car=car, year=int(a.year), yr_group=a.yr_group, session_a=a.session_key, session_b=c.session_key,
                             category_a=a.category, category_b=c.category, block_a=int(a.block), block_b=int(c.block), cb_a=a.cb_id, cb_b=c.cb_id,
                             comp_first=a.composition, comp_second=c.composition, time_sep_s=abs(c.t - a.t), same_stint=a.stint_key == c.stint_key,
                             stint_separation=stsep, adjacent_block=bool(a.session_key == c.session_key and abs(int(a.block) - int(c.block)) == 1)))
    return pd.DataFrame(rows)


def comp_label(x, y):
    s = sorted([x, y])
    return "-".join(s)


def dependence(pairs, label, cb):
    if pairs.empty:
        return dict(population=label, raw_pairs=0)
    ends = pd.concat([pairs.cb_a, pairs.cb_b])
    use = ends.value_counts()
    reused = pairs.cb_a.map(use).ge(2) | pairs.cb_b.map(use).ge(2)
    cars = pd.concat([pairs.cb_a.str.rsplit("|", n=2).str[-2] + "|" + pairs.cb_a.str.rsplit("|", n=1).str[-1],
                      pairs.cb_b.str.rsplit("|", n=2).str[-2] + "|" + pairs.cb_b.str.rsplit("|", n=1).str[-1]])
    carpairs = pairs.apply(lambda r: tuple(sorted((r.car_a, r.car_b))) if "car_a" in r else (r.car, r.car), axis=1)
    lab = cb.set_index("cb_id")
    laps = int(lab.loc[use.index].n_laps.sum())
    teams = set(pairs.team_a) | set(pairs.team_b) if "team_a" in pairs else set(lab.loc[use.index].team)
    tys = {f"{y}|{t}" for y, t in zip(lab.loc[use.index].year, lab.loc[use.index].team)}
    sess = set(pairs.session_key) if "session_key" in pairs else set(pairs.session_a) | set(pairs.session_b)
    # graph summaries (union-find)
    parent = {n: n for n in use.index}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in zip(pairs.cb_a, pairs.cb_b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    comp = pd.Series([find(n) for n in use.index]).value_counts()
    top = use.sort_values(ascending=False).head(max(1, int(np.ceil(0.05 * len(use))))).index
    touch_top = float((pairs.cb_a.isin(top) | pairs.cb_b.isin(top)).mean())
    return dict(population=label, raw_pairs=len(pairs), unique_laps=laps, unique_carblocks=len(use),
                unique_cars=pd.concat([pairs.car_a, pairs.car_b]).nunique() if "car_a" in pairs else pairs.car.nunique(),
                unique_car_pairs=carpairs.nunique(), unique_teams=len(teams), unique_team_years=len(tys), unique_sessions=len(sess), independent_session_clusters=len(sess),
                max_carblock_reuse=int(use.max()), median_carblock_reuse=float(use.median()), share_pairs_involving_reused_carblock=float(reused.mean()),
                max_share_pairs_touching_one_carblock=float(use.max() / len(pairs)), share_edges_touching_top5pct_degree_nodes=touch_top,
                graph_components=len(comp), largest_component_share_of_nodes=float(comp.max() / len(use)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    P, L = load()
    seqs = {sk: G.Seq(g.ts.values) for sk, g in L.groupby("session_key")}
    wx = pd.read_csv(V4 / "output/phase4e/inputs/ptsc_event_observations_extracted.csv")
    wx["ts_s"] = (pd.to_datetime(wx.local_ts, utc=True, format="mixed") - pd.Timestamp("1970-01-01", tz="UTC")) / pd.Timedelta(seconds=1)
    wts = np.sort(wx.ts_s.values)
    blocks = P[["session_key", "block"]].drop_duplicates()
    wxc = {(s, b): int(np.searchsorted(wts, b * 300 + 300, "right") - np.searchsorted(wts, b * 300 - 900, "left")) for s, b in zip(blocks.session_key, blocks.block)}

    eo, allp, sc_all, cbs = [], [], [], {}
    for tier, ok in TIERS.items():
        E = P[P.cls.isin(ok) & (P.join_status == "MATCHED")].copy()
        eo.append(E.assign(tier=tier))
        cb = carblocks(E)
        cbs[tier] = cb
        laps = {k: g.ts.values for k, g in E.groupby(["session_key", "block", "car_id"])}
        wb = within_block_pairs(cb, laps, seqs, wxc).assign(tier=tier)
        sc = same_car_pairs(cb).assign(tier=tier)
        allp.append(wb)
        sc_all.append(sc)
    EO = pd.concat(eo, ignore_index=True)
    WB = pd.concat(allp, ignore_index=True)
    SC = pd.concat(sc_all, ignore_index=True)
    cols = ["tier", "yr_group", "year", "session_key", "category", "source_id", "car", "car_id", "driver", "canonical_engineering_team", "primary_layer",
            "technical_partnership_only", "stint", "stint_provenance", "lap_in_stint", "block", "ts", "ts_tied", "laptime", "speed_mph", "cls", "coherent_prev", "evidence_source"]
    EO[cols].to_csv(OUT / "eligible_observations.csv", index=False)

    # ---- per-tier support tables
    def tier_support(tier):
        cb, wb, sc = cbs[tier], WB[WB.tier == tier], SC[SC.tier == tier]
        rows = []
        for lvl, by in [("YEAR_GROUP", ["yr_group"]), ("YEAR", ["yr_group", "year"]), ("CATEGORY", ["yr_group", "category"]), ("SESSION", ["yr_group", "session_key", "category"])]:
            for k, g in cb.groupby(by):
                k = k if isinstance(k, tuple) else (k,)
                d = dict(zip(by, k))
                m = pd.Series(True, index=wb.index)
                for c_, v in d.items():
                    m &= wb[c_] == v
                w = wb[m]
                s = sc[(sc.yr_group == d["yr_group"]) & ((sc.year == d["year"]) if "year" in d else True)
                       & ((sc.session_a == d["session_key"]) if "session_key" in d else True) & ((sc.category_a == d["category"]) if "category" in d else True)]
                rows.append(dict(tier=tier, level=lvl, **d, eligible_laps=int(g.n_laps.sum()), eligible_carblocks=len(g), cars=g.car_id.nunique(), teams=g.team.nunique(),
                                 sessions=g.session_key.nunique(), blocks=g[["session_key", "block"]].drop_duplicates().shape[0],
                                 carblocks_with_2plus_laps=int((g.n_laps >= 2).sum()), same_team_pairs=int((w.layer == "SAME_TEAM").sum()),
                                 diff_team_pairs=int((w.layer == "DIFF_TEAM").sum()), same_car_local_pairs=int((s.subtype == "SAME_CAR_LOCAL_REPEAT").sum()),
                                 same_car_cross_run_pairs=int((s.subtype == "SAME_CAR_CROSS_RUN").sum()),
                                 same_car_cross_session_pairs=int(s.subtype.str.startswith("SAME_CAR_CROSS_SESSION").sum())))
        for (yg, y, t), g in cb.groupby(["yr_group", "year", "team"]):
            w = wb[(wb.layer == "SAME_TEAM") & (wb.team_a == t) & (wb.year == y)]
            rows.append(dict(tier=tier, level="TEAM_YEAR_COVERAGE_ALPHABETICAL", yr_group=yg, year=y, team=t, eligible_laps=int(g.n_laps.sum()), eligible_carblocks=len(g),
                             cars=g.car_id.nunique(), sessions=g.session_key.nunique(), same_team_pairs=len(w)))
        for (yg, car), g in cb.groupby(["yr_group", "car_id"]):
            rows.append(dict(tier=tier, level="CAR", yr_group=yg, car_id=car, team=g.team.iloc[0], eligible_laps=int(g.n_laps.sum()), eligible_carblocks=len(g),
                             sessions=g.session_key.nunique()))
        for (yg, sk, car), g in cb.groupby(["yr_group", "session_key", "car_id"]):
            rows.append(dict(tier=tier, level="CAR_SESSION", yr_group=yg, session_key=sk, car_id=car, eligible_laps=int(g.n_laps.sum()), eligible_carblocks=len(g),
                             stints=g.stint_key.nunique()))
        return pd.DataFrame(rows)
    T1, T2 = tier_support("TIER1_STRICT"), tier_support("TIER2_EXTENDED")
    T1.to_csv(OUT / "tier1_strict_support.csv", index=False)
    T2.to_csv(OUT / "tier2_extended_support.csv", index=False)

    # ---- same-car support
    scr = []
    for (tier, yg, sub), g in SC.groupby(["tier", "yr_group", "subtype"]):
        scr.append(dict(tier=tier, yr_group=yg, subtype=sub, pairs=len(g), cars=g.car.nunique(), sessions=len(set(g.session_a) | set(g.session_b)),
                        carblocks=pd.concat([g.cb_a, g.cb_b]).nunique(), time_sep_s_p10=g.time_sep_s.quantile(.1), time_sep_s_median=g.time_sep_s.median(),
                        time_sep_s_p90=g.time_sep_s.quantile(.9), stint_separation_median=g.stint_separation.median(), adjacent_block_pairs=int(g.adjacent_block.sum()),
                        share_same_stint=float(g.same_stint.mean())))
    for tier, cb in cbs.items():
        for yg, g in cb.groupby("yr_group"):
            scr.append(dict(tier=tier, yr_group=yg, subtype="WITHIN_CARBLOCK_LAP_REPEAT", pairs=int((g.n_laps * (g.n_laps - 1) / 2).sum()),
                            cars=g[g.n_laps >= 2].car_id.nunique(), sessions=g[g.n_laps >= 2].session_key.nunique(), carblocks=int((g.n_laps >= 2).sum())))
    pd.DataFrame(scr).to_csv(OUT / "same_car_support.csv", index=False)
    SC.to_csv(OUT / "same_car_pairs.csv", index=False)
    WB.to_csv(OUT / "within_block_pairs.csv", index=False)

    # ---- same-team / diff-team support
    def layer_support(layer, fname):
        rows = []
        for (tier, yg), g in WB[WB.layer == layer].groupby(["tier", "yr_group"]):
            use = pd.concat([g.cb_a, g.cb_b]).value_counts()
            tshare = pd.concat([g.team_a, g.team_b]).value_counts() / (2 * len(g)) if layer == "DIFF_TEAM" else g.team_a.value_counts() / len(g)
            sshare = g.session_key.value_counts() / len(g)
            row = dict(tier=tier, yr_group=yg, layer=layer, pairs=len(g), distinct_carblocks=len(use), distinct_cars=pd.concat([g.car_a, g.car_b]).nunique(),
                       distinct_teams=len(set(g.team_a) | set(g.team_b)), team_years=len({f"{y}|{t}" for y, t in zip(pd.concat([g.year, g.year]), pd.concat([g.team_a, g.team_b]))}),
                       sessions=g.session_key.nunique(), session_categories=g.category.nunique(), years=g.year.nunique(), blocks=g[["session_key", "block"]].drop_duplicates().shape[0],
                       independent_car_pairs=g.apply(lambda r: tuple(sorted((r.car_a, r.car_b))), axis=1).nunique(), max_carblock_reuse=int(use.max()),
                       carblocks_used_2plus=int((use >= 2).sum()), max_team_share=float(tshare.max()), max_session_share=float(sshare.max()),
                       time_sep_s_p10=g.time_sep_s.quantile(.1), time_sep_s_p25=g.time_sep_s.quantile(.25), time_sep_s_median=g.time_sep_s.median(),
                       time_sep_s_p75=g.time_sep_s.quantile(.75), time_sep_s_p90=g.time_sep_s.quantile(.9),
                       **{f"adj_{c}": float((g.adjacency_category == c).mean()) for c in G.CATS},
                       share_blocks_with_ptsc=float((g.ptsc_readings > 0).mean()))
            rows.append(row)
            if layer == "SAME_TEAM":
                for t, h in g.groupby("team_a"):
                    rows.append(dict(tier=tier, yr_group=yg, layer="SAME_TEAM_CONCENTRATION_BY_TEAM_ALPHABETICAL", team=t, pairs=len(h), share=len(h) / len(g), sessions=h.session_key.nunique()))
                for s, h in g.groupby("session_key"):
                    rows.append(dict(tier=tier, yr_group=yg, layer="SAME_TEAM_CONCENTRATION_BY_SESSION", session_key=s, pairs=len(h), share=len(h) / len(g), teams=h.team_a.nunique()))
        pd.DataFrame(rows).to_csv(OUT / fname, index=False)
        return pd.DataFrame(rows)
    STS = layer_support("SAME_TEAM", "same_team_support.csv")
    DTS = layer_support("DIFF_TEAM", "different_team_candidate_support.csv")

    # ---- common support
    cs_s, cs_b = [], []
    for tier, cb in cbs.items():
        wb, sc = WB[WB.tier == tier], SC[SC.tier == tier]
        # block-scale same-car support: car-block with >=2 laps, or same car eligible at b+1 same session+stint
        nxt = set(zip(cb.session_key, cb.block - 1, cb.car_id, cb.stint_key))
        cb = cb.assign(sc_support=(cb.n_laps >= 2).values | np.array([(s, b, c, st) in nxt for s, b, c, st in zip(cb.session_key, cb.block, cb.car_id, cb.stint_key)], dtype=bool))
        blk = cb.groupby(["session_key", "block"]).agg(yr_group=("yr_group", "first"), year=("year", "first"), category=("category", "first"), cars=("car_id", "size"),
                                                       teams=("team", "nunique"), SC=("sc_support", "any")).reset_index()
        stb = wb[wb.layer == "SAME_TEAM"].groupby(["session_key", "block"]).size().rename("st_pairs")
        dtb = wb[wb.layer == "DIFF_TEAM"].groupby(["session_key", "block"]).size().rename("dt_pairs")
        blk = blk.merge(stb, on=["session_key", "block"], how="left").merge(dtb, on=["session_key", "block"], how="left").fillna({"st_pairs": 0, "dt_pairs": 0})
        blk["ST"], blk["DT"] = blk.st_pairs > 0, blk.dt_pairs > 0
        blk["ST_DT"], blk["SC_ST"], blk["ALL3"] = blk.ST & blk.DT, blk.SC & blk.ST, blk.SC & blk.ST & blk.DT
        blk["ptsc_readings"] = [wxc.get((s, b), 0) for s, b in zip(blk.session_key, blk.block)]
        cs_b.append(blk.assign(tier=tier))
        for (yg, sk), g in blk.groupby(["yr_group", "session_key"]):
            s = sc[(sc.session_a == sk) & (sc.session_b == sk)]
            cs_s.append(dict(tier=tier, yr_group=yg, session_key=sk, year=g.year.iloc[0], category=g.category.iloc[0], eligible_blocks=len(g),
                             blocks_SC=int(g.SC.sum()), blocks_ST=int(g.ST.sum()), blocks_DT=int(g.DT.sum()), blocks_ST_DT=int(g.ST_DT.sum()),
                             blocks_SC_ST=int(g.SC_ST.sum()), blocks_ALL3=int(g.ALL3.sum()),
                             all_three_layers_block_scale=bool(g.ST.any() and g.DT.any() and g.SC.any()),
                             all_three_layers_session_scale=bool(len(s) > 0 or g.SC.any()) and bool(g.ST.any()) and bool(g.DT.any()),
                             same_team_pairs=int(g.st_pairs.sum()), diff_team_pairs=int(g.dt_pairs.sum()), same_car_within_session_pairs=len(s),
                             teams_in_same_team_pairs=wb[(wb.layer == "SAME_TEAM") & (wb.session_key == sk)].team_a.nunique()))
    CSS, CSB = pd.DataFrame(cs_s), pd.concat(cs_b, ignore_index=True)
    CSS.to_csv(OUT / "common_support_by_session.csv", index=False)
    CSB.to_csv(OUT / "common_support_by_block.csv", index=False)

    # ---- adjacency support / balance feasibility
    ad = []
    bal_rows = []
    for tier in TIERS:
        wb = WB[WB.tier == tier]
        dt = wb[wb.layer == "DIFF_TEAM"]
        # candidate categories relative to each car (both orientations) in block
        cand = {}
        for r in dt.itertuples(index=False):
            cand.setdefault((r.session_key, r.block, r.car_a), []).append(r.adjacency_code)
            cand.setdefault((r.session_key, r.block, r.car_b), []).append(r.adjacency_code)
        for r in wb[wb.layer == "SAME_TEAM"].itertuples(index=False):
            for tgt in (r.car_a, r.car_b):
                cs = cand.get((r.session_key, r.block, tgt), [])
                n = sum(1 for c in cs if c == r.adjacency_code)
                bal_rows.append(dict(tier=tier, yr_group=r.yr_group, session_key=r.session_key, stratum=r.adjacency_category, n_same_stratum_candidates=n, n_candidates=len(cs)))
        for (yg, layer), g in wb.groupby(["yr_group", "layer"]):
            for c in G.CATS:
                ad.append(dict(tier=tier, yr_group=yg, table="ADJACENCY_DISTRIBUTION", layer=layer, stratum=c, pairs=int((g.adjacency_category == c).sum()),
                               share=float((g.adjacency_category == c).mean())))
    BAL = pd.DataFrame(bal_rows)
    for (tier, yg), g in BAL.groupby(["tier", "yr_group"]):
        ad.append(dict(tier=tier, yr_group=yg, table="BALANCE_FEASIBILITY", layer="SAME_TEAM_ORIENTED", stratum="ALL", pairs=len(g),
                       share_ge1_same_stratum_candidate=float((g.n_same_stratum_candidates >= 1).mean()), share_ge3_same_stratum_candidate=float((g.n_same_stratum_candidates >= 3).mean()),
                       share_any_candidate=float((g.n_candidates >= 1).mean())))
        for c, h in g.groupby("stratum"):
            ad.append(dict(tier=tier, yr_group=yg, table="BALANCE_FEASIBILITY", layer="SAME_TEAM_ORIENTED", stratum=c, pairs=len(h),
                           share_ge1_same_stratum_candidate=float((h.n_same_stratum_candidates >= 1).mean()), share_ge3_same_stratum_candidate=float((h.n_same_stratum_candidates >= 3).mean()),
                           share_any_candidate=float((h.n_candidates >= 1).mean())))
    # tier-2 composition
    wb2 = WB[WB.tier == "TIER2_EXTENDED"]
    for (yg, layer), g in wb2.groupby(["yr_group", "layer"]):
        for lab, cnt in g.apply(lambda r: comp_label(r.comp_a, r.comp_b), axis=1).value_counts().items():
            ad.append(dict(tier="TIER2_EXTENDED", yr_group=yg, table="TIER2_COMPOSITION_UNORDERED", layer=layer, stratum=lab, pairs=int(cnt), share=cnt / len(g)))
        for lab, cnt in (g.comp_a + ">" + g.comp_b).value_counts().items():
            ad.append(dict(tier="TIER2_EXTENDED", yr_group=yg, table="TIER2_COMPOSITION_ORDERED_TARGET_SMALLER_CARID", layer=layer, stratum=lab, pairs=int(cnt), share=cnt / len(g)))
    sc2 = SC[SC.tier == "TIER2_EXTENDED"]
    for (yg, sub), g in sc2.groupby(["yr_group", "subtype"]):
        for lab, cnt in (g.comp_first + ">" + g.comp_second).value_counts().items():
            ad.append(dict(tier="TIER2_EXTENDED", yr_group=yg, table="TIER2_COMPOSITION_ORDERED_TIME", layer=sub, stratum=lab, pairs=int(cnt), share=cnt / len(g)))
    ADJ = pd.DataFrame(ad)
    ADJ.to_csv(OUT / "adjacency_support.csv", index=False)

    # ---- dependence
    dep = []
    for tier, cb in cbs.items():
        for yg in ["2023_2024_PRIMARY", "2025_SECONDARY"]:
            c = cb[cb.yr_group == yg]
            w = WB[(WB.tier == tier) & (WB.yr_group == yg)]
            for lab, pp in [("SAME_TEAM", w[w.layer == "SAME_TEAM"]), ("DIFF_TEAM", w[w.layer == "DIFF_TEAM"]), ("WITHIN_BLOCK_ST_PLUS_DT", w)]:
                dep.append(dict(tier=tier, yr_group=yg, **dependence(pp, lab, c)))
            s = SC[(SC.tier == tier) & (SC.yr_group == yg)]
            for sub, pp in s.groupby("subtype"):
                dep.append(dict(tier=tier, yr_group=yg, **dependence(pp.assign(car_a=pp.car, car_b=pp.car, session_key=pp.session_a), sub, c)))
    DEP = pd.DataFrame(dep)
    DEP.to_csv(OUT / "reuse_dependence_audit.csv", index=False)

    # ---- year / era support
    era = [dict(period="2018-2021", source="Timing71 legacy analysis files", temporal_resolution="stint-level timestamps only; lap times; derived lap timestamps inconsistent",
                phase4e_tier="D (all sessions)", phase4h_classifier_applied=False, lap_level_hierarchy_support="NONE (not lap-level comparable; classifier not projected backwards)",
                contributes="registry / team identity; longitudinal context; session-level indicative summaries only"),
           dict(period="2022", source="official INDYCAR session records only (no Timing71 lap data retrieved)", temporal_resolution="session-level only",
                phase4e_tier="D", phase4h_classifier_applied=False, lap_level_hierarchy_support="NONE",
                contributes="registry / team identity; session-level results context")]
    for tier, cb in cbs.items():
        for y, g in cb.groupby("year"):
            w = WB[(WB.tier == tier) & (WB.year == y)]
            era.append(dict(period=str(y), tier=tier, source=SOURCE_LABEL, temporal_resolution="lap-level; feed-update timestamps (~1.67 s)",
                            phase4e_tier="A/B sessions only", phase4h_classifier_applied=True,
                            lap_level_hierarchy_support="PRIMARY (2023-2024)" if y < 2025 else "SECONDARY (separate; not Design-1 feasible in Phase 4E)",
                            eligible_laps=int(g.n_laps.sum()), eligible_carblocks=len(g), sessions=g.session_key.nunique(), cars=g.car_id.nunique(), teams=g.team.nunique(),
                            same_team_pairs=int((w.layer == "SAME_TEAM").sum()), diff_team_pairs=int((w.layer == "DIFF_TEAM").sum()),
                            sessions_all_three_block_scale=int(CSS[(CSS.tier == tier) & (CSS.year == y)].all_three_layers_block_scale.sum())))
    pd.DataFrame(era).to_csv(OUT / "year_era_support.csv", index=False)

    # ---- performance-scale reference (descriptive; qualifying + same car only)
    Q = pd.read_csv(P4H / "qualifying_performance_reference.csv", dtype={"session_key": str, "car": str})
    ps = []
    o = Q[Q.provenance == "OFFICIAL_ANCHORED"]
    for y, g in o.groupby("year"):
        at = g.groupby("attempt_id").speed_mph
        sd, rg, v = at.std(), at.max() - at.min(), g.speed_mph.median()
        ps.append(dict(reference="QUALIFYING_OFFICIAL_WITHIN_ATTEMPT", scope=str(y), n_units=len(sd), median_sd_mph=sd.median(), median_range_mph=rg.median(),
                       p90_range_mph=rg.quantile(.9), median_speed_mph=v, median_sd_pct=100 * sd.median() / v, median_range_pct=100 * rg.median() / v))
    A = EO[(EO.tier == "TIER1_STRICT")]
    for yg, g in A.groupby("yr_group"):
        cbg = g.groupby(["session_key", "block", "car_id"]).speed_mph
        sd, rg, n = cbg.std(), cbg.max() - cbg.min(), cbg.size()
        sd, rg = sd[n >= 2], rg[n >= 2]
        v = g.speed_mph.median()
        ps.append(dict(reference="SAME_CAR_A_WITHIN_CARBLOCK", scope=yg, n_units=len(sd), median_sd_mph=sd.median(), median_range_mph=rg.median(), p90_range_mph=rg.quantile(.9),
                       median_speed_mph=v, median_sd_pct=100 * sd.median() / v, median_range_pct=100 * rg.median() / v))
        h = g.sort_values(["session_key", "source_id", "car", "stint", "lap_in_stint"])
        cons = (h.groupby(["session_key", "source_id", "car", "stint"]).lap_in_stint.diff() == 1)
        dv = h.groupby(["session_key", "source_id", "car", "stint"]).speed_mph.diff().abs()[cons]
        ps.append(dict(reference="SAME_CAR_A_CONSECUTIVE_LAP_ABS_DELTA", scope=yg, n_units=len(dv), median_abs_delta_mph=dv.median(), p90_abs_delta_mph=dv.quantile(.9),
                       median_speed_mph=v, median_abs_delta_pct=100 * dv.median() / v))
        cs = g.groupby(["car_id", "session_key"]).speed_mph.median().groupby("car_id")
        sdc = cs.std()[cs.size() >= 2]
        ps.append(dict(reference="SAME_CAR_A_CROSS_SESSION_SD_OF_SESSION_MEDIANS", scope=yg, n_units=len(sdc), median_sd_mph=sdc.median(), p90_sd_mph=sdc.quantile(.9),
                       median_speed_mph=v, median_sd_pct=100 * sdc.median() / v))
    v225, lt = 225.0, 2.5 * 3600 / 225.0
    ps.append(dict(reference="LAPTIME_PRECISION", scope="1e-4 s recorded precision", median_sd_mph=2.5 * 3600 / (lt - 1e-4) - v225, median_speed_mph=v225,
                   note="speed change for a 0.0001 s lap-time change at 225 mph"))
    ps.append(dict(reference="TIMESTAMP_RESOLUTION", scope="Timing71 feed update", note="~1.67 s feed-update cycle (Phase 4G); lap times themselves are not affected"))
    PS = pd.DataFrame(ps)
    for c in ["median_sd_mph", "median_range_mph", "median_abs_delta_mph"]:
        if c in PS:
            PS[c.replace("_mph", "_laptime_equiv_s_at_225")] = PS[c] / v225 * lt
    PS.to_csv(OUT / "performance_scale_reference.csv", index=False)

    # ---- gate (spec §10)
    def metrics(tier, yg):
        css = CSS[(CSS.tier == tier) & (CSS.yr_group == yg)]
        csb = CSB[(CSB.tier == tier) & (CSB.yr_group == yg)]
        w = WB[(WB.tier == tier) & (WB.yr_group == yg)]
        st = w[w.layer == "SAME_TEAM"]
        b = BAL[(BAL.tier == tier) & (BAL.yr_group == yg)]
        use = pd.concat([w.cb_a, w.cb_b]).value_counts()
        s = SC[(SC.tier == tier) & (SC.yr_group == yg) & (SC.subtype == "SAME_CAR_LOCAL_REPEAT")]
        cb = cbs[tier][cbs[tier].yr_group == yg]
        m9 = len(set(s.session_a) | set(cb[cb.n_laps >= 2].session_key))
        return dict(M1=int(css.all_three_layers_block_scale.sum()), M2=int(css[css.all_three_layers_block_scale].year.nunique()), M3=int(csb.ALL3.sum()),
                    M4=int(st.team_a.nunique()), M5=float(st.team_a.value_counts(normalize=True).max()) if len(st) else np.nan,
                    M6=float(st.session_key.value_counts(normalize=True).max()) if len(st) else np.nan,
                    M7=float((b.n_same_stratum_candidates >= 1).mean()) if len(b) else 0.0, M8=float(use.max() / len(w)) if len(w) else np.nan, M9=m9)

    def level(m):
        if (m["M1"] >= 6 and m["M2"] == 2 and m["M3"] >= 30 and m["M4"] >= 5 and m["M5"] <= 0.40 and m["M6"] <= 0.40 and m["M7"] >= 0.50 and m["M8"] <= 0.05 and m["M9"] >= 6):
            return "STRONG"
        if m["M1"] >= 3 and m["M3"] >= 10 and m["M4"] >= 3 and m["M5"] <= 0.60 and m["M6"] <= 0.60 and m["M7"] >= 0.25 and m["M9"] >= 3:
            return "ADEQUATE"
        if m["M1"] >= 1 and m["M4"] >= 2:
            return "MINIMAL"
        return "NONE"
    ce = []
    lv = {}
    for tier in TIERS:
        for yg in ["2023_2024_PRIMARY", "2025_SECONDARY"]:
            m = metrics(tier, yg)
            L_ = level(m) if yg.startswith("2023") else level({**m, "M2": 2}) + " (M2 not applicable; single year)"
            if yg.startswith("2023"):
                lv[tier] = L_
            for k, v in m.items():
                ce.append(dict(tier=tier, yr_group=yg, criterion=k, value=v))
            ce.append(dict(tier=tier, yr_group=yg, criterion="LEVEL", value=L_))
    rank = {"STRONG": 3, "ADEQUATE": 2, "MINIMAL": 1, "NONE": 0}
    t1, t2 = lv["TIER1_STRICT"], lv["TIER2_EXTENDED"]
    if t1 == "STRONG" and t2 == "STRONG":
        case = "A"
    elif rank[t1] >= 2 or rank[t2] >= 2:
        case = "B"
    elif rank[t2] >= 1:
        case = "C"
    else:
        case = "D"
    restricted = [t for t in TIERS if rank[lv[t]] >= 2]
    ce += [dict(criterion="SUPPORT_CASE", value=case), dict(criterion="restricted_supported_tiers", value=";".join(restricted) if restricted else ""),
           dict(criterion="phase4j_gate", value={"A": "Phase 4J may pre-specify one confirmatory analysis (not run)",
                                                 "B": "Phase 4J only within restricted supported population (not run)"}.get(case, "NO hierarchy test")),
           dict(criterion="phase4f_case_unchanged", value=pd.read_csv(V4 / "output/phase4f/case_evaluation.csv").set_index("criterion").value["CASE"]),
           dict(criterion="phase4g_case_unchanged", value=pd.read_csv(V4 / "output/phase4g/phase4g_case_evaluation.csv").set_index("criterion").value["CASE"]),
           dict(criterion="phase4h_case_unchanged", value=pd.read_csv(P4H / "case_evaluation.csv").set_index("criterion").value["MEASUREMENT_VALIDITY_CASE"])]
    pd.DataFrame(ce).to_csv(OUT / "case_evaluation.csv", index=False)
    print(pd.DataFrame(ce).to_string())


if __name__ == "__main__":
    main()
