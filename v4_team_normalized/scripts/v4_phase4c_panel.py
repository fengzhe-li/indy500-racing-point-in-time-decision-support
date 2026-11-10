"""V4 Phase 4C: pre-specified 2025 exploratory within-team panel analysis.

Implements output/phase4c/phase4c_prespecified_analysis.md (committed before any fit) exactly.
Exploratory falsification/sensitivity only; nothing here validates or changes the frozen model.
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4c"
SEED, B = 20250517, 2000
MODELS = {"M0": [], "M1": ["time"], "M2": ["track", "ambient"], "M3": ["time", "track", "ambient"]}
PHYS = ["track", "ambient"]
FROZEN_SIGN = {"track": -1, "ambient": 1}


# ------------------------------------------------------------------ population
def load_population():
    j = pd.read_csv(V4 / "output/phase4b/team_timeline_long.csv", dtype={"car_number": str, "registry_car_number": str}, low_memory=False)
    for b in ["primary_teammate_layer", "on_performance_timeline", "is_frozen_core_attempt"]:
        j[b] = j[b].astype(str).eq("True")
    p3 = pd.read_csv(V4 / "output/phase3/team_attempt_join.csv", low_memory=False)
    t0 = pd.to_datetime(p3.loc[p3.year == 2025, "attempt_timestamp_utc"], utc=True, format="mixed").min()
    y = j[(j.year == 2025) & j.primary_teammate_layer & j.on_performance_timeline & j.four_lap_average_speed_mph.notna()].copy()
    y["attempt_timestamp_utc"] = pd.to_datetime(y.attempt_timestamp_utc, utc=True, format="mixed")
    y["time"] = (y.attempt_timestamp_utc - t0).dt.total_seconds() / 60
    y["speed"] = y.four_lap_average_speed_mph
    y["track"], y["ambient"] = y.track_temp_c, y.ambient_temp_c
    y["car"], y["team"], y["driver"] = y.registry_car_number, y.canonical_engineering_team, y.registry_driver
    y["repeat_attempt"] = (y.car_timeline_order > 1).astype(int)
    elig = []
    for team, g in y.groupby("team"):
        n = g.groupby("car").size()
        if len(n) >= 2 and (n >= 2).sum() >= 2:
            elig.append(team)
    pall = y[y.team.isin(elig)].copy()
    pwx = pall.dropna(subset=["track", "ambient"]).copy()
    return j, y, pall, pwx, elig, t0


def counts(df):
    return dict(teams=df.team.nunique(), cars=df.car.nunique(), drivers=df.driver.nunique(), attempts=len(df),
                informative_cars=int((df.groupby("car").size() >= 2).sum()))


def population_table(y, pall, pwx, elig):
    rows = [dict(level="SUMMARY", population=nm, **counts(d)) for nm, d in [("2025_PERFORMANCE_TIMELINE_ALL_TEAMS", y), ("P_all", pall), ("P_wx", pwx)]]
    for team, g in y.groupby("team"):
        rows.append(dict(level="TEAM", population="2025_PERFORMANCE_TIMELINE_ALL_TEAMS", team=team, eligible=team in elig,
                         attempts=len(g), attempts_p_wx=int(len(pwx[pwx.team == team])), cars=g.car.nunique(),
                         cars_with_2plus=int((g.groupby("car").size() >= 2).sum())))
    for (team, car), g in pall.groupby(["team", "car"]):
        rows.append(dict(level="CAR", population="P_all", team=team, car=car, driver=g.driver.iloc[0], attempts=len(g),
                         attempts_p_wx=int(len(pwx[(pwx.car == car)])),
                         informative_under_car_fe_p_wx=int(len(pwx[(pwx.car == car)])) >= 2,
                         missing_weather_rows=int(len(g) - len(pwx[pwx.car == car]))))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ diagnostics
def eta2(v, g):
    grand = v.mean()
    ssb = sum(len(h) * (h.mean() - grand) ** 2 for _, h in v.groupby(g))
    sst = ((v - grand) ** 2).sum()
    return ssb / sst if sst > 0 else np.nan


def demean(df, cols):
    return df[cols] - df.groupby("car")[cols].transform("mean")


def vif(X):
    X = np.asarray(X, float)
    out = []
    for k in range(X.shape[1]):
        others = np.delete(X, k, axis=1)
        b = np.linalg.lstsq(others, X[:, k], rcond=None)[0] if others.shape[1] else np.zeros(0)
        r = X[:, k] - (others @ b if others.shape[1] else 0)
        ss = (X[:, k] ** 2).sum()  # demeaned: uncentered R2 is the correct within R2
        out.append(np.inf if (r ** 2).sum() == 0 else ss / (r ** 2).sum())
    return out


def diagnostics(d):
    rows = []
    add = lambda k, v, note="": rows.append(dict(diagnostic=k, value=v, note=note, **{f"n_{a}": b for a, b in counts(d).items()}))
    for a, b in [("track", "time"), ("ambient", "time"), ("track", "ambient")]:
        add(f"pearson_{a}_vs_{b}", d[a].corr(d[b]))
        add(f"spearman_{a}_vs_{b}", d[a].corr(d[b], method="spearman"))
    for v in ["track", "ambient", "time"]:
        add(f"distinct_{v}_values", d[v].round(3).nunique())
        add(f"{v}_min", d[v].min()); add(f"{v}_max", d[v].max()); add(f"{v}_range", d[v].max() - d[v].min())
        inf = d.groupby("car").filter(lambda g: len(g) >= 2)
        wsd = inf.groupby("car")[v].std()
        wr = inf.groupby("car")[v].agg(lambda s: s.max() - s.min())
        add(f"within_car_{v}_sd_median", wsd.median(), f"cars with >=2 rows: {len(wsd)}")
        add(f"within_car_{v}_sd_min", wsd.min()); add(f"within_car_{v}_range_median", wr.median())
        add(f"within_car_{v}_range_min", wr.min())
        add(f"within_team_{v}_sd_median", d.groupby("team")[v].std().median())
        add(f"within_team_{v}_range_median", d.groupby("team")[v].agg(lambda s: s.max() - s.min()).median())
        add(f"share_of_{v}_variance_within_car", 1 - eta2(d[v], d.car))
    add("eta2_time_on_car", eta2(d.time, d.car), "car/time confounding")
    add("eta2_time_on_team", eta2(d.time, d.team), "team/time confounding")
    W = demean(d, ["time", "track", "ambient"])
    for m, cols in [("M2", ["track", "ambient"]), ("M3", ["time", "track", "ambient"]), ("M1", ["time"])]:
        for c, v in zip(cols, vif(W[cols].values)):
            add(f"within_vif_{m}_{c}", v, "within-car demeaned design; >=10 flags weak identification")
    Z = W[["time", "track", "ambient"]]
    Z = Z / Z.std()
    add("within_condition_number_M3_standardised", np.linalg.cond(Z.values))
    for a, b in [("track", "time"), ("ambient", "time"), ("track", "ambient")]:
        add(f"within_car_pearson_{a}_vs_{b}", W[a].corr(W[b]), "after removing car means")
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ fixed effects OLS
def design(d, terms, param="car_fe"):
    if param == "car_fe":
        D = pd.get_dummies(d.car, prefix="car", dtype=float)
    elif param == "team_plus_effect_coded_car":
        parts = [pd.get_dummies(d.team, prefix="team", dtype=float)]
        for team, g in d.groupby("team"):
            cars = sorted(g.car.unique())
            for c in cars[:-1]:
                col = np.where(d.car == c, 1.0, np.where((d.team == team) & (d.car == cars[-1]), -1.0, 0.0))
                parts.append(pd.Series(col, index=d.index, name=f"carwithin_{team}_{c}").to_frame())
        D = pd.concat(parts, axis=1)
    elif param == "team_dummies_plus_all_car_dummies":
        D = pd.concat([pd.get_dummies(d.team, prefix="team", dtype=float), pd.get_dummies(d.car, prefix="car", dtype=float)], axis=1)
    X = pd.concat([D, d[terms].astype(float)], axis=1) if terms else D
    return X


def crse(X, u, groups, k_slopes, bread):
    G = pd.unique(groups)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for g in G:
        idx = groups == g
        s = X[idx].T @ u[idx]
        meat += np.outer(s, s)
    n = len(u)
    c = len(G) / (len(G) - 1) * (n - 1) / max(n - k_slopes - len(G), 1) if len(G) > 1 else np.nan
    V = bread @ meat @ bread * c
    return np.sqrt(np.clip(np.diag(V), 0, None)), len(G)


def ols(d, terms, param="car_fe", with_se=True):
    X = design(d, terms, param)
    Xv, yv = X.values, d.speed.values.astype(float)
    rank = np.linalg.matrix_rank(Xv)
    res = dict(n=len(d), columns=Xv.shape[1], rank=rank, estimable=rank == Xv.shape[1] and len(d) > Xv.shape[1], **counts(d))
    if not res["estimable"]:
        res["status"] = "NOT_ESTIMABLE" if rank < Xv.shape[1] else "NO_RESIDUAL_DF"
        return res, None
    beta = np.linalg.lstsq(Xv, yv, rcond=None)[0]
    fit = Xv @ beta
    u = yv - fit
    dfres = len(d) - Xv.shape[1]
    s2 = (u ** 2).sum() / dfres
    bread = np.linalg.inv(Xv.T @ Xv)
    res.update(status="OK", rss=(u ** 2).sum(), resid_sd=np.sqrt(s2), df_resid=dfres,
               loglik=-0.5 * len(d) * (np.log(2 * np.pi * (u ** 2).sum() / len(d)) + 1))
    k = Xv.shape[1] + 1
    res["aic"], res["bic"] = 2 * k - 2 * res["loglik"], k * np.log(len(d)) - 2 * res["loglik"]
    se_cl = np.sqrt(np.diag(bread) * s2)
    se_car, g_car = crse(Xv, u, d.car.values, len(terms), bread) if with_se else (None, None)
    se_team, g_team = crse(Xv, u, d.team.values, len(terms), bread) if with_se else (None, None)
    cols = list(X.columns)
    for t in terms:
        i = cols.index(t)
        res[f"beta_{t}"] = beta[i]
        if with_se:
            res[f"se_classical_{t}"] = se_cl[i]
            res[f"se_cr1_car_{t}"], res[f"se_cr1_team_{t}"] = se_car[i], se_team[i]
    res["g_car"], res["g_team"] = g_car, g_team
    return res, pd.Series(fit, index=d.index)


def boot(d, terms, unit, rng):
    ids = d[unit].unique()
    draws, ok = [], 0
    for _ in range(B):
        pick = rng.choice(ids, size=len(ids), replace=True)
        parts = []
        for k, c in enumerate(pick):
            g = d[d[unit] == c].copy()
            g["car"] = g.car.astype(str) + f"__b{k}"   # each resampled cluster is a distinct cluster
            g["team"] = g.team.astype(str) + f"__b{k}" if unit == "team" else g.team
            parts.append(g)
        r, _ = ols(pd.concat(parts), terms, with_se=False)
        if r["estimable"]:
            ok += 1
            draws.append([r[f"beta_{t}"] for t in terms])
    a = np.array(draws) if draws else np.empty((0, len(terms)))
    out = {f"boot_{unit}_estimable_fraction": ok / B}
    for i, t in enumerate(terms):
        out[f"boot_{unit}_{t}_lo"] = np.percentile(a[:, i], 2.5) if len(a) else np.nan
        out[f"boot_{unit}_{t}_hi"] = np.percentile(a[:, i], 97.5) if len(a) else np.nan
    return out


# ------------------------------------------------------------------ main
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    j, y, pall, pwx, elig, t0 = load_population()
    pop = population_table(y, pall, pwx, elig)
    pop.to_csv(OUT / "analysis_population.csv", index=False)
    print("POPULATION (before fitting):"); print(pop[pop.level == "SUMMARY"].to_string()); print("eligible teams:", elig)
    diag = diagnostics(pwx)
    diag.to_csv(OUT / "identifiability_diagnostics.csv", index=False)

    rng = np.random.default_rng(SEED)
    fe_rows, fits = [], {}
    for pop_name, d in [("P_wx", pwx), ("P_all", pall)]:
        for m, terms in MODELS.items():
            if pop_name == "P_all" and m in ("M2", "M3"):
                continue
            r, fit = ols(d, terms)
            row = dict(model=m, population=pop_name, parameterisation="car_fe", terms="+".join(terms) or "(none)", **r)
            if r["estimable"] and terms and pop_name == "P_wx":
                row.update(boot(d, terms, "car", rng))
                row.update(boot(d, terms, "team", rng))
            fe_rows.append(row)
            if pop_name == "P_wx":
                fits[m] = fit
    # M4 reparameterisation + documentation of the redundant design
    r4, fit4 = ols(pwx, PHYS, param="team_plus_effect_coded_car")
    fe_rows.append(dict(model="M4", population="P_wx", parameterisation="team_intercepts_plus_effect_coded_car_within_team",
                        terms="track+ambient", **r4,
                        max_abs_fitted_diff_vs_M2=float(np.max(np.abs(fit4 - fits["M2"]))) if fit4 is not None and fits.get("M2") is not None else np.nan))
    rr, _ = ols(pwx, PHYS, param="team_dummies_plus_all_car_dummies", with_se=False)
    fe_rows.append(dict(model="M4_redundant_team_plus_all_car_dummies", population="P_wx", parameterisation="team_dummies_plus_all_car_dummies",
                        terms="track+ambient", **rr, note="documents collinearity: team dummies are sums of car dummies"))
    fe = pd.DataFrame(fe_rows)
    fe.to_csv(OUT / "fixed_effects_results.csv", index=False)

    # within transformation
    W = demean(pwx, ["speed", "time", "track", "ambient"])
    wrows = []
    for m, terms in MODELS.items():
        if not terms:
            continue
        b = np.linalg.lstsq(W[terms].values, W.speed.values, rcond=None)[0]
        fer = fe[(fe.model == m) & (fe.population == "P_wx")].iloc[0]
        for t, v in zip(terms, b):
            wrows.append(dict(model=m, term=t, beta_within=v, beta_car_fe=fer[f"beta_{t}"], abs_diff=abs(v - fer[f"beta_{t}"]),
                              agrees_1e_8=abs(v - fer[f"beta_{t}"]) < 1e-8, **counts(pwx)))
    pd.DataFrame(wrows).to_csv(OUT / "within_transformation_results.csv", index=False)

    # mixed models (one attempt each, as specified)
    import statsmodels.formula.api as smf
    mrows = []
    for name, formula in [("MX1", "speed ~ track + ambient"), ("MX2", "speed ~ time + track + ambient")]:
        with warnings.catch_warnings(record=True) as wl:
            warnings.simplefilter("always")
            try:
                mod = smf.mixedlm(formula, pwx, groups="team", re_formula="1", vc_formula={"car": "0 + C(car)"})
                res = mod.fit(reml=True)
                row = dict(model=name, formula=formula, status="FITTED", converged=bool(res.converged),
                           team_intercept_variance=float(res.cov_re.iloc[0, 0]), car_within_team_variance=float(res.vcomp[0]),
                           residual_variance=float(res.scale), llf_reml=float(res.llf))
                for k in res.fe_params.index:
                    row[f"beta_{k}"], row[f"se_{k}"] = float(res.fe_params[k]), float(res.bse_fe[k])
            except Exception as e:  # failure is a result
                row = dict(model=name, formula=formula, status=f"FAILED: {type(e).__name__}: {e}", converged=False)
        msgs = sorted({f"{w.category.__name__}: {str(w.message)[:160]}" for w in wl})
        row["warnings"] = " || ".join(msgs)
        row["boundary_or_singular_flag"] = any(("boundary" in m.lower() or "singular" in m.lower() or "hessian" in m.lower()) for m in msgs) or \
            (row.get("team_intercept_variance", 1) < 1e-6) or (row.get("car_within_team_variance", 1) < 1e-6)
        row.update(counts(pwx))
        mrows.append(row)
    pd.DataFrame(mrows).to_csv(OUT / "mixed_effects_results.csv", index=False)

    # LOTO / LOCO
    lrows = []
    for team in sorted(pwx.team.unique()):
        d = pwx[pwx.team != team]
        for m in ["M1", "M2", "M3"]:
            r, _ = ols(d, MODELS[m], with_se=False)
            lrows.append(dict(left_out_team=team, model=m, **{k: v for k, v in r.items() if k.startswith("beta_") or k in
                                                               ("n", "teams", "cars", "drivers", "attempts", "informative_cars", "estimable", "rank", "columns")},
                              status=r.get("status", "OK")))
    pd.DataFrame(lrows).to_csv(OUT / "leave_one_team_out.csv", index=False)
    crows = []
    for car in sorted(pwx.car.unique(), key=lambda s: (len(s), s)):
        if (pwx.car == car).sum() < 2:
            continue
        d = pwx[pwx.car != car]
        for m in ["M1", "M2", "M3"]:
            r, _ = ols(d, MODELS[m], with_se=False)
            crows.append(dict(left_out_car=car, team=pwx[pwx.car == car].team.iloc[0], model=m,
                              **{k: v for k, v in r.items() if k.startswith("beta_") or k in ("n", "teams", "cars", "drivers", "attempts",
                                                                                               "informative_cars", "estimable", "rank", "columns")},
                              status=r.get("status", "OK")))
    pd.DataFrame(crows).to_csv(OUT / "leave_one_car_out.csv", index=False)

    # S1 strategy sensitivity
    rs, _ = ols(pwx, PHYS + ["repeat_attempt"])
    m2 = fe[(fe.model == "M2") & (fe.population == "P_wx")].iloc[0]
    srow = dict(model="S1", terms="track+ambient+repeat_attempt", **rs)
    if rs["estimable"]:
        srow.update(boot(pwx, PHYS + ["repeat_attempt"], "car", rng))
        for t in PHYS:
            srow[f"M2_beta_{t}"] = m2[f"beta_{t}"]
            srow[f"change_vs_M2_{t}"] = rs[f"beta_{t}"] - m2[f"beta_{t}"]
    srow["repeat_attempt_rows"] = int(pwx.repeat_attempt.sum())
    srow["within_car_repeat_variation_cars"] = int((pwx.groupby("car").repeat_attempt.nunique() > 1).sum())
    pd.DataFrame([srow]).to_csv(OUT / "strategy_sensitivity_results.csv", index=False)

    # model comparison + pre-declared case evaluation
    base = fe[(fe.model == "M0") & (fe.population == "P_wx")].iloc[0]
    lo = pd.DataFrame(lrows)
    co = pd.DataFrame(crows)
    cmp_rows = []
    for m in ["M0", "M1", "M2", "M3"]:
        r = fe[(fe.model == m) & (fe.population == "P_wx")].iloc[0]
        row = dict(model=m, n=r.n, columns=r.columns, estimable=r.estimable, rss=r.get("rss"), resid_sd=r.get("resid_sd"),
                   aic=r.get("aic"), bic=r.get("bic"), within_r2_vs_M0=1 - r.get("rss") / base.rss if r.estimable else np.nan,
                   **counts(pwx))
        for t in MODELS[m]:
            full = r[f"beta_{t}"]
            lt = lo[(lo.model == m) & lo.estimable.astype(bool)][f"beta_{t}"]
            lc = co[(co.model == m) & co.estimable.astype(bool)][f"beta_{t}"]
            row.update({f"{t}_beta": full, f"{t}_loto_sign_flips": int((np.sign(lt) != np.sign(full)).sum()),
                        f"{t}_loto_min": lt.min(), f"{t}_loto_max": lt.max(),
                        f"{t}_loto_max_rel_change": float((lt - full).abs().max() / abs(full)) if full else np.nan,
                        f"{t}_loco_sign_flips": int((np.sign(lc) != np.sign(full)).sum()), f"{t}_loco_median": lc.median(),
                        f"{t}_loco_min": lc.min(), f"{t}_loco_max": lc.max(),
                        f"{t}_boot_car_lo": r.get(f"boot_car_{t}_lo"), f"{t}_boot_car_hi": r.get(f"boot_car_{t}_hi"),
                        f"{t}_frozen_sign_label": ("" if t not in FROZEN_SIGN else "SAME_SIGN" if np.sign(full) == FROZEN_SIGN[t] else "OPPOSITE_SIGN")})
            if t in FROZEN_SIGN and (row[f"{t}_loto_sign_flips"] >= 1 or row[f"{t}_loco_sign_flips"] > 1):
                row[f"{t}_frozen_sign_label"] = "UNSTABLE_SIGN"
        cmp_rows.append(row)
    cmp = pd.DataFrame(cmp_rows)
    cmp.to_csv(OUT / "model_comparison.csv", index=False)
    cases = evaluate_cases(fe, cmp, diag)
    cases.to_csv(OUT / "case_evaluation.csv", index=False)
    print(cases.to_string())


def evaluate_cases(fe, cmp, diag):
    dv = dict(zip(diag.diagnostic, diag.value))
    m2 = cmp[cmp.model == "M2"].iloc[0]
    m3 = cmp[cmp.model == "M3"].iloc[0]
    crit = []
    d_hit = (not m2.estimable) or (not m3.estimable) or dv["within_vif_M2_track"] >= 10 or dv["within_vif_M2_ambient"] >= 10
    crit.append(dict(case="D", satisfied=bool(d_hit), detail=f"M2 est={m2.estimable}, M3 est={m3.estimable}, "
                     f"VIF_M2 track={dv['within_vif_M2_track']:.2f}, ambient={dv['within_vif_M2_ambient']:.2f}"))
    b_parts = []
    if not d_hit:
        for t in PHYS:
            b2, b3 = m2[f"{t}_beta"], m3[f"{t}_beta"]
            ex2 = not (m2[f"{t}_boot_car_lo"] <= 0 <= m2[f"{t}_boot_car_hi"])
            ex3 = not (m3[f"{t}_boot_car_lo"] <= 0 <= m3[f"{t}_boot_car_hi"])
            if np.sign(b2) != np.sign(b3):
                b_parts.append(f"{t}: sign M2 {b2:+.4f} -> M3 {b3:+.4f}")
            if abs(b3) < 0.5 * abs(b2) and ex2 and not ex3:
                b_parts.append(f"{t}: |M3|<50% |M2| and car-boot CI excludes 0 in M2 but not M3")
            if dv[f"within_vif_M3_{t}"] >= 10:
                b_parts.append(f"{t}: within VIF in M3 = {dv[f'within_vif_M3_{t}']:.1f}")
    crit.append(dict(case="B", satisfied=bool(b_parts), detail="; ".join(b_parts) or "no criterion met"))
    c_parts = []
    if not d_hit:
        for m, r in (("M2", m2), ("M3", m3)):
            for t in PHYS:
                if r[f"{t}_loto_sign_flips"] >= 1:
                    c_parts.append(f"{m} {t}: {r[f'{t}_loto_sign_flips']} LOTO sign flip(s)")
                if r[f"{t}_loco_sign_flips"] >= 2:
                    c_parts.append(f"{m} {t}: {r[f'{t}_loco_sign_flips']} LOCO sign flips")
                if r[f"{t}_loto_max_rel_change"] > 1:
                    c_parts.append(f"{m} {t}: single-team removal changes beta by {100 * r[f'{t}_loto_max_rel_change']:.0f}%")
    crit.append(dict(case="C", satisfied=bool(c_parts), detail="; ".join(c_parts) or "no criterion met"))
    a_ok = (not d_hit) and not b_parts and not c_parts and all(np.sign(m2[f"{t}_beta"]) == np.sign(m3[f"{t}_beta"]) for t in PHYS)
    crit.append(dict(case="A", satisfied=bool(a_ok), detail="all A conditions met" if a_ok else "not met"))
    head = next((c["case"] for c in sorted(crit, key=lambda c: "DBCA".index(c["case"])) if c["satisfied"]), "NONE")
    for c in crit:
        c["headline_by_precedence_D_B_C_A"] = head
    return pd.DataFrame(crit)


if __name__ == "__main__":
    main()
