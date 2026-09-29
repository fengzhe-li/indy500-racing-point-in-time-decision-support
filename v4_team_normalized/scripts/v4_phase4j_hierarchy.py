"""V4 Phase 4J: FINAL pre-registered performance-control hierarchy (implements output/phase4j/phase4j_final_hierarchy_spec.md, commit 28af221).

Empirical control hierarchy in the restricted Phase 4H/4I-supported population. Not causal, not a team effect, no ranking,
no nearest-time selection, no model. Order: Tier 1 2023-24 primary -> case written -> Tier 2 sensitivity -> 2025 replication.
Lap records = Timing71 archived recordings of the INDYCAR live timing feed (third-party).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4j"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4g_adjacency as G  # noqa: E402
import v4_phase4i_support as S  # noqa: E402

SEED, B = 20261001, 2000
SESS = {"PRIMARY_TIER1_2023_2024": ("TIER1_STRICT", ["6199", "6207", "6208", "6375", "6378", "6380", "6387", "6388"]),
        "TIER2_SENSITIVITY_2023_2024": ("TIER2_EXTENDED", ["6198", "6199", "6200", "6207", "6208", "6375", "6378", "6380", "6387", "6388"]),
        "REPLICATION_2025_TIER1": ("TIER1_STRICT", ["6651", "6653", "6654", "6655", "6662", "6663"])}
LABEL = {"PRIMARY_TIER1_2023_2024": "PRIMARY", "TIER2_SENSITIVITY_2023_2024": "EXTENDED MEASUREMENT-VALIDITY SENSITIVITY",
         "REPLICATION_2025_TIER1": "2025 HYBRID-ERA SECONDARY REPLICATION"}
V225, LT225 = 225.0, 2.5 * 3600 / 225.0


def build(P, seqs, tier, sessions, drop_team=None):
    E = P[P.cls.isin(S.TIERS[tier]) & (P.join_status == "MATCHED") & P.session_key.isin(sessions)].copy()
    if drop_team is not None:
        E = E[E.canonical_engineering_team != drop_team]
    if E.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    cb = S.carblocks(E)
    v = E.groupby(["session_key", "block", "car_id"]).speed_mph.median().rename("v").reset_index()
    cb = cb.merge(v, on=["session_key", "block", "car_id"])
    laps = {k: g.ts.values for k, g in E.groupby(["session_key", "block", "car_id"])}
    # same-car local repeats: same session, car, stint_key, consecutive blocks
    nxt = cb.assign(block=cb.block - 1)[["session_key", "block", "car_id", "stint_key", "v", "t", "cb_id", "composition"]]
    sc = cb.merge(nxt, on=["session_key", "block", "car_id", "stint_key"], suffixes=("", "_next"))
    SC = pd.DataFrame(dict(session_key=sc.session_key, year=sc.year, car_id=sc.car_id, team=sc.team, block=sc.block, cb_a=sc.cb_id, cb_b=sc.cb_id_next,
                           comp_a=sc.composition, comp_b=sc.composition_next, time_sep_s=(sc.t_next - sc.t).abs(), D_mph=(sc.v - sc.v_next).abs()))
    # same-team contexts and different-team candidates
    ctx, cand = [], []
    cache = {}

    def cat(sk, b, a, c):
        k = (sk, b, a, c)
        if k not in cache:
            cache[k] = G.pair_metrics(seqs[sk], laps[(sk, b, a)], laps[(sk, b, c)])["pair_category_code"]
        return cache[k]
    for (sk, b), g in cb.groupby(["session_key", "block"]):
        g = g.reset_index(drop=True)
        for i in range(len(g)):
            if not g.st_eligible.iloc[i]:
                continue
            for j in range(len(g)):
                if i == j or not g.st_eligible.iloc[j] or g.team.iloc[j] != g.team.iloc[i]:
                    continue
                ci, cj = g.car_id.iloc[i], g.car_id.iloc[j]
                cij = cat(sk, b, ci, cj)
                cid = f"{sk}|{b}|{ci}>{cj}"
                ks = [k for k in range(len(g)) if g.team.iloc[k] != g.team.iloc[i]]
                adm = []
                for k in ks:
                    cik = cat(sk, b, ci, g.car_id.iloc[k])
                    d = abs(g.v.iloc[i] - g.v.iloc[k])
                    cand.append(dict(context_id=cid, session_key=sk, year=int(g.year.iloc[i]), block=int(b), target=ci, candidate=g.car_id.iloc[k], candidate_team=g.team.iloc[k],
                                     candidate_comp=g.composition.iloc[k], candidate_category=G.CATS[cik], context_category=G.CATS[cij], admissible=cik == cij,
                                     time_sep_s=abs(g.t.iloc[k] - g.t.iloc[i]), D_mph=d))
                    if cik == cij:
                        adm.append(d)
                ctx.append(dict(context_id=cid, session_key=sk, year=int(g.year.iloc[i]), category=g.category.iloc[i], block=int(b), target=ci, teammate=cj,
                                team=g.team.iloc[i], target_cb=g.cb_id.iloc[i], teammate_cb=g.cb_id.iloc[j], comp_target=g.composition.iloc[i], comp_teammate=g.composition.iloc[j],
                                adjacency_category=G.CATS[cij], teammate_time_sep_s=abs(g.t.iloc[j] - g.t.iloc[i]), n_candidates=len(ks), n_admissible=len(adm),
                                in_common_support=len(adm) >= 1, D_same_team=abs(g.v.iloc[i] - g.v.iloc[j]),
                                D_diff_team_ctx=float(np.median(adm)) if adm else np.nan))
    CX = pd.DataFrame(ctx)
    CA = pd.DataFrame(cand)
    if len(CX):
        CX["paired_C2"] = CX.D_diff_team_ctx - CX.D_same_team
    return CX, SC, CA


def sessions_table(CX, SC):
    rows = []
    cs = CX[CX.in_common_support] if len(CX) else CX
    for sk in sorted(set(cs.session_key if len(cs) else []) | set(SC.session_key if len(SC) else [])):
        c, s = (cs[cs.session_key == sk] if len(cs) else cs), (SC[SC.session_key == sk] if len(SC) else SC)
        r = dict(session_key=sk, contexts=len(c), same_car_pairs=len(s), evaluable=bool(len(c) >= 1 and len(s) >= 1),
                 D_same_car=s.D_mph.median() if len(s) else np.nan, D_same_team=c.D_same_team.median() if len(c) else np.nan,
                 D_diff_team=c.D_diff_team_ctx.median() if len(c) else np.nan)
        r["C1"] = r["D_same_team"] - r["D_same_car"]
        r["C2"] = c.paired_C2.median() if len(c) else np.nan
        r["C3"] = r["D_diff_team"] - r["D_same_car"]
        rows.append(r)
    return pd.DataFrame(rows, columns=["session_key", "contexts", "same_car_pairs", "evaluable", "D_same_car", "D_same_team", "D_diff_team", "C1", "C2", "C3"])


def summarize(ST):
    e = ST[ST.evaluable]
    out = dict(evaluable_sessions=len(e))
    for k in ["D_same_car", "D_same_team", "D_diff_team", "C1", "C2", "C3"]:
        out[k] = float(e[k].median()) if len(e) else np.nan
    for k in ["C1", "C2", "C3"]:
        out[f"share_sessions_{k}_pos"] = float((e[k] > 0).mean()) if len(e) else np.nan
        out[f"share_sessions_{k}_neg"] = float((e[k] < 0).mean()) if len(e) else np.nan
    out["C1_from_layer_medians"] = out["D_same_team"] - out["D_same_car"]
    out["C2_from_layer_medians"] = out["D_diff_team"] - out["D_same_team"]
    return out


def boot(vals):
    v = np.asarray(vals, float)
    if len(v) < 2:
        return np.nan, np.nan
    rng = np.random.default_rng(SEED)
    d = [np.median(rng.choice(v, len(v), replace=True)) for _ in range(B)]
    return float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def analyse(P, seqs, key):
    tier, sessions = SESS[key]
    CX, SC, CA = build(P, seqs, tier, sessions)
    ST = sessions_table(CX, SC)
    sm = summarize(ST)
    e = ST[ST.evaluable]
    for k in ["C1", "C2", "C3"]:
        sm[f"{k}_boot_lo"], sm[f"{k}_boot_hi"] = boot(e[k].values)
    sm["common_support_contexts"] = int(CX.in_common_support.sum()) if len(CX) else 0
    sm["all_contexts"] = len(CX)
    # LOSO
    lo = []
    for sk in e.session_key:
        s2 = summarize(ST[ST.session_key != sk])
        lo.append(dict(analysis=key, dropped_session=sk, evaluable_sessions=s2["evaluable_sessions"], C1=s2["C1"], C2=s2["C2"], C3=s2["C3"]))
    LO = pd.DataFrame(lo)
    # LOTO
    teams = sorted(CX[CX.in_common_support].team.unique()) if len(CX) else []
    lt = []
    for t in teams:
        cx2, sc2, _ = build(P, seqs, tier, sessions, drop_team=t)
        st2 = sessions_table(cx2, sc2) if len(cx2) or len(sc2) else pd.DataFrame(columns=["evaluable"])
        s2 = summarize(st2) if len(st2) else dict(evaluable_sessions=0, C1=np.nan, C2=np.nan, C3=np.nan)
        lt.append(dict(analysis=key, dropped_team=t, evaluable_sessions=s2["evaluable_sessions"], feasible=s2["evaluable_sessions"] >= 1,
                       common_support_contexts=int(cx2.in_common_support.sum()) if len(cx2) else 0, C1=s2["C1"], C2=s2["C2"], C3=s2["C3"]))
    LT = pd.DataFrame(lt)
    return CX, SC, CA, ST, sm, LO, LT


def status(sm, LO, LT, k):
    lf = LT[LT.feasible] if len(LT) else LT
    c = sm[k]
    if c > 0 and sm[f"share_sessions_{k}_pos"] >= 0.75 and (LO[k] > 0).all() and (lf[k] > 0).all():
        return "POSITIVE_CONSISTENT"
    if c < 0 and sm[f"share_sessions_{k}_neg"] >= 0.75 and (LO[k] < 0).all() and (lf[k] < 0).all():
        return "NEGATIVE_CONSISTENT"
    return "INCONSISTENT"


def case_of(sm, LO, LT):
    if sm["evaluable_sessions"] < 5 or sm["common_support_contexts"] < 20:
        return "E", "n/a", "n/a"
    s1, s2 = status(sm, LO, LT, "C1"), status(sm, LO, LT, "C2")
    if "NEGATIVE_CONSISTENT" in (s1, s2):
        return "D", s1, s2
    if s1 == s2 == "POSITIVE_CONSISTENT":
        return "A", s1, s2
    if (s1 == "POSITIVE_CONSISTENT") != (s2 == "POSITIVE_CONSISTENT") or (sm["C1"] > 0 and sm["C2"] > 0):
        return "B", s1, s2
    return "C", s1, s2


def cov(CX, SC, CA, key):
    rows = []
    if len(CX):
        cs = CX[CX.in_common_support]
        rows.append(dict(analysis=key, item="same-team oriented contexts (all)", value=len(CX)))
        rows.append(dict(analysis=key, item="same-team contexts in strict common support", value=len(cs)))
        rows.append(dict(analysis=key, item="contexts with >=3 admissible candidates (descriptive)", value=int((CX.n_admissible >= 3).sum())))
        for c in G.CATS:
            rows.append(dict(analysis=key, item=f"contexts {c}: all / in support", value=f"{int((CX.adjacency_category == c).sum())} / {int((cs.adjacency_category == c).sum())}"))
        up = cs.apply(lambda r: tuple(sorted((r.target, r.teammate))), axis=1) if len(cs) else pd.Series(dtype=object)
        rows += [dict(analysis=key, item="distinct unordered teammate pairs in support", value=up.nunique()),
                 dict(analysis=key, item="cars in support contexts", value=len(set(cs.target) | set(cs.teammate))),
                 dict(analysis=key, item="teams in support contexts", value=cs.team.nunique()),
                 dict(analysis=key, item="team-years in support", value=len({f"{y}|{t}" for y, t in zip(cs.year, cs.team)})),
                 dict(analysis=key, item="sessions with support contexts", value=cs.session_key.nunique()),
                 dict(analysis=key, item="blocks with support contexts", value=cs[["session_key", "block"]].drop_duplicates().shape[0]),
                 dict(analysis=key, item="max single-team share of support contexts", value=float(cs.team.value_counts(normalize=True).max()) if len(cs) else np.nan),
                 dict(analysis=key, item="max single-session share of support contexts", value=float(cs.session_key.value_counts(normalize=True).max()) if len(cs) else np.nan),
                 dict(analysis=key, item="same-team time separation median (s)", value=float(cs.teammate_time_sep_s.median()) if len(cs) else np.nan),
                 dict(analysis=key, item="max reuse of one target car-block across support contexts", value=int(cs.target_cb.value_counts().max()) if len(cs) else 0)]
        a = CA[CA.context_id.isin(cs.context_id)] if len(cs) else CA.iloc[:0]
        rows += [dict(analysis=key, item="different-team candidate pairs (all contexts, before aggregation)", value=len(CA)),
                 dict(analysis=key, item="admissible different-team candidates in support contexts (before aggregation)", value=int(a.admissible.sum())),
                 dict(analysis=key, item="distinct admissible candidate car-blocks", value=a[a.admissible][["session_key", "block", "candidate"]].drop_duplicates().shape[0]),
                 dict(analysis=key, item="admissible candidate teams", value=a[a.admissible].candidate_team.nunique()),
                 dict(analysis=key, item="admissible candidate time separation median (s)", value=float(a[a.admissible].time_sep_s.median()) if a.admissible.any() else np.nan)]
    if len(SC):
        rows += [dict(analysis=key, item="same-car local pairs", value=len(SC)), dict(analysis=key, item="same-car cars", value=SC.car_id.nunique()),
                 dict(analysis=key, item="same-car sessions", value=SC.session_key.nunique()),
                 dict(analysis=key, item="same-car time separation median (s)", value=float(SC.time_sep_s.median())),
                 dict(analysis=key, item="same-car time separation IQR (s)", value=f"{SC.time_sep_s.quantile(.25):.1f}-{SC.time_sep_s.quantile(.75):.1f}"),
                 dict(analysis=key, item="same-car max car-block reuse", value=int(pd.concat([SC.cb_a, SC.cb_b]).value_counts().max()))]
    return pd.DataFrame(rows)


def composition(CX, SC, CA, key):
    rows = []
    cs = CX[CX.in_common_support]
    for lab, s in [("same-team context (target|teammate)", cs.comp_target + "|" + cs.comp_teammate), ("same-car pair", SC.comp_a + "|" + SC.comp_b),
                   ("admissible candidate", CA[CA.admissible & CA.context_id.isin(cs.context_id)].candidate_comp)]:
        for k, v in s.value_counts(normalize=True).items():
            rows.append(dict(analysis=key, layer=lab, composition=k, share=float(v), n=int((s == k).sum())))
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    P, L = S.load()
    seqs = {sk: G.Seq(g.ts.values) for sk, g in L.groupby("session_key")}
    res = {}
    # ---------------- 1. PRIMARY (Tier 1, 2023-24) -> write, write case
    key = "PRIMARY_TIER1_2023_2024"
    CX, SC, CA, ST, sm, LO, LT = analyse(P, seqs, key)
    case, s1, s2 = case_of(sm, LO, LT)
    res[key] = (CX, SC, CA, ST, sm, LO, LT, case, s1, s2)
    CX.to_csv(OUT / "primary_common_support.csv", index=False)
    SC.to_csv(OUT / "same_car_primary.csv", index=False)
    cov(CX, SC, CA, key).to_csv(OUT / "same_team_primary.csv", index=False)
    CA.to_csv(OUT / "different_team_candidates.csv", index=False)
    CX[["context_id", "session_key", "block", "target", "teammate", "team", "adjacency_category", "n_candidates", "n_admissible", "in_common_support",
        "D_same_team", "D_diff_team_ctx", "paired_C2"]].to_csv(OUT / "different_team_context_aggregate.csv", index=False)
    pd.DataFrame([dict(criterion=k, value=v) for k, v in [("analysis", key), ("pre_result_spec_commit", "28af221"), ("evaluable_sessions", sm["evaluable_sessions"]),
                                                            ("common_support_contexts", sm["common_support_contexts"]), ("C1", sm["C1"]), ("C2", sm["C2"]), ("C3", sm["C3"]),
                                                            ("C1_status", s1), ("C2_status", s2), ("PRIMARY_CASE", case)]]).to_csv(OUT / "case_evaluation.csv", index=False)

    # ---------------- 2. Tier 2 sensitivity, 3. 2025 replication (after primary written)
    for key2 in ["TIER2_SENSITIVITY_2023_2024", "REPLICATION_2025_TIER1"]:
        cx, sc, ca, st, s_, lo, lt = analyse(P, seqs, key2)
        c_, a1, a2 = case_of(s_, lo, lt)
        res[key2] = (cx, sc, ca, st, s_, lo, lt, c_, a1, a2)
    ce = pd.read_csv(OUT / "case_evaluation.csv")
    for key2, lab in [("TIER2_SENSITIVITY_2023_2024", "TIER2_SENSITIVITY_LABEL"), ("REPLICATION_2025_TIER1", "REPLICATION_2025_LABEL")]:
        c_ = res[key2][7]
        ce = pd.concat([ce, pd.DataFrame([dict(criterion=lab, value=("NOT IDENTIFIABLE / INSUFFICIENT SUPPORT (E)" if c_ == "E" else c_) + f" [{LABEL[key2]}; never replaces primary]")])])
    ce.to_csv(OUT / "case_evaluation.csv", index=False)

    # ---------------- tables
    sl, hs, hc, los, lts = [], [], [], [], []
    for key2, (cx, sc, ca, st, s_, lo, lt, c_, a1, a2) in res.items():
        sl.append(st.assign(analysis=key2, role=LABEL[key2]))
        hs.append(dict(analysis=key2, role=LABEL[key2], case=c_, C1_status=a1, C2_status=a2, **s_))
        for r in st[st.evaluable].itertuples(index=False):
            hc.append(dict(analysis=key2, session_key=r.session_key, C1=r.C1, C2=r.C2, C3=r.C3, C1_sign=np.sign(r.C1), C2_sign=np.sign(r.C2)))
        los.append(lo)
        lts.append(lt)
    SL = pd.concat(sl, ignore_index=True)
    HS = pd.DataFrame(hs)
    SL.to_csv(OUT / "session_level_hierarchy.csv", index=False)
    HS[HS.analysis == "PRIMARY_TIER1_2023_2024"].to_csv(OUT / "primary_hierarchy_summary.csv", index=False)
    HS.to_csv(OUT / "hierarchy_summary_all_analyses.csv", index=False)
    HC = pd.DataFrame(hc)
    for key2 in res:
        s_ = res[key2][4]
        HC = pd.concat([HC, pd.DataFrame([dict(analysis=key2, session_key="SESSION_BALANCED_MEDIAN", C1=s_["C1"], C2=s_["C2"], C3=s_["C3"])])], ignore_index=True)
    HC.to_csv(OUT / "hierarchy_contrasts.csv", index=False)
    pd.concat(los, ignore_index=True).to_csv(OUT / "leave_one_session_out.csv", index=False)
    pd.concat(lts, ignore_index=True).to_csv(OUT / "leave_one_team_out.csv", index=False)
    for key2, fname in [("TIER2_SENSITIVITY_2023_2024", "tier2_sensitivity.csv"), ("REPLICATION_2025_TIER1", "replication_2025.csv")]:
        cx, sc, ca, st, s_, lo, lt, c_, a1, a2 = res[key2]
        t = pd.concat([HS[HS.analysis == key2].assign(table="SUMMARY"), st.assign(table="SESSION", analysis=key2), cov(cx, sc, ca, key2).assign(table="COVERAGE"),
                       composition(cx, sc, ca, key2).assign(table="COMPOSITION")], ignore_index=True)
        t.to_csv(OUT / fname, index=False)
    composition(*res["PRIMARY_TIER1_2023_2024"][:3], "PRIMARY_TIER1_2023_2024").to_csv(OUT / "primary_composition.csv", index=False)

    # ---------------- performance-scale context
    ps4i = pd.read_csv(V4 / "output/phase4i/performance_scale_reference.csv")
    rows = []
    for key2 in res:
        s_ = res[key2][4]
        vref = float(P[P.session_key.isin(SESS[key2][1]) & P.cls.isin(S.TIERS[SESS[key2][0]])].speed_mph.median())
        for k in ["D_same_car", "D_same_team", "D_diff_team", "C1", "C2", "C3"]:
            x = s_[k]
            rows.append(dict(analysis=key2, quantity=k, mph=x, pct_of_median_speed=100 * x / vref, laptime_equiv_s_at_225=x / V225 * LT225, median_eligible_speed=vref))
    for r in ps4i.itertuples(index=False):
        val = r.median_sd_mph if pd.notna(r.median_sd_mph) else r.median_abs_delta_mph
        rows.append(dict(analysis="PHASE4I_REFERENCE", quantity=f"{r.reference} [{r.scope}]", mph=val, laptime_equiv_s_at_225=(val / V225 * LT225) if pd.notna(val) else np.nan))
    pd.DataFrame(rows).to_csv(OUT / "performance_scale_context.csv", index=False)
    print(HS.drop(columns=[c for c in HS.columns if c.startswith("share_sessions_C3")]).T.to_string())


if __name__ == "__main__":
    main()
