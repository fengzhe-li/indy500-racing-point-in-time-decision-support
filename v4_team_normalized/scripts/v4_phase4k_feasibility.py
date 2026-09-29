"""V4 Phase 4K: point-in-time teammate prediction FEASIBILITY audit (implements output/phase4k/phase4k_prediction_feasibility_spec.md, dae6856).

Support/identifiability only: no predictions, no errors, no fitting, no predictor comparison. Target movement dv is never computed.
Speeds (v) are only carried for non-missingness. Lap records = Timing71 archived live-feed recordings (third-party).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4k"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4f_hierarchy as F  # noqa: E402
import v4_phase4g_adjacency as G  # noqa: E402
import v4_phase4h_audit as H  # noqa: E402
import v4_phase4i_support as S  # noqa: E402

KEY = ["session_key", "source_id", "car", "stint", "lap_in_stint"]
POPS = {"PRIMARY_TIER1_2023_2024": ("TIER1_STRICT", ["6199", "6207", "6208", "6375", "6378", "6380", "6387", "6388"]),
        "TIER2_2023_2024_EXTENDED": ("TIER2_EXTENDED", ["6198", "6199", "6200", "6207", "6208", "6375", "6378", "6380", "6387", "6388"]),
        "TIER1_2025_SECONDARY": ("TIER1_STRICT", ["6651", "6653", "6654", "6655", "6662", "6663"])}
PTSC_MAX_AGE = 900.0
A_, B_ = "A_PERFORMANCE_COMPARABLE", "B_PLAUSIBLY_PERFORMANCE_COMPARABLE"


# ------------------------------------------------------------------ point-in-time confirmation machinery (Phase 4H rule, info < tau)
def pit_machinery(P):
    pop = F.population()
    reg, sessions, off, L = F.laps_for(set(P.session_key) | set(H.QUAL))
    ren = lambda d: d.merge(pop[["session_key", "role", "normalized_category"]], on="session_key").rename(columns={"normalized_category": "category"})
    Lp, Lq = ren(L[L.session_key.isin(set(P.session_key))]), ren(L[L.session_key.isin(H.QUAL)])
    X = H.inventory(Lp, H.pit_matching(Lp))
    Qa, _, _ = H.qualifying_attempts(H.inventory(Lq, H.pit_matching(Lq)))
    T = H.thresholds(Qa)
    Xc, W = H.classify(X, T)
    Xc["car"] = Xc.car.astype(str)
    W["end_ts"] = Xc.ts.values[W.i0.values + 3]
    W["car_session"] = W.session_key + "|" + W.car_id
    lapwin = {}
    for wi, i0 in enumerate(W.i0.values):
        for p in range(i0, i0 + 4):
            lapwin.setdefault(p, []).append(wi)
    steady = {}
    for q, Ts, TL in [(95, T["T_steady_95"], T["T_level_95"]), (100, T["T_steady_100"], T["T_level_100"])]:
        for cs, g in W[W.r_w <= Ts].groupby("car_session"):
            g = g.sort_values("end_ts")
            steady[(q, cs)] = (g.end_ts.values, np.maximum.accumulate(g.m_w.values))
    pos = pd.Series(np.arange(len(Xc)), index=pd.MultiIndex.from_frame(Xc[KEY]))
    return Xc, W, T, lapwin, steady, pos


def lap_confirmed(p, tau, cls, W, T, lapwin, steady):
    """Unchanged Phase 4H rule with information < tau. A: q=95 thresholds; B: q=100 thresholds (A or B)."""
    qs = [95] if cls == A_ else [95, 100]
    for q in qs:
        Ts, TL = T[f"T_steady_{q}"], T[f"T_level_{q}"]
        for wi in lapwin.get(p, []):
            r_w, m_w, end, cs = W.r_w.values[wi], W.m_w.values[wi], W.end_ts.values[wi], W.car_session.values[wi]
            if end >= tau or r_w > Ts:
                continue
            ends, cm = steady[(q, cs)]
            k = np.searchsorted(ends, tau, "left")
            if k == 0:
                continue
            if m_w >= (1 - TL) * cm[k - 1]:
                return True
    return False


# ------------------------------------------------------------------ physics readings
def ptsc():
    wx = pd.read_csv(V4 / "output/phase4e/inputs/ptsc_event_observations_extracted.csv")
    wx["ts_s"] = (pd.to_datetime(wx.local_ts, utc=True, format="mixed") - pd.Timestamp("1970-01-01", tz="UTC")) / pd.Timedelta(seconds=1)
    wx = wx.dropna(subset=["track_c", "ambient_c"]).sort_values("ts_s").reset_index(drop=True)
    return wx


def reading(wts, x):
    k = np.searchsorted(wts, x, "right") - 1
    if k < 0 or x - wts[k] > PTSC_MAX_AGE:
        return -1
    return int(k)


# ------------------------------------------------------------------ main enumeration
def enumerate_pop(name, P, mach, wx, seqs):
    tier, sessions = POPS[name]
    Xc, W, T, lapwin, steady, pos = mach
    wts = wx.ts_s.values
    E = P[P.cls.isin(S.TIERS[tier]) & (P.join_status == "MATCHED") & P.session_key.isin(sessions)].copy()
    E["xpos"] = pos.reindex(pd.MultiIndex.from_frame(E[KEY])).values
    assert E.xpos.notna().all(), "lap position mapping incomplete"
    cb = S.carblocks(E)
    agg = E.groupby(["session_key", "block", "car_id"]).agg(first_ts=("ts", "min"), avail_ts=("ts", "max"), v=("speed_mph", "median")).reset_index()
    cb = cb.merge(agg, on=["session_key", "block", "car_id"])
    cb["source_ts"] = cb.t
    cb["reading"] = [reading(wts, x) for x in cb.source_ts]
    lapmap = {k: list(zip(g.xpos.values, g.cls.values)) for k, g in E.groupby(["session_key", "block", "car_id"])}
    laps_ts = {k: g.ts.values for k, g in E.groupby(["session_key", "block", "car_id"])}
    cb = cb.sort_values(["session_key", "car_id", "block"]).reset_index(drop=True)
    cb["prev_idx"] = cb.groupby(["session_key", "car_id"]).cumcount()
    idx = {(r.session_key, r.car_id, r.block): i for i, r in enumerate(cb.itertuples(index=False))}
    seq = {k: g.index.values for k, g in cb.groupby(["session_key", "car_id"])}
    conf_cache = {}

    def cb_confirmed(i, tau):
        k = (i, tau)
        if k not in conf_cache:
            r = cb.iloc[i]
            conf_cache[k] = all(lap_confirmed(int(p), tau, c, W, T, lapwin, steady) for p, c in lapmap[(r.session_key, r.block, r.car_id)])
        return conf_cache[k]

    def movement(car_rows, tau):
        """latest eligible car-block fully available before tau (s1) and its predecessor (s0), by chronology only."""
        avail = cb.avail_ts.values[car_rows]
        ok = np.where(avail < tau)[0]
        if len(ok) == 0:
            return None, None
        k = ok[-1]
        s1 = car_rows[k]
        s0 = car_rows[k - 1] if k >= 1 else None
        return s0, s1

    ev, tsig, psig = [], [], []
    for (sk, car), rows in seq.items():
        for n in range(1, len(rows)):
            i0, i1 = rows[n - 1], rows[n]
            r0, r1 = cb.iloc[i0], cb.iloc[i1]
            eid = f"{name}|{sk}|{car}|{int(r1.block)}"
            for cut, tau in [("PRIMARY", r1.first_ts), ("CONSERVATIVE", r0.avail_ts)]:
                team = r0.team
                mates = [c for (s_, c), rr in seq.items() if s_ == sk and c != car and cb.team.values[rr[0]] == team and cb.st_eligible.values[rr[0]] and r0.st_eligible]
                others = [c for (s_, c), rr in seq.items() if s_ == sk and c != car and cb.team.values[rr[0]] != team]
                prior_mate_obs = any((cb.avail_ts.values[seq[(sk, c)]] < tau).any() for c in mates)
                msig = []
                for c in mates:
                    s0, s1 = movement(seq[(sk, c)], tau)
                    if s1 is not None and s0 is not None:
                        msig.append((c, s0, s1))
                psl = []
                for c in others:
                    s0, s1 = movement(seq[(sk, c)], tau)
                    if s1 is not None and s0 is not None:
                        psl.append((c, s0, s1))
                sstint = lambda a, b: cb.stint_key.values[a] == cb.stint_key.values[b]
                comp = []
                for (c, s0, s1) in msig:
                    for (q, q0, q1) in psl:
                        if cb.block.values[q1] == cb.block.values[s1] and (cb.block.values[q1] - cb.block.values[q0]) == (cb.block.values[s1] - cb.block.values[s0]) and sstint(q0, q1) == sstint(s0, s1):
                            comp.append((c, s0, s1, q, q0, q1))
                phys_t = r0.reading >= 0 and r1.reading >= 0
                F1 = phys_t
                F2 = F1 and prior_mate_obs
                F3 = F2 and len(msig) > 0
                F4 = F3 and len(comp) > 0
                F5 = False
                n5 = 0
                if F4 and cb_confirmed(i0, tau):
                    for (c, s0, s1, q, q0, q1) in comp:
                        rd = [cb.reading.values[x] for x in (s0, s1, q0, q1)]
                        if min(rd) < 0 or max(wts[x] for x in rd) >= tau:
                            continue
                        if all(cb_confirmed(x, tau) for x in (s0, s1, q0, q1)):
                            n5 += 1
                    F5 = n5 > 0
                pit_known_t1 = r1.reading >= 0 and wts[r1.reading] < tau
                mf_exact = mf_match = False
                for (c, s0, s1, q, q0, q1) in comp:
                    rt = (r0.reading, r1.reading)
                    rs, rq = (cb.reading.values[s0], cb.reading.values[s1]), (cb.reading.values[q0], cb.reading.values[q1])
                    if min(rt + rs + rq) < 0:
                        continue
                    if rt[0] == rt[1] and rs[0] == rs[1] and rq[0] == rq[1]:
                        mf_exact = True
                    if rt == rs == rq:
                        mf_match = True
                ev.append(dict(population=name, cutoff=cut, event_id=eid, session_key=sk, year=int(r1.year), category=r1.category, target_car=car, target_team=team,
                               t0_cb=r0.cb_id, t1_cb=r1.cb_id, t0_block=int(r0.block), t1_block=int(r1.block), t0_source_ts=r0.source_ts, t0_avail_ts=r0.avail_ts,
                               t1_first_ts=r1.first_ts, t1_source_ts=r1.source_ts, prediction_time=tau, horizon_s=r1.source_ts - tau, baseline_interval_s=r1.source_ts - r0.source_ts,
                               same_stint=r0.stint_key == r1.stint_key, block_gap=int(r1.block - r0.block), t0_reading=int(r0.reading), t1_reading=int(r1.reading),
                               physical_resolved_change=bool(phys_t and r0.reading != r1.reading), t1_reading_pit_known=bool(pit_known_t1),
                               frozen_beta_applicable=bool(phys_t), genuine_forecast_vintage=False,
                               n_teammates_in_session=len(mates), n_teammate_movements=len(msig), n_placebo_movements=len(psl), n_comparable_pairs=len(comp),
                               n_f5_pairs=n5, t0_pit_confirmed=bool(cb_confirmed(i0, tau)) if F4 else np.nan,
                               F0=True, F1=F1, F2=F2, F3=F3, F4=F4, F5=F5, model_free_exact=bool(F4 and mf_exact), model_free_matched=bool(F4 and mf_match)))
                if cut == "PRIMARY":
                    for (c, s0, s1) in msig:
                        tsig.append(dict(population=name, event_id=eid, session_key=sk, target_car=car, teammate_car=c, s0_cb=cb.cb_id.values[s0], s1_cb=cb.cb_id.values[s1],
                                         s0_source_ts=cb.source_ts.values[s0], s1_source_ts=cb.source_ts.values[s1], s1_avail_ts=cb.avail_ts.values[s1], prediction_time=tau,
                                         age_s=tau - cb.avail_ts.values[s1], interval_s=cb.source_ts.values[s1] - cb.source_ts.values[s0],
                                         block_gap=int(cb.block.values[s1] - cb.block.values[s0]), same_stint=bool(sstint(s0, s1)),
                                         overlap_with_target_interval=bool(cb.source_ts.values[s1] > r0.source_ts and cb.source_ts.values[s0] < r1.source_ts),
                                         s0_reading=int(cb.reading.values[s0]), s1_reading=int(cb.reading.values[s1]), avail_before_cutoff=bool(cb.avail_ts.values[s1] < tau)))
                    for (c, s0, s1, q, q0, q1) in comp:
                        m = G.pair_metrics(seqs[sk], laps_ts[(sk, int(cb.block.values[s1]), c)], laps_ts[(sk, int(cb.block.values[q1]), q)])
                        psig.append(dict(population=name, event_id=eid, session_key=sk, target_car=car, teammate_car=c, placebo_car=q, placebo_team=cb.team.values[q1],
                                         q0_cb=cb.cb_id.values[q0], q1_cb=cb.cb_id.values[q1], placebo_age_s=tau - cb.avail_ts.values[q1],
                                         placebo_interval_s=cb.source_ts.values[q1] - cb.source_ts.values[q0], block_gap=int(cb.block.values[q1] - cb.block.values[q0]),
                                         same_stint=bool(sstint(q0, q1)), s1_vs_q1_adjacency=m["pair_category"], q_avail_before_cutoff=bool(cb.avail_ts.values[q1] < tau)))
    return pd.DataFrame(ev), pd.DataFrame(tsig), pd.DataFrame(psig), cb


def qtab(x):
    x = pd.Series(x).dropna()
    if not len(x):
        return {}
    return dict(n=len(x), p10=x.quantile(.1), p25=x.quantile(.25), median=x.median(), p75=x.quantile(.75), p90=x.quantile(.9), max=x.max())


def metrics(EV, TS):
    e = EV[(EV.cutoff == "PRIMARY") & EV.F5]
    ts = TS[TS.event_id.isin(e.event_id)] if len(TS) else TS
    pair = (ts.target_car + ">" + ts.teammate_car) if len(ts) else pd.Series(dtype=str)
    return dict(N5=len(e), S5=e.session_key.nunique(), K5=e.target_team.nunique(), C5=e.target_car.nunique(), Y5=e.year.nunique(),
                MS=float(e.session_key.value_counts(normalize=True).max()) if len(e) else np.nan, MT=float(e.target_team.value_counts(normalize=True).max()) if len(e) else np.nan,
                MP=float(pair.value_counts(normalize=True).max()) if len(pair) else np.nan)


def case_of(m):
    if m["N5"] == 0:
        return "D"
    if m["N5"] >= 100 and m["S5"] >= 6 and m["K5"] >= 6 and m["C5"] >= 20 and m["Y5"] == 2 and m["MS"] <= .35 and m["MT"] <= .35 and m["MP"] <= .15:
        return "A"
    if m["N5"] >= 30 and m["S5"] >= 4 and m["K5"] >= 4 and m["C5"] >= 10 and m["MS"] <= .5 and m["MT"] <= .5:
        return "B"
    return "C"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    P, L = S.load()
    P["car"] = P.car.astype(str)
    mach = pit_machinery(P)
    wx = ptsc()
    seqs = {sk: G.Seq(g.ts.values) for sk, g in L.groupby("session_key")}
    R = {}
    # primary first, then secondary
    for name in POPS:
        R[name] = enumerate_pop(name, P, mach, wx, seqs)
        if name == "PRIMARY_TIER1_2023_2024":
            EV, TS, PSG, cb = R[name]
            m = metrics(EV, TS)
            case = case_of(m)
            pd.DataFrame([dict(criterion=k, value=v) for k, v in m.items()] + [dict(criterion="PRIMARY_FEASIBILITY_CASE", value=case),
                         dict(criterion="spec_commit", value="dae6856"),
                         dict(criterion="phase4l_gate", value={"A": "single pre-registered Phase 4L justified (not run)", "B": "Phase 4L only within restricted supported population (not run)"}.get(case, "NO Phase 4L"))]
                         ).to_csv(OUT / "case_evaluation.csv", index=False)

    EV, TS, PSG, cb = R["PRIMARY_TIER1_2023_2024"]
    EV.to_csv(OUT / "target_prediction_events.csv", index=False)
    TS.to_csv(OUT / "teammate_signal_support.csv", index=False)
    PSG.to_csv(OUT / "placebo_signal_support.csv", index=False)
    EV[(EV.cutoff == "PRIMARY") & EV.F5].to_csv(OUT / "fully_comparable_events.csv", index=False)

    # attrition (all populations, both cutoffs)
    att = []
    for name, (ev, ts, ps, _) in R.items():
        for cut, g in ev.groupby("cutoff"):
            prev = None
            for f in ["F0", "F1", "F2", "F3", "F4", "F5"]:
                n = int(g[f].sum())
                att.append(dict(population=name, cutoff=cut, level=f, events=n, sessions=g[g[f]].session_key.nunique(), target_cars=g[g[f]].target_car.nunique(),
                                target_teams=g[g[f]].target_team.nunique(), lost_from_previous=(prev - n) if prev is not None else 0,
                                retained_share_of_F0=n / max(int(g.F0.sum()), 1)))
                prev = n
    ATT = pd.DataFrame(att)
    ATT.to_csv(OUT / "event_attrition.csv", index=False)

    # physical input support
    ph = []
    for name, (ev, ts, ps, _) in R.items():
        g = ev[ev.cutoff == "PRIMARY"]
        ph.append(dict(population=name, events_F0=len(g), realized_environment_t0_t1=int(g.F1.sum()), t1_reading_point_in_time_known=int((g.F1 & g.t1_reading_pit_known).sum()),
                       resolved_physical_change=int(g.physical_resolved_change.sum()), same_reading_zero_change=int((g.F1 & ~g.physical_resolved_change).sum()),
                       frozen_beta_mechanically_applicable=int(g.frozen_beta_applicable.sum()), genuine_forecast_vintage_events=0,
                       note="PTSC 15-min observed readings (latest at/before time, age<=15 min); no forecast vintages in frozen evidence (HRRR not retrieved); wind unit unverified -> unused"))
    pd.DataFrame(ph).to_csv(OUT / "physical_input_support.csv", index=False)

    # overlap / dependence
    dep = []
    for name, (ev, ts, ps, _) in R.items():
        for lvl in ["F3", "F4", "F5"]:
            e = ev[(ev.cutoff == "PRIMARY") & ev[lvl]]
            t = ts[ts.event_id.isin(e.event_id)] if len(ts) else ts
            p = ps[ps.event_id.isin(e.event_id)] if len(ps) else ps
            tm_reuse = t.groupby(["teammate_car", "s0_cb", "s1_cb"]).size() if len(t) else pd.Series(dtype=int)
            pl_reuse = p.groupby(["placebo_car", "q0_cb", "q1_cb"]).size() if len(p) else pd.Series(dtype=int)
            dep.append(dict(population=name, level=lvl, total_events=len(e), unique_future_target_outcomes=e.t1_cb.nunique(), unique_target_cars=e.target_car.nunique(),
                            unique_teams=e.target_team.nunique(), unique_sessions=e.session_key.nunique(), unique_teammate_cars=t.teammate_car.nunique() if len(t) else 0,
                            unique_target_teammate_pairs=(t.target_car + ">" + t.teammate_car).nunique() if len(t) else 0,
                            events_sharing_same_target_outcome=int(e.t1_cb.duplicated(keep=False).sum()), unique_teammate_movements=len(tm_reuse),
                            max_teammate_movement_reuse=int(tm_reuse.max()) if len(tm_reuse) else 0, median_teammate_movement_reuse=float(tm_reuse.median()) if len(tm_reuse) else np.nan,
                            events_sharing_a_teammate_movement=int(t[t.set_index(["teammate_car", "s0_cb", "s1_cb"]).index.map(tm_reuse).values >= 2].event_id.nunique()) if len(t) else 0,
                            unique_placebo_movements=len(pl_reuse), max_placebo_movement_reuse=int(pl_reuse.max()) if len(pl_reuse) else 0,
                            max_events_per_car_session_trajectory=int(e.groupby(["session_key", "target_car"]).size().max()) if len(e) else 0,
                            median_events_per_car_session_trajectory=float(e.groupby(["session_key", "target_car"]).size().median()) if len(e) else np.nan,
                            events_within_same_stint=int(e.same_stint.sum()), mean_teammate_signals_per_event=float(e.n_teammate_movements.mean()) if len(e) else np.nan,
                            mean_comparable_pairs_per_event=float(e.n_comparable_pairs.mean()) if len(e) else np.nan))
    pd.DataFrame(dep).to_csv(OUT / "event_overlap_dependence.csv", index=False)

    # horizons
    hz = []
    for name, (ev, ts, ps, _) in R.items():
        for lvl in ["F0", "F3", "F5"]:
            e = ev[(ev.cutoff == "PRIMARY") & ev[lvl]]
            t = ts[ts.event_id.isin(e.event_id)] if len(ts) else ts
            p = ps[ps.event_id.isin(e.event_id)] if len(ps) else ps
            for q, x in [("target_horizon_s (t1 - prediction_time)", e.horizon_s), ("target_baseline_interval_s (t1 - t0)", e.baseline_interval_s),
                         ("teammate_signal_age_s (prediction_time - s1)", t.age_s if len(t) else []), ("teammate_movement_interval_s (s1 - s0)", t.interval_s if len(t) else []),
                         ("placebo_signal_age_s", p.placebo_age_s if len(p) else []), ("placebo_movement_interval_s", p.placebo_interval_s if len(p) else [])]:
                hz.append(dict(population=name, level=lvl, quantity=q, **qtab(x)))
    pd.DataFrame(hz).to_csv(OUT / "horizon_structure.csv", index=False)

    # coverage
    cv = []
    for name, (ev, ts, ps, _) in R.items():
        e0 = ev[ev.cutoff == "PRIMARY"]
        for lvl_name, by in [("YEAR", "year"), ("SESSION", "session_key"), ("CATEGORY", "category"), ("TARGET_TEAM_ALPHABETICAL", "target_team"), ("TARGET_CAR", "target_car")]:
            for k, g in sorted(e0.groupby(by), key=lambda z: str(z[0])):
                cv.append(dict(population=name, level=lvl_name, key=k, F0=int(g.F0.sum()), F3=int(g.F3.sum()), F4=int(g.F4.sum()), F5=int(g.F5.sum()),
                               share_of_F5=float(g.F5.sum() / max(e0.F5.sum(), 1))))
    CV = pd.DataFrame(cv)
    CV.to_csv(OUT / "session_team_coverage.csv", index=False)

    # model-free
    mf = []
    for name, (ev, ts, ps, _) in R.items():
        for cut, g in ev.groupby("cutoff"):
            mf.append(dict(population=name, cutoff=cut, F4=int(g.F4.sum()), F4_model_free_exact=int(g.model_free_exact.sum()), F4_model_free_matched=int(g.model_free_matched.sum()),
                           F5=int(g.F5.sum()), F5_model_free_exact=int((g.F5 & g.model_free_exact).sum()), F5_model_free_matched=int((g.F5 & g.model_free_matched).sum()),
                           note="EXACT = no measured PTSC change within target, teammate and placebo intervals; MATCHED = identical PTSC reading pairs across all three intervals"))
    pd.DataFrame(mf).to_csv(OUT / "model_free_support.csv", index=False)

    # secondary populations
    for name, fname in [("TIER2_2023_2024_EXTENDED", "tier2_feasibility.csv"), ("TIER1_2025_SECONDARY", "replication_2025_feasibility.csv")]:
        ev, ts, ps, _ = R[name]
        m = metrics(ev, ts)
        lab = case_of(m)
        rows = [dict(table="LABEL", item="population_label", value="EXTENDED MEASUREMENT-VALIDITY FEASIBILITY" if name.startswith("TIER2") else "2025 SECONDARY FEASIBILITY (not pooled)"),
                dict(table="LABEL", item="feasibility_case_same_rules", value=lab + " [secondary; never changes primary]")]
        rows += [dict(table="METRIC", item=k, value=v) for k, v in m.items()]
        a = ATT[(ATT.population == name)]
        rows += [dict(table="ATTRITION", item=f"{r.cutoff}|{r.level}", value=r.events) for r in a.itertuples(index=False)]
        if name.startswith("TIER2"):
            comp = ev[(ev.cutoff == "PRIMARY") & ev.F5]
            cbt = R[name][3].set_index("cb_id").composition
            for k, v in (comp.t0_cb.map(cbt) + "|" + comp.t1_cb.map(cbt)).value_counts().items():
                rows.append(dict(table="F5_TARGET_COMPOSITION_t0|t1", item=k, value=int(v)))
        pd.DataFrame(rows).to_csv(OUT / fname, index=False)
        ce = pd.read_csv(OUT / "case_evaluation.csv")
        ce = pd.concat([ce, pd.DataFrame([dict(criterion=f"{name}_label", value=lab + " [secondary; never changes primary]")])])
        ce.to_csv(OUT / "case_evaluation.csv", index=False)
    print(ATT.to_string())
    print(pd.read_csv(OUT / "case_evaluation.csv").to_string())


if __name__ == "__main__":
    main()
