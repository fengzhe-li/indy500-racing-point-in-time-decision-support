"""V4 Phase 4H: performance-lap / run-state validity audit (implements output/phase4h/phase4h_performance_validity_spec.md, a56b4dd).

Measurement-validity audit only: no hierarchy recomputation, no team effects, no ranking, no model, no tow/traffic claims.
Lap records = Timing71 archived recordings of the INDYCAR live timing feed (third-party). Official INDYCAR session details
(2023-2024) anchor official qualifying laps only. Phase 4E/4F/4G are imported/read read-only.
"""
import glob
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4h"
P4G = V4 / "output" / "phase4g"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import v4_phase4f_hierarchy as F  # noqa: E402
import v4_phase4g_adjacency as G  # noqa: E402  (Seq / pair_metrics only)

SOURCE_LABEL = F.SOURCE_LABEL
OFFICIAL_LABEL = "INDYCAR_OFFICIAL_SESSION_DETAILS (QualLap1-4)"
PRACTICE_CATS = ["PRACTICE", "FAST_FRIDAY", "QUALIFYING_WEEKEND_PRACTICE", "POST_QUALIFYING_PRACTICE", "CARB_DAY"]
QUAL = {"6202": ["6202"], "2023|2023-05-21|QUALIFYING_OTHER|6204+6205+6206": ["6204", "6205", "6206"], "6382": ["6382"], "6386": ["6386"], "6656": [], "6660": []}
BAND = (37.0, 45.0)  # Phase 4E plausibility band (pre-existing)
COH = 2.0
PIT_TOL = 5.0
CLASSES = ["A_PERFORMANCE_COMPARABLE", "B_PLAUSIBLY_PERFORMANCE_COMPARABLE", "C_RUN_STATE_AMBIGUOUS", "D_CLEARLY_NON_COMPARABLE", "E_INPUT_INSUFFICIENT"]
SHORT = dict(zip(CLASSES, "ABCDE"))


# ------------------------------------------------------------------ inventory helpers
def pit_matching(L):
    """Stint start/end vs feed pit messages (same source file, same car) within PIT_TOL seconds."""
    man = pd.read_csv(V4 / "evidence/phase4e/retrieval_manifest.csv").set_index("source_id")
    rows = []
    for sid in L.source_id.unique():
        d = json.load(open(REPO / man.loc[sid, "local_path"]))
        msgs = pd.DataFrame(d.get("messages", {}).get("messages", []))
        if msgs.empty:
            msgs = pd.DataFrame(columns=["carNum", "message", "timestamp"])
        msgs["message"] = msgs.message.astype(str)
        outm = msgs[msgs.message.str.contains("has left the pits", na=False)]
        inm = msgs[msgs.message.str.contains("has entered the pits", na=False)]
        for car, cv in d["cars"]["cars"].items():
            o = outm[outm.carNum.astype(str) == str(car)].timestamp.values / 1000.0
            i = inm[inm.carNum.astype(str) == str(car)].timestamp.values / 1000.0
            for si, st in enumerate(cv.get("stints", [])):
                s0, s1 = st.get("startTime"), st.get("endTime")
                rows.append(dict(source_id=sid, car=car, stint=si,
                                 start_matched=bool(s0 is not None and len(o) and np.min(np.abs(o - s0 / 1000.0)) <= PIT_TOL),
                                 end_matched=bool(s1 is not None and len(i) and np.min(np.abs(i - s1 / 1000.0)) <= PIT_TOL),
                                 has_end=s1 is not None))
    return pd.DataFrame(rows)


def inventory(L, pm):
    x = L.merge(pm, on=["source_id", "car", "stint"], how="left")
    x[["start_matched", "end_matched"]] = x[["start_matched", "end_matched"]].fillna(False).astype(bool)
    x = x.sort_values(["session_key", "source_id", "car", "stint", "lap_in_stint"]).reset_index(drop=True)
    g = x.groupby(["session_key", "source_id", "car", "stint"])
    x["speed_mph"] = 2.5 * 3600 / x.laptime
    x["prev_speed"] = g.speed_mph.shift(1)
    x["next_speed"] = g.speed_mph.shift(-1)
    x["delta_from_prev"] = x.speed_mph - x.prev_speed
    x["delta_to_next"] = x.next_speed - x.speed_mph
    prev_ts, prev_pos = g.ts.shift(1), g.lap_in_stint.shift(1)
    x["coherent_prev"] = ((x.ts - prev_ts - x.laptime).abs() <= COH) & (x.lap_in_stint == prev_pos + 1)
    x["stint_best_speed"] = g.speed_mph.transform("max")
    x["session_best_speed"] = x.groupby(["session_key", "car_id"]).speed_mph.transform("max")
    x["deficit_to_stint_best"] = 1 - x.speed_mph / x.stint_best_speed
    x["deficit_to_session_best"] = 1 - x.speed_mph / x.session_best_speed
    tsr = x.ts.round(3)
    x["ts_tied"] = tsr.groupby(x.session_key).transform(lambda s: s.duplicated(keep=False))
    x["stint_provenance"] = np.where(x.start_matched & x.end_matched, "PIT_MESSAGE_MATCHED_START_AND_END",
                                     np.where(x.start_matched, "PIT_MESSAGE_MATCHED_START", np.where(x.end_matched, "PIT_MESSAGE_MATCHED_END", "TIMING71_ANALYSIS_STINT_UNMATCHED")))
    x["prev_flag"] = g.flag.shift(1)
    x["evidence_source"] = SOURCE_LABEL
    return x


# ------------------------------------------------------------------ classifier (spec §5)
def windows(x):
    """All valid 4-lap windows: rows (row indices of 4 laps, r_w, m_w, session_key, car_id)."""
    lt, ts, pos, v = x.laptime.values, x.ts.values, x.lap_in_stint.values, x.speed_mph.values
    nonD = ~x.D.values
    coh = x.coherent_prev.values
    key = (x.session_key + "|" + x.source_id + "|" + x.car.astype(str) + "|" + x.stint.astype(str)).values
    W = []
    n = len(x)
    for i in range(n - 3):
        if key[i] != key[i + 3]:
            continue
        if not nonD[i:i + 4].all() or not coh[i + 1:i + 4].all():
            continue
        vv = v[i:i + 4]
        W.append((i, (vv.max() - vv.min()) / vv.max(), float(np.median(vv))))
    W = pd.DataFrame(W, columns=["i0", "r_w", "m_w"])
    W["session_key"] = x.session_key.values[W.i0] if len(W) else []
    W["car_id"] = x.car_id.values[W.i0] if len(W) else []
    return W


def d_flags(x):
    last = x.lap_in_stint == x.laps_in_stint - 1
    d1 = x.flag.astype(str).str.lower() != "green"
    d2 = (x.lap_in_stint == 0) & x.start_matched
    d3 = last & x.end_matched
    d4 = ~x.laptime.between(*BAND)
    return d1, d2, d3, d4


def classify(x, T):
    """x must be sorted by session, source, car, stint, lap_in_stint (inventory order). Uses only the car's own laps."""
    x = x.copy()
    d1, d2, d3, d4 = d_flags(x)
    x["d1_nongreen"], x["d2_observed_outlap"], x["d3_observed_inlap"], x["d4_outside_band"] = d1.values, d2.values, d3.values, d4.values
    x["D"] = d1 | d2 | d3 | d4
    W = windows(x)
    x["in_window"] = False
    x["cls"] = np.where(x.D, "D_CLEARLY_NON_COMPARABLE", "E_INPUT_INSUFFICIENT")
    if len(W):
        for q in (95, 100):
            ok = W.r_w <= T[f"T_steady_{q}"]
            Ms = W[ok].groupby(["session_key", "car_id"]).m_w.max().rename(f"M{q}")
            W = W.merge(Ms, left_on=["session_key", "car_id"], right_index=True, how="left")
            W[f"l{q}"] = 1 - W.m_w / W[f"M{q}"]
            W[f"pass{q}"] = ok & (W[f"l{q}"] <= T[f"T_level_{q}"])
        n = len(x)
        inw, pA, pB = np.zeros(n, bool), np.zeros(n, bool), np.zeros(n, bool)
        for r in W.itertuples(index=False):
            sl = slice(r.i0, r.i0 + 4)
            inw[sl] = True
            if r.pass95:
                pA[sl] = True
            if r.pass100:
                pB[sl] = True
        x["in_window"] = inw
        x.loc[inw, "cls"] = "C_RUN_STATE_AMBIGUOUS"
        x.loc[inw & pB, "cls"] = "B_PLAUSIBLY_PERFORMANCE_COMPARABLE"
        x.loc[inw & pA, "cls"] = "A_PERFORMANCE_COMPARABLE"
    return x, W


# ------------------------------------------------------------------ qualifying reference (spec §2, §5 thresholds)
def qualifying_attempts(Q):
    Q = Q.sort_values(["session_key", "source_id", "car", "ts"]).copy()
    g = Q.groupby(["session_key", "source_id", "car"])
    brk = ((Q.ts - g.ts.shift(1) - Q.laptime).abs() > COH) | g.ts.shift(1).isna()
    Q["attempt_no"] = brk.groupby([Q.session_key, Q.source_id, Q.car]).cumsum()
    Q["attempt_id"] = Q.session_key + "|" + Q.source_id + "|" + Q.car.astype(str) + "|" + Q.attempt_no.astype(str)
    Q["attempt_len"] = Q.groupby("attempt_id").laptime.transform("size")
    Q["lap_in_attempt"] = Q.groupby("attempt_id").cumcount() + 1
    # official anchoring
    off = []
    for sk, ids in QUAL.items():
        for sid in ids:
            f = glob.glob(str(V4 / f"evidence/phase4e/official_session_details/*_session_{sid}_raw.json"))
            o = json.load(open(f[0]))
            for r in o["records"]:
                q = [r.get(f"QualLap{i}") for i in range(1, 5)]
                if all(isinstance(z, str) and z.strip() for z in q):
                    off.append(dict(session_key=sk, official_segment=o["SessionName"], official_session_id=sid, car_off=str(r["CarNumber"]),
                                    q=tuple(round(float(z), 4) for z in q), official_speed_avg=r.get("SpeedAvg")))
    OFF = pd.DataFrame(off)
    Q["provenance"] = np.where(Q.attempt_len == 4, "INFERRED_4LAP", "OTHER_LENGTH")
    Q["official_segment"] = ""
    Q["official_speed_avg"] = np.nan
    atts = Q.groupby("attempt_id").agg(session_key=("session_key", "first"), car=("car", "first"), lt=("laptime", lambda s: tuple(np.round(s.values, 4))))
    n_matched = 0
    for r in OFF.itertuples(index=False):
        cand = atts[(atts.session_key == r.session_key) & atts["lt"].apply(lambda t: t == r.q)]
        c1 = cand[cand.car.astype(str) == r.car_off]
        if c1.empty:
            c1 = cand[cand.car.astype(str).str.lstrip("0") == r.car_off.lstrip("0")]
        if len(c1) == 1:
            aid = c1.index[0]
            Q.loc[Q.attempt_id == aid, ["provenance", "official_segment", "official_speed_avg"]] = ["OFFICIAL_ANCHORED", r.official_segment, r.official_speed_avg]
            n_matched += 1
    OFF["matched"] = False
    Q["four_lap_avg_speed"] = Q.groupby("attempt_id").laptime.transform(lambda s: len(s) * 2.5 * 3600 / s.sum())
    Q["attempt_fastest_speed"] = Q.groupby("attempt_id").speed_mph.transform("max")
    Q["attempt_slowest_speed"] = Q.groupby("attempt_id").speed_mph.transform("min")
    Q["dev_from_attempt_fastest"] = 1 - Q.speed_mph / Q.attempt_fastest_speed
    Q["dev_from_four_lap_avg"] = Q.speed_mph / Q.four_lap_avg_speed - 1
    Q["within_attempt_rel_range"] = (Q.attempt_fastest_speed - Q.attempt_slowest_speed) / Q.attempt_fastest_speed
    Q["attempt_median_speed"] = Q.groupby("attempt_id").speed_mph.transform("median")
    Q["sequential_pattern"] = Q.groupby("attempt_id").speed_mph.transform(lambda s: "".join("+" if d > 0 else ("-" if d < 0 else "=") for d in np.diff(s.values)))
    ref = Q[Q.provenance.isin(["OFFICIAL_ANCHORED", "INFERRED_4LAP"])].groupby(["session_key", "car_id"]).attempt_median_speed.max().rename("car_best_attempt_median")
    Q = Q.merge(ref, left_on=["session_key", "car_id"], right_index=True, how="left")
    Q["level_deficit_to_car_best_attempt"] = 1 - Q.attempt_median_speed / Q.car_best_attempt_median
    return Q, OFF, n_matched


def thresholds(Q):
    a = Q[(Q.provenance == "OFFICIAL_ANCHORED") & (Q.year == 2023)].drop_duplicates("attempt_id")
    return dict(n_2023_official_attempts=len(a), n_2024_official_attempts=int(Q[(Q.provenance == "OFFICIAL_ANCHORED") & (Q.year == 2024)].attempt_id.nunique()),
                T_steady_95=float(np.percentile(a.within_attempt_rel_range, 95)), T_steady_100=float(np.percentile(a.within_attempt_rel_range, 100)),
                T_level_95=float(np.percentile(a.level_deficit_to_car_best_attempt, 95)), T_level_100=float(np.percentile(a.level_deficit_to_car_best_attempt, 100)))


def shares(df, by, col="cls"):
    t = df.groupby(by)[col].value_counts().unstack(fill_value=0).reindex(columns=CLASSES, fill_value=0)
    out = t.copy()
    out["n_laps"] = t.sum(axis=1)
    nonD = t.sum(axis=1) - t["D_CLEARLY_NON_COMPARABLE"]
    evalb = t[["A_PERFORMANCE_COMPARABLE", "B_PLAUSIBLY_PERFORMANCE_COMPARABLE", "C_RUN_STATE_AMBIGUOUS"]].sum(axis=1)
    out["n_nonD"], out["n_evaluable"] = nonD, evalb
    for c in CLASSES:
        out[f"share_all_{SHORT[c]}"] = t[c] / t.sum(axis=1)
    for c in CLASSES[:3] + [CLASSES[4]]:
        out[f"share_nonD_{SHORT[c]}"] = t[c] / nonD.replace(0, np.nan)
    out["share_nonD_AB"] = (t[CLASSES[0]] + t[CLASSES[1]]) / nonD.replace(0, np.nan)
    for c in CLASSES[:3]:
        out[f"share_eval_{SHORT[c]}"] = t[c] / evalb.replace(0, np.nan)
    return out.reset_index()


def q(s):
    return {f"p{k}": float(s.quantile(k / 100)) for k in (5, 10, 25, 50, 75, 90, 95)}


# ------------------------------------------------------------------ main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pop = F.population()
    reg, sessions, off_recs, L = F.laps_for(set(pop.session_key))
    L = L.merge(pop[["session_key", "role", "normalized_category"]], on="session_key", how="left").rename(columns={"normalized_category": "category"})
    prac_keys = list(pop[(pop.role.eq("PRIMARY") | pop.role.str.startswith("ERA_C")) & pop.normalized_category.isin(PRACTICE_CATS)].session_key)
    qual_keys = list(QUAL)
    L = L[L.session_key.isin(prac_keys + qual_keys)].copy()
    pm = pit_matching(L)
    X = inventory(L, pm)

    # ---- qualifying reference + thresholds (2023 official only)
    Qraw = X[X.session_key.isin(qual_keys)].copy()
    Qa, OFF, n_matched = qualifying_attempts(Qraw)
    T = thresholds(Qa)
    enough = T["n_2023_official_attempts"] >= 20 and T["n_2024_official_attempts"] >= 10

    # ---- classify practice and qualifying with the frozen thresholds
    P = X[X.session_key.isin(prac_keys)].copy()
    Pc, PW = classify(P, T)
    Qc, QW = classify(X[X.session_key.isin(qual_keys)].copy(), T)
    Qa = Qa.merge(Qc[["session_key", "source_id", "car", "stint", "lap_in_stint", "cls", "D", "in_window", "d2_observed_outlap"]],
                  on=["session_key", "source_id", "car", "stint", "lap_in_stint"], how="left")
    Qa["reference_group"] = np.where(Qa.provenance == "OFFICIAL_ANCHORED", Qa.year.astype(str) + "_OFFICIAL_ANCHORED", Qa.year.astype(str) + "_" + Qa.provenance)
    Qa["evidence_source"] = SOURCE_LABEL
    Qa["anchor_source"] = np.where(Qa.provenance == "OFFICIAL_ANCHORED", OFFICIAL_LABEL, "")
    qcols = ["year", "session_key", "official_segment", "source_id", "car", "car_id", "driver", "canonical_engineering_team", "attempt_id", "provenance", "attempt_len",
             "lap_in_attempt", "stint", "lap_in_stint", "ts", "ts_tied", "laptime", "speed_mph", "four_lap_avg_speed", "official_speed_avg", "dev_from_attempt_fastest",
             "dev_from_four_lap_avg", "within_attempt_rel_range", "attempt_median_speed", "car_best_attempt_median", "level_deficit_to_car_best_attempt", "sequential_pattern",
             "flag", "cls", "D", "d2_observed_outlap", "reference_group", "evidence_source", "anchor_source"]
    Qa[qcols].to_csv(OUT / "qualifying_performance_reference.csv", index=False)

    # ---- practice lap inventory
    pcols = ["source_id", "session_key", "category", "year", "role", "car", "car_id", "driver", "canonical_engineering_team", "stint", "stint_provenance", "lap_in_stint",
             "laps_in_stint", "lap_number", "ts", "ts_tied", "coherent_prev", "flag", "prev_flag", "laptime", "speed_mph", "prev_speed", "next_speed", "delta_from_prev",
             "delta_to_next", "stint_best_speed", "session_best_speed", "deficit_to_stint_best", "deficit_to_session_best", "broad", "comparable",
             "d1_nongreen", "d2_observed_outlap", "d3_observed_inlap", "d4_outside_band", "D", "in_window", "cls", "evidence_source"]
    Pc[pcols].to_csv(OUT / "practice_lap_inventory.csv", index=False)
    Pc["lap_position"] = np.where(Pc.lap_in_stint == 0, "1 (first)", np.where(Pc.lap_in_stint == 1, "2", np.where(Pc.lap_in_stint == Pc.laps_in_stint - 1, "last",
                                  np.where(Pc.lap_in_stint == Pc.laps_in_stint - 2, "penultimate", "3+ interior"))))
    Pc["yr_group"] = np.where(Pc.year == 2025, "2025_SECONDARY", "2023_2024_PRIMARY")

    # ---- raw speed distributions (4H.4)
    rows = []
    green_at_speed = Pc[~Pc.D]
    for lvl, by in [("SESSION", ["role", "year", "category", "session_key"]), ("YEAR", ["role", "year"]), ("CATEGORY", ["role", "category"])]:
        for layer, D_ in [("ALL_RECORDS", Pc), ("NON_D", green_at_speed)]:
            for k, g in D_.groupby(by):
                k = k if isinstance(k, tuple) else (k,)
                pc = g.groupby("car_id").speed_mph
                ps = g.groupby(["car_id", "source_id", "stint"]).speed_mph
                rows.append(dict(level=lvl, layer=layer, **dict(zip(by, k)), n_laps=len(g), n_cars=g.car_id.nunique(), speed_min=g.speed_mph.min(), speed_max=g.speed_mph.max(),
                                 **{f"speed_{a}": b for a, b in q(g.speed_mph).items()},
                                 **{f"def_session_best_{a}": b for a, b in q(g.deficit_to_session_best).items()},
                                 **{f"def_stint_best_{a}": b for a, b in q(g.deficit_to_stint_best).items()},
                                 within_car_iqr_median=float((pc.quantile(.75) - pc.quantile(.25)).median()), within_car_range_median=float((pc.max() - pc.min()).median()),
                                 within_stint_iqr_median=float((ps.quantile(.75) - ps.quantile(.25)).median()), within_stint_range_median=float((ps.max() - ps.min()).median()),
                                 share_def_session_best_gt_1pct=float((g.deficit_to_session_best > 0.01).mean()), share_def_session_best_gt_2pct=float((g.deficit_to_session_best > 0.02).mean()),
                                 share_def_stint_best_gt_1pct=float((g.deficit_to_stint_best > 0.01).mean())))
    pd.DataFrame(rows).to_csv(OUT / "practice_speed_distribution.csv", index=False)

    # ---- stint sequence audit
    st = Pc.groupby(["role", "year", "category", "session_key", "source_id", "car_id", "stint"]).agg(
        stint_provenance=("stint_provenance", "first"), n_laps=("laptime", "size"), n_nonD=("D", lambda s: int((~s).sum())), n_windows_member=("in_window", "sum"),
        first_lap_s=("laptime", "first"), last_lap_s=("laptime", "last"), best_speed=("speed_mph", "max"), n_A=("cls", lambda s: int((s == CLASSES[0]).sum())),
        n_C=("cls", lambda s: int((s == CLASSES[2]).sum())), n_incoherent=("coherent_prev", lambda s: int((~s).sum()) - 1)).reset_index()
    pos = Pc[~Pc.D].assign(pos=Pc.lap_in_stint.clip(upper=15)).groupby(["yr_group", "pos"]).agg(
        n=("speed_mph", "size"), speed_median=("speed_mph", "median"), def_stint_best_median=("deficit_to_stint_best", "median"),
        share_A=("cls", lambda s: (s == CLASSES[0]).mean())).reset_index().assign(level="POSITION_NON_D")
    pd.concat([st.assign(level="STINT"), pos], ignore_index=True).to_csv(OUT / "stint_sequence_audit.csv", index=False)

    # ---- run-state classification shares (4H.8)
    rc = [shares(Pc, ["yr_group"]).assign(level="YEAR_GROUP"), shares(Pc, ["yr_group", "year"]).assign(level="YEAR"),
          shares(Pc, ["yr_group", "category"]).assign(level="CATEGORY"), shares(Pc, ["yr_group", "session_key", "category"]).assign(level="SESSION"),
          shares(Pc, ["yr_group", "lap_position"]).assign(level="STINT_POSITION"),
          shares(Pc, ["yr_group", "canonical_engineering_team"]).sort_values(["yr_group", "canonical_engineering_team"]).assign(level="TEAM_COVERAGE_ONLY_ALPHABETICAL")]
    RC = pd.concat(rc, ignore_index=True)
    RC.to_csv(OUT / "run_state_classification.csv", index=False)

    # ---- classification rule audit
    h = hashlib.sha256("".join(Pc.cls.values).encode()).hexdigest()
    Pc2, _ = classify(P, T)
    ra = [dict(item=k, value=v) for k, v in T.items()]
    ra += [dict(item="threshold_source", value="2023 OFFICIAL_ANCHORED qualifying attempts only; numpy percentile (linear)"),
           dict(item="official attempts in records (2023-2024)", value=len(OFF)), dict(item="official attempts matched to Timing71 4-lap runs", value=n_matched),
           dict(item="reference sufficiency (>=20 2023, >=10 2024)", value=bool(enough))]
    for yg, g in Pc.groupby("yr_group"):
        ra += [dict(item=f"{yg}: laps", value=len(g)), dict(item=f"{yg}: d1 non-green", value=int(g.d1_nongreen.sum())),
               dict(item=f"{yg}: d2 observed out-lap (pit-exit matched)", value=int(g.d2_observed_outlap.sum())),
               dict(item=f"{yg}: d3 observed in-lap (pit-entry matched)", value=int(g.d3_observed_inlap.sum())),
               dict(item=f"{yg}: d4 outside 37-45 s band", value=int(g.d4_outside_band.sum())), dict(item=f"{yg}: D total", value=int(g.D.sum())),
               dict(item=f"{yg}: first laps of UNMATCHED-start stints (inferred out-lap; not D by rule)", value=int(((g.lap_in_stint == 0) & ~g.d2_observed_outlap).sum())),
               dict(item=f"{yg}: of those, inside 37-45 s band", value=int(((g.lap_in_stint == 0) & ~g.d2_observed_outlap & ~g.d4_outside_band).sum())),
               dict(item=f"{yg}: E (no valid 4-lap window)", value=int((g.cls == CLASSES[4]).sum())),
               dict(item=f"{yg}: windows", value=int((PW.session_key.isin(g.session_key.unique())).sum()))]
    ra += [dict(item="stint start matched to pit-exit message (practice stints)", value=float(pm[pm.source_id.isin(P.source_id.unique())].start_matched.mean())),
           dict(item="stint end matched to pit-entry message (practice stints with endTime)", value=float(pm[pm.source_id.isin(P.source_id.unique()) & pm.has_end].end_matched.mean())),
           dict(item="qualifying stints start matched to pit-exit message", value=float(pm[pm.source_id.isin(Qraw.source_id.unique())].start_matched.mean())),
           dict(item="classification SHA-256 (practice)", value=h), dict(item="classification deterministic on re-run", value=bool((Pc2.cls.values == Pc.cls.values).all())),
           dict(item="inputs used by classifier", value="flag, stint position/provenance, pit-message match, laptime, timestamp coherence (car's own laps only)")]
    # descriptive decomposition (not a criterion): which window condition fails for evaluable laps
    ev = Pc[Pc.in_window].copy()
    stA = np.zeros(len(Pc), bool); stB = np.zeros(len(Pc), bool)
    for r in PW.itertuples(index=False):
        if r.r_w <= T["T_steady_95"]:
            stA[r.i0:r.i0 + 4] = True
        if r.r_w <= T["T_steady_100"]:
            stB[r.i0:r.i0 + 4] = True
    Pc["in_steady_window_95"], Pc["in_steady_window_100"] = stA, stB
    for yg, g in Pc[Pc.in_window].groupby("yr_group"):
        ra += [dict(item=f"{yg}: evaluable laps in >=1 steady window (r_w <= T_steady_95), any level", value=float(g.in_steady_window_95.mean())),
               dict(item=f"{yg}: evaluable laps in >=1 steady window (r_w <= T_steady_100), any level", value=float(g.in_steady_window_100.mean())),
               dict(item=f"{yg}: evaluable laps steady(95) but failing level(95) -> not A", value=float((g.in_steady_window_95 & (g.cls != CLASSES[0])).mean())),
               dict(item=f"{yg}: window r_w median", value=float(PW[PW.session_key.isin(g.session_key.unique())].r_w.median())),
               dict(item=f"{yg}: window level deficit l_100 median (steady windows)", value=float(PW[PW.session_key.isin(g.session_key.unique()) & (PW.r_w <= T["T_steady_100"])].l100.median()))]
    pd.DataFrame(ra).to_csv(OUT / "classification_rule_audit.csv", index=False)

    # ---- qualifying calibration (4H.7)
    cal = []
    for grp, g in Qa[Qa.provenance.isin(["OFFICIAL_ANCHORED", "INFERRED_4LAP"])].groupby("reference_group"):
        at = g.groupby("attempt_id").cls.nunique()
        cal.append(dict(reference_group=grp, in_sample=grp == "2023_OFFICIAL_ANCHORED", attempts=g.attempt_id.nunique(), laps=len(g),
                        retention_A=float((g.cls == CLASSES[0]).mean()), retention_AB=float(g.cls.isin(CLASSES[:2]).mean()),
                        share_C=float((g.cls == CLASSES[2]).mean()), share_D=float((g.cls == CLASSES[3]).mean()), share_E=float((g.cls == CLASSES[4]).mean()),
                        share_D_via_observed_outlap_rule=float(g.d2_observed_outlap.mean()), attempt_coherence_same_class=float((at == 1).mean()),
                        within_attempt_rel_range_median=float(g.drop_duplicates("attempt_id").within_attempt_rel_range.median()),
                        within_attempt_rel_range_max=float(g.drop_duplicates("attempt_id").within_attempt_rel_range.max())))
    cal.append(dict(reference_group="QUALIFYING_KNOWN_NON_PERFORMANCE_LAPS", attempts=0, laps=0,
                    note="NOT AVAILABLE: Timing71 qualifying captures record only timed laps (no warm-up / cool-down laps)"))
    for lab, m in [("PRACTICE_PROXY_BUILD_LAP_pos2_pitbounded", (Pc.lap_in_stint == 1) & Pc.start_matched & ~Pc.D),
                   ("PRACTICE_PROXY_PRE_INLAP_penultimate", (Pc.lap_in_stint == Pc.laps_in_stint - 2) & Pc.end_matched & ~Pc.D),
                   ("PRACTICE_PROXY_RESTART_prev_nongreen", Pc.prev_flag.notna() & (Pc.prev_flag.astype(str).str.lower() != "green") & ~Pc.D),
                   ("PRACTICE_REFERENCE_interior_pos3plus", (Pc.lap_in_stint >= 2) & (Pc.lap_in_stint < Pc.laps_in_stint - 2) & ~Pc.D)]:
        for yg in ["2023_2024_PRIMARY", "2025_SECONDARY"]:
            g = Pc[m & (Pc.yr_group == yg)]
            cal.append(dict(reference_group=f"{lab}|{yg}", laps=len(g), retention_A=float((g.cls == CLASSES[0]).mean()) if len(g) else np.nan,
                            retention_AB=float(g.cls.isin(CLASSES[:2]).mean()) if len(g) else np.nan, share_C=float((g.cls == CLASSES[2]).mean()) if len(g) else np.nan,
                            share_E=float((g.cls == CLASSES[4]).mean()) if len(g) else np.nan, note="inferred proxy negative; descriptive only (not a criterion)"))
    # post-hoc DESCRIPTIVE (not a criterion; spec attempt definition unchanged): 2025 captures record a yellow warm-up lap before each run
    Qa["first_flag"] = Qa.groupby("attempt_id").flag.transform(lambda s: str(s.iloc[0]).lower())
    Qa["rest_green"] = Qa.groupby("attempt_id").flag.transform(lambda s: bool((s.iloc[1:].astype(str).str.lower() == "green").all()))
    w5 = Qa[(Qa.year == 2025) & (Qa.attempt_len == 5) & (Qa.first_flag != "green") & Qa.rest_green]
    for lab, g in [("2025_WARMUP_PLUS_4|timed laps 2-5 (post-hoc descriptive; not a criterion)", w5[w5.lap_in_attempt >= 2]),
                   ("2025_WARMUP_PLUS_4|warm-up lap 1 = observed non-performance qualifying lap (post-hoc descriptive)", w5[w5.lap_in_attempt == 1])]:
        cal.append(dict(reference_group=lab, attempts=g.attempt_id.nunique(), laps=len(g), retention_A=float((g.cls == CLASSES[0]).mean()),
                        retention_AB=float(g.cls.isin(CLASSES[:2]).mean()), share_C=float((g.cls == CLASSES[2]).mean()), share_D=float((g.cls == CLASSES[3]).mean()),
                        share_E=float((g.cls == CLASSES[4]).mean()),
                        note="2025 Timing71 qualifying captures include a yellow-flag warm-up lap before each timed run; the pre-specified 4-lap attempt definition does not capture these runs"))
    CAL = pd.DataFrame(cal)
    CAL.to_csv(OUT / "qualifying_calibration.csv", index=False)

    # ---- car-block run-state labels (Phase 4F comparable layer, 5 min)
    comp = X.merge(Pc[["session_key", "source_id", "car", "stint", "lap_in_stint", "cls"]], on=["session_key", "source_id", "car", "stint", "lap_in_stint"])
    comp = comp[comp.comparable & (comp.join_status == "MATCHED") & ~comp.technical_partnership_only.fillna(False).astype(bool)]
    comp["block"] = np.floor(comp.ts / 300).astype(int)
    rank = {c: i for i, c in enumerate(CLASSES)}

    def modal(s):
        vc = s.value_counts()
        top = vc[vc == vc.max()].index
        return max(top, key=lambda c: rank[c])
    CBL = comp.groupby(["session_key", "block", "car_id"]).cls.agg(modal).rename("cb_cls")
    cbl = CBL.to_dict()

    # ---- Phase 4F/4G population audit (4H.9)
    TS = pd.read_csv(P4G / "timing_sequence_adjacency.csv", dtype={"session_key": str}, low_memory=False)
    TS = TS[TS.population.isin(["A_PRIMARY_CONTROL", "B_ELIGIBLE_CANDIDATES", "C1_TEAMMATE_OF_TARGET", "C2_ALL_TEAMMATES", "TEAM_BALANCED_DIFF"])].copy()
    TS["t_cls"] = [cbl.get((s, b, c), "NO_LABEL") for s, b, c in zip(TS.session_key, TS.block, TS.target)]
    TS["c_cls"] = [cbl.get((s, b, c), "NO_LABEL") for s, b, c in zip(TS.session_key, TS.block, TS.comparator)]
    TS["matched"] = TS.t_cls == TS.c_cls
    TS["both_A"] = (TS.t_cls == CLASSES[0]) & (TS.c_cls == CLASSES[0])
    TS["both_AB"] = TS.t_cls.isin(CLASSES[:2]) & TS.c_cls.isin(CLASSES[:2])
    TS["involves_C"] = (TS.t_cls == CLASSES[2]) | (TS.c_cls == CLASSES[2])
    TS["involves_DE"] = TS.t_cls.isin(CLASSES[3:]) | TS.c_cls.isin(CLASSES[3:])
    TS["NO_INTERVENING"] = TS.pair_category_code <= 1
    au = []
    for (role, popn), g in TS.groupby(["role", "population"]):
        w = g.weight.values
        au.append(dict(role=role, population=popn, n_pairs=len(g), weighted=bool(not np.allclose(w, 1)), share_labelled=float((g.t_cls != "NO_LABEL").mean() * (g.c_cls != "NO_LABEL").mean()),
                       share_matched=float(np.average(g.matched, weights=w)), share_mismatched=float(np.average(~g.matched, weights=w)),
                       share_both_A=float(np.average(g.both_A, weights=w)), share_both_AB=float(np.average(g.both_AB, weights=w)),
                       share_involves_C_ambiguous=float(np.average(g.involves_C, weights=w)), share_involves_D_or_E=float(np.average(g.involves_DE, weights=w)),
                       target_share_A=float(np.average(g.t_cls == CLASSES[0], weights=w)), comparator_share_A=float(np.average(g.c_cls == CLASSES[0], weights=w)),
                       comparator_share_C=float(np.average(g.c_cls == CLASSES[2], weights=w))))
    CB_all = pd.Series(CBL)
    for role, keys in [("PRIMARY", [k for k in prac_keys if k in set(pop[pop.role == "PRIMARY"].session_key)]), ("ERA_C_SECONDARY", [k for k in prac_keys if k in set(pop[pop.role.str.startswith("ERA_C")].session_key)])]:
        s = CB_all[CB_all.index.get_level_values(0).isin(keys)]
        au.append(dict(role=role, population="ALL_COMPARABLE_CARBLOCKS", n_pairs=len(s), **{f"carblock_share_{SHORT[c]}": float((s == c).mean()) for c in CLASSES}))
    pd.DataFrame(au).to_csv(OUT / "phase4f_population_run_state_audit.csv", index=False)

    # ---- adjacency x run state (4H.8), different-team pool pairs only
    ad = []
    for role in ["PRIMARY", "ERA_C_SECONDARY"]:
        B = TS[(TS.role == role) & (TS.population == "B_ELIGIBLE_CANDIDATES")]
        for strat in G.CATS + ["NO_INTERVENING"]:
            g = B[B.NO_INTERVENING] if strat == "NO_INTERVENING" else B[B.pair_category == strat]
            row = dict(role=role, table="MATCH_BY_ADJACENCY", stratum=strat, n_pairs=len(g), share_matched=g.matched.mean(), share_both_A=g.both_A.mean(),
                       share_both_AB=g.both_AB.mean(), share_involves_C=g.involves_C.mean(), share_involves_DE=g.involves_DE.mean())
            for subset, m in [("ALL", np.ones(len(g), bool)), ("BOTH_A", g.both_A.values), ("RUNSTATE_MATCHED", g.matched.values), ("RUNSTATE_MISMATCHED", ~g.matched.values)]:
                h_ = g[m]
                sbm = h_.groupby("session_key").D_mph.median().median() if len(h_) else np.nan
                row[f"D_sb_median_{subset}"] = sbm
                row[f"n_{subset}"] = len(h_)
            ad.append(row)
        # gradient contrasts (GT5 - NO_INTERVENING) within subsets, per year
        for subset in ["ALL", "BOTH_A", "RUNSTATE_MATCHED", "RUNSTATE_MISMATCHED"]:
            for yr in ["ALL"] + sorted(B.year.unique().astype(str)):
                b = B if yr == "ALL" else B[B.year == int(yr)]
                m = {"ALL": np.ones(len(b), bool), "BOTH_A": b.both_A.values, "RUNSTATE_MATCHED": b.matched.values, "RUNSTATE_MISMATCHED": ~b.matched.values}[subset]
                b = b[m]
                ni, gt = b[b.NO_INTERVENING], b[b.pair_category == "BETWEEN_GT5"]
                sni = ni.groupby("session_key").D_mph.median().median() if len(ni) else np.nan
                sgt = gt.groupby("session_key").D_mph.median().median() if len(gt) else np.nan
                ad.append(dict(role=role, table="ADJACENCY_GRADIENT_WITHIN_SUBSET", stratum=f"{subset}|{yr}", n_pairs=len(b), n_no_intervening=len(ni), n_gt5=len(gt),
                               D_sb_no_intervening=sni, D_sb_gt5=sgt, gradient_gt5_minus_no_intervening=sgt - sni))
    AD = pd.DataFrame(ad)

    # ---- qualifying negative control (4H.10)
    qn = []
    for yg, keys in [("2023_2024", [k for k in qual_keys if k not in ("6656", "6660")]), ("2025", ["6656", "6660"])]:
        cb = F.car_blocks(L[L.session_key.isin(keys)], "comparable", 5)
        seqs = {sk: G.Seq(g.ts.values) for sk, g in L[L.session_key.isin(keys)].groupby("session_key")}
        cq = L[L.session_key.isin(keys) & L.comparable & (L.join_status == "MATCHED")].copy()
        cq["block"] = np.floor(cq.ts / 300).astype(int)
        laps = {k: g.ts.values for k, g in cq.groupby(["session_key", "block", "car_id"])}
        prs = []
        for (sk, b), g in cb.groupby(["session_key", "block"]):
            g = g.reset_index(drop=True)
            for i in range(len(g)):
                for j in range(i + 1, len(g)):
                    if g.team.iloc[i] != g.team.iloc[j]:
                        m = G.pair_metrics(seqs[sk], laps[(sk, b, g.car_id.iloc[i])], laps[(sk, b, g.car_id.iloc[j])])
                        prs.append(dict(cat=m["pair_category_code"], D=abs(g.v.iloc[i] - g.v.iloc[j])))
        pr = pd.DataFrame(prs, columns=["cat", "D"])
        n_ni, n_gt = int((pr.cat <= 1).sum()), int((pr.cat == 4).sum())
        ident = n_ni >= 30 and n_gt >= 30
        qn.append(dict(role=yg, table="QUALIFYING_NEGATIVE_CONTROL", stratum="different-team within-block pairs", n_pairs=len(pr), n_no_intervening=n_ni, n_gt5=n_gt,
                       qualifying_carblocks=len(cb), blocks_with_2plus_cars=int((cb.groupby(["session_key", "block"]).size() >= 2).sum()),
                       identifiable=ident, D_pooled_median_no_intervening=float(pr[pr.cat <= 1].D.median()) if ident else np.nan,
                       D_pooled_median_gt5=float(pr[pr.cat == 4].D.median()) if ident else np.nan,
                       note="NOT IDENTIFIABLE (<30 pairs in a stratum); single-car qualifying structure" if not ident else "descriptive"))
    AD = pd.concat([AD, pd.DataFrame(qn)], ignore_index=True)
    AD.to_csv(OUT / "adjacency_run_state_audit.csv", index=False)

    # ---- session/year validity summary + case (spec §9)
    cal_i = CAL.set_index("reference_group")
    r24A = cal_i.loc["2024_OFFICIAL_ANCHORED", "retention_A"] if "2024_OFFICIAL_ANCHORED" in cal_i.index else np.nan
    r24AB = cal_i.loc["2024_OFFICIAL_ANCHORED", "retention_AB"] if "2024_OFFICIAL_ANCHORED" in cal_i.index else np.nan
    r25AB = cal_i.loc["2025_INFERRED_4LAP", "retention_AB"] if "2025_INFERRED_4LAP" in cal_i.index else np.nan
    C1 = bool(r24AB >= 0.90 and r24A >= 0.80)
    C2 = bool(r25AB >= 0.80)
    prim = Pc[Pc.yr_group == "2023_2024_PRIMARY"]
    nonD = prim[~prim.D]
    S_AB = float(nonD.cls.isin(CLASSES[:2]).mean())
    S_A = float((nonD.cls == CLASSES[0]).mean())
    S_C = float((nonD.cls == CLASSES[2]).mean())
    S_E = float((nonD.cls == CLASSES[4]).mean())
    S_A_year = {y: float((g.cls == CLASSES[0]).mean()) for y, g in nonD.groupby("year")}
    stab = abs(S_AB - S_A)
    if (not enough) or (not C1):
        case = "C"
    elif S_AB < 0.20:
        case = "D"
    elif C2 and all(v >= 0.50 for v in S_A_year.values()) and S_C <= 0.25 and stab <= 0.15:
        case = "A"
    else:
        case = "B"
    sec = Pc[(Pc.yr_group == "2025_SECONDARY") & ~Pc.D]
    ce = [("phase4f_case_unchanged", pd.read_csv(V4 / "output/phase4f/case_evaluation.csv").set_index("criterion").value["CASE"]),
          ("phase4g_case_unchanged", pd.read_csv(P4G / "phase4g_case_evaluation.csv").set_index("criterion").value["CASE"]),
          ("reference_sufficient", enough), ("n_2023_official_attempts", T["n_2023_official_attempts"]), ("n_2024_official_attempts", T["n_2024_official_attempts"]),
          ("T_steady_95", T["T_steady_95"]), ("T_steady_100", T["T_steady_100"]), ("T_level_95", T["T_level_95"]), ("T_level_100", T["T_level_100"]),
          ("C1_2024_official_retention_A", r24A), ("C1_2024_official_retention_AB", r24AB), ("C1_pass", C1), ("C2_2025_inferred_retention_AB", r25AB), ("C2_pass", C2),
          ("S_AB_nonD_2023_2024", S_AB), ("S_A_nonD_2023_2024", S_A), ("S_A_2023", S_A_year.get(2023)), ("S_A_2024", S_A_year.get(2024)), ("S_C_nonD", S_C), ("S_E_nonD", S_E),
          ("stability_abs_S_AB_minus_S_A", stab), ("MEASUREMENT_VALIDITY_CASE", case),
          ("agreement_2025_S_AB_nonD", float(sec.cls.isin(CLASSES[:2]).mean())), ("agreement_2025_S_A_nonD", float((sec.cls == CLASSES[0]).mean())),
          ("agreement_2025_S_C_nonD", float((sec.cls == CLASSES[2]).mean())),
          ("phase4i_gate", {"A": "DESIGN PRINCIPLES ONLY (not run)", "B": "RESTRICTED SENSITIVITY ONLY (not confirmatory; not run)"}.get(case, "STOP practice-based hierarchy"))]
    pd.DataFrame(ce, columns=["criterion", "value"]).to_csv(OUT / "case_evaluation.csv", index=False)
    sv = shares(Pc, ["yr_group", "year", "session_key", "category"])
    sv = sv.merge(Pc.groupby("session_key").agg(share_ts_tied=("ts_tied", "mean"), share_incoherent=("coherent_prev", lambda s: 1 - s.mean())).reset_index(), on="session_key")
    sv["validity_note"] = "measurement-validity case is evaluated on pooled 2023-2024 primary practice; 2025 reported separately"
    sv.to_csv(OUT / "session_year_validity_summary.csv", index=False)
    print(pd.DataFrame(ce, columns=["criterion", "value"]).to_string())
    print(CAL.drop(columns=["note"], errors="ignore").round(3).to_string())


if __name__ == "__main__":
    main()
