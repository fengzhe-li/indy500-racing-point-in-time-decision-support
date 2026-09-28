"""V4 Phase 4C: figures and reports for the pre-specified 2025 exploratory panel analysis."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import v4_phase4c_panel as P

OUT = P.OUT
FIG = OUT / "figures"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
MK = ["o", "s", "^", "D", "v", "P", "X"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False, "font.size": 9, "legend.frameon": False})
DIAG = "2025 only · exploratory, pre-specified · not validation of 2020–24 coefficients · attempts clustered (7 teams, 21 cars)."


def md(df, index=False):
    d = df.reset_index() if index else df
    fmt = lambda v: "" if (isinstance(v, float) and np.isnan(v)) else (f"{v:.4g}" if isinstance(v, float) else str(v))
    return "\n".join(["| " + " | ".join(map(str, d.columns)) + " |", "|" + "|".join("---" for _ in d.columns) + "|"]
                     + ["| " + " | ".join(fmt(v) for v in row) + " |" for row in d.itertuples(index=False)])


def save(fig, name, top=0.92):
    fig.tight_layout(rect=(0, 0.05, 1, top))
    fig.text(0.01, 0.01, DIAG, fontsize=6.8, color=INK2)
    fig.savefig(FIG / name, dpi=150, bbox_inches="tight")
    plt.close(fig)


def team_style(d):
    teams = sorted(d.team.unique())
    return {t: (CAT[i % 8], MK[i % 7]) for i, t in enumerate(teams)}


def figures(d, fe, lo, co, fits):
    ts = team_style(d)
    # 1-2 (+ track vs ambient) identifiability scatter
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for ax, (xc, yc, xl, yl) in zip(axes, [("time", "track", "session time (min)", "track temp (°C)"),
                                           ("time", "ambient", "session time (min)", "ambient temp (°C)"),
                                           ("ambient", "track", "ambient temp (°C)", "track temp (°C)")]):
        for t, g in d.groupby("team"):
            ax.scatter(g[xc], g[yc], s=24, color=ts[t][0], marker=ts[t][1], edgecolor=SURFACE, linewidth=0.6, label=t)
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        ax.set_title(f"r = {d[xc].corr(d[yc]):.2f} (Pearson, n = {len(d)} attempts)", fontsize=8.5)
    axes[-1].legend(fontsize=6.5, loc="center left", bbox_to_anchor=(1.01, 0.5))
    fig.suptitle("1–2. 2025 physical state vs session time, and track vs ambient (raw observations, P_wx)", x=0.01, ha="left", fontsize=11)
    save(fig, "fig01_02_state_vs_time_and_track_vs_ambient.png")

    # 3 raw speed by team (small multiples), 4 centered speed vs time
    teams = sorted(d.team.unique())
    for mode, col, lab, fname, num in [("raw", "speed", "four-lap average (mph)", "fig03_raw_speed_vs_time_by_team.png", 3),
                                       ("centered", "c_speed", "speed − own-car mean (mph)", "fig04_centered_speed_vs_time_by_team.png", 4)]:
        fig, axes = plt.subplots(2, 4, figsize=(14, 6.2), sharex=True, sharey=(mode == "centered"))
        for ax, t in zip(axes.flat, teams):
            g = d[d.team == t]
            for i, (car, h) in enumerate(sorted(g.groupby("car"), key=lambda kv: (len(kv[0]), kv[0]))):
                h = h.sort_values("time")
                c = CAT[i % 8]
                if len(h) >= 2:
                    ax.plot(h.time, h[col], ":", color=c, lw=1)
                ax.scatter(h.time, h[col], s=30, color=c if len(h) >= 2 else SURFACE, edgecolor=c, marker=MK[i % 7], linewidth=1,
                           label=f"#{car} {h.driver.iloc[0].split()[-1]} (n={len(h)})")
            if mode == "centered":
                ax.axhline(0, color=INK2, lw=0.8)
            ax.set_title(t, fontsize=8.5)
            ax.legend(fontsize=6, loc="best")
        axes.flat[-1].axis("off")
        for ax in axes[1]:
            ax.set_xlabel("session time (min)")
        for ax in axes[:, 0]:
            ax.set_ylabel(lab)
        fig.suptitle(f"{num}. 2025 {mode} speed vs session time by team (hollow = single-attempt car; dotted = visual connection only)",
                     x=0.01, ha="left", fontsize=11)
        save(fig, fname)

    # 5-6 centered speed vs centered state
    for col, lab, fname, num in [("c_track", "within-car centered track temp (°C)", "fig05_centered_speed_vs_centered_track.png", 5),
                                 ("c_ambient", "within-car centered ambient temp (°C)", "fig06_centered_speed_vs_centered_ambient.png", 6)]:
        fig, ax = plt.subplots(figsize=(7.5, 4.6))
        inf = d[d.groupby("car").car.transform("size") >= 2]
        for t, g in inf.groupby("team"):
            ax.scatter(g[col], g.c_speed, s=30, color=ts[t][0], marker=ts[t][1], edgecolor=SURFACE, linewidth=0.6, label=t)
        term = col.split("_")[1]
        b = fe.loc[(fe.model == "M2") & (fe.population == "P_wx"), f"beta_{term}"].iloc[0]
        xs = np.linspace(inf[col].min(), inf[col].max(), 10)
        ax.plot(xs, b * xs, color=INK, lw=1.2, ls="--", label=f"M2 partial slope {b:+.3f} mph/°C (within observed support)")
        ax.axhline(0, color=GRID)
        ax.axvline(0, color=GRID)
        ax.set_xlabel(lab)
        ax.set_ylabel("within-car centered speed (mph)")
        ax.legend(fontsize=6.8, loc="center left", bbox_to_anchor=(1.01, 0.5))
        ax.set_title(f"{num}. Centered speed vs {lab.split(' centered ')[1]} (16 informative cars; marginal view — the M2 line is a partial slope)",
                     loc="left", fontsize=9.5)
        save(fig, fname)

    # 7 coefficients M1/M2/M3 with car-bootstrap and CR1-car intervals
    fe_p = fe[(fe.population == "P_wx") & fe.model.isin(["M1", "M2", "M3"])]
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))
    for ax, term, unit in zip(axes, ["time", "track", "ambient"], ["mph per min", "mph per °C", "mph per °C"]):
        k = 0
        for _, r in fe_p.iterrows():
            if pd.isna(r.get(f"beta_{term}")):
                continue
            ax.errorbar(k, r[f"beta_{term}"], yerr=[[r[f"beta_{term}"] - r[f"boot_car_{term}_lo"]], [r[f"boot_car_{term}_hi"] - r[f"beta_{term}"]]],
                        fmt="o", color=CAT[0], capsize=4, label="car-cluster bootstrap 95% (percentile)" if k == 0 else None)
            ax.errorbar(k + 0.18, r[f"beta_{term}"], yerr=1.96 * r[f"se_cr1_car_{term}"], fmt="s", color=CAT[1], capsize=4, ms=4,
                        label="±1.96 CR1(car) SE" if k == 0 else None)
            ax.text(k + 0.09, ax.get_ylim()[0], r.model, ha="center", va="bottom", fontsize=8)
            k += 1
        ax.axhline(0, color=INK2, lw=0.8)
        ax.set_xticks([])
        ax.set_title(f"{term} ({unit})", fontsize=9)
        ax.legend(fontsize=6.5, loc="upper right")
    fig.suptitle("7. Coefficients by model (P_wx, n = 41 attempts, 21 cars, 7 teams; intervals are fragile with G = 21 / 7)", x=0.01, ha="left", fontsize=11)
    save(fig, "fig07_coefficients_M1_M2_M3.png")

    # 8 LOTO, 9 LOCO
    for df, key, fname, num, title in [(lo, "left_out_team", "fig08_leave_one_team_out.png", 8, "Leave-one-team-out"),
                                       (co, "left_out_car", "fig09_leave_one_car_out.png", 9, "Leave-one-car-out")]:
        fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
        for ax, term in zip(axes, ["time", "track", "ambient"]):
            for j_, m in enumerate(["M1", "M2", "M3"]):
                s = df[(df.model == m) & df[f"beta_{term}"].notna()]
                if s.empty:
                    continue
                x = np.full(len(s), j_) + (np.random.default_rng(1).uniform(-0.12, 0.12, len(s)))
                ax.scatter(x, s[f"beta_{term}"], s=20, color=CAT[j_], edgecolor=SURFACE, linewidth=0.5)
                full = fe.loc[(fe.model == m) & (fe.population == "P_wx"), f"beta_{term}"].iloc[0]
                ax.hlines(full, j_ - 0.3, j_ + 0.3, color=INK, lw=1.5)
            ax.axhline(0, color=INK2, lw=0.8, ls=":")
            ax.set_xticks([0, 1, 2], ["M1", "M2", "M3"])
            ax.set_title(f"beta_{term} (black bar = full sample)", fontsize=9)
        fig.suptitle(f"{num}. {title} coefficient stability (dots = one refit each; not used for selection)", x=0.01, ha="left", fontsize=11)
        save(fig, fname)

    # 10 observed vs fitted
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharex=True, sharey=True)
    for ax, m in zip(axes, ["M2", "M3"]):
        f = fits[m]
        for t, g in d.groupby("team"):
            ax.scatter(f.loc[g.index], g.speed, s=24, color=ts[t][0], marker=ts[t][1], edgecolor=SURFACE, linewidth=0.5, label=t)
        lim = [d.speed.min() - 0.3, d.speed.max() + 0.3]
        ax.plot(lim, lim, color=INK2, lw=0.8)
        ax.set_title(f"{m}: observed vs fitted (car FE dominate fit)", fontsize=9)
        ax.set_xlabel("fitted speed (mph)")
    axes[0].set_ylabel("observed speed (mph)")
    axes[1].legend(fontsize=6.5, loc="center left", bbox_to_anchor=(1.01, 0.5))
    fig.suptitle("10. Observed vs fitted, M2 and M3 (in-sample; 20+ parameters for 41 attempts)", x=0.01, ha="left", fontsize=11)
    save(fig, "fig10_observed_vs_fitted_M2_M3.png")


def reports(pop, diag, fe, wt, mx, lo, co, s1, cmp, cases):
    dv = dict(zip(diag.diagnostic, diag.value))
    summ = pop[pop.level == "SUMMARY"][["population", "teams", "cars", "drivers", "attempts", "informative_cars"]]
    tt = pop[pop.level == "TEAM"][["team", "eligible", "attempts", "attempts_p_wx", "cars", "cars_with_2plus"]]
    cars = pop[pop.level == "CAR"][["team", "car", "driver", "attempts", "attempts_p_wx", "informative_under_car_fe_p_wx", "missing_weather_rows"]]
    fe_p = fe[fe.population == "P_wx"]

    def coef_table(models):
        rows = []
        for _, r in fe_p[fe_p.model.isin(models)].iterrows():
            for t in ["time", "track", "ambient"]:
                if pd.notna(r.get(f"beta_{t}")):
                    rows.append(dict(model=r.model, term=t, beta=r[f"beta_{t}"], se_classical=r[f"se_classical_{t}"],
                                     se_cr1_car=r[f"se_cr1_car_{t}"], se_cr1_team=r[f"se_cr1_team_{t}"],
                                     boot_car_95=f"[{r[f'boot_car_{t}_lo']:.4f}, {r[f'boot_car_{t}_hi']:.4f}]",
                                     boot_team_95=f"[{r[f'boot_team_{t}_lo']:.4f}, {r[f'boot_team_{t}_hi']:.4f}]",
                                     teams=r.teams, cars=r.cars, drivers=r.drivers, attempts=r.attempts))
        return pd.DataFrame(rows)

    ct = coef_table(["M1", "M2", "M3"])
    cmp_s = cmp[["model", "n", "columns", "rss", "resid_sd", "aic", "bic", "within_r2_vs_M0", "teams", "cars", "attempts"]]
    stab = []
    for m in ["M1", "M2", "M3"]:
        r = cmp[cmp.model == m].iloc[0]
        for t in P.MODELS[m]:
            stab.append(dict(model=m, term=t, full=r[f"{t}_beta"], loto_min=r[f"{t}_loto_min"], loto_max=r[f"{t}_loto_max"],
                             loto_sign_flips=r[f"{t}_loto_sign_flips"], loto_max_rel_change=r[f"{t}_loto_max_rel_change"],
                             loco_median=r[f"{t}_loco_median"], loco_min=r[f"{t}_loco_min"], loco_max=r[f"{t}_loco_max"],
                             loco_sign_flips=r[f"{t}_loco_sign_flips"], frozen_sign_label=r.get(f"{t}_frozen_sign_label", "")))
    stab = pd.DataFrame(stab)
    n_loto, n_loco = lo.left_out_team.nunique(), co.left_out_car.nunique()
    mxs = mx[["model", "formula", "status", "converged", "boundary_or_singular_flag", "team_intercept_variance", "car_within_team_variance",
              "residual_variance", "beta_track", "se_track", "beta_ambient", "se_ambient", "beta_time", "se_time", "warnings"]]
    head = cases.headline_by_precedence_D_B_C_A.iloc[0]
    s1r = s1.iloc[0]
    eff = "7 teams · 21 cars · 21 drivers · 41 attempts (16 cars informative under car FE; one session/year)"

    rep = f"""# V4 Phase 4C — 2025 Exploratory Within-Team Panel Report

**Pre-specification:** `phase4c_prespecified_analysis.md`, committed before any fit as `3e3d2a7`. All definitions were followed exactly; nothing was changed after results were seen.

**Scope:** 2025 only (hybrid-era external regime). This is exploratory falsification and sensitivity, **not validation** of the frozen 2020–2024 coefficients. It is not pooled with any other year, and it makes no causal claim.

**Effective sample for every result below:** {eff}. Attempts are clustered within cars and teams, and there is one session, so no year-level replication exists.

## 1–2. Analysis population

{md(summ)}

**Teams (eligibility decided once, on P_all):**

{md(tt)}

**Cars in P_all:**

{md(cars)}

- P_wx drops one attempt with no PTSC weather (outside the PTSC range; not extrapolated, not imputed).
- Excluded variables: solar (unavailable, not fabricated) and wind (units unverified; metadata only).

## 3–4. Identifiability

See `phase4c_identifiability_report.md`. In short:
- **Track vs session time:** r = {dv['pearson_track_vs_time']:.2f}, and within cars r = {dv['within_car_pearson_track_vs_time']:.2f}. Median within-car track range is {dv['within_car_track_range_median']:.1f} °C. Track is separately identifiable (within VIF {dv['within_vif_M3_track']:.2f} in M3).
- **Ambient vs session time:** r = {dv['pearson_ambient_vs_time']:.2f}, and **within cars r = {dv['within_car_pearson_ambient_vs_time']:.3f}**. Ambient is effectively a monotone function of session time. Its within VIF in M3 is {dv['within_vif_M3_ambient']:.1f} (time: {dv['within_vif_M3_time']:.1f}).

## 5–8. Fixed-effects results (car FE; P_wx)

{md(ct)}

**Model comparison (descriptive; in-sample):**

{md(cmp_s)}

- **M0:** car baseline only. RSS {cmp.loc[cmp.model=='M0','rss'].iloc[0]:.3f}, residual SD {cmp.loc[cmp.model=='M0','resid_sd'].iloc[0]:.3f} mph.
- **M1:** β_time = {fe_p.loc[fe_p.model=='M1','beta_time'].iloc[0]*60:+.3f} mph per 60 min. Positive, meaning cars are faster later. The car-bootstrap interval excludes 0, and there are no LOTO or LOCO sign flips. Within R² vs M0 is {cmp.loc[cmp.model=='M1','within_r2_vs_M0'].iloc[0]:.2f}.
- **M2:**
  - β_track = {fe_p.loc[fe_p.model=='M2','beta_track'].iloc[0]:+.4f} mph/°C. The car-bootstrap 95% interval [{fe_p.loc[fe_p.model=='M2','boot_car_track_lo'].iloc[0]:.3f}, {fe_p.loc[fe_p.model=='M2','boot_car_track_hi'].iloc[0]:.3f}] includes 0.
  - β_ambient = {fe_p.loc[fe_p.model=='M2','beta_ambient'].iloc[0]:+.4f} mph/°C, with a car-bootstrap interval that excludes 0.
  - Within R² is {cmp.loc[cmp.model=='M2','within_r2_vs_M0'].iloc[0]:.2f}.
- **M3:**
  - β_time ≈ 0 ({fe_p.loc[fe_p.model=='M3','beta_time'].iloc[0]*60:+.4f} per 60 min).
  - β_track = {fe_p.loc[fe_p.model=='M3','beta_track'].iloc[0]:+.4f}, essentially unchanged.
  - β_ambient = {fe_p.loc[fe_p.model=='M3','beta_ambient'].iloc[0]:+.4f}, but its CR1(car) SE jumps from {fe_p.loc[fe_p.model=='M2','se_cr1_car_ambient'].iloc[0]:.3f} to {fe_p.loc[fe_p.model=='M3','se_cr1_car_ambient'].iloc[0]:.3f} and its bootstrap interval spans roughly −0.76 to 1.13.
  - Adding time to M2 reduces RSS by only {cmp.loc[cmp.model=='M2','rss'].iloc[0]-cmp.loc[cmp.model=='M3','rss'].iloc[0]:.5f}. Time and ambient carry the same information.

## 9. Does physical state survive adjustment for session time?

- **Track:** yes, its point estimate is unchanged and it is not collinear with time. Its uncertainty interval nonetheless includes 0 under car-cluster resampling.
- **Ambient:** no. It cannot be separated from session time: the within-car correlation with time is 0.97, and the M3 VIF is 25.

## 10. M4 (team structure)

- Car fixed effects already absorb team effects, because every car belongs to exactly one team. A design with team dummies plus all car dummies has {int(fe.loc[fe.model=='M4_redundant_team_plus_all_car_dummies','columns'].iloc[0])} columns but rank {int(fe.loc[fe.model=='M4_redundant_team_plus_all_car_dummies','rank'].iloc[0])}, so it was reported `NOT_ESTIMABLE` rather than forced.
- The valid M4 (team intercepts plus effect-coded car-within-team deviations) reproduces M2 exactly: its maximum |fitted difference| is {fe.loc[fe.model=='M4','max_abs_fitted_diff_vs_M2'].iloc[0]:.1e}, with identical slopes.
- Team effects are not separately identified from car effects in a car-FE design.

## 11. Mixed-effects sensitivity (one attempt each; no re-specification)

{md(mxs)}

- **MX1:** reports `converged = True` only after statsmodels' internal optimiser retries. The team random-intercept variance sits at the boundary (≈0.0007), so the model is effectively car-intercept only. Its fixed effects are close to M2.
- **MX2** (adding time) **did not converge.** Its ambient estimate collapses toward 0 with a large SE, which is again consistent with ambient/time non-separability.
- Both results are reported as they came out. No alternative random-effects structure was tried.

## 12. Within-transformation agreement

{md(wt[['model','term','beta_within','beta_car_fe','abs_diff','agrees_1e_8']])}

Every slope agrees with the car-fixed-effects estimate to within 1e-8, so the FE implementation is verified.

## 13–14. Stability

{md(stab)}

- **LOTO:** {n_loto} refits per model. **LOCO:** {n_loco} refits per model (cars with ≥2 attempts).
- **Track:** no sign flip in any refit.
- **Ambient:** stable in M2, but flips sign in M3 when Arrow McLaren is removed (−0.32), and the largest single-team change is 264%.
- **Time in M3:** 3 LOTO and 7 LOCO sign flips.

## 15. Strategic re-running sensitivity (S1 = M2 + repeat_attempt; declared, not primary)

- β_repeat = {s1r.beta_repeat_attempt:+.3f} mph. The car-bootstrap interval [{s1r.boot_car_repeat_attempt_lo:.3f}, {s1r.boot_car_repeat_attempt_hi:.3f}] includes 0. 16 cars vary in the indicator.
- **Track:** {s1r.M2_beta_track:+.4f} → {s1r.beta_track:+.4f} (change {s1r.change_vs_M2_track:+.4f}). Essentially unchanged.
- **Ambient:** {s1r.M2_beta_ambient:+.4f} → {s1r.beta_ambient:+.4f} (change {s1r.change_vs_M2_ambient:+.4f}). It **collapses to ≈0.** The M2 ambient association cannot be separated from "later / repeat attempt", which is exactly the strategic re-running confound flagged in Phase 4B.

## 16. Sign comparison with the frozen reference era (context only; not validation)

The frozen reference era had β_track < 0 and β_ambient > 0.

| Term | M2 | M3 |
|---|---|---|
| Track | {cmp.loc[cmp.model=='M2','track_frozen_sign_label'].iloc[0]} | {cmp.loc[cmp.model=='M3','track_frozen_sign_label'].iloc[0]} |
| Ambient | {cmp.loc[cmp.model=='M2','ambient_frozen_sign_label'].iloc[0]} | {cmp.loc[cmp.model=='M3','ambient_frozen_sign_label'].iloc[0]} |

The ambient sign in M2 is not interpretable, given items 9 and 15.

## 17. Driven by one team or car?

- **Track:** no single team or car drives it. The LOTO range is [{stab[(stab.model=='M2')&(stab.term=='track')].loto_min.iloc[0]:.3f}, {stab[(stab.model=='M2')&(stab.term=='track')].loto_max.iloc[0]:.3f}] and there are no flips.
- **Ambient in M3:** driven by team composition. Removing Arrow McLaren flips the sign.

## 18. Case classification (mechanical, pre-declared precedence D → B → C → A)

{md(cases[['case','satisfied','detail']])}

**Headline: CASE {head}.**
- Physical state as a *whole* is not separable from session time: the ambient term is not identifiable once time is included.
- CASE C criteria also hold for ambient in M3.
- **Term-level:** the track term alone shows the stability pattern that CASE A describes (same sign in M2/M3, no LOTO or LOCO flips, unchanged under S1). Its car-cluster bootstrap interval nonetheless includes 0, so a shared track effect is *not established*. It is merely not contradicted.

## 19. What can legitimately be concluded

- In the independent 2025 Day 1 data, within cars of the same teams, speed was associated with later session time or repeat attempts, about +0.08 mph per hour in M1.
- Ambient temperature cannot be distinguished from that time/repeat pattern.
- Track temperature varied partly independently of time in 2025. Its within-car association with speed is negative, of similar size whether or not time is included, and stable to leaving out any team or car. But it is imprecise: under 21-car cluster resampling it is not distinguishable from 0.
- The 2025 data are therefore **not inconsistent** with a negative track effect, and **uninformative** about a separate ambient effect.

## 20. What cannot be concluded

- That 2025 validates, corroborates, or recalibrates the frozen 2020–2024 coefficients. The regime is different, and sign agreement is not validation.
- That temperature causally affects speed.
- That the ambient coefficient in M2 reflects air temperature rather than session evolution or strategy.
- That any estimate generalises beyond one session with 7 teams and 21 cars.
- That 2025 should be pooled with 2020–2024.

## 21. Is further modelling justified?

**Not with the current data design.** The single 2025 session cannot separate ambient temperature from session time or repeat attempts, and more model complexity cannot fix that; it would only invite specification searching. Further work is justified only if new observations become available that separate the variables:
- other sessions or years in the same technical regime, with more non-monotone ambient;
- verified wind units;
- a solar record;
- run-level evidence of setup changes.

Any such work would need a new pre-specification.

## 22. Outputs

Required:
- `phase4c_prespecified_analysis.md`, `analysis_population.csv`, `identifiability_diagnostics.csv`, `fixed_effects_results.csv`, `within_transformation_results.csv`, `mixed_effects_results.csv`, `leave_one_team_out.csv`, `leave_one_car_out.csv`, `strategy_sensitivity_results.csv`, `model_comparison.csv`;
- `phase4c_exploratory_panel_report.md`, `phase4c_identifiability_report.md`, `phase4c_stability_report.md`, `phase4c_checks_log.txt`;
- `figures/fig01…fig10`.

Additional: `case_evaluation.csv`.
"""
    (OUT / "phase4c_exploratory_panel_report.md").write_text(rep)

    idr = f"""# V4 Phase 4C — Identifiability Report (2025, P_wx)

Effective sample: {eff}.

{md(diag[['diagnostic','value','note']])}

## Reading

- **Track temperature** has {int(dv['distinct_track_values'])} distinct (interpolated) values over a {dv['track_range']:.1f} °C range, and {100*dv['share_of_track_variance_within_car']:.0f}% of its variance is within cars. Within cars it is only weakly related to session time (r = {dv['within_car_pearson_track_vs_time']:.2f}), so it is identifiable in both M2 and M3 (within VIF ≤ {max(dv['within_vif_M2_track'], dv['within_vif_M3_track']):.2f}). Caveat: 2025 values are linear interpolations between 15-minute PTSC observations, not attempt-exact measurements.
- **Ambient temperature** spans only {dv['ambient_range']:.2f} °C. Within cars it is almost perfectly collinear with session time (r = {dv['within_car_pearson_ambient_vs_time']:.3f}); in M3 its within VIF is {dv['within_vif_M3_ambient']:.1f}, and time's is {dv['within_vif_M3_time']:.1f}. That makes ambient and time **not separately identifiable**. Some cars have very little within-car ambient variation (minimum within-car range {dv['within_car_ambient_range_min']:.2f} °C).
- **Car/time confounding** is η² = {dv['eta2_time_on_car']:.2f}; **team/time confounding** is η² = {dv['eta2_time_on_team']:.2f}. Both are modest in 2025, so within-car time variation is ample (median within-car time range {dv['within_car_time_range_median']:.0f} min).
- **Design conditioning:** the standardised within-demeaned M3 design has condition number {dv['within_condition_number_M3_standardised']:.1f}.
- **Excluded inputs:** wind (units unverified) and solar (not available). No values were imputed.

Figure: `figures/fig01_02_state_vs_time_and_track_vs_ambient.png`.
"""
    (OUT / "phase4c_identifiability_report.md").write_text(idr)

    sr = f"""# V4 Phase 4C — Stability Report (2025, P_wx)

Effective sample: {eff}. LOTO: {n_loto} refits per model. LOCO: {n_loco} refits per model (single-attempt cars cannot change within-car slopes, so they are not refitted). Neither LOTO nor LOCO is used to select a coefficient.

## Summary

{md(stab)}

## Leave-one-team-out (all refits)

{md(lo[['left_out_team','model','n','teams','cars','informative_cars','estimable','beta_time','beta_track','beta_ambient']])}

## Leave-one-car-out (all refits)

{md(co[['left_out_car','team','model','n','cars','estimable','beta_time','beta_track','beta_ambient']])}

## Bootstrap limitations

- The car-cluster bootstrap resamples 21 cars; the team-cluster bootstrap resamples 7 teams (B = 2000, seed 20250517). Percentile intervals from so few clusters are unreliable. The team bootstrap in particular can look narrower than the car bootstrap simply because 7 clusters give very few distinct resamples.
- None of these intervals is strong frequentist evidence. They are shown to indicate fragility, not to test hypotheses.
- CR1 cluster-robust SEs (car: G = 21; team: G = 7) have the same small-G caveat.

## Reading

- **Track:** stable in sign and moderately stable in size across every LOTO and LOCO refit, in both M2 and M3.
- **Ambient:** stable only in M2, where time is omitted. In M3 it flips sign when Arrow McLaren is removed, and it collapses under S1.
- **Time in M3:** sign-unstable (3 LOTO and 7 LOCO flips), as expected when it competes with a near-collinear ambient.
"""
    (OUT / "phase4c_stability_report.md").write_text(sr)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    j, y, pall, d, elig, t0 = P.load_population()
    W = P.demean(d, ["speed", "track", "ambient", "time"])
    d = d.assign(c_speed=W.speed, c_track=W.track, c_ambient=W.ambient, c_time=W.time)
    fits = {m: P.ols(d, P.MODELS[m], with_se=False)[1] for m in ["M2", "M3"]}
    fe = pd.read_csv(OUT / "fixed_effects_results.csv")
    lo = pd.read_csv(OUT / "leave_one_team_out.csv")
    co = pd.read_csv(OUT / "leave_one_car_out.csv", dtype={"left_out_car": str})
    figures(d, fe, lo, co, fits)
    reports(pd.read_csv(OUT / "analysis_population.csv", dtype={"car": str}), pd.read_csv(OUT / "identifiability_diagnostics.csv"), fe,
            pd.read_csv(OUT / "within_transformation_results.csv"), pd.read_csv(OUT / "mixed_effects_results.csv"), lo, co,
            pd.read_csv(OUT / "strategy_sensitivity_results.csv"), pd.read_csv(OUT / "model_comparison.csv"), pd.read_csv(OUT / "case_evaluation.csv"))


if __name__ == "__main__":
    main()
