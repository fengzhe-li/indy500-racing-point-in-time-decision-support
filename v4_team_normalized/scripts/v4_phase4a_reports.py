"""V4 Phase 4A reporting: diagnostic figures and the two Markdown reports (descriptive only)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4a"
FIG = OUT / "figures"
WINDOWS = [5, 10, 15, 20, 30, 45, 60]

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False, "font.size": 9,
                     "legend.frameon": False})
DIAG = "Diagnostic figure — descriptive; frozen 41 transitions unchanged; no threshold or rule selected."
DIR_COLOR = {"ANY": BLUE, "PRIOR": ORANGE, "FUTURE": AQUA}
DIR_LABEL = {"ANY": "any direction (retrospective)", "PRIOR": "prior-only (PIT-compatible)", "FUTURE": "future-only (retrospective)"}


def md(df, index=True):
    d = df.reset_index() if index else df
    fmt = lambda v: "" if (isinstance(v, float) and np.isnan(v)) else (f"{v:.3f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))
    return "\n".join(["| " + " | ".join(map(str, d.columns)) + " |", "|" + "|".join("---" for _ in d.columns) + "|"]
                     + ["| " + " | ".join(fmt(v) for v in row) + " |" for row in d.itertuples(index=False)])


def save(fig, name):
    fig.tight_layout(rect=(0, 0.06, 1, 0.92 if fig._suptitle is not None else 1))
    fig.text(0.01, 0.01, DIAG, fontsize=7, color=INK2)
    fig.savefig(FIG / name, dpi=150, bbox_inches="tight")
    plt.close(fig)


def figures(sup, ctrl, cand, ss):
    a = sup[sup.scope == "ALL"].copy()
    a["w"] = a.window_min.astype(int)

    # 1 both-endpoint support vs window
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for d in ["ANY", "PRIOR", "FUTURE"]:
        g = a[a.direction == d].sort_values("w")
        ax.plot(g.w, g.support_both, "-o", color=DIR_COLOR[d], lw=2, ms=5, label=DIR_LABEL[d])
    cc = ss[(ss.strategy == "CAR_BALANCED_COMMON_CARS") & (ss.direction == "ANY") & (ss.window_min != "UNBOUNDED")].copy()
    cc["w"] = cc.window_min.astype(int)
    ax.plot(cc.w, cc.n_supported_both, "--s", color=INK2, lw=1.5, ms=4, label="any direction, same teammate car(s) at both endpoints")
    ax.axhline(41, color=GRID, lw=1)
    ax.text(5, 41.5, "41 frozen transitions", fontsize=7.5, color=INK2)
    ax.set_xticks(WINDOWS)
    ax.set_xlabel("± matching window around each endpoint (min)")
    ax.set_ylabel("frozen transitions supported at BOTH endpoints")
    ax.set_ylim(0, 44)
    ax.legend(fontsize=7.5, loc="center right")
    ax.set_title("1. Frozen transitions with teammate support at both endpoints", loc="left", fontsize=11)
    save(fig, "fig1_both_endpoint_support_vs_window.png")

    # 2 nearest-teammate distance distribution per endpoint
    e = cand[cand.eligible_control].copy()
    near = e.loc[e.groupby(["transition_id", "endpoint"]).abs_offset_min.idxmin()]
    nearp = e[e.signed_offset_min <= 0].groupby(["transition_id", "endpoint"]).abs_offset_min.min()
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True)
    bins = np.arange(0, max(near.abs_offset_min.max(), nearp.max()) + 10, 10)
    for ax, (lab, x, col) in zip(axes, [("nearest, any direction", near.abs_offset_min, BLUE), ("nearest prior-only (PIT)", nearp, ORANGE)]):
        ax.hist(x, bins=bins, color=col, edgecolor=SURFACE)
        ax.set_title(f"{lab} (n = {len(x)} endpoints of 82)", fontsize=8.5)
        ax.set_xlabel("|endpoint → nearest eligible teammate attempt| (min)")
    axes[0].set_ylabel("endpoints")
    fig.suptitle("2. Endpoint nearest-teammate time distance", x=0.01, ha="left", fontsize=11)
    save(fig, "fig2_endpoint_nearest_teammate_distance.png")

    # 3 delta_target vs delta_team_control by strategy (±60, any direction)
    strats = ["NEAREST", "WINDOW_MEDIAN", "CAR_BALANCED_MEAN", "CAR_BALANCED_COMMON_CARS"]
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.6), sharex=True, sharey=True)
    for ax, s in zip(axes, strats):
        b = ctrl[(ctrl.strategy == s) & (ctrl.window_min == "60") & (ctrl.direction == "ANY") & ctrl.supported_both]
        circ = b.control_equals_other_frozen_transition.fillna("") != ""
        deg = b.degenerate_identical_control.astype(bool)
        ok = ~circ & ~deg
        ax.scatter(b.delta_team_control[ok], b.delta_target[ok], s=22, color=BLUE, edgecolor=SURFACE, label="independent control")
        ax.scatter(b.delta_team_control[circ], b.delta_target[circ], s=26, facecolor="none", edgecolor=ORANGE, linewidth=1.2,
                   label="control = another frozen transition")
        ax.scatter(b.delta_team_control[deg], b.delta_target[deg], s=26, marker="x", color=INK2, label="degenerate (same attempts)")
        lim = 1.6
        ax.plot([-lim, lim], [-lim, lim], color=GRID, lw=1)
        ax.axhline(0, color=GRID, lw=0.8)
        ax.axvline(0, color=GRID, lw=0.8)
        ax.set_title(f"{s}\n(±60 min, n = {len(b)})", fontsize=8)
        ax.set_xlabel("delta_team_control (mph)")
    axes[0].set_ylabel("delta_target — frozen (mph)")
    axes[-1].legend(fontsize=6.5, loc="lower right")
    fig.suptitle("3. Frozen target change vs teammate control change by strategy", x=0.01, ha="left", fontsize=11)
    save(fig, "fig3_delta_target_vs_team_control_by_strategy.png")

    # 4 same-direction fraction vs window
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    for s, col, mk in [("NEAREST", BLUE, "o"), ("CAR_BALANCED_MEAN", ORANGE, "s"), ("CAR_BALANCED_COMMON_CARS", AQUA, "^")]:
        g = ss[(ss.strategy == s) & (ss.direction == "ANY") & (ss.window_min != "UNBOUNDED")].copy()
        g["w"] = g.window_min.astype(int)
        g = g[g.same_direction_n > 0]
        ax.plot(g.w, g.same_direction_fraction, "-" + mk, color=col, lw=2, ms=5, label=s)
        for w_, f_, n_ in zip(g.w, g.same_direction_fraction, g.same_direction_n):
            ax.annotate(f"n={n_}", (w_, f_), textcoords="offset points", xytext=(0, 6), fontsize=6.5, color=INK2, ha="center")
    ax.axhline(0.5, color=INK2, lw=0.8, ls=":")
    ax.set_ylim(0, 1.1)
    ax.set_xticks(WINDOWS)
    ax.set_xlabel("± matching window (min), any direction")
    ax.set_ylabel("fraction with same sign")
    ax.legend(fontsize=7.5, loc="lower right")
    ax.set_title("4. Same-direction fraction vs window (small n; not a test)", loc="left", fontsize=11)
    save(fig, "fig4_same_direction_fraction_vs_window.png")

    # 5 team-adjusted delta distribution vs raw delta and frozen residual (±60, any)
    fig, ax = plt.subplots(figsize=(8, 3.8))
    series = []
    for s in ["NEAREST", "CAR_BALANCED_MEAN", "CAR_BALANCED_COMMON_CARS"]:
        b = ctrl[(ctrl.strategy == s) & (ctrl.window_min == "60") & (ctrl.direction == "ANY") & ctrl.supported_both
                 & ~ctrl.degenerate_identical_control.astype(bool)]
        series.append((f"team-adjusted\n{s}", b.team_adjusted_delta.values))
    b0 = ctrl[(ctrl.strategy == "NEAREST") & (ctrl.window_min == "UNBOUNDED") & (ctrl.direction == "ANY")]
    series = [("frozen delta_target", b0.delta_target.values), ("frozen LOYO residual", b0.frozen_loyo_residual_raw_mph.values)] + series
    bp = ax.boxplot([v for _, v in series], orientation="horizontal", patch_artist=True, widths=0.55, medianprops=dict(color=INK))
    for p_, col in zip(bp["boxes"], [INK2, INK2, BLUE, ORANGE, AQUA]):
        p_.set_facecolor(col)
        p_.set_alpha(0.55)
    ax.set_yticks(range(1, len(series) + 1), [f"{l} (n={len(v)})" for l, v in series], fontsize=7.5)
    ax.axvline(0, color=GRID, lw=1)
    ax.set_xlabel("mph")
    ax.set_title("5. Team-adjusted delta distribution (±60 min, any direction, non-degenerate)", loc="left", fontsize=11)
    save(fig, "fig5_team_adjusted_delta_distribution.png")

    # 6/7 support by year / team (heatmap: both-endpoint support, ANY)
    def heat(prefix, fname, title, num):
        g = sup[(sup.direction == "ANY") & sup.scope.str.startswith(prefix)].copy()
        g["w"] = g.window_min.astype(int)
        h = g.pivot_table(index="scope", columns="w", values="support_both").astype(int)
        tot = g.groupby("scope").frozen_transitions.first()
        h.index = [f"{i.split('=')[1]} ({tot[i]} frozen)" for i in h.index]
        h.columns = [f"±{c}" for c in h.columns]
        fig, ax = plt.subplots(figsize=(7.5, 0.4 * len(h) + 1.4))
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("seq", ["#eef4fc", BLUE, "#0f3f7a"])
        ax.imshow(h.values, aspect="auto", cmap=cmap, vmin=0, vmax=max(h.values.max(), 1))
        for (i, k), v in np.ndenumerate(h.values):
            ax.text(k, i, int(v), ha="center", va="center", fontsize=8, color="white" if v > h.values.max() * 0.55 else INK)
        ax.set_xticks(range(len(h.columns)), h.columns)
        ax.set_yticks(range(len(h)), h.index)
        ax.grid(False)
        ax.set_xlabel("matching window, any direction")
        ax.set_title(f"{num}. {title}: frozen transitions supported at both endpoints", loc="left", fontsize=10.5)
        save(fig, fname)

    heat("YEAR=", "fig6_support_by_year.png", "Support by year", 6)
    heat("TEAM=", "fig7_support_by_team.png", "Support by canonical team", 7)

    # 8 retrospective vs PIT support
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5), sharey=True)
    for ax, col, lab in zip(axes, ["support_t1", "support_t2", "support_both"], ["T1 supported", "T2 supported", "both endpoints"]):
        for d in ["ANY", "PRIOR"]:
            g = a[a.direction == d].sort_values("w")
            ax.plot(g.w, g[col], "-o", color=DIR_COLOR[d], lw=2, ms=4, label=DIR_LABEL[d])
        ax.set_title(lab, fontsize=9)
        ax.set_xticks(WINDOWS)
        ax.set_xlabel("± window (min)")
    axes[0].set_ylabel("frozen transitions (of 41)")
    axes[0].legend(fontsize=7.5)
    fig.suptitle("8. Retrospective vs PIT-compatible (prior-only) teammate support", x=0.01, ha="left", fontsize=11)
    save(fig, "fig8_retrospective_vs_pit_support.png")


def reports(anch, cand, ctrl, sup, ss, dep):
    a = sup[sup.scope == "ALL"]
    supw = a.pivot_table(index="window_min", columns="direction", values=["support_t1", "support_t2", "support_both"]).astype(int)
    supw.columns = [f"{v}:{d}" for v, d in supw.columns]
    supw = supw[[f"{v}:{d}" for d in ["ANY", "PRIOR", "FUTURE"] for v in ["support_t1", "support_t2", "support_both"]]]
    multi = a[a.direction == "ANY"][["window_min", "multi_car_t1", "multi_car_t2", "multi_car_both"]]
    e = cand[cand.eligible_control]
    near = e.loc[e.groupby(["transition_id", "endpoint"]).abs_offset_min.idxmin()]
    nq = pd.DataFrame([dict(view=v, endpoints_with_any_eligible_teammate=len(x), **{f"q{int(q*100):02d}": x.quantile(q) for q in [0, .25, .5, .75, .9, 1]})
                       for v, x in [("nearest any direction", near.abs_offset_min),
                                    ("nearest prior-only (PIT)", e[e.signed_offset_min <= 0].groupby(["transition_id", "endpoint"]).abs_offset_min.min()),
                                    ("nearest future-only", e[e.signed_offset_min > 0].groupby(["transition_id", "endpoint"]).abs_offset_min.min())]]).round(1)
    cols = ["strategy", "window_min", "direction", "n_supported_both", "n_nondegenerate", "n_same_teammate_car_set",
            "n_control_equals_other_frozen_transition", "n_reciprocal_frozen_pairs", "n_independent_of_frozen_transitions",
            "same_direction_n", "same_direction_fraction"]
    assoc = ["strategy", "window_min", "n_nondegenerate", "pearson_r", "spearman_rho", "median_team_adjusted", "iqr_team_adjusted",
             "sd_delta_target", "sd_team_adjusted", "sd_frozen_loyo_residual_same_subset", "pearson_team_control_vs_frozen_prediction"]
    fid = ["strategy", "window_min", "n_nondegenerate", "env_fidelity_corr_delta_track", "env_fidelity_median_abs_diff_delta_track_c",
           "env_fidelity_corr_delta_ambient", "env_fidelity_median_abs_diff_delta_ambient_c"]
    keyw = ["15", "30", "45", "60", "UNBOUNDED"]
    sany = ss[(ss.direction == "ANY") & ss.window_min.isin(keyw)]
    sprior = ss[(ss.direction == "PRIOR") & ss.window_min.isin(keyw)]
    sfut = ss[(ss.direction == "FUTURE") & ss.window_min.isin(keyw)]
    depk = dep[(dep.direction == "ANY") & dep.window_min.isin(keyw)].drop(columns=["view"])
    ysup = sup[(sup.direction == "ANY") & sup.scope.str.startswith("YEAR=")].pivot_table(index="scope", columns="window_min", values="support_both").astype(int)
    ysup.columns = [f"±{c}" for c in ysup.columns]
    tsup = sup[(sup.direction == "ANY") & sup.scope.str.startswith("TEAM=")].pivot_table(index="scope", columns="window_min", values="support_both").astype(int)
    tsup.columns = [f"±{c}" for c in tsup.columns]
    tsup = tsup.sort_values("±60", ascending=False)
    cc60 = ctrl[(ctrl.strategy == "CAR_BALANCED_COMMON_CARS") & (ctrl.window_min == "60") & (ctrl.direction == "ANY") & ctrl.supported_both][
        ["year", "canonical_engineering_team", "target_driver", "cars_t1", "cars_t2", "delta_target", "delta_team_control", "team_adjusted_delta",
         "frozen_loyo_residual_raw_mph", "degenerate_identical_control", "control_equals_other_frozen_transition", "reciprocal_frozen_pair"]].copy()
    tid = anch.set_index("transition_id")
    cc60["control_equals_other_frozen_transition"] = cc60.control_equals_other_frozen_transition.fillna("").map(
        lambda t: f"{tid.target_driver[t]} #{tid.target_car[t]}" if t else "")
    fdt = anch.frozen_delta_track_temp_c.abs().quantile([.25, .5, .75]).round(2).tolist()

    mr = f"""# V4 Phase 4A — Frozen-Transition Teammate-Control Matching Design

**Status:** design and diagnostics only.
- No coefficient was fitted or refitted.
- The frozen 41 transitions are read-only anchors, and teammate observations were not added to them.
- No matching rule was implemented as final, and no inferential test was run.

## Anchors (4A.1)

The 41 frozen transitions come from `r5_2/manual/r5_2_repeat_analysis_set_v1.csv`, restricted to rows with non-missing target, track and ambient changes. Every frozen value is carried unaltered into `frozen_transition_anchors.csv`.

**Model values.** Existing frozen LOYO predictions and residuals come from `r5_2/manual/probabilistic_physics_loyo_residuals_v1.csv`, which is in the frozen manifest. Its rows were linked by row order and verified on year, car, driver, Δspeed, Δtrack and Δair for all 41. A second column, `derived_full_data_frozen_prediction_mph`, applies the frozen full-data coefficients; it is labelled as derived.

**Endpoint times.**
- 38 transitions use the frozen repeat-set timestamps.
- The 3 R5.2 public-rescue transitions have no timestamp in the repeat set. They use the Phase 3 rescue timestamp, and the source is recorded in `t1_source` / `t2_source`.

**Eligibility.**
- One transition (2021 Paretta #16) belongs to a technical-partnership entry, so it has no eligible teammates by decision.
- The remaining 40 are eligible.
- Eligible teammate observations: complete four-lap, timed attempts from a different entry of the same canonical team.
- Excluded: the target entry (including backup chassis), technical partnerships, and ambiguous affiliations.

## 1. Endpoint support by window (4A.3)

{md(supw)}

Transitions with ≥2 distinct teammate cars inside the window (any direction):

{md(multi, index=False)}

## 2. Nearest-match support

{md(nq, index=False)}

## 3–4. Strategy comparison, car-balanced support and PIT support (4A.4–4A.7)

**Degenerate** controls use the identical teammate attempts at both endpoints, so the control change is zero by construction. They are excluded from the association columns. **Control = another frozen transition** means the teammate control change is exactly another car's frozen same-car transition, so the pair re-uses same-car evidence.

### Retrospective, any direction

{md(sany[cols].round(3), index=False)}

### PIT-compatible (prior-only: teammate_timestamp ≤ endpoint)

{md(sprior[cols].round(3), index=False)}

### Future-only (retrospective)

{md(sfut[cols].round(3), index=False)}

## 5–7. Same direction, association and team-adjusted delta (descriptive; no p-values)

{md(sany[assoc].round(3), index=False)}

**How to read this:** `sd_team_adjusted > sd_delta_target` means subtracting the teammate control *adds* variance. For comparison, `sd_frozen_loyo_residual_same_subset` is the frozen physics model's out-of-year residual spread on the same transitions.

### Environmental fidelity of the control

Does the teammate control experience the same Δtrack and Δambient as the frozen target? For scale, the frozen |Δtrack| quartiles are {fdt} °C.

{md(sany[fid].round(3), index=False)}

### Case table: same-teammate-car (common-car) control, ±60 min, any direction

{md(cc60.round(3), index=False)}

## 8–9. Sensitivity to strategy and window

- **Nearest, median, mean and car-balanced mean are identical up to ±15 min,** because each supported endpoint then has one teammate attempt. From ±20 min, windows start to hold several attempts and the strategies diverge.
- **Car-balancing is identical to the plain window mean up to ±45 min** (no window yet holds several attempts from one teammate car). At ±60 min it differs only slightly.
- **All strategies except common-car let the teammate car differ between T1 and T2.** Their control change then includes a car-to-car speed offset. This shows up as `sd_team_adjusted` well above `sd_delta_target`.
- **Common-car controls fix composition, but most of them are another frozen transition:** {int(sany[(sany.strategy=='CAR_BALANCED_COMMON_CARS')&(sany.window_min=='30')].n_control_equals_other_frozen_transition.iloc[0])} of {int(sany[(sany.strategy=='CAR_BALANCED_COMMON_CARS')&(sany.window_min=='30')].n_nondegenerate.iloc[0])} at ±30 min and {int(sany[(sany.strategy=='CAR_BALANCED_COMMON_CARS')&(sany.window_min=='60')].n_control_equals_other_frozen_transition.iloc[0])} of {int(sany[(sany.strategy=='CAR_BALANCED_COMMON_CARS')&(sany.window_min=='60')].n_nondegenerate.iloc[0])} at ±60 min. Many are reciprocal pairs, so they carry no information independent of the frozen core.
- **Window:** support at both endpoints rises from 0 (±5) to 9 (±30) to 21 (±60), and to 35 unbounded (of which 10 are degenerate). The same-direction fraction is unstable at 0.43–1.0 because n is small.

## 10. Dependence / reuse

{md(depk, index=False)}

Frozen transitions frequently act as each other's controls, so the frozen core and this layer are not independent.

## 11–12. Strongest years and teams (both-endpoint support, any direction)

{md(ysup)}

{md(tsup)}

2022 is absent from the frozen 41, so no 2022 transition can be anchored. It stays visible in the Phase 3 coverage reports. R6 (2018/2019/2025) is excluded from this reference-period analysis.

## 13. Quality limitations

See `phase4a_data_quality_report.md`. In short:
- Track temperature is past-safe PTSC on a 15-minute grid.
- Timestamps are approximate recorder captures. Rescued endpoints have minute-level or tighter-bound times.
- Some controls mix environment bases.
- Session state is unrecorded outside 2022.
- The teammate Δtrack tracks the target Δtrack only weakly within ±30 min.

## 14–15. Can a primary matching rule be selected? Recommendation (not implemented)

**Can a primary rule be selected now? Only in narrow form.**
- **The design is clear.** Only a composition-fixed control (the same teammate car or cars at both endpoints, car-balanced) avoids the car-to-car offset that inflates every other strategy.
- **The support is not.** Under that rule the independent (non-frozen, non-degenerate) evidence is only {int(sany[(sany.strategy=='CAR_BALANCED_COMMON_CARS')&(sany.window_min=='30')].n_independent_of_frozen_transitions.iloc[0])} transition at ±30 min and {int(sany[(sany.strategy=='CAR_BALANCED_COMMON_CARS')&(sany.window_min=='60')].n_independent_of_frozen_transitions.iloc[0])} at ±60 min.
- **The PIT-compatible version is smaller still.**
- **Consequence:** the teammate layer cannot serve as an independent statistical corroboration of the frozen β estimates in the 2020–2024 reference period.

**Recommended rule (for the Phase 4B design, not final):**
1. **Primary retrospective control:** `CAR_BALANCED_COMMON_CARS`, any direction, window **±30 min**. The window is justified physically, not by N: it is two PTSC 15-minute steps, and the median frozen transition spans ≈150 min, so ±30 min is ≲20% of the elapsed interval. Pre-declared sensitivities: ±15, ±45 and ±60.
2. **Explicitly partition** each matched control into:
   - independent of the frozen core;
   - equal to another frozen transition (reciprocal: report once, as a *pair consistency check*, not as corroboration);
   - degenerate (exclude).
3. **Unit of analysis:** the frozen transition, with reuse and reciprocity reported. No per-attempt pooling and no independence-based tests.
4. **PIT:** report prior-only support separately as operational-availability evidence only.
5. **Suggested use:** qualitative, case-level corroboration (sign and magnitude consistency, alongside environmental fidelity) rather than a quantitative coefficient check. Treat R6 2025 (the separate regime) as its own later analysis if broader teammate evidence is wanted.

## 16. Outputs

`frozen_transition_anchors.csv`, `frozen_transition_teammate_candidates.csv`, `endpoint_support_by_window.csv`, `matched_controls_nearest.csv`, `matched_controls_window_median.csv`, `matched_controls_window_mean.csv`, `matched_controls_car_balanced.csv`, `pit_prior_only_controls.csv`, `all_matched_controls.csv`, `strategy_summary.csv`, `dependence_audit.csv`, `phase4a_matching_report.md`, `phase4a_data_quality_report.md`, `phase4a_checks_log.txt`, `figures/fig1…fig8*.png`.
"""
    (OUT / "phase4a_matching_report.md").write_text(mr)

    tb = cand[cand.eligible_control]
    near_ep = tb.loc[tb.groupby(["transition_id", "endpoint"]).abs_offset_min.idxmin()]
    qual = pd.DataFrame([
        dict(issue="Endpoint time source", count=f"{int((anch.t1_source != 'FROZEN_REPEAT_SET').sum() + (anch.t2_source != 'FROZEN_REPEAT_SET').sum())} of 82 endpoints use Phase 3 rescue times",
             handling="labelled in t1_source/t2_source; frozen timestamp columns preserved (NaN)"),
        dict(issue="Teammate time class not a recorder point", count=f"{int((tb.teammate_time_class != 'APPROX_POINT_RECORDER_CAPTURE').sum())} of {len(tb)} eligible teammate attempts",
             handling="any_non_point_time flag per control"),
        dict(issue="Mixed temperature measurement basis (teammate vs endpoint)", count=f"{int((tb.env_basis_matches_endpoint.astype(str) == 'False').sum())} of {len(tb)} eligible candidate rows",
             handling="any_mixed_basis flag per control"),
        dict(issue="15-min PTSC quantisation: teammate shares the endpoint's PTSC track observation", count=f"{int((tb.same_ptsc_track_observation_as_endpoint.astype(str) == 'True').sum())} of {len(tb)}",
             handling="any_same_ptsc_obs flag; identical track values are resolution, not identical state"),
        dict(issue="Missing teammate weather", count=f"{int(tb.teammate_track_temp_c.isna().sum())} track / {int(tb.teammate_ambient_temp_c.isna().sum())} ambient missing among eligible",
             handling="speed controls still computed; env-fidelity metrics use available values"),
        dict(issue="2020 recorder data gap crossed between endpoint and teammate", count=f"{int(tb.crosses_2020_data_gap.sum())}", handling="any_crosses_data_gap flag (data note, not a track interruption)"),
        dict(issue="Session state", count="no interruption record for 2020/2021/2023/2024 (no frozen 2022 transitions)",
             handling="SAME_DAY1_SESSION_NO_INTERRUPTION_RECORD; absence of record ≠ uninterrupted"),
        dict(issue="PIT ordering within timestamp resolution", count=f"{int(tb.pit_order_fragile.sum())} prior-only candidate rows (|offset| < 2 min or non-point time)",
             handling="pit_order_fragile / any_pit_fragile flags"),
        dict(issue="R6 wind units unverified", count="R6 excluded from Phase 4A", handling="not used"),
        dict(issue="Technical-partnership target", count="1 transition (2021 Paretta #16)", handling="no teammates by decision; kept in anchors"),
        dict(issue="Incomplete or untimed teammate attempts", count=f"{int((~cand.eligible_control).sum())} of {len(cand)} candidate rows",
             handling="retained in candidates, eligible_control = False"),
    ])
    dq = f"""# V4 Phase 4A — Data-Quality Report

Inputs:
- Phase 3 `team_attempt_join.csv`, core tier only (all Phase 3 quality flags carried forward).
- The frozen repeat set and frozen LOYO residual file, both read-only.

{md(qual, index=False)}

## Endpoint-level candidate coverage

- Endpoints with ≥1 eligible teammate attempt anywhere in the session: {len(near_ep)} of 82.
- Eligible candidate rows: {len(tb)} (complete four-lap and timed), out of {len(cand)} candidate rows.
- **Precision:** temperatures are carried at source precision, and no interpolation beyond the Phase 3 rules was added. Differences below one PTSC step (≈0.5 °C at the published °F resolution) or between observations in the same 15-minute bin should not be read as physical differences.
"""
    (OUT / "phase4a_data_quality_report.md").write_text(dq)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    anch = pd.read_csv(OUT / "frozen_transition_anchors.csv", dtype={"target_car": str})
    anch["t1"] = pd.to_datetime(anch.t1, utc=True)
    anch["t2"] = pd.to_datetime(anch.t2, utc=True)
    cand = pd.read_csv(OUT / "frozen_transition_teammate_candidates.csv", dtype={"teammate_car": str, "target_car": str}, low_memory=False)
    ctrl = pd.read_csv(OUT / "all_matched_controls.csv", dtype={"window_min": str, "target_car": str, "cars_t1": str, "cars_t2": str}, low_memory=False)
    sup = pd.read_csv(OUT / "endpoint_support_by_window.csv", dtype={"window_min": str})
    ss = pd.read_csv(OUT / "strategy_summary.csv", dtype={"window_min": str})
    dep = pd.read_csv(OUT / "dependence_audit.csv", dtype={"window_min": str})
    figures(sup, ctrl, cand, ss)
    reports(anch, cand, ctrl, sup, ss, dep)


if __name__ == "__main__":
    main()
