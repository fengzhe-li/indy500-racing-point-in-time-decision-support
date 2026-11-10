"""V4 Phase 4J: figures and reports (reads Phase 4J outputs only)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "output" / "phase4j"
FIG = OUT / "figures"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 9, "legend.frameon": False})
DIAG = ("Phase 4J FINAL pre-registered hierarchy (spec 28af221) · Tier 1 class-A car-blocks · 2023–24 primary; 2025 separate · "
        "Timing71 archived live-feed (third-party) · empirical control hierarchy, not causal · no team ranking")
LC = {"same car": CAT[0], "same team": CAT[1], "different team": CAT[2]}
AN = {"PRIMARY_TIER1_2023_2024": "Tier 1 2023–24 (PRIMARY)", "TIER2_SENSITIVITY_2023_2024": "Tier 2 2023–24 (sensitivity)", "REPLICATION_2025_TIER1": "Tier 1 2025 (replication)"}


def md(df):
    f = lambda v: "" if (isinstance(v, float) and np.isnan(v)) else (f"{v:.3f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))
    return "\n".join(["| " + " | ".join(map(str, df.columns)) + " |", "|" + "|".join("---" for _ in df.columns) + "|"]
                     + ["| " + " | ".join(f(v) for v in r) + " |" for r in df.itertuples(index=False)])


def save(fig, name, top=0.92):
    fig.tight_layout(rect=(0, 0.05, 1, top))
    fig.text(0.01, 0.01, DIAG, fontsize=6.2, color=INK2)
    fig.savefig(FIG / name, dpi=140, bbox_inches="tight")
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    CX = pd.read_csv(OUT / "primary_common_support.csv", dtype={"session_key": str})
    SC = pd.read_csv(OUT / "same_car_primary.csv", dtype={"session_key": str})
    SL = pd.read_csv(OUT / "session_level_hierarchy.csv", dtype={"session_key": str})
    HS = pd.read_csv(OUT / "hierarchy_summary_all_analyses.csv")
    LO = pd.read_csv(OUT / "leave_one_session_out.csv", dtype={"dropped_session": str})
    LT = pd.read_csv(OUT / "leave_one_team_out.csv")
    PS = pd.read_csv(OUT / "performance_scale_context.csv")
    CE = pd.read_csv(OUT / "case_evaluation.csv").set_index("criterion").value
    COV = pd.read_csv(OUT / "same_team_primary.csv")
    T2 = pd.read_csv(OUT / "tier2_sensitivity.csv", dtype={"session_key": str}, low_memory=False)
    R25 = pd.read_csv(OUT / "replication_2025.csv", dtype={"session_key": str}, low_memory=False)
    cs = CX[CX.in_common_support]
    P = SL[SL.analysis == "PRIMARY_TIER1_2023_2024"]
    Pe = P[P.evaluable]

    # 1 three-layer dispersion
    fig, ax = plt.subplots(figsize=(9, 4))
    data = [SC[SC.session_key.isin(Pe.session_key)].D_mph, cs.D_same_team, cs.D_diff_team_ctx]
    names = ["same car\n(local repeat pairs)", "same team\n(common-support contexts)", "different team\n(context median of admissible candidates)"]
    bp = ax.boxplot(data, tick_labels=[f"{n}\nn={len(d)}" for n, d in zip(names, data)], widths=0.5, showfliers=False, medianprops=dict(color=INK, lw=2))
    rng = np.random.default_rng(1)
    for k, (d, c) in enumerate(zip(data, LC.values())):
        ax.scatter(k + 1 + rng.uniform(-0.15, 0.15, len(d)), d, s=12, color=c, alpha=0.6, zorder=3)
    ax.set_ylabel("D = |Δ car-block median speed| (mph)")
    ax.set_title("1. Tier 1 primary: three-layer dispersion (pooled context values; the estimand is session-balanced)", loc="left", fontsize=10)
    save(fig, "fig01_three_layer_tier1.png", top=0.97)

    # 2 session-level hierarchy
    fig, ax = plt.subplots(figsize=(10, 3.8))
    x = np.arange(len(Pe))
    for k, (col, lab) in enumerate([("D_same_car", "same car"), ("D_same_team", "same team"), ("D_diff_team", "different team")]):
        ax.plot(x + (k - 1) * 0.12, Pe[col], "o", ms=8, color=LC[lab], label=lab)
    for xi, r in zip(x, Pe.itertuples(index=False)):
        ax.plot([xi - 0.12, xi, xi + 0.12], [r.D_same_car, r.D_same_team, r.D_diff_team], color=INK2, lw=0.8)
    ax.set_xticks(x, [f"{s}\n(ctx {c}, sc {n})" for s, c, n in zip(Pe.session_key, Pe.contexts, Pe.same_car_pairs)], fontsize=7.5)
    ax.set_ylabel("session median D (mph)")
    ax.legend(fontsize=7.5)
    ax.set_title("2. Session-level three-layer medians, Tier 1 2023–24 (evaluable sessions)", loc="left", fontsize=10.5)
    save(fig, "fig02_session_level_hierarchy.png", top=0.97)

    # 3 C1/C2 by session
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.bar(x - 0.2, Pe.C1, width=0.38, color=CAT[3], label="C1 = D_same-team − D_same-car")
    ax.bar(x + 0.2, Pe.C2, width=0.38, color=CAT[6], label="C2 = paired D_diff-team − D_same-team")
    ax.axhline(0, color=INK)
    ax.set_xticks(x, Pe.session_key)
    ax.set_ylabel("mph")
    ax.legend(fontsize=7.5)
    ax.set_title(f"3. Contrasts by session (C1 positive in {int((Pe.C1 > 0).sum())}/{len(Pe)}; C2 positive in {int((Pe.C2 > 0).sum())}/{len(Pe)})", loc="left", fontsize=10.5)
    save(fig, "fig03_contrasts_by_session.png", top=0.97)

    # 4 common support / adjacency
    cats = ["SAME_UPDATE", "CONSECUTIVE", "BETWEEN_1_2", "BETWEEN_3_5", "BETWEEN_GT5"]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    allc = CX.adjacency_category.value_counts().reindex(cats, fill_value=0)
    inc = cs.adjacency_category.value_counts().reindex(cats, fill_value=0)
    ax.bar(np.arange(5) - 0.2, allc, width=0.38, color=INK2, alpha=0.5, label="all same-team contexts")
    ax.bar(np.arange(5) + 0.2, inc, width=0.38, color=CAT[1], label="in strict common support (≥1 same-stratum candidate)")
    ax.set_xticks(range(5), ["same update\n(order unobserved)", "consecutive", "1–2 between", "3–5 between", ">5 between"])
    ax.set_ylabel("oriented contexts")
    ax.legend(fontsize=7.5)
    ax.set_title("4. Common support by timing-adjacency stratum (exact-stratum rule; no substitution)", loc="left", fontsize=10.5)
    save(fig, "fig04_common_support_adjacency.png", top=0.97)

    # 5 LOSO / LOTO
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True)
    lo, lt = LO[LO.analysis == "PRIMARY_TIER1_2023_2024"], LT[LT.analysis == "PRIMARY_TIER1_2023_2024"]
    prim = HS[HS.analysis == "PRIMARY_TIER1_2023_2024"].iloc[0]
    for ax, d, lab, col in [(axes[0], lo, "dropped session", "dropped_session"), (axes[1], lt, "dropped team", "dropped_team")]:
        xx = np.arange(len(d))
        ax.plot(xx, d.C1, "o", color=CAT[3], label="C1")
        ax.plot(xx, d.C2, "s", color=CAT[6], label="C2")
        ax.axhline(prim.C1, color=CAT[3], ls=":", lw=1)
        ax.axhline(prim.C2, color=CAT[6], ls=":", lw=1)
        ax.axhline(0, color=INK)
        ax.set_xticks(xx, d[col].astype(str).str.replace("_", " ").str.lower(), rotation=35, ha="right", fontsize=7)
        ax.set_title(f"leave one {lab.split()[1]} out", loc="left", fontsize=9.5)
    axes[0].set_ylabel("contrast (mph); dotted = full primary")
    axes[0].legend(fontsize=7.5)
    fig.suptitle("5. Leave-one-out stability of the primary contrasts (diagnostic only)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig05_leave_one_out.png")

    # 6 / 7 cross-analysis comparisons
    for fname, keys, title in [("fig06_tier1_vs_tier2.png", ["PRIMARY_TIER1_2023_2024", "TIER2_SENSITIVITY_2023_2024"], "6. Tier 1 primary vs Tier 2 sensitivity"),
                               ("fig07_2023_24_vs_2025.png", ["PRIMARY_TIER1_2023_2024", "REPLICATION_2025_TIER1"], "7. 2023–24 primary vs 2025 hybrid-era replication")]:
        fig, ax = plt.subplots(figsize=(9, 3.8))
        for k, key in enumerate(keys):
            r = HS[HS.analysis == key].iloc[0]
            for j, c in enumerate(["C1", "C2", "C3"]):
                xx = j + (k - 0.5) * 0.3
                ax.errorbar(xx, r[c], yerr=[[r[c] - r[f"{c}_boot_lo"]], [r[f"{c}_boot_hi"] - r[c]]], fmt="o", ms=8, capsize=4, color=CAT[k], label=f"{AN[key]} · CASE {r.case}" if j == 0 else None)
        ax.axhline(0, color=INK)
        ax.set_xticks(range(3), ["C1\nsame-team − same-car", "C2\ndiff-team − same-team (paired)", "C3\ndiff-team − same-car"])
        ax.set_ylabel("session-balanced median (mph)\nbar = session-bootstrap 95%")
        ax.legend(fontsize=7.5)
        ax.set_title(title, loc="left", fontsize=10.5)
        save(fig, fname, top=0.97)

    # 8 scale
    ps = PS[PS.analysis.isin(["PRIMARY_TIER1_2023_2024", "PHASE4I_REFERENCE"]) & PS.mph.notna()].copy()
    ps = ps[~ps.quantity.str.contains("CROSS_SESSION|TIMESTAMP")]
    fig, ax = plt.subplots(figsize=(10, 4))
    y = np.arange(len(ps))
    ax.barh(y, ps.mph.abs(), color=[CAT[1] if a.startswith("PRIMARY") else INK2 for a in ps.analysis])
    for yi, (v, lt_) in enumerate(zip(ps.mph, ps.laptime_equiv_s_at_225)):
        ax.annotate(f"{v:+.3f} mph ≈ {lt_:+.3f} s" if pd.notna(lt_) else f"{v:.3f}", (abs(v), yi), xytext=(3, -3), textcoords="offset points", fontsize=7)
    ax.set_xscale("log")
    ax.set_yticks(y, [q.replace("_", " ").lower() for q in ps.quantity], fontsize=7)
    ax.set_xlabel("|value| (mph, log); orange = Phase 4J primary, grey = Phase 4I scale references")
    ax.set_title("8. Primary D and contrasts vs empirical measurement scale (no universal threshold)", loc="left", fontsize=10.5)
    save(fig, "fig08_performance_scale_context.png", top=0.97)

    reports(CX, SC, SL, HS, LO, LT, PS, CE, COV, T2, R25)


def reports(CX, SC, SL, HS, LO, LT, PS, CE, COV, T2, R25):
    f3 = lambda v: f"{float(v):+.3f}"
    p = HS[HS.analysis == "PRIMARY_TIER1_2023_2024"].iloc[0]
    t2 = HS[HS.analysis == "TIER2_SENSITIVITY_2023_2024"].iloc[0]
    r5 = HS[HS.analysis == "REPLICATION_2025_TIER1"].iloc[0]
    lt225 = lambda v: f"{float(v) / 225 * 40:+.3f} s"
    hs = HS[["analysis", "role", "case", "C1_status", "C2_status", "evaluable_sessions", "common_support_contexts", "D_same_car", "D_same_team", "D_diff_team", "C1", "C1_boot_lo",
             "C1_boot_hi", "share_sessions_C1_pos", "C2", "C2_boot_lo", "C2_boot_hi", "share_sessions_C2_pos", "C3", "C3_boot_lo", "C3_boot_hi", "C1_from_layer_medians", "C2_from_layer_medians"]]
    sl = SL[["analysis", "session_key", "contexts", "same_car_pairs", "evaluable", "D_same_car", "D_same_team", "D_diff_team", "C1", "C2", "C3"]]
    ce = pd.DataFrame({"criterion": CE.index, "value": CE.values})
    ps = PS
    comp2 = T2[T2.table == "COMPOSITION"][["layer", "composition", "share", "n"]]
    cov2 = T2[T2.table == "COVERAGE"][["item", "value"]]
    cov5 = R25[R25.table == "COVERAGE"][["item", "value"]]
    lo, lt = LO, LT
    rep1 = f"""# V4 Phase 4J — FINAL Pre-registered Performance-Control Hierarchy

**Pre-result specification:** `phase4j_final_hierarchy_spec.md`, committed as **`28af221`** before any D, contrast, bootstrap or leave-one-out value was computed.

**Frozen inputs (verified before the spec; `phase4j_input_verification.csv`):**
- Phase 4F **D**, 4G **A**, 4H **D** and 4I **B**, all unchanged;
- the Phase 4H classes and the Phase 4I eligibility, reproduced exactly.

**Finality:** this is the final V4 hierarchy analysis, and its result is accepted as it is.

## Primary result: CASE {CE['PRIMARY_CASE']} (partial hierarchy)

Population: Tier 1 (class A ↔ A), 2023–2024, strict adjacency common support. There are **{int(p.evaluable_sessions)} evaluable sessions** (the replication unit) and {int(p.common_support_contexts)} common-support same-team contexts.

**Session-balanced medians:**

| Quantity | mph | Lap-time equivalent at 225 mph |
|---|---|---|
| D_same-car | {p.D_same_car:.3f} | |
| D_same-team | {p.D_same_team:.3f} | |
| D_different-team | {p.D_diff_team:.3f} | |
| **C1** = D_same-team − D_same-car | **{f3(p.C1)}** | {lt225(p.C1)} |
| **C2** = paired D_diff-team − D_same-team | **{f3(p.C2)}** | {lt225(p.C2)} |
| C3 = D_diff-team − D_same-car | {f3(p.C3)} | {lt225(p.C3)} |

**C1 is `{p.C1_status}`: supported.**
- The session-bootstrap interval is [{p.C1_boot_lo:.3f}, {p.C1_boot_hi:.3f}].
- It is positive in {p.share_sessions_C1_pos:.0%} of sessions and in every leave-one-session-out and leave-one-team-out recomputation.

**C2 is `{p.C2_status}`: not supported.**
- The session-bootstrap interval is [{p.C2_boot_lo:.3f}, {p.C2_boot_hi:.3f}].
- It is positive in only {p.share_sessions_C2_pos:.0%} of sessions (below the pre-registered 75%).
- Removing Ed Carpenter Racing turns it negative.
- The difference of layer medians is {f3(p.C2_from_layer_medians)}, so its sign depends on the construction.

**What is supported:** *same car < same team*.

**What is not established:** *same team < different team*. The same-team and different-team layers overlap within the adjacency-balanced design.

**Interpretation:**
- This is an **empirical control hierarchy in a restricted population**: 2023–24 practice-type sessions, frozen class-A car-blocks, and 5-min blocks with exact adjacency-stratum support.
- It is **not** a causal team effect, not a variance decomposition, and not a team or driver ranking.
- Tier 2 and 2025 can neither overturn nor replace it.

## All analyses

{md(hs)}

## Session level

{md(sl)}

## Case evaluation

{md(ce)}

## Tier 2 sensitivity (extended measurement validity; never replaces the primary)

**Result:** CASE {t2.case}. C1 is {f3(t2.C1)} (`{t2.C1_status}`) and C2 is {f3(t2.C2)} (`{t2.C2_status}`). Direction agrees with the primary: C1 is supported, C2 is not (its sign reverses).

**Composition** (A_ONLY / B_ONLY / MIXED_AB car-blocks):

{md(comp2)}

## 2025 hybrid-era secondary replication (not pooled)

**Result:** CASE {r5.case}, with {int(r5.evaluable_sessions)} evaluable sessions and {int(r5.common_support_contexts)} contexts.
- C1 is {f3(r5.C1)} (`{r5.C1_status}`); C2 is {f3(r5.C2)} (`{r5.C2_status}`, 60% of sessions positive; interval [{r5.C2_boot_lo:.2f}, {r5.C2_boot_hi:.2f}]).
- It agrees with the primary pattern: C1 is supported and C2 is not consistent.

## Scale (4J.17)

{md(ps)}

**Empirical separation vs competitive significance:**
- **C1 ({p.C1:.2f} mph ≈ {float(p.C1) / 225 * 40:.2f} s per lap)** is larger than the Phase 4I same-car local variation (consecutive A-lap median |Δ| about 0.5 mph) and than the qualifying within-attempt SD (0.37–0.59 mph). It is empirically separated at the session level in this population.
- **C2's point value** ({p.C2:.2f} mph ≈ {float(p.C2) / 225 * 40:.3f} s) is below those references, and its sign is unstable.
- Whether a given mph difference matters competitively depends on context (for example, qualifying margins are often hundredths of a second). **No universal threshold is claimed.**
"""
    rep2 = f"""# V4 Phase 4J — Common-Support Report

## Primary coverage (Tier 1 2023–24)

{md(COV[['item', 'value']])}

**Readings:**
- **Same-update contexts:** none of the 10 has a same-update different-team candidate. They are excluded from the strict contrast, kept in the coverage tables, and no controls were manufactured.
- **Strata in support:** most are in the >5-intervening stratum (41 of 53).
- **Sessions:** 6375 and 6380 have no common-support context, so 6 of the 8 supported sessions are evaluable.
- **Concentration:** one session supplies 38% of contexts, and one team 36%.

## Tier 2 coverage

{md(cov2)}

## 2025 coverage

{md(cov5)}
"""
    rep3 = f"""# V4 Phase 4J — Robustness Report

## Leave-one-session-out

{md(lo)}

## Leave-one-team-out (every car-block of the team removed from all layers)

{md(lt)}

**Readings:**
- **C1** is positive in every primary LOSO and LOTO recomputation.
- **C2** is positive in every LOSO recomputation but negative when Ed Carpenter Racing is removed. Only 4 of 6 sessions are positive.
- **Bootstrap:** the C2 interval spans zero.
- These are diagnostics only. The estimator was not tuned.
"""
    rep4 = f"""# V4 Phase 4J — Limitations Report

1. **Restricted population.** 2023–2024 practice-type sessions only, the frozen Phase 4H class-A car-blocks only (a small minority of raw practice), and 6 evaluable sessions. The result does not generalise to raw practice, other years, qualifying, or the race.
2. **Small, session-clustered evidence.**
   - 53 common-support contexts from 26 teammate pairs and 9 teams.
   - Concentration: up to 38% from one session and 36% from one team.
   - Bootstrap intervals over 6 sessions are wide and only descriptive.
3. **Layer structure differs.**
   - Same-car pairs compare consecutive 5-min blocks (about 82 s apart).
   - Same-team and different-team comparisons are within one block (about 104 s apart).
   - The time scales are comparable but not identical.
4. **Unobserved variables.** Run purpose, fuel, tyres, tow and traffic are unobserved even in class A. Timing adjacency was balanced as a design variable, not modelled.
5. **Adjacency support.** Exact-stratum common support removes all same-update contexts and most close-adjacency contexts. The primary therefore mostly reflects the >5-intervening stratum.
6. **C2 construction.** C2 is paired within context (the same target, block and stratum). The difference of layer medians has the opposite sign. This instability is part of the result.
7. **Oriented contexts.** Each unordered teammate pair contributes two oriented contexts with the same D_same-team, as pre-specified, while the different-team candidates are matched to each target separately. Session medians therefore weight a pair twice when both orientations are in support.
8. **Not claimed:** team effects, rankings, causal decomposition.
9. **Finality.** No Phase 4K and no redesign. The classifier, block width, adjacency rule, aggregation and weighting are frozen as specified in `28af221`.
"""
    for n, r in [("phase4j_final_hierarchy_report.md", rep1), ("phase4j_common_support_report.md", rep2), ("phase4j_robustness_report.md", rep3), ("phase4j_limitations_report.md", rep4)]:
        (OUT / n).write_text(r)


if __name__ == "__main__":
    main()
