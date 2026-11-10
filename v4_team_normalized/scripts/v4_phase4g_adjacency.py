"""V4 Phase 4G: different-team control-selection / timing-sequence adjacency diagnostic.

Implements output/phase4g/phase4g_design_diagnostic_spec.md (committed ffdfacd before any computation).
DIAGNOSTIC ONLY: no new hierarchy test, no model, no team effects, no ranking, no tow labels.
Lap records = Timing71 archived recordings of the INDYCAR live timing feed (third-party).
Phase 4F / 4E are imported read-only; outputs are written only to output/phase4g/.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
P4F = V4 / "output" / "phase4f"
OUT = V4 / "output" / "phase4g"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4f_hierarchy as F  # noqa: E402  (read-only: population, laps_for, car_blocks)

SOURCE_LABEL = F.SOURCE_LABEL
CATS = ["SAME_UPDATE", "CONSECUTIVE", "BETWEEN_1_2", "BETWEEN_3_5", "BETWEEN_GT5"]
TS_BINS, TS_LABELS = [-1, 5, 15, 60, 300], ["<=5s", "5-15s", "15-60s", "60-300s"]  # Phase 4F fig08b bins
CUM_K = [0, 1, 2, 3, 5]


# ------------------------------------------------------------------ sequence (spec §3)
def chain_estimates(L):
    """DERIVED_LAPTIME_CHAIN_ESTIMATE: anchor + cumulative laptime within timestamp-coherent chains (sensitivity only)."""
    x = L.sort_values(["session_key", "car", "stint", "lap_in_stint"]).copy()
    g = x.groupby(["session_key", "car", "stint"])
    brk = ((x.ts - g.ts.shift(1) - x.laptime).abs() > 2.0) | g.ts.shift(1).isna()
    x["chain"] = brk.groupby([x.session_key, x.car, x.stint]).cumsum()
    x["C"] = x.groupby(["session_key", "car", "stint", "chain"]).laptime.cumsum()
    anchor = (x.ts - x.C).groupby([x.session_key, x.car, x.stint, x.chain]).transform("min")
    x["ts_est"] = anchor + x.C
    x["seq_gap_before"] = brk & g.ts.shift(1).notna()
    return x


class Seq:
    """Chronological sequence of all lap-line records in one session (all flags, all laps)."""

    def __init__(self, ts):
        self.S = np.sort(np.round(np.asarray(ts, float), 3))
        self.U = np.unique(self.S)

    def lap_pair(self, a, c):
        a, c = round(a, 3), round(c, 3)
        ua, uc = np.searchsorted(self.U, a), np.searchsorted(self.U, c)
        lo, hi = min(a, c), max(a, c)
        inter = int(np.searchsorted(self.S, hi, "left") - np.searchsorted(self.S, lo, "right")) if hi > lo else 0
        us = abs(int(uc) - int(ua))
        cat = 0 if us == 0 else (1 if inter == 0 else (2 if inter <= 2 else (3 if inter <= 5 else 4)))
        order = "SAME_UPDATE_ORDER_UNOBSERVED" if c == a else ("CONTROL_AFTER" if c > a else "CONTROL_BEFORE")
        return abs(c - a), us, inter, cat, order


def pair_metrics(seq, ta, tc):
    """Car-block pair: for each target lap, nearest comparator lap (ties -> earlier)."""
    tc = np.sort(tc)
    r = []
    for a in np.sort(ta):
        c = tc[int(np.argmin(np.abs(tc - a)))]
        r.append(seq.lap_pair(a, c))
    r.sort(key=lambda z: (z[3], z[2]))
    lm = r[(len(r) - 1) // 2]
    return dict(n_target_laps=len(r), median_abs_ts_sep_s=float(np.median([z[0] for z in r])), median_update_sep=float(np.median([z[1] for z in r])),
                median_intervening=float(np.median([z[2] for z in r])), min_intervening=int(min(z[2] for z in r)),
                pair_category=CATS[lm[3]], pair_category_code=lm[3], intervening_lower_median_lap=lm[2],
                share_control_after=float(np.mean([z[4] == "CONTROL_AFTER" for z in r])),
                share_same_update=float(np.mean([z[4] == "SAME_UPDATE_ORDER_UNOBSERVED" for z in r])))


def with_metrics(row, seqs, laps, ka, kc, prefix=""):
    m = pair_metrics(seqs[ka[0]], laps[ka], laps[kc])
    row.update({prefix + k: v for k, v in m.items()})
    return row


# ------------------------------------------------------------------ reconstruction (spec §4-§5)
def car_key(car):
    return (int(str(car)) if str(car).isdigit() else 999, str(car))


def reconstruct(cb, role, cat, seqs, laps, seqs_est, laps_est):
    rec, pairs = [], []
    for (sk, b), g in cb.groupby(["session_key", "block"]):
        g = g.reset_index(drop=True)
        teams, t, v, cid, tm, car = g.team_key.values, g.t.values, g.v.values, g.car_id.values, g.team.values, g.car.values
        for i in range(len(g)):
            if teams[i].startswith("SOLO:"):
                continue
            mates = [k for k in range(len(g)) if k != i and teams[k] == teams[i]]
            others = [k for k in range(len(g)) if tm[k] != tm[i]]
            if not mates or not others:
                continue
            key = lambda k: (abs(t[k] - t[i]),) + car_key(car[k])
            m, o = min(mates, key=key), min(others, key=key)
            base = dict(role=role, session_key=sk, year=int(g.year.iloc[0]), category=cat[sk], block=int(b), target=cid[i], target_team=tm[i])
            rec.append(dict(**base, target_carblock_time=t[i], teammate=cid[m], teammate_team=tm[m], teammate_carblock_time=t[m],
                            control=cid[o], control_team=tm[o], control_carblock_time=t[o],
                            abs_target_teammate_sep_s=abs(t[m] - t[i]), abs_target_control_sep_s=abs(t[o] - t[i]),
                            D_same_team_target=abs(v[i] - v[m]), D_diff_team_target=abs(v[i] - v[o]),
                            candidate_pool_size=len(others), teammates_in_block=len(mates), evidence_source=SOURCE_LABEL))
            ka = (sk, b, cid[i])
            specs = [("A_PRIMARY_CONTROL", [o]), ("B_ELIGIBLE_CANDIDATES", others), ("C1_TEAMMATE_OF_TARGET", [m]), ("C2_ALL_TEAMMATES", mates)]
            for pop, ks in specs:
                for k in ks:
                    kc = (sk, b, cid[k])
                    row = dict(population=pop, **base, comparator=cid[k], comparator_team=tm[k], selected_control=bool(k == o),
                               D_mph=abs(v[i] - v[k]), carblock_time_sep_s=abs(t[k] - t[i]), weight=1.0, pool_size=len(others))
                    row = with_metrics(row, seqs, laps, ka, kc)
                    row = with_metrics(row, seqs_est, laps_est, ka, kc, "derived_")
                    pairs.append(row)
    return pd.DataFrame(rec), pd.DataFrame(pairs)


# ------------------------------------------------------------------ design populations (spec §10)
def team_balanced_pairs(cb, eligible, seqs, laps, cat):
    rows = []
    for (sk, b), g in cb.groupby(["session_key", "block"]):
        if (sk, b) not in eligible:
            continue
        g = g.sort_values("car_id").reset_index(drop=True)
        prs = [(i, j) for i in range(len(g)) for j in range(i + 1, len(g)) if g.team.iloc[i] != g.team.iloc[j]]
        cnt = pd.Series([tuple(sorted((g.team.iloc[i], g.team.iloc[j]))) for i, j in prs]).value_counts()
        for i, j in prs:
            tp = tuple(sorted((g.team.iloc[i], g.team.iloc[j])))
            row = dict(population="TEAM_BALANCED_DIFF", role="PRIMARY", session_key=sk, year=int(g.year.iloc[0]), category=cat[sk], block=int(b),
                       target=g.car_id.iloc[i], target_team=g.team.iloc[i], comparator=g.car_id.iloc[j], comparator_team=g.team.iloc[j],
                       D_mph=abs(g.v.iloc[i] - g.v.iloc[j]), carblock_time_sep_s=abs(g.t.iloc[i] - g.t.iloc[j]), weight=1.0 / cnt[tp])
            rows.append(with_metrics(row, seqs, laps, (sk, b, g.car_id.iloc[i]), (sk, b, g.car_id.iloc[j])))
    return pd.DataFrame(rows)


def adjacent_block_pairs(cb, seqs, laps, cat):
    """Mirror of Phase 4F adjacent_fairness DIFF_TEAM_ADJ selection (same expressions), with laps retained."""
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
                o = others.iloc[(others.t - r.t).abs().argsort().iloc[0]]
                row = dict(population="ADJACENT_BLOCK_DIFF", role="PRIMARY", session_key=sk, year=int(r.year), category=cat[sk], block=int(b),
                           target=r.car_id, target_team=r.team, comparator=o.car_id, comparator_team=o.team, D_mph=abs(r.v - o.v),
                           carblock_time_sep_s=abs(o.t - r.t), weight=1.0)
                rows.append(with_metrics(row, seqs, laps, (sk, b, r.car_id), (sk, b + 1, o.car_id)))
    return pd.DataFrame(rows)


def reweight(A, same_car_sep_min):
    """Phase 4F §8(ii) weights for within-block DIFF_TEAM pairs (same formula)."""
    bins = np.arange(0, 11, 1)
    h_sc = np.histogram(same_car_sep_min.clip(upper=9.999), bins=bins)[0] / max(len(same_car_sep_min), 1)
    sep = (A.carblock_time_sep_s / 60).clip(upper=9.999)
    hb = np.histogram(sep, bins=bins)[0] / max(len(A), 1)
    idx = np.clip(np.digitize(sep, bins) - 1, 0, 9)
    return np.where(hb[idx] > 0, h_sc[idx] / np.where(hb[idx] > 0, hb[idx], 1), 0)


# ------------------------------------------------------------------ summaries
def wq(x, w, q):
    x, w = np.asarray(x, float), np.asarray(w, float)
    if len(x) == 0 or w.sum() == 0:
        return np.nan
    o = np.argsort(x)
    cw = np.cumsum(w[o])
    return float(x[o][min(np.searchsorted(cw, q * cw[-1]), len(x) - 1)])


def adj_summary(P, label, prefix=""):
    w = P.weight.values if "weight" in P else np.ones(len(P))
    code, ilm = P[prefix + "pair_category_code"].values, P[prefix + "intervening_lower_median_lap"].values
    d = dict(population=label, basis="DERIVED_LAPTIME_CHAIN_ESTIMATE" if prefix else "OBSERVED_FEED_SEQUENCE", n_pairs=len(P),
             n_sessions=P.session_key.nunique(), n_blocks=P[["session_key", "block"]].drop_duplicates().shape[0],
             weighted=bool(not np.allclose(w, 1)))
    ws = w.sum()
    d["share_same_update"] = float(w[code == 0].sum() / ws)
    d["share_consecutive_strict"] = float(w[code == 1].sum() / ws)
    for k in CUM_K:
        d[f"share_le{k}_intervening"] = float(w[(code == 0) | (ilm <= k)].sum() / ws)
    for col, nm in [("carblock_time_sep_s", "carblock_sep_s"), (prefix + "median_abs_ts_sep_s", "lap_ts_sep_s"), (prefix + "median_intervening", "intervening")]:
        for q, qn in [(.1, "p10"), (.25, "p25"), (.5, "median"), (.75, "p75"), (.9, "p90")]:
            d[f"{nm}_{qn}"] = wq(P[col], w, q)
        d[f"{nm}_iqr"] = d[f"{nm}_p75"] - d[f"{nm}_p25"]
    return d


def random_pick_expectation(B, prefix=""):
    """Per target: share of its pool in each category; averaged over targets (uniform-random pick from the same pool)."""
    code, ilm = B[prefix + "pair_category_code"], B[prefix + "intervening_lower_median_lap"]
    x = B.assign(_same=code == 0, _cons=code == 1, **{f"_le{k}": (code == 0) | (ilm <= k) for k in CUM_K})
    g = x.groupby(["session_key", "block", "target"])
    per = g[["_same", "_cons"] + [f"_le{k}" for k in CUM_K]].mean()
    d = dict(population="B_RANDOM_PICK_EXPECTATION", basis="DERIVED_LAPTIME_CHAIN_ESTIMATE" if prefix else "OBSERVED_FEED_SEQUENCE",
             n_pairs=len(per), n_sessions=B.session_key.nunique(), n_blocks=B[["session_key", "block"]].drop_duplicates().shape[0], weighted=False,
             share_same_update=float(per._same.mean()), share_consecutive_strict=float(per._cons.mean()))
    for k in CUM_K:
        d[f"share_le{k}_intervening"] = float(per[f"_le{k}"].mean())
    for col, nm in [("carblock_time_sep_s", "carblock_sep_s"), (prefix + "median_abs_ts_sep_s", "lap_ts_sep_s"), (prefix + "median_intervening", "intervening")]:
        pm = g[col].median()
        for q, qn in [(.1, "p10"), (.25, "p25"), (.5, "median"), (.75, "p75"), (.9, "p90")]:
            d[f"{nm}_{qn}"] = float(pm.quantile(q))
        d[f"{nm}_iqr"] = d[f"{nm}_p75"] - d[f"{nm}_p25"]
    d["note"] = "per-target pool shares averaged over targets; quantiles of per-target pool medians"
    return d


def pool_rank(B, prefix=""):
    out = []
    for (sk, b, tg), g in B.groupby(["session_key", "block", "target"]):
        s = g[g.selected_control]
        if s.empty:
            continue
        x = s[prefix + "median_intervening"].iloc[0]
        pool = g[prefix + "median_intervening"]
        out.append(((pool < x).sum() + 0.5 * (pool == x).sum()) / len(pool))
    return np.array(out)


def sb_median(df, col="D_mph"):
    s = df.groupby("session_key")[col].median()
    return (float(s.median()) if len(s) else np.nan), s


# ------------------------------------------------------------------ main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pop = F.population()
    reg, sessions, off, L = F.laps_for(set(pop.session_key))
    L = L.merge(pop[["session_key", "role", "normalized_category"]], on="session_key", how="left")
    cat = dict(zip(pop.session_key, pop.normalized_category))
    roles = {"PRIMARY": list(pop[pop.role == "PRIMARY"].session_key), "ERA_C_SECONDARY": list(pop[pop.role.str.startswith("ERA_C")].session_key)}
    keys_all = roles["PRIMARY"] + roles["ERA_C_SECONDARY"]
    X = chain_estimates(L[L.session_key.isin(keys_all)])

    # sequences (all records in session) + comparable car-block lap timestamps (observed and derived)
    seqs = {sk: Seq(g.ts.values) for sk, g in X.groupby("session_key")}
    seqs_est = {sk: Seq(g.ts_est.values) for sk, g in X.groupby("session_key")}
    comp = X[X.comparable & (X.join_status == "MATCHED") & ~X.technical_partnership_only.fillna(False).astype(bool)].copy()
    comp["block"] = np.floor(comp.ts / 300).astype(int)
    laps = {k: g.ts.values for k, g in comp.groupby(["session_key", "block", "car_id"])}
    laps_est = {k: g.ts_est.values for k, g in comp.groupby(["session_key", "block", "car_id"])}
    # seqs dicts keyed by session; pair_metrics uses seqs[ka[0]]

    # sequence completeness
    sc = []
    for sk, g in X.groupby("session_key"):
        sc.append(dict(session_key=sk, role="PRIMARY" if sk in roles["PRIMARY"] else "ERA_C_SECONDARY", year=int(g.year.iloc[0]), category=cat[sk],
                       lap_records=len(g), distinct_feed_updates=len(seqs[sk].U), share_records_in_shared_update=float((pd.Series(seqs[sk].S).duplicated(keep=False)).mean()),
                       min_update_spacing_s=float(np.diff(seqs[sk].U).min()) if len(seqs[sk].U) > 1 else np.nan,
                       median_update_spacing_s=float(np.median(np.diff(seqs[sk].U))) if len(seqs[sk].U) > 1 else np.nan,
                       share_records_after_capture_gap=float(g.seq_gap_before.mean()), evidence_source=SOURCE_LABEL))
    SC = pd.DataFrame(sc)
    SC.to_csv(OUT / "sequence_completeness.csv", index=False)

    REC, PAIRS = [], []
    cbs = {}
    for role, keys in roles.items():
        cb = F.car_blocks(L[L.session_key.isin(keys)], "comparable", 5)
        cbs[role] = cb
        r, p = reconstruct(cb, role, cat, seqs, laps, seqs_est, laps_est)
        REC.append(r)
        PAIRS.append(p)
    REC, PAIRS = pd.concat(REC, ignore_index=True), pd.concat(PAIRS, ignore_index=True)

    # verify exact reproduction of Phase 4F primary / secondary controls
    C4 = pd.read_csv(P4F / "comparison_pairs.csv", low_memory=False, dtype={"session_key": str})
    ok_all = []
    for role in roles:
        c = C4[(C4.role == role) & (C4.layer == "comparable") & (C4.width_min == 5)]
        for cls, col_b, col_d, col_t in [("DIFF_TEAM", "control", "D_diff_team_target", "abs_target_control_sep_s"),
                                          ("TEAMMATE_OF_TARGET", "teammate", "D_same_team_target", "abs_target_teammate_sep_s")]:
            a = c[c["class"] == cls][["session_key", "block", "car_a", "car_b", "D_mph", "time_sep_min"]].rename(columns={"car_a": "target"})
            m = REC[REC.role == role].astype({"session_key": str}).merge(a, on=["session_key", "block", "target"], how="outer", indicator=True)
            ok = (m._merge == "both").all() and (m[col_b] == m.car_b).all() and np.allclose(m[col_d], m.D_mph) and np.allclose(m[col_t] / 60, m.time_sep_min)
            ok_all.append(dict(role=role, comparison_class=cls, phase4f_rows=len(a), reconstructed_rows=int((REC.role == role).sum()), exact_match=bool(ok)))
    RV = pd.DataFrame(ok_all)
    RV.to_csv(OUT / "reproduction_verification.csv", index=False)
    REC = REC.merge(RV[RV.comparison_class == "DIFF_TEAM"][["role", "exact_match"]].rename(columns={"exact_match": "phase4f_reproduced"}), on="role")
    REC.to_csv(OUT / "primary_control_reconstruction.csv", index=False)

    # design populations (primary)
    BLK = pd.read_csv(P4F / "block_level_contrasts.csv", dtype={"session_key": str})
    bp = BLK[(BLK.role == "PRIMARY") & (BLK.layer == "comparable")]
    eligible = set(zip(bp.session_key, bp.block))
    TB = team_balanced_pairs(cbs["PRIMARY"], eligible, seqs, laps, cat)
    AB = adjacent_block_pairs(cbs["PRIMARY"], seqs, laps, cat)
    A = PAIRS[(PAIRS.role == "PRIMARY") & (PAIRS.population == "A_PRIMARY_CONTROL")].copy()
    sc_sep = C4[(C4.role == "PRIMARY") & (C4.layer == "comparable") & (C4["class"] == "SAME_CAR")].time_sep_min
    RW = A.assign(population="REWEIGHTED_DIFF", weight=reweight(A, sc_sep))
    ALLP = pd.concat([PAIRS, TB.assign(selected_control=False), AB.assign(selected_control=True), RW], ignore_index=True)
    ALLP["evidence_source"] = SOURCE_LABEL
    ALLP.to_csv(OUT / "timing_sequence_adjacency.csv", index=False)

    # verify design populations against Phase 4F fairness summaries
    FA = pd.read_csv(P4F / "same_car_fairness.csv")
    fa_adj = FA[(FA.construction == "ADJACENT_BLOCK_ALL_CLASSES") & (FA.layer == "comparable") & (FA["class"] == "DIFF_TEAM_ADJ")].iloc[0]
    fa_rw = FA[(FA.construction == "TIME_SEPARATION_REWEIGHTED_TO_SAME_CAR") & (FA.layer == "comparable") & (FA["class"] == "DIFF_TEAM")].iloc[0]
    dv = [dict(population="ADJACENT_BLOCK_DIFF", phase4f_n=int(fa_adj.n), phase4g_n=len(AB), phase4f_session_balanced_D=fa_adj.session_balanced_median,
               phase4g_session_balanced_D=sb_median(AB)[0]),
          dict(population="REWEIGHTED_DIFF", phase4f_n=int(fa_rw.n), phase4g_n=len(RW), phase4f_pooled_weighted_D=fa_rw.pooled_median,
               phase4g_pooled_weighted_D=F.wmedian(RW.D_mph, RW.weight))]
    tbm = TB.groupby(["session_key", "block", TB.apply(lambda r: tuple(sorted((r.target_team, r.comparator_team))), axis=1)]).D_mph.median().groupby(level=[0, 1]).median()
    chk = bp.set_index(["session_key", "block"]).team_balanced_D_diff
    dv.append(dict(population="TEAM_BALANCED_DIFF", phase4f_n=len(chk), phase4g_n=len(tbm), team_balanced_block_values_match=bool(np.allclose(tbm.reindex(chk.index).values, chk.values))))
    pd.DataFrame(dv).to_csv(OUT / "design_population_verification.csv", index=False)

    # ---------------- adjacency distribution summary (4G.6)
    rows = []
    for role in roles:
        P = PAIRS[PAIRS.role == role]
        for prefix in ["", "derived_"]:
            for popn in ["A_PRIMARY_CONTROL", "B_ELIGIBLE_CANDIDATES", "C1_TEAMMATE_OF_TARGET", "C2_ALL_TEAMMATES"]:
                rows.append(dict(role=role, **adj_summary(P[P.population == popn], popn, prefix)))
            B = P[P.population == "B_ELIGIBLE_CANDIDATES"]
            rows.append(dict(role=role, **random_pick_expectation(B, prefix)))
            pr = pool_rank(B, prefix)
            rows.append(dict(role=role, population="A_POOL_PERCENTILE_RANK", basis="DERIVED_LAPTIME_CHAIN_ESTIMATE" if prefix else "OBSERVED_FEED_SEQUENCE",
                             n_pairs=len(pr), intervening_median=float(np.median(pr)), intervening_p25=float(np.quantile(pr, .25)), intervening_p75=float(np.quantile(pr, .75)),
                             note="selected control's percentile rank of median_intervening within its pool (0 = most adjacent; 0.5 = random expectation)"))
    ADS = pd.DataFrame(rows)
    ADS.to_csv(OUT / "adjacency_distribution_summary.csv", index=False)

    # ---------------- D by adjacency stratum (4G.8), population B
    st_rows = []
    for role in roles:
        B = PAIRS[(PAIRS.role == role) & (PAIRS.population == "B_ELIGIBLE_CANDIDATES")].copy()
        B["NO_INTERVENING"] = B.pair_category_code <= 1
        B["ts_bin"] = pd.cut(B.carblock_time_sep_s, TS_BINS, labels=TS_LABELS).astype(str)
        years = sorted(B.year.unique())
        for stype, col, levels in [("SEQUENCE", "pair_category", CATS + ["NO_INTERVENING"]), ("TIMESTAMP_CARBLOCK_SEP", "ts_bin", TS_LABELS)]:
            for lev in levels:
                sub = B[B.NO_INTERVENING] if lev == "NO_INTERVENING" else B[B[col] == lev]
                for scope in ["ALL"] + [str(y) for y in years]:
                    s = sub if scope == "ALL" else sub[sub.year == int(scope)]
                    sbm, sv = sb_median(s)
                    st_rows.append(dict(role=role, stratum_type=stype, stratum=lev, scope=scope, n_pairs=len(s), n_sessions=s.session_key.nunique(),
                                        n_blocks=s[["session_key", "block"]].drop_duplicates().shape[0], D_p10=s.D_mph.quantile(.1), D_p25=s.D_mph.quantile(.25),
                                        D_median=s.D_mph.median(), D_p75=s.D_mph.quantile(.75), D_p90=s.D_mph.quantile(.9), D_session_balanced_median=sbm))
        # within-target paired diagnostic
        pt = []
        for (sk, b, tg), g in B.groupby(["session_key", "block", "target"]):
            ni, gt = g[g.NO_INTERVENING], g[g.pair_category == "BETWEEN_GT5"]
            if len(ni) and len(gt):
                pt.append(dict(session_key=sk, year=g.year.iloc[0], d=gt.D_mph.median() - ni.D_mph.median()))
        PT = pd.DataFrame(pt)
        for scope in ["ALL"] + [str(y) for y in years]:
            s = PT if scope == "ALL" or PT.empty else PT[PT.year == int(scope)]
            sbm, sv = sb_median(s, "d") if len(s) else (np.nan, pd.Series(dtype=float))
            st_rows.append(dict(role=role, stratum_type="WITHIN_TARGET_PAIRED", stratum="D(GT5) - D(NO_INTERVENING)", scope=scope, n_pairs=len(s),
                                n_sessions=s.session_key.nunique() if len(s) else 0, D_median=s.d.median() if len(s) else np.nan, D_session_balanced_median=sbm,
                                share_positive=float((s.d > 0).mean()) if len(s) else np.nan))
        # per-session S2 contrast
        for sk, g in B.groupby("session_key"):
            ni, gt = g[g.NO_INTERVENING], g[g.pair_category == "BETWEEN_GT5"]
            st_rows.append(dict(role=role, stratum_type="SESSION_CONTRAST", stratum="D(GT5) - D(NO_INTERVENING)", scope=sk, n_pairs=len(ni) + len(gt),
                                n_no_intervening=len(ni), n_gt5=len(gt), D_median=(gt.D_mph.median() - ni.D_mph.median()) if len(ni) and len(gt) else np.nan,
                                eligible_for_S2_session_rule=bool(len(ni) >= 3 and len(gt) >= 3), year=int(g.year.iloc[0])))
    ST = pd.DataFrame(st_rows)
    ST.to_csv(OUT / "different_team_adjacency_strata.csv", index=False)

    # ---------------- negative vs positive blocks (4G.9)
    Ap = PAIRS[(PAIRS.role == "PRIMARY") & (PAIRS.population == "A_PRIMARY_CONTROL")]
    Bp = PAIRS[(PAIRS.role == "PRIMARY") & (PAIRS.population == "B_ELIGIBLE_CANDIDATES")]
    exp_blk = Bp.assign(ni=Bp.pair_category_code <= 1).groupby(["session_key", "block", "target"]).ni.mean().groupby(level=[0, 1]).median()
    nb = []
    for (sk, b), g in Ap.groupby(["session_key", "block"]):
        rb = bp[(bp.session_key == sk) & (bp.block == b)].iloc[0]
        ctl = REC[(REC.role == "PRIMARY") & (REC.session_key == sk) & (REC.block == b)]
        ni = float((g.pair_category_code <= 1).mean())
        nb.append(dict(level="BLOCK", session_key=sk, year=int(g.year.iloc[0]), category=cat[sk], block=int(b), delta_block=rb.delta_block,
                       group="NEGATIVE" if rb.delta_block < 0 else ("POSITIVE" if rb.delta_block > 0 else "ZERO"), targets=len(g),
                       median_control_carblock_sep_s=g.carblock_time_sep_s.median(), median_control_lap_ts_sep_s=g.median_abs_ts_sep_s.median(),
                       median_control_intervening=g.median_intervening.median(), share_controls_no_intervening=ni,
                       pool_expectation_no_intervening=float(exp_blk.get((sk, b), np.nan)), excess_no_intervening=ni - float(exp_blk.get((sk, b), np.nan)),
                       median_pool_size=float(ctl.candidate_pool_size.median()), control_reuse_ratio=len(ctl) / ctl.control.nunique()))
    NB = pd.DataFrame(nb)
    grp = NB.groupby("group").agg(blocks=("block", "size"), sessions=("session_key", "nunique"), median_control_carblock_sep_s=("median_control_carblock_sep_s", "median"),
                                  median_control_lap_ts_sep_s=("median_control_lap_ts_sep_s", "median"), median_control_intervening=("median_control_intervening", "median"),
                                  share_controls_no_intervening=("share_controls_no_intervening", "median"), pool_expectation_no_intervening=("pool_expectation_no_intervening", "median"),
                                  excess_no_intervening=("excess_no_intervening", "median"), median_pool_size=("median_pool_size", "median"),
                                  control_reuse_ratio=("control_reuse_ratio", "median"), targets=("targets", "sum")).reset_index().assign(level="GROUP_MEDIAN_OF_BLOCKS")
    pd.concat([grp, NB], ignore_index=True).to_csv(OUT / "negative_positive_block_diagnostics.csv", index=False)

    # ---------------- control reuse (4G.10)
    ru = []
    for role in roles:
        R = REC[REC.role == role]
        Ar = PAIRS[(PAIRS.role == role) & (PAIRS.population == "A_PRIMARY_CONTROL")]
        use = R.groupby(["session_key", "block", "control"]).size().rename("targets_per_control").reset_index()
        Ar = Ar.merge(use.rename(columns={"control": "comparator"}), on=["session_key", "block", "comparator"])
        ru.append(dict(role=role, level="OVERALL", scope="ALL", targets=len(R), unique_control_carblocks=len(use), unique_control_cars=R.control.nunique(),
                       mean_targets_per_control=use.targets_per_control.mean(), median_targets_per_control=use.targets_per_control.median(),
                       max_targets_per_control=int(use.targets_per_control.max()), share_controls_reused_ge2=float((use.targets_per_control >= 2).mean()),
                       share_targets_with_reused_control=float((Ar.targets_per_control >= 2).mean()),
                       max_control_car_appearances=int(R.control.value_counts().max())))
        for k in range(1, int(use.targets_per_control.max()) + 1):
            ru.append(dict(role=role, level="REUSE_DISTRIBUTION", scope=f"{k} targets", unique_control_carblocks=int((use.targets_per_control == k).sum())))
        for lvl, col in [("YEAR", "year"), ("SESSION", "session_key")]:
            for s, g in R.groupby(col):
                u = g.groupby(["session_key", "block", "control"]).size()
                ru.append(dict(role=role, level=lvl, scope=str(s), targets=len(g), unique_control_carblocks=len(u), unique_control_cars=g.control.nunique(),
                               mean_targets_per_control=u.mean(), max_targets_per_control=int(u.max()), share_controls_reused_ge2=float((u >= 2).mean())))
        for lab, s in [("HIGH_REUSE_GE3", Ar[Ar.targets_per_control >= 3]), ("REUSE_1_2", Ar[Ar.targets_per_control < 3])]:
            ru.append(dict(role=role, level="ADJACENCY_BY_REUSE", scope=lab, targets=len(s), share_no_intervening=float((s.pair_category_code <= 1).mean()) if len(s) else np.nan,
                           median_carblock_sep_s=s.carblock_time_sep_s.median(), median_intervening=s.median_intervening.median(),
                           median_pool_size=s.pool_size.median()))
    pd.DataFrame(ru).to_csv(OUT / "control_reuse_audit.csv", index=False)

    # ---------------- design population comparison (4G.11/12)
    dp = []
    for lab, P in [("A_PRIMARY_CONTROL", Ap), ("TEAM_BALANCED_DIFF", TB), ("ADJACENT_BLOCK_DIFF", AB), ("REWEIGHTED_DIFF", RW),
                   ("C1_TEAMMATE_OF_TARGET", PAIRS[(PAIRS.role == "PRIMARY") & (PAIRS.population == "C1_TEAMMATE_OF_TARGET")])]:
        d = adj_summary(P, lab)
        w = P.weight.values
        ct = P.groupby("comparator_team").weight.sum() / w.sum()
        app = pd.concat([P[["session_key", "block", "target"]].rename(columns={"target": "c"}), P[["session_key", "block", "comparator"]].rename(columns={"comparator": "c"})]).value_counts()
        d.update(distinct_comparator_teams=int(P.comparator_team.nunique()), largest_single_comparator_team_share=float(ct.max()),
                 distinct_target_teams=int(P.target_team.nunique()), max_carblock_appearances=int(app.max()), median_carblock_appearances=float(app.median()),
                 blocks_covered=P[["session_key", "block"]].drop_duplicates().shape[0], weighted_D_median_for_reference=F.wmedian(P.D_mph, w),
                 comparator_team_shares_alphabetical="; ".join(f"{k}={v:.3f}" for k, v in sorted(ct.items())))
        dp.append(d)
    pd.DataFrame(dp).to_csv(OUT / "design_population_comparison.csv", index=False)

    # ---------------- year / session-category adjacency (4G.7)
    YS = pd.read_csv(P4F / "year_sensitivity.csv")
    CT = pd.read_csv(P4F / "session_type_sensitivity.csv")
    ya = []
    for role in roles:
        P = PAIRS[PAIRS.role == role]
        for lvl, col in [("YEAR", "year"), ("CATEGORY", "category"), ("SESSION", "session_key")]:
            for s, g in P.groupby(col):
                a, b_, c1 = g[g.population == "A_PRIMARY_CONTROL"], g[g.population == "B_ELIGIBLE_CANDIDATES"], g[g.population == "C1_TEAMMATE_OF_TARGET"]
                if a.empty:
                    continue
                e = random_pick_expectation(b_)
                ref = np.nan
                if lvl == "YEAR":
                    y = YS[(YS.layer == "comparable") & (YS.year == int(s))]
                    ref = y.session_balanced_delta.iloc[0] if len(y) else np.nan
                elif lvl == "CATEGORY" and role == "PRIMARY":
                    y = CT[(CT.layer == "comparable") & (CT.category == s)]
                    ref = y.session_balanced_delta.iloc[0] if len(y) else np.nan
                elif lvl == "SESSION":
                    ref = bp[bp.session_key == s].delta_block.median() if role == "PRIMARY" else np.nan
                ya.append(dict(role=role, level=lvl, scope=str(s), targets=len(a), sessions=a.session_key.nunique(),
                               A_share_no_intervening=float((a.pair_category_code <= 1).mean()), A_share_same_update=float((a.pair_category_code == 0).mean()),
                               B_expected_share_no_intervening=e["share_le0_intervening"], A_minus_B_expectation=float((a.pair_category_code <= 1).mean()) - e["share_le0_intervening"],
                               C1_share_no_intervening=float((c1.pair_category_code <= 1).mean()),
                               A_minus_C1_share_no_intervening=float((a.pair_category_code <= 1).mean()) - float((c1.pair_category_code <= 1).mean()),
                               A_median_carblock_sep_s=a.carblock_time_sep_s.median(), C1_median_carblock_sep_s=c1.carblock_time_sep_s.median(),
                               A_median_intervening=a.median_intervening.median(), C1_median_intervening=c1.median_intervening.median(),
                               phase4f_session_balanced_delta_reference=ref))
    pd.DataFrame(ya).to_csv(OUT / "year_session_adjacency.csv", index=False)

    # ---------------- case evaluation (spec §11), PRIMARY only
    Pp = PAIRS[PAIRS.role == "PRIMARY"]
    gate = float(Ap.pair_category.notna().mean()), float(Bp.pair_category.notna().mean())
    G = gate[0] >= 0.9 and gate[1] >= 0.9
    a_share = float((Ap.pair_category_code <= 1).mean())
    E = random_pick_expectation(Bp)["share_le0_intervening"]
    S1 = "SUBSTANTIAL" if (a_share - E >= 0.20 and a_share / E >= 2) else ("MATERIAL" if a_share - E >= 0.05 else "NOT_MATERIAL")
    stp = ST[(ST.role == "PRIMARY")]
    d_ni = stp[(stp.stratum_type == "SEQUENCE") & (stp.stratum == "NO_INTERVENING")].set_index("scope").D_session_balanced_median
    d_gt = stp[(stp.stratum_type == "SEQUENCE") & (stp.stratum == "BETWEEN_GT5")].set_index("scope").D_session_balanced_median
    dS2 = float(d_gt["ALL"] - d_ni["ALL"])
    yrs_pos = all((d_gt[str(y)] - d_ni[str(y)]) > 0 for y in [2023, 2024])
    sess = stp[(stp.stratum_type == "SESSION_CONTRAST") & stp.eligible_for_S2_session_rule.fillna(False).astype(bool)]
    sess_share = float((sess.D_median > 0).mean()) if len(sess) else np.nan
    wt = stp[(stp.stratum_type == "WITHIN_TARGET_PAIRED") & (stp.scope == "ALL")].D_session_balanced_median.iloc[0]
    S2 = "CONSISTENT" if (dS2 >= 0.25 and yrs_pos and sess_share >= 2 / 3 and wt > 0) else ("MODEST_OR_INCONSISTENT" if dS2 > 0 else "NONE")
    case = "D" if not G else ("A" if (S1 == "SUBSTANTIAL" and S2 == "CONSISTENT") else ("C" if (S1 == "NOT_MATERIAL" or S2 == "NONE") else "B"))
    # agreement diagnostics (do not change the case)
    Ad, Bd = Ap, Bp
    a_der = float((Ad.derived_pair_category_code <= 1).mean())
    E_der = random_pick_expectation(Bd, "derived_")["share_le0_intervening"]
    As = PAIRS[(PAIRS.role == "ERA_C_SECONDARY") & (PAIRS.population == "A_PRIMARY_CONTROL")]
    Bs = PAIRS[(PAIRS.role == "ERA_C_SECONDARY") & (PAIRS.population == "B_ELIGIBLE_CANDIDATES")]
    sts = ST[ST.role == "ERA_C_SECONDARY"]
    d25 = float(sts[(sts.stratum_type == "SEQUENCE") & (sts.stratum == "BETWEEN_GT5") & (sts.scope == "ALL")].D_session_balanced_median.iloc[0]
                - sts[(sts.stratum_type == "SEQUENCE") & (sts.stratum == "NO_INTERVENING") & (sts.scope == "ALL")].D_session_balanced_median.iloc[0])
    ce = [("gate_share_A_defined", gate[0]), ("gate_share_B_defined", gate[1]), ("gate_G_pass", G),
          ("S1_A_share_no_intervening", a_share), ("S1_B_random_pick_expectation", E), ("S1_difference", a_share - E), ("S1_ratio", a_share / E), ("S1_level", S1),
          ("S2_sb_D_no_intervening", float(d_ni["ALL"])), ("S2_sb_D_gt5", float(d_gt["ALL"])), ("S2_delta", dS2),
          ("S2_2023_delta", float(d_gt["2023"] - d_ni["2023"])), ("S2_2024_delta", float(d_gt["2024"] - d_ni["2024"])), ("S2_both_years_positive", yrs_pos),
          ("S2_sessions_eligible", len(sess)), ("S2_share_sessions_positive", sess_share), ("S2_within_target_sb_median", float(wt)), ("S2_level", S2),
          ("CASE", case),
          ("agreement_derived_A_share_no_intervening", a_der), ("agreement_derived_B_expectation", E_der),
          ("agreement_2025_A_share_no_intervening", float((As.pair_category_code <= 1).mean())),
          ("agreement_2025_B_expectation", random_pick_expectation(Bs)["share_le0_intervening"]), ("agreement_2025_S2_delta", d25),
          ("phase4f_case_unchanged", pd.read_csv(P4F / "case_evaluation.csv").set_index("criterion").value["CASE"]),
          ("phase4h_justified", "YES" if case in ("A", "B") else "NO")]
    pd.DataFrame(ce, columns=["criterion", "value"]).to_csv(OUT / "phase4g_case_evaluation.csv", index=False)
    print(RV.to_string())
    print(pd.read_csv(OUT / "design_population_verification.csv").to_string())
    print(pd.DataFrame(ce, columns=["criterion", "value"]).to_string())


if __name__ == "__main__":
    main()
