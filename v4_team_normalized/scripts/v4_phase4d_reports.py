"""V4 Phase 4D: figures and reports for the latent team-state feasibility audit (descriptive only)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4d"
FIG = OUT / "figures"
TZ = "America/Indiana/Indianapolis"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
MK = ["o", "s", "^", "D", "v", "P", "X"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False, "font.size": 9, "legend.frameon": False})
DIAG = "Phase 4D feasibility diagnostic · descriptive · no latent model fitted · frozen values unchanged · labels are not causal."
FROZEN_LINKED = {"RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE", "FROZEN_CORE_ENDPOINT"}


def md(df, index=False):
    d = df.reset_index() if index else df
    fmt = lambda v: "" if (isinstance(v, float) and np.isnan(v)) else (f"{v:.3f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))
    return "\n".join(["| " + " | ".join(map(str, d.columns)) + " |", "|" + "|".join("---" for _ in d.columns) + "|"]
                     + ["| " + " | ".join(fmt(v) for v in row) + " |" for row in d.itertuples(index=False)])


def save(fig, path, top=0.9):
    fig.tight_layout(rect=(0, 0.05, 1, top))
    fig.text(0.01, 0.01, DIAG, fontsize=6.5, color=INK2)
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def loc(t):
    return pd.to_datetime(t, utc=True, format="mixed").tz_convert(TZ).tz_localize(None)


def car_key(c):
    s = str(c)
    return (int(s) if s.isdigit() else 999, s)


# ------------------------------------------------------------------ per-transition context timeline
def context_figure(a, team_j, obs, tco, path, title_note=""):
    team = team_j[(team_j.year == a.year) & (team_j.canonical_engineering_team == a.canonical_engineering_team) & team_j.on_performance_timeline]
    cars = sorted(team.registry_car_number.unique(), key=car_key)
    others = [c for c in cars if c != a.target_car]
    style = {c: (CAT[i % 8], MK[i % 7]) for i, c in enumerate(others)}
    fig, (ax, axw) = plt.subplots(2, 1, figsize=(10.5, 5.8), sharex=True, gridspec_kw=dict(height_ratios=[3.2, 1.3]))
    t1, t2 = loc(a.t1) if pd.notna(a.t1) else None, loc(a.t2) if pd.notna(a.t2) else None
    for tt in (t1, t2):
        if tt is not None:
            ax.axvspan(tt - pd.Timedelta(minutes=30), tt + pd.Timedelta(minutes=30), color=GRID, alpha=0.6, zorder=0)
    lab_obs = obs.set_index("obs_id")
    used = set(tco[tco.transition_id == a.transition_id].obs_id)
    for c in others:
        h = team[team.registry_car_number == c].sort_values("attempt_timestamp_utc")
        col, mk = style[c]
        for r in h.itertuples(index=False):
            lab = lab_obs.loc["LEVEL|" + r.attempt_id, "independence_label"] if "LEVEL|" + r.attempt_id in lab_obs.index else ""
            frozen = lab in FROZEN_LINKED
            ax.scatter(loc(r.attempt_timestamp_utc), r.speed_minus_car_mean if r.car_n_timeline >= 2 else 0.0, s=46, marker=mk,
                       color=SURFACE if frozen or r.car_n_timeline < 2 else col, edgecolor=col, linewidth=1.3, zorder=3)
        mv = obs[(obs.obs_type == "MOVE") & (obs.car == c) & (obs.year == a.year) & obs.obs_id.isin(used)]
        for m in mv.itertuples(index=False):
            y0 = h[h.attempt_id == m.attempt_prev].speed_minus_car_mean.iloc[0]
            y1 = h[h.attempt_id == m.attempt_curr].speed_minus_car_mean.iloc[0]
            ls = ":" if m.independence_label in FROZEN_LINKED else "-"
            ax.annotate("", xy=(loc(m.t_curr), y1), xytext=(loc(m.t_prev), y0), arrowprops=dict(arrowstyle="->", color=col, lw=1.3, ls=ls))
        n = int((h.car_n_timeline >= 2).any())
        ax.scatter([], [], marker=mk, color=col, label=f"#{c} {h.registry_driver.iloc[0]} (n={len(h)}{'' if n else '; centered ≡ 0'})")
    tgt = team[team.registry_car_number == a.target_car]
    if len(tgt):
        ax.scatter([loc(x) for x in tgt.attempt_timestamp_utc], tgt.speed_minus_car_mean, s=30, color=INK2, marker="o", zorder=3, label=f"target #{a.target_car} other attempts")
    if t1 is not None and t2 is not None:
        tm = tgt.set_index("attempt_id").speed_minus_car_mean
        y1, y2 = tm.get(a.before_attempt_id, np.nan), tm.get(a.after_attempt_id, np.nan)
        ax.scatter([t1, t2], [y1, y2], s=150, marker="*", color=INK, zorder=5, label=f"target #{a.target_car} {a.target_driver} t1 / t2")
        ax.annotate("", xy=(t2, y2), xytext=(t1, y1), arrowprops=dict(arrowstyle="->", color=INK, lw=2))
    ax.axhline(0, color=INK2, lw=0.7)
    ax.scatter([], [], marker="o", facecolor=SURFACE, edgecolor=INK2, label="hollow = frozen-core-linked or single-attempt car")
    ax.plot([], [], ":", color=INK2, label="dotted arrow = frozen-linked previous-attempt move")
    ax.plot([], [], "-", color=INK2, label="solid arrow = frozen-independent move")
    ax.set_ylabel("speed − own-car mean (mph)\n(car-relative; raw in CSV)")
    ax.legend(fontsize=6.5, loc="center left", bbox_to_anchor=(1.01, 0.5))
    wx = team.dropna(subset=["track_temp_c"])
    axw.scatter([loc(x) for x in wx.attempt_timestamp_utc], wx.track_temp_c, s=14, color=INK, label="track °C (at attempts)")
    axw.scatter([loc(x) for x in wx.attempt_timestamp_utc], wx.ambient_temp_c, s=14, color=INK2, marker="x", label="ambient °C")
    if len(wx) == 0:
        axw.text(0.5, 0.5, "no weather for these attempts", transform=axw.transAxes, ha="center", color=INK2)
    axw.legend(fontsize=6.5, loc="center left", bbox_to_anchor=(1.01, 0.5))
    axw.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    axw.set_xlabel("local time; grey bands = ±30 min around t1 and t2 (primary context window)")
    fig.suptitle(f"{a.year} {a.canonical_engineering_team} — target #{a.target_car} {a.target_driver}{title_note}", x=0.01, y=0.995, ha="left", va="top", fontsize=10.5)
    fig.text(0.01, 0.915, f"observed Δ {a.observed_delta_speed:+.3f} mph · frozen LOYO expected {a.frozen_expected_delta_loyo:+.3f} · target residual {a.target_residual:+.3f} · "
             f"category(±30) {a.category} · label {a.label}", fontsize=7.5, color=INK2)
    save(fig, path, top=0.9)


# ------------------------------------------------------------------ summary figures
def summary_figures(tt, st, al, obs, tco, perm_draws, perm, st25):
    S = FIG / "summary"
    # 1 attrition
    anyctx = set(tco.transition_id)
    movectx = set(tco[tco.obs_type == "MOVE"].transition_id)
    ind = obs.set_index("obs_id").frozen_independent
    indctx = set(tco[tco.obs_id.map(ind)].transition_id)
    indmove = set(tco[(tco.obs_type == "MOVE") & tco.obs_id.map(ind)].transition_id)
    p30 = st[st.window == "30"]
    steps = [("frozen transitions", 41), ("target in primary layer, timed", int(tt.target_team_in_primary_layer.sum())),
             ("any timed teammate attempt (session)", len(anyctx)), ("any frozen-independent teammate attempt", len(indctx)),
             ("any teammate previous-attempt move", len(movectx)), ("any frozen-independent move", len(indmove)),
             ("±30 context: category A or B", int(p30.category.isin(["A", "B"]).sum())), ("±30 context: category A", int((p30.category == "A").sum()))]
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    ax.barh(range(len(steps))[::-1], [s[1] for s in steps], color=CAT[0], height=0.62)
    for i, (lab, v) in enumerate(steps):
        ax.text(v + 0.4, len(steps) - 1 - i, str(v), va="center", fontsize=8)
    ax.set_yticks(range(len(steps))[::-1], [s[0] for s in steps], fontsize=8)
    ax.set_xlim(0, 46)
    ax.set_xlabel("frozen same-car transitions")
    ax.set_title("1. Evidence attrition: 41 frozen transitions → structurally identifiable team context", loc="left", fontsize=10.5)
    save(fig, S / "fig1_evidence_attrition.png", top=0.97)
    # 2 independent teammate evidence per transition
    cnt = tco.assign(lab=tco.obs_id.map(obs.set_index("obs_id").independence_label)).groupby(["transition_id", "obs_type", "lab"]).size().unstack([1, 2], fill_value=0)
    cnt = cnt.reindex(tt.transition_id, fill_value=0)
    lbl = [f"{r.year} #{r.target_car} {r.target_driver.split()[-1]}" for r in tt.itertuples(index=False)]
    order = [("LEVEL", "INDEPENDENT_OF_FROZEN_CORE"), ("LEVEL", "OTHER_DEPENDENT_REUSE"), ("LEVEL", "UNKNOWN_DEPENDENCE"), ("LEVEL", "FROZEN_CORE_ENDPOINT"),
             ("MOVE", "INDEPENDENT_OF_FROZEN_CORE"), ("MOVE", "UNKNOWN_DEPENDENCE"), ("MOVE", "RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE")]
    fig, ax = plt.subplots(figsize=(9, 9))
    left = np.zeros(len(cnt))
    for k, key in enumerate(order):
        v = cnt[key].values if key in cnt.columns else np.zeros(len(cnt))
        ax.barh(range(len(cnt)), v, left=left, color=CAT[k], edgecolor=SURFACE, linewidth=1.2, height=0.7, label=f"{key[0]} · {key[1]}")
        left += v
    ax.set_yticks(range(len(cnt)), lbl, fontsize=6.8)
    ax.invert_yaxis()
    ax.set_xlabel("teammate observations anywhere in the session (all windows)")
    ax.legend(fontsize=6.8, loc="lower right")
    ax.set_title("2. Teammate evidence per frozen transition by independence label", loc="left", fontsize=10.5)
    save(fig, S / "fig2_independent_evidence_per_transition.png", top=0.97)
    # 3 target residual vs S6 (all windows where defined)
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.6), sharex=True, sharey=True)
    for ax, w in zip(axes, ["15", "30", "45", "60"]):
        x = al[(al.window == w) & (al.variant == "S6") & al.team_context_value.notna()]
        raw = tt  # all residuals on the axis for context
        ax.axhline(0, color=GRID)
        ax.axvline(0, color=GRID)
        ax.scatter(raw.target_residual, np.zeros(len(raw)) - 0.9, marker="|", color=INK2, s=40, label="all 41 residuals (rug)")
        ax.scatter(x.target_residual, x.team_context_value, s=36, color=CAT[1], edgecolor=INK, label="labelled (cat. A/B)")
        ss = pd.read_csv(OUT / "team_context_summary.csv")
        y = ss[(ss.window == w) & ss.S6_car_balanced_median_adj_move.notna()]
        ax.scatter(y.target_residual, y.S6_car_balanced_median_adj_move, s=22, facecolor="none", edgecolor=CAT[0],
                   label="S6 defined (incl. category C; frozen-reciprocal moves)")
        ax.set_title(f"±{w} min (S6 defined n={len(y)})", fontsize=9)
        ax.set_xlabel("target residual (mph)")
    axes[0].set_ylabel("team context S6 (mph, physics-adjusted)")
    axes[-1].legend(fontsize=6.3, loc="upper left")
    fig.suptitle("3. Target residual vs car-balanced teammate previous-attempt move (S6)", x=0.01, ha="left", fontsize=10.5)
    save(fig, S / "fig3_residual_vs_team_context.png")
    # 5 category distribution by window (Era B and 2025 separately)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    for ax, d, ttl in [(axes[0], st, "2020–2024 frozen anchors (41)"), (axes[1], st25, "2025 extension (separate; raw deltas)")]:
        tab = pd.crosstab(d.window, d.category).reindex(columns=["A", "B", "C", "D"], fill_value=0).reindex(["15", "30", "45", "60", "INTERVAL"])
        left = np.zeros(len(tab))
        for k, c in enumerate(["A", "B", "C", "D"]):
            ax.barh(tab.index, tab[c], left=left, color=CAT[k], edgecolor=SURFACE, linewidth=1.5, label=c, height=0.6)
            left += tab[c].values
        ax.set_title(ttl, fontsize=9)
        ax.set_xlabel("transitions")
        ax.legend(fontsize=7, ncol=4, loc="lower right")
    axes[0].set_ylabel("context window")
    fig.suptitle("5. Structural identifiability category by window (pre-declared rules)", x=0.01, ha="left", fontsize=10.5)
    save(fig, S / "fig5_identifiability_categories.png")
    # placebo/permutation figure
    P = FIG / "placebo"
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    for ax, col, lab in [(axes[0], "T1_sign_agree", "T1: fraction sign(S6)=sign(r)"), (axes[1], "T2_median_abs_diff", "T2: median |S6 − r| (mph)")]:
        ax.hist(perm_draws[col].dropna(), bins=30, color=CAT[0], edgecolor=SURFACE)
        o = perm[perm.statistic == col].observed.iloc[0]
        ax.axvline(o, color=CAT[1], lw=2.5, label=f"observed same-team = {o:.3f}")
        ax.set_xlabel(lab)
        ax.legend(fontsize=7.5)
    axes[0].set_ylabel("within-year team-label shuffles (2000)")
    fig.suptitle(f"4. Same-team vs shuffled-team context (±30; n = {int(perm[perm.statistic=='T3_n_defined'].observed.iloc[0])} transitions with S6, all built from frozen-reciprocal moves)",
                 x=0.01, ha="left", fontsize=10)
    save(fig, P / "fig4_same_team_vs_shuffled_permutation.png")


def andretti(tt, team_j, obs, tco):
    A = FIG / "2021_andretti"
    g = team_j[(team_j.year == 2021) & (team_j.canonical_engineering_team == "ANDRETTI") & team_j.on_performance_timeline].sort_values("attempt_timestamp_utc")
    cars = sorted(g.registry_car_number.unique(), key=car_key)
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 8.5), sharex=True)
    for i, c in enumerate(cars):
        h = g[g.registry_car_number == c]
        col, mk = CAT[i % 8], MK[i % 7]
        x = [loc(t) for t in h.attempt_timestamp_utc]
        fr = h.is_frozen_core_attempt.values
        axes[0].scatter(x, h.four_lap_average_speed_mph, s=46, marker=mk, color=col, edgecolor=INK if fr.any() else SURFACE,
                        label=f"#{c} {h.registry_driver.iloc[0]} (n={len(h)})")
        axes[1].scatter(x, h.speed_minus_car_mean if len(h) >= 2 else [0] * len(h), s=46, marker=mk, color=col if len(h) >= 2 else SURFACE, edgecolor=col)
        mv = obs[(obs.obs_type == "MOVE") & (obs.year == 2021) & (obs.car == c)]
        for m in mv.itertuples(index=False):
            axes[2].plot([loc(m.t_prev), loc(m.t_curr)], [m.physics_adjusted_move] * 2, color=col, lw=3, solid_capstyle="butt")
            axes[2].text(loc(m.t_curr), m.physics_adjusted_move, f" {m.independence_label.split('_')[0]}", fontsize=6.5, color=col, va="center")
    axes[0].set_ylabel("raw four-lap (mph)")
    axes[1].set_ylabel("speed − car mean")
    axes[1].axhline(0, color=INK2, lw=0.7)
    axes[2].axhline(0, color=INK2, lw=0.7)
    axes[2].set_ylabel("physics-adjusted\nprevious-attempt move")
    axes[0].legend(fontsize=6.8, loc="center left", bbox_to_anchor=(1.01, 0.5))
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    axes[2].set_xlabel("local time; bars span each car's previous→current attempt interval; text = independence label")
    fig.suptitle("2021 Andretti — dense QA case: raw, car-relative, and previous-attempt moves (not representative)", x=0.01, ha="left", fontsize=10.5)
    save(fig, A / "andretti_2021_team_overview.png")
    for a in tt[(tt.year == 2021) & (tt.canonical_engineering_team == "ANDRETTI")].itertuples(index=False):
        context_figure(a, team_j, obs, tco, A / f"andretti_2021_{a.target_car}_{a.transition_id[:8]}.png", " [2021 Andretti QA]")


def reports(tt, st, al, obs, tco, summ, plc, perm, case, st25, al25):
    p30 = st[st.window == "30"]
    anyctx = set(tco.transition_id)
    ind = obs.set_index("obs_id").frozen_independent
    indctx = set(tco[tco.obs_id.map(ind)].transition_id)
    movectx = set(tco[tco.obs_type == "MOVE"].transition_id)
    indmove = set(tco[(tco.obs_type == "MOVE") & tco.obs_id.map(ind)].transition_id)
    cat = pd.crosstab(st.window, st.category).reindex(columns=["A", "B", "C", "D"], fill_value=0).reindex(["15", "30", "45", "60", "INTERVAL"])
    dom = st.groupby("window").apply(lambda d: pd.Series({"with_move_context": int((d.n_move.fillna(0) > 0).sum()),
                                                          "dominated_by_frozen_reuse": int(d.dominated_by_frozen_reuse.fillna(False).astype(bool).sum())}),
                                     include_groups=False).reindex(["15", "30", "45", "60", "INTERVAL"])
    labs = pd.crosstab([al.window, al.variant], al.label)
    defined = al[al.team_context_value.notna()][["window", "variant", "transition_id", "category", "label", "contributing_cars", "target_residual",
                                                  "team_context_value", "abs_residual", "abs_team_context", "ratio_S_over_r", "abs_diff"]]
    r = tt.target_residual
    rq = pd.DataFrame([dict(n=len(r), mean=r.mean(), sd=r.std(), min=r.min(), q25=r.quantile(.25), median=r.median(), q75=r.quantile(.75), max=r.max(),
                            abs_median=r.abs().median())])
    s30 = summ[summ.window == "30"]
    sq = []
    for c in ["S1_centered_near_t1", "S2_centered_near_t2", "S3_centered_between", "S4_nearest_move_adj", "S5_median_adj_move",
              "S6_car_balanced_median_adj_move", "S6_IND", "S8_common_car_centered_change"]:
        x = s30[c].dropna() if c in s30 else pd.Series(dtype=float)
        sq.append(dict(summary=c, n_defined=len(x), median=x.median() if len(x) else np.nan, abs_median=x.abs().median() if len(x) else np.nan,
                       min=x.min() if len(x) else np.nan, max=x.max() if len(x) else np.nan))
    sq = pd.DataFrame(sq)
    s6 = summ[summ.S6_car_balanced_median_adj_move.notna()]
    sgn = s6.groupby("window").apply(lambda d: pd.Series({"n_S6_defined": len(d), "sign_agree": float((np.sign(d.S6_car_balanced_median_adj_move) == np.sign(d.target_residual)).mean()),
                                                          "median_abs_diff": float((d.S6_car_balanced_median_adj_move - d.target_residual).abs().median()),
                                                          "median_abs_S6": float(d.S6_car_balanced_median_adj_move.abs().median()),
                                                          "median_abs_residual_same_transitions": float(d.target_residual.abs().median())}), include_groups=False).reset_index()
    big = pd.read_csv(OUT / "large_residual_case_summary.csv")[["year", "canonical_engineering_team", "target_driver", "observed_delta_speed",
                                                                "frozen_expected_delta_loyo", "target_residual", "category", "n_level", "n_move", "label"]]
    ol = obs.groupby(["obs_type", "independence_label"]).size().rename("observations").reset_index()
    reuse = obs.groupby("obs_type").agg(max_contexts=("context_of_n_transitions_any", "max"), median_contexts=("context_of_n_transitions_any", "median"),
                                        used_in_2plus=("used_elsewhere_in_analysis", "sum")).reset_index()
    and_t = tt[(tt.year == 2021) & (tt.canonical_engineering_team == "ANDRETTI")][["target_driver", "target_car", "observed_delta_speed", "frozen_expected_delta_loyo",
                                                                                     "target_residual", "category", "n_level", "n_move", "move_cars", "frozen_independent_moves", "label"]]
    and_mv = obs[(obs.obs_type == "MOVE") & (obs.year == 2021) & (obs.canonical_engineering_team == "ANDRETTI")][
        ["car", "driver", "previous_attempt_delta", "delta_time_min", "delta_track_c", "physics_adjusted_move", "independence_label", "frozen_pair_transition"]]
    c25 = pd.crosstab(st25.window, st25.category).reindex(columns=["A", "B", "C", "D"], fill_value=0)
    l25 = al25[al25.window == "30"].groupby(["variant", "label"]).size().rename("n").reset_index()
    head = case.headline_by_precedence_C_D_B_A.iloc[0]

    fr = f"""# V4 Phase 4D — Latent Team-State / Residual-Attribution Feasibility Report

**Specification:** `phase4d_identifiability_spec.md`, committed as `7a817ae` before any context, category or alignment was computed. The rules were not changed afterwards.

**Scope:**
- No latent, state-space, Gaussian-process, factor or HMM model was fitted, and no coefficient was refitted.
- Phase 4C, FINAL_V2, V3 and the paper are untouched.
- The frozen full-data coefficients are only *applied* to teammate previous-attempt changes (spec §2).

**Anchors:** the 41 frozen 2020–2024 transitions. The target residual is the frozen `residual_loyo_raw` (= observed − frozen LOYO expected Δ). No in-sample full-model expected value is stored per transition in the frozen manifest; that is reported, not reconstructed. The frozen backtest median is carried as secondary context.

## 1–3. Coverage

| Level | Transitions |
|---|---|
| Frozen transitions | 41 |
| Target in primary layer with timed endpoints | {int(tt.target_team_in_primary_layer.sum())} |
| Any timed teammate attempt anywhere in the session | **{len(anyctx)}** |
| Any frozen-independent teammate attempt (LEVEL) | **{len(indctx)}** |
| Any teammate previous-attempt move (repeated teammate-car information) | **{len(movectx)}** |
| Any frozen-independent teammate move | **{len(indmove)}** |

- **Why moves are almost all frozen evidence:** across 2020–2024, the teammate previous-attempt moves available are {int((obs.obs_type=='MOVE').sum())} in total. Of these, **{int(((obs.obs_type=='MOVE') & (obs.independence_label=='RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE')).sum())} are themselves frozen transitions**. The remaining ones are 1 `UNKNOWN_DEPENDENCE` (2024 Ilott, link-uncertain) and 1 without weather (2024 Rossi, not physics-adjustable).
- **Consequence:** repeated teammate-car information in the reference era *is* the frozen core, seen from another car.

## 4–5. Structural categories by window (pre-declared rules)

{md(cat, index=True)}

Transitions with move context, and how many of them are dominated by frozen-core reuse:

{md(dom, index=True)}

**Category A: none at any window.** B appears only at ±45 (2) and ±60 (3), always from frozen-reciprocal moves of ≥2 cars.

## 6–7. Team-context movement estimates

- **At ±30:** S6 (car-balanced median physics-adjusted teammate move) is *defined* for {int(s30.S6_car_balanced_median_adj_move.notna().sum())} transitions, but every one rests on single-car, frozen-reciprocal moves (category C). **0 transitions** support a structurally identifiable team-context movement estimate at ±30.
- **Dominated by frozen-core reuse:** every transition with move context, at every window (table above).

## 8. Target-residual distribution (all 41; frozen LOYO residuals)

{md(rq)}

## 9. Team-context summaries at ±30 (descriptive; where defined)

{md(sq)}

## 10–12. Alignment (pre-declared labels)

{md(labs, index=True)}

- **Primary (S6, ±30):** all 41 transitions are `INSUFFICIENT_TEAM_CONTEXT`.
- **Wider windows:** at ±45/±60, the handful of labels come from category-B cases built entirely from frozen-reciprocal moves. They carry no evidence independent of the frozen core.
- **Independent-evidence-only (S6_IND):** `INSUFFICIENT_TEAM_CONTEXT` for all 41 transitions at every window.

**Descriptive S6 vs residual wherever S6 is defined** (including category C; not a label):

{md(sgn.round(3))}

**Magnitude:**
- **The rows in the table above** (sign agreement, median |S6 − r|): at ±30, sign agreement is about a coin flip, 0.50.
- **Scale:** the typical |S6| is a fraction of the typical |residual|.
- **Where labels exist**, the ratio and absolute difference are listed per transition below. No magnitude threshold was declared, and none is inferred.

{md(defined.round(3))}

## 13. Same-team vs unrelated-team placebo

- **At ±30:** no transition is category A/B, so the pre-declared placebo is **not identifiable** (`unrelated_team_placebo.csv` is empty by rule).
- **Descriptive substitute:** the permutation below compares same-team with shuffled-team context on all transitions where S6 is defined. See `phase4d_placebo_report.md`.

## 14. Permutation (within-year team-label shuffle, 2000 draws)

{md(perm[['statistic','observed','perm_median','perm_p05','perm_p95','observed_percentile','meaningful']].round(3))}

- **Sign agreement:** same-team context is no better than shuffled-team context (49th percentile).
- **Magnitude:** same-team |S6 − r| is somewhat smaller than typical shuffles (79th percentile). But every same-team S6 here is another frozen transition's physics-adjusted change, so this is **not** independent team-state evidence.
- **Meaningfulness:** the diagnostic is formally meaningful (≥5 transitions defined) but substantively uninformative.

## 15. Large-residual case studies (the 8 largest |residual|; selection only)

{md(big.round(3))}

- **Largest cases:** the five largest residuals (Harvey 2021 +4.70, Ilott 2023 +3.47, Hanley 2020, Chilton 2020, VeeKay 2024) have **no timed teammate attempt at all** (category D). Their unexplained movement cannot be attributed to shared or isolated anything.
- **The next three:** Herta 2021, Kellett 2021 and Kanaan 2023 have teammate LEVEL observations only (category C), so they are also unidentifiable.
- **Figures:** `figures/large_residual_cases/`.

## 16. 2021 Andretti (dense QA case; not representative)

{md(and_t.round(3))}

Andretti 2021 teammate moves:

{md(and_mv.round(3))}

- **Every move is frozen evidence.** All {len(and_mv)} Andretti 2021 previous-attempt moves are themselves frozen transitions (Wilson ×2, Herta ×1, Marco Andretti ×2). Rossi, Hunter-Reay and Hinchcliffe contribute only single attempts.
- **Why the movements appear to conflict:**
  - *Different car baselines* (raw speeds span ≈2 mph).
  - *Different temporal positions* (local time):
    - Herta: ≈14:12 → 16:25.
    - Marco: ≈12:06 → 14:55 → 17:25.
    - Wilson: ≈12:30 → 15:07 → 17:12.
  - *Different repeated-run trajectories:*
    - Herta −1.42 mph.
    - Marco +0.61, then −0.00.
    - Wilson −0.02, then −0.06.
  - These moves overlap in time yet disagree, so a "team state" moving everyone together is not supported. Each move is a frozen transition, so it is not independent evidence either way.
- **Verdict:** a common team state is **not identifiable**. The only repeated-car information is frozen, and single-attempt cars carry no within-car movement. Figures: `figures/2021_andretti/`.

## 17–18. Interpretation and feasibility case

- **Attribution:** the apparent residual structure is **mostly unidentified**. Where context exists, it is frozen-core evidence re-seen. There is no transition where team-shared vs car-specific movement can be distinguished with independent evidence.

Mechanical case evaluation (precedence C → D → B → A):

{md(case[['case','satisfied','detail']])}

**Headline: CASE {head}, NOT IDENTIFIED.**

## 19–21. Is a latent team-state model justified?

**No.**
- In the 2020–2024 reference era, the "repeated multi-car local information" a latent team state would need is almost exactly the frozen same-car transitions themselves.
- Independent teammate information consists of single attempts, which carry no within-car movement.
- A state-space, Gaussian-process or factor model would produce smooth latent curves that the data do not identify.

**What team context is still useful for:**
- (i) *Case-level qualitative context* around individual transitions: who else ran, when, and under what state (`figures/context_timelines/`).
- (ii) *Flagging* transitions whose residuals have no teammate context at all. These include the five largest residuals.
- (iii) *A documented negative result* for the paper's limitations: teammate data cannot separate team-shared from car-specific unexplained movement in this historical design.
- (iv) *A starting point:* if future sessions provide many independent repeated runs per car, the same structural audit can be re-run before any latent model is considered.

**2025 extension** (separate; raw deltas; never pooled):

{md(c25, index=True)}

{md(l25)}

In 2025, every teammate move is itself another 2025 anchor (reciprocal by construction), so `S6_IND` is insufficient everywhere. The few category-B labels are self-referential and give no independent attribution.

## 22. Outputs

See `phase4d_checks_log.txt` and the file list in `README`.
"""
    (OUT / "phase4d_feasibility_report.md").write_text(fr)

    ir = f"""# V4 Phase 4D — Evidence-Independence Report

Labels follow spec §3: exclusive, with precedence RECIPROCAL → FROZEN_ENDPOINT → UNKNOWN → OTHER_REUSE → INDEPENDENT.

{md(ol)}

**Reuse:** the number of frozen transitions whose session context contains the observation.

{md(reuse)}

## Findings

- **LEVEL observations:** {int(((obs.obs_type=='LEVEL') & obs.independence_label.isin(FROZEN_LINKED)).sum())} of {int((obs.obs_type=='LEVEL').sum())} teammate attempts are frozen-core endpoints. The frozen-independent ones are mostly single attempts of cars that ran once, so they carry no within-car movement.
- **MOVE observations** (the primary local-movement representation): **{int(((obs.obs_type=='MOVE') & (obs.independence_label=='RECIPROCAL_OR_OVERLAPPING_CORE_EVIDENCE')).sum())} of {int((obs.obs_type=='MOVE').sum())} are themselves frozen transitions.** Using them as "team context" for another frozen transition would count the frozen core twice. Reciprocity is common: when two teammates both have frozen transitions in a team-year, each serves as the other's context.
- **Link uncertainty:** `UNKNOWN_DEPENDENCE` MOVEs are flagged where a car has untimed attempts, or timed incomplete attempts inside the pair, so the "immediately previous attempt" cannot be confirmed.
- **Conclusion:** there is no body of independent, repeated teammate evidence in 2020–2024 from which to separate a team-level state.
"""
    (OUT / "phase4d_independence_report.md").write_text(ir)

    pr = f"""# V4 Phase 4D — Placebo / Negative-Control Report

## Pre-declared unrelated-team placebo (spec §8)

- **Scope:** defined only for transitions in category A/B at ±30. There are **none**, so the placebo is **not identifiable**, and `unrelated_team_placebo.csv` contains no rows.
- **This is itself a finding:** no transition has structurally adequate same-team context to compare against unrelated teams.

## Permutation diagnostic (spec §9)

- **Shuffle:** within each year, team labels are reassigned to cars, preserving team sizes. 2000 draws, seed 20260928.
- **Statistics:** computed on transitions whose (pseudo-)team S6 at ±30 is defined, whatever their category.

{md(perm[['statistic','observed','perm_median','perm_p05','perm_p95','observed_percentile','meaningful','note']].round(3))}

## Reading

- **Sign alignment:** the real team is no better than a random team (T1 at the 49th percentile).
- **Magnitude:** T2 at the 79th percentile means the same-team |S6 − r| is smaller than most shuffles. The observed same-team S6 values are other frozen transitions' physics-adjusted deltas, so any closeness partly reflects frozen transitions from the same team and session sharing environment, and the frozen model's residual structure. It does not reflect independent team-state evidence.
- **Not tested:** no unrelated-team signal was tested beyond this. CASE D (session-wide rather than team-specific structure) could not be evaluated, because the placebo is not identifiable.
- **Caveats:** transitions are dependent (shared teammates, reciprocity), and no p-value is claimed.

Figure: `figures/placebo/fig4_same_team_vs_shuffled_permutation.png`.
"""
    (OUT / "phase4d_placebo_report.md").write_text(pr)


def main():
    for d in ["context_timelines", "large_residual_cases", "2021_andretti", "placebo", "summary"]:
        (FIG / d).mkdir(parents=True, exist_ok=True)
    tt = pd.read_csv(OUT / "transition_team_context.csv", dtype={"target_car": str})
    tt["t1"], tt["t2"] = pd.to_datetime(tt.t1, utc=True, format="mixed"), pd.to_datetime(tt.t2, utc=True, format="mixed")
    st = pd.read_csv(OUT / "identifiability_by_transition.csv", dtype={"window": str})
    al = pd.read_csv(OUT / "residual_context_alignment.csv", dtype={"window": str})
    obs = pd.read_csv(OUT / "evidence_independence_audit.csv", dtype={"car": str}, low_memory=False)
    for c in ["t_prev", "t_curr"]:
        obs[c] = pd.to_datetime(obs[c], utc=True, format="mixed")
    obs["frozen_independent"] = obs.frozen_independent.astype(str).eq("True")
    tco = pd.read_csv(OUT / "team_context_observations.csv", low_memory=False)
    summ = pd.read_csv(OUT / "team_context_summary.csv", dtype={"window": str})
    plc = pd.read_csv(OUT / "unrelated_team_placebo.csv")
    perm = pd.read_csv(OUT / "permutation_diagnostic.csv")
    perm_draws = pd.read_csv(OUT / "permutation_draws.csv")
    case = pd.read_csv(OUT / "feasibility_case_evaluation.csv")
    st25 = pd.read_csv(OUT / "extension_2025_identifiability.csv", dtype={"window": str})
    al25 = pd.read_csv(OUT / "extension_2025_alignment.csv", dtype={"window": str})
    j = pd.read_csv(V4 / "output/phase4b/team_timeline_long.csv", dtype={"car_number": str, "registry_car_number": str}, low_memory=False)
    for b in ["on_performance_timeline", "is_frozen_core_attempt"]:
        j[b] = j[b].astype(str).eq("True")
    j["attempt_timestamp_utc"] = pd.to_datetime(j.attempt_timestamp_utc, utc=True, format="mixed")
    tt["label"] = tt.label.fillna("INSUFFICIENT_TEAM_CONTEXT")
    for a in tt[tt.category != "D"].itertuples(index=False):
        context_figure(a, j, obs, tco, FIG / "context_timelines" / f"{a.year}_{a.canonical_engineering_team}_{a.target_car}_{a.transition_id[:8]}.png")
    for a in tt.nsmallest(8, "abs_target_residual_rank").itertuples(index=False):
        context_figure(a, j, obs, tco, FIG / "large_residual_cases" / f"rank{a.abs_target_residual_rank:02d}_{a.year}_{a.target_car}.png",
                       f"  [large-residual case, |r| rank {a.abs_target_residual_rank}]")
    andretti(tt, j, obs, tco)
    summary_figures(tt, st, al, obs, tco, perm_draws, perm, st25)
    reports(tt, st, al, obs, tco, summ, plc, perm, case, st25, al25)


if __name__ == "__main__":
    main()
