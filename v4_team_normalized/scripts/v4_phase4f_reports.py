"""V4 Phase 4F: figures and reports (descriptive; reads Phase 4F outputs only)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "output" / "phase4f"
FIG = OUT / "figures"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
CLS_C = {"SAME_CAR": CAT[0], "SAME_TEAM": CAT[1], "DIFF_TEAM": CAT[2]}
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 9, "legend.frameon": False})
DIAG = "Phase 4F · Timing71 archived live-feed laps (third-party) · 2023–24 primary; 2025 separate · race excluded · no model · no team ranking."


def md(df, index=False):
    d = df.reset_index() if index else df
    f = lambda v: "" if (isinstance(v, float) and np.isnan(v)) else (f"{v:.3f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))
    return "\n".join(["| " + " | ".join(map(str, d.columns)) + " |", "|" + "|".join("---" for _ in d.columns) + "|"]
                     + ["| " + " | ".join(f(v) for v in r) + " |" for r in d.itertuples(index=False)])


def save(fig, name, top=0.92):
    fig.tight_layout(rect=(0, 0.05, 1, top))
    fig.text(0.01, 0.01, DIAG, fontsize=6.5, color=INK2)
    fig.savefig(FIG / name, dpi=140, bbox_inches="tight")
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    C = pd.read_csv(OUT / "comparison_pairs.csv", low_memory=False)
    BL = pd.read_csv(OUT / "block_level_contrasts.csv")
    SB = pd.read_csv(OUT / "session_balanced_results.csv")
    YS = pd.read_csv(OUT / "year_sensitivity.csv")
    CT = pd.read_csv(OUT / "session_type_sensitivity.csv")
    LT = pd.read_csv(OUT / "leave_one_team_out.csv")
    FA = pd.read_csv(OUT / "same_car_fairness.csv")
    DV = pd.read_csv(OUT / "team_relative_deviations.csv")
    CP = pd.read_csv(OUT / "cross_session_persistence.csv")
    DS = pd.read_csv(OUT / "comparison_distribution_summary.csv")
    VA = pd.read_csv(OUT / "car_block_validity.csv")
    DEP = pd.read_csv(OUT / "dependence_audit.csv")
    CE = pd.read_csv(OUT / "case_evaluation.csv")
    WX = pd.read_csv(OUT / "weather_block_diagnostic.csv")
    OX = pd.read_csv(OUT / "official_crosscheck.csv")
    RA = pd.read_csv(OUT / "race_appendix_structural.csv")
    AP = pd.read_csv(OUT / "analysis_population.csv")
    sbs = SB[SB.level == "SESSION_BALANCED"]
    P = C[(C.role == "PRIMARY") & (C.layer == "comparable")]

    # 1 D distributions
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True)
    for ax, (role, ttl) in zip(axes, [("PRIMARY", "2023–2024 primary (comparable layer, 5 min)"), ("ERA_C_SECONDARY", "2025 secondary (separate)")]):
        g = C[(C.role == role) & (C.layer == "comparable")]
        for k, cls in enumerate(["SAME_CAR", "SAME_TEAM", "DIFF_TEAM"]):
            x = g[g["class"] == cls].D_mph.clip(upper=10)
            ax.hist(x, bins=np.arange(0, 10.25, 0.25), histtype="step", lw=1.8, color=CLS_C[cls], density=True, label=f"{cls} (n={len(x)}; median {x.median():.2f})")
        ax.set_xlabel("D = |Δ car-block median speed| (mph, clipped at 10)")
        ax.set_title(ttl, fontsize=9)
        ax.legend(fontsize=7)
    axes[0].set_ylabel("density")
    fig.suptitle("1. Empirical D distributions by comparison class (DIFF_TEAM = pre-registered time-nearest control)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig01_D_distributions.png")

    # 2 block-balanced contrast (per session, both definitions)
    pb = BL[(BL.role == "PRIMARY") & (BL.layer == "comparable")]
    sm = pb.groupby(["session_key", "category"]).agg(delta=("delta_block", "median"), delta_tb=("delta_block_team_balanced", "median"), blocks=("block", "size")).reset_index()
    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(sm))
    ax.bar(x - 0.2, sm.delta, width=0.4, color=CAT[0], label="primary: time-nearest different-team control")
    ax.bar(x + 0.2, sm.delta_tb, width=0.4, color=CAT[1], label="sensitivity: team-balanced all cross-team pairs")
    ax.axhline(0, color=INK2)
    ax.set_xticks(x, [f"{s}\n{c[:12]}\n({b} blk)" for s, c, b in zip(sm.session_key.astype(str).str[-9:], sm.category, sm.blocks)], fontsize=6.5)
    ax.set_ylabel("session median Δ_block (mph)\n>0 = same-team more similar")
    ax.legend(fontsize=7.5)
    ax.set_title("2. Block-level same-team vs different-team contrast per primary session", loc="left", fontsize=10.5)
    save(fig, "fig02_block_contrast_by_session.png", top=0.97)

    # 3 by year, 4 by category
    fig, ax = plt.subplots(figsize=(7, 3.6))
    for k, layer in enumerate(["comparable", "broad"]):
        g = YS[YS.layer == layer]
        ax.bar(np.arange(len(g)) + (k - 0.5) * 0.4, g.session_balanced_delta, width=0.4, color=CAT[k], label=f"{layer} layer")
        ax.set_xticks(np.arange(len(g)), [f"{y}\n{'secondary' if r.startswith('ERA_C') else 'primary'}" for y, r in zip(g.year, g.role)])
    ax.axhline(0, color=INK2)
    ax.set_ylabel("session-balanced Δ (mph)")
    ax.legend(fontsize=7.5)
    ax.set_title("3. Contrast by year (primary control; 2025 separate)", loc="left", fontsize=10.5)
    save(fig, "fig03_contrast_by_year.png", top=0.97)
    fig, ax = plt.subplots(figsize=(10, 3.8))
    cats = sorted(CT.category.unique())
    for k, layer in enumerate(["comparable", "broad"]):
        g = CT[CT.layer == layer].set_index("category").reindex(cats)
        ax.bar(np.arange(len(cats)) + (k - 0.5) * 0.4, g.session_balanced_delta, width=0.4, color=CAT[k], label=f"{layer} layer")
    ax.set_xticks(range(len(cats)), [f"{c}\n({int(CT[(CT.category == c)].sessions.max())} sess)" for c in cats], fontsize=7)
    ax.axhline(0, color=INK2)
    ax.legend(fontsize=7.5)
    ax.set_ylabel("session-balanced Δ (mph)")
    ax.set_title("4. Contrast by session category (primary 2023–24; sparse categories are noisy)", loc="left", fontsize=10.5)
    save(fig, "fig04_contrast_by_category.png", top=0.97)

    # 5 broad vs comparable, 6 window sensitivity
    s1 = sbs[(sbs.min_laps == 1)]
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True)
    for ax, role in zip(axes, ["PRIMARY", "ERA_C_SECONDARY"]):
        for k, (layer, col, lab) in enumerate([("comparable", "session_balanced_delta", "comparable · primary control"), ("broad", "session_balanced_delta", "broad · primary control"),
                                               ("comparable", "session_balanced_delta_team_balanced", "comparable · team-balanced"), ("broad", "session_balanced_delta_team_balanced", "broad · team-balanced")]):
            g = s1[(s1.role == role) & (s1.layer == layer)].sort_values("width_min")
            ax.plot(g.width_min, g[col], "-o" if "primary" in lab else "--s", color=CAT[k], label=lab, ms=4)
        ax.axhline(0, color=INK2)
        ax.set_xticks([1, 2, 5, 10])
        ax.set_xlabel("fixed block width (min)")
        ax.set_title(role, fontsize=9)
    axes[0].set_ylabel("session-balanced Δ (mph)")
    axes[1].legend(fontsize=7)
    fig.suptitle("5–6. Broad vs comparable layer and block-width sensitivity", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig05_06_layer_and_window_sensitivity.png")

    # 7 LOTO
    base = sbs[(sbs.role == "PRIMARY") & (sbs.layer == "comparable") & (sbs.width_min == 5) & (sbs.min_laps == 1)].session_balanced_delta.iloc[0]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    lt = LT.sort_values("dropped_team")
    ax.scatter(lt.session_balanced_delta, range(len(lt)), color=CAT[0], s=30)
    ax.axvline(base, color=CAT[1], label=f"all teams: {base:+.3f}")
    ax.axvline(0, color=INK2, lw=0.8)
    ax.set_yticks(range(len(lt)), [f"without team {i + 1}" for i in range(len(lt))], fontsize=7)
    ax.legend(fontsize=7.5)
    ax.set_xlabel("session-balanced Δ (mph), primary")
    ax.set_title("7. Leave-one-team-out stability (teams anonymised by alphabetical index; no ranking)", loc="left", fontsize=10)
    save(fig, "fig07_leave_one_team_out.png", top=0.97)

    # 8 fairness
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
    for ax, cons in zip(axes, ["ADJACENT_BLOCK_ALL_CLASSES", "TIME_SEPARATION_REWEIGHTED_TO_SAME_CAR"]):
        for k, layer in enumerate(["comparable", "broad"]):
            g = FA[(FA.construction == cons) & (FA.layer == layer)].copy()
            g["c"] = g["class"].str.replace("_ADJ", "")
            g = g.set_index("c").reindex(["SAME_CAR", "SAME_TEAM", "DIFF_TEAM"])
            ax.bar(np.arange(3) + (k - 0.5) * 0.4, g.session_balanced_median, width=0.4, color=CAT[k], label=f"{layer} layer")
        ax.set_xticks(range(3), ["same car", "same team", "different team"])
        ax.set_title(cons.replace("_", " ").lower(), fontsize=8.5)
        ax.set_ylabel("session-balanced median D (mph)")
    axes[0].legend(fontsize=7.5)
    fig.suptitle("8. Same-car fairness: comparisons at matched time separation", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig08_same_car_fairness.png")

    # 8b adjacency diagnostic
    g = P[P["class"].isin(["TEAMMATE_OF_TARGET", "DIFF_TEAM"])]
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.6))
    for k, cls in enumerate(["TEAMMATE_OF_TARGET", "DIFF_TEAM"]):
        axes[0].hist((g[g["class"] == cls].time_sep_min * 60).clip(upper=300), bins=np.arange(0, 305, 5), histtype="step", lw=1.8, color=CAT[k], label=cls)
    axes[0].set_xlabel("time separation between target and comparator (s)")
    axes[0].legend(fontsize=7.5)
    d = g[g["class"] == "DIFF_TEAM"].assign(b=lambda x: pd.cut(x.time_sep_min * 60, [-1, 5, 15, 60, 300]))
    m = d.groupby("b", observed=True).D_mph.median()
    axes[1].bar(range(len(m)), m.values, color=CAT[2])
    axes[1].set_xticks(range(len(m)), ["≤5 s", "5–15 s", "15–60 s", "60–300 s"])
    axes[1].set_ylabel("median D, time-nearest\ndifferent-team control (mph)")
    fig.suptitle("8b. Why the primary control is likely confounded: the time-nearest different-team car is usually adjacent on track", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig08b_primary_control_adjacency_diagnostic.png")

    # 9 LOO team-relative deviations
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for k, role in enumerate(["PRIMARY", "ERA_C_SECONDARY"]):
        x = DV[DV.role == role].abs_deviation.clip(upper=10)
        ax.hist(x, bins=np.arange(0, 10.25, 0.25), histtype="step", lw=1.8, color=CAT[k], density=True, label=f"{role} (n={len(x)}, median {x.median():.2f})")
    ax.set_xlabel("|speed − leave-one-out teammate reference| (mph)")
    ax.legend(fontsize=7.5)
    ax.set_title("9. Leave-one-out team-relative deviation (not a team effect)", loc="left", fontsize=10.5)
    save(fig, "fig09_team_relative_deviation.png", top=0.97)

    # 10 persistence
    cp = CP[CP.spearman.notna()]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    lab = [f"{r.year}: {r.from_category[:10]}→{r.to_category[:10]} (n={r.linked_cars})" for r in cp.itertuples(index=False)]
    ax.barh(range(len(cp)), cp.spearman, color=[CAT[0] if r.startswith("PRIMARY") else CAT[1] for r in cp.role])
    ax.axvline(0, color=INK2)
    ax.set_yticks(range(len(cp)), lab, fontsize=7)
    ax.set_xlabel("Spearman ρ of per-car median team-relative deviation (exploratory)")
    ax.set_title("10. Cross-session persistence (blue = 2023–24, orange = 2025; pairs with ≥8 linked cars)", loc="left", fontsize=10)
    save(fig, "fig10_cross_session_persistence.png", top=0.97)

    # car-block validity figure (addendum 3)
    v = VA[(VA.role == "PRIMARY")]
    fig, ax = plt.subplots(figsize=(10, 3.6))
    for k, layer in enumerate(["broad", "comparable"]):
        g = v[v.layer == layer]
        ax.bar(np.arange(len(g)) + (k - 0.5) * 0.4, g.spread_median, width=0.4, color=CAT[k], label=f"{layer}: median within-car-block speed spread")
    ax.set_xticks(range(len(v[v.layer == 'broad'])), v[v.layer == "broad"].category, rotation=25, ha="right", fontsize=7)
    ax.set_ylabel("mph")
    ax.legend(fontsize=7.5)
    ax.set_title("0. Car-block validity: within-block lap-speed spread (practice blocks mix towed/un-towed laps)", loc="left", fontsize=10)
    save(fig, "fig00_car_block_validity.png", top=0.97)

    reports(C, P, BL, SB, sbs, YS, CT, LT, FA, DV, CP, DS, VA, DEP, CE, WX, OX, RA, AP)


def reports(C, P, BL, SB, sbs, YS, CT, LT, FA, DV, CP, DS, VA, DEP, CE, WX, OX, RA, AP):
    prim = sbs[(sbs.role == "PRIMARY") & (sbs.min_laps == 1)][["layer", "width_min", "sessions_with_eligible_blocks", "eligible_blocks", "session_balanced_delta", "boot_session_lo",
                                                                "boot_session_hi", "share_sessions_positive", "session_balanced_delta_team_balanced", "sb_D_same_car", "sb_D_same_team", "sb_D_diff_team"]]
    sec = sbs[(sbs.role == "ERA_C_SECONDARY") & (sbs.min_laps == 1)][prim.columns]
    ml2 = sbs[sbs.min_laps == 2][["role", "layer", "width_min", "session_balanced_delta", "share_sessions_positive", "session_balanced_delta_team_balanced"]]
    adj = P[P["class"].isin(["TEAMMATE_OF_TARGET", "DIFF_TEAM"])].groupby("class").time_sep_min.agg(
        median_sep_s=lambda s: s.median() * 60, share_le_10s=lambda s: (s <= 1 / 6).mean(), share_le_30s=lambda s: (s <= 0.5).mean()).reset_index()
    dd = P[P["class"] == "DIFF_TEAM"].assign(sep=lambda x: pd.cut(x.time_sep_min * 60, [-1, 5, 15, 60, 300], labels=["<=5s", "5-15s", "15-60s", "60-300s"]))
    dd = dd.groupby("sep", observed=True).D_mph.agg(["size", "median"]).reset_index()
    fa = FA[["construction", "layer", "class", "n", "sessions", "session_balanced_median", "pooled_median", "time_sep_median_min", "same_car_separation_mass_covered"]]
    ce = CE
    head = CE[CE.criterion == "CASE"].value.iloc[0]
    rep = f"""# V4 Phase 4F — Empirical Performance-Control Hierarchy Report

**Pre-specification:** `phase4f_prespecified_design.md`, committed as `fa480ed` before any hierarchy computation. Primary rules were not changed after results were seen.

**Evidence and scope:**
- Lap data are **Timing71 archived recordings of the INDYCAR live timing feed** (third-party). Official INDYCAR session details are used only as a cross-check (§Cross-check).
- No model was fitted, no coefficient estimated, and no team or driver ranked.

## Population (addendum 1)

- **Primary:** exactly the 15 Phase 4E Design-1-feasible sessions (Era B, 2023–2024; Tier A/B; all three comparison classes present; race excluded).
- **2025:** Tier A/B, but its Phase 4E Design-1 label is "feasible with additional data" (only one in-scope year of the hybrid regime). It is analysed identically, reported separately, and does not enter the case evaluation.
- **Race:** structural appendix only.

{md(AP[['session_key','role','normalized_category','raw_laps','broad_laps','comparable_laps','cars','teams']])}

## Car-block validity (addendum 3; reported before the hierarchy)

{md(VA.round(2))}

- **Practice-type sessions:** car-blocks typically hold 3–4 laps with a within-block speed spread of several mph. Roughly half to two-thirds exceed 3 mph (`wide_spread_share`), even in the comparable layer. The spread reflects towed vs un-towed laps and run-plan variation that the data cannot identify.
- **Qualifying sessions:** spreads are tight (≈0.2–0.4 mph).
- **Consequence:** the car-block median speed is an **observed local performance summary, not pure pace**.

## Primary hierarchy (2023–2024, session-balanced; D in mph)

{md(prim.round(3))}

**Class distributions (5 min):**

{md(DS[['scope','class','n_raw_comparisons','n_unique_cars','n_unique_teams','n_unique_sessions','n_unique_blocks','weighted_median','mean','sd','iqr','p10','p25','p75','p90','block_balanced_median','session_balanced_median','time_sep_median_min']].round(3))}

**Minimum-laps ≥2 sensitivity:**

{md(ml2.round(3))}

**2025 secondary (separate; not pooled):**

{md(sec.round(3))}

## The pre-registered primary control is confounded by on-track adjacency

{md(adj.round(3))}

D of the time-nearest different-team control, by how close it ran:

{md(dd.round(3))}

- **What the primary control is:** the pre-registered control is the different-team car nearest in time within the block. It is within 10 s of the target in about two-thirds of cases, far more often than the nearest teammate. That means it is typically the car running directly ahead of or behind the target, in the same tow group.
- **Why that matters:** such adjacent cars have markedly smaller D (≈1.3 mph within 5 s vs 2–2.9 mph farther away). The primary contrast therefore compares teammates against drafting partners.
- **This is a design limitation discovered after pre-specification.** The primary rule is **not** changed. The pre-declared sensitivity designs that do not select controls by track adjacency (team-balanced within-block pairs, the adjacent-block design and time-separation reweighting) are reported alongside.

## Year, category, leave-one-team-out

{md(YS.round(3))}

{md(CT.round(3))}

**Leave-one-team-out** (primary; teams are listed only to show stability, not ranked):

{md(LT.round(3))}

## Same-car fairness

{md(fa.round(3))}

- **At matched time separation:**
  - In the adjacent-block design (k → k+1 for every class), the comparable layer orders same car < same team < different team.
  - In the broad layer, same car ≈ same team < different team.
  - With within-block comparisons reweighted to the same-car time-separation distribution (comparable layer), the order is same car ≤ same team < different team.
  - **Contradictory broad-layer reweighting:** in the broad layer the reweighted result is unstable. The session-balanced different-team median (1.38) falls *below* same-team (2.80), while the pooled median points the other way (4.44 vs 2.55). The reweighting covers only 82% of the same-car separation mass there.
- **The same-car advantage is small:** in the comparable layer it is about 0.27 mph over same-team in the adjacent-block design, and it vanishes in the broad layer.

## Leave-one-out team-relative deviation

{md(DV.groupby('role').abs_deviation.describe().round(3).reset_index())}

## Weather inside blocks (diagnostic only)

{md(WX[['ptsc_readings','track_range_c','ambient_range_c']].describe().round(2).reset_index())}

PTSC is 15-minute resolution. The median block spans ≤2 readings, with a median track range of 0.56 °C and ambient 0 °C. Local blocks remove most measurable environmental mismatch, within that resolution.

## Dependence

{md(DEP)}

The Phase 4E raw same-team pair count for these sessions (92,893) compresses to 1,648 same-team block-pair comparisons, 209 eligible contrast blocks, and **15 independent sessions**. The raw pair counts exaggerate the effective sample by roughly two to three orders of magnitude.

## Case evaluation (pre-declared, mechanical)

{md(ce)}

**Headline: CASE {head}.**

**Why it is D:** the pre-registered primary contrast (time-nearest different-team control, comparable layer, 5 min) is:
- only +0.046 mph session-balanced, with a session-bootstrap interval of −0.21 to +0.71;
- positive in only 50% of sessions;
- negative in 2024;
- sign-unstable across block widths and leave-one-team-out removals;
- negative in the broad layer.

**What the pre-declared sensitivities show instead:** a **consistent** same-team advantage.
- The team-balanced within-block contrast is +0.22 to +0.49 mph in every primary layer and width, and mostly positive in 2025.
- The adjacent-block design gives different team 2.62 > same team 2.00 > same car 1.74 mph (comparable layer).
- Time-separation reweighting (comparable layer) gives different team 2.51 > same team 1.73 ≈ same car 1.71. The broad-layer reweighting is unstable and contradictory (see Same-car fairness).

**What this means:** the evidence is mixed. By the committed rule it is CASE D. The documented adjacency confound means that result is plausibly an artefact of how the primary control was defined, not evidence against team control. This report does not re-label the case.
"""
    (OUT / "phase4f_evidence_hierarchy_report.md").write_text(rep)

    (OUT / "phase4f_comparability_report.md").write_text(f"""# V4 Phase 4F — Comparability Report

## Layers

- **BROAD:** the Phase 4E valid lap (green or none flag; not an out-lap or in-lap; 37–45 s).
- **COMPARABLE:** BROAD plus all of the following:
  - explicit green flag, and the previous lap also green;
  - not the 2nd lap of a stint;
  - not the last or penultimate lap of a stint that ended in the pits (`endTime` present);
  - timestamp coherence (|Δts − laptime| ≤ 2 s).
- **Not identifiable from the Timing71 archived feed:** fuel load, tyre age, tow/slipstream state, boost, run purpose, qualifying or race simulations. No lap was removed for slowness beyond the Phase 4E band.

{md(AP[['session_key','role','broad_laps','comparable_laps']])}

## Car-block validity

{md(VA.round(2))}

- **Stated limit:** car-block values in practice-type sessions are observed local performance summaries, not pure pace.
- **Multimodality:** wide within-block spreads (a 3–6 mph median in practice/Carb Day) indicate towed and un-towed laps inside one 5-minute block.
- **Pit adjacency:** removed in the comparable layer wherever identifiable (`with_pit_adjacent_laps_share` = 0 in that layer).

## Primary-control comparability problem

The time-nearest different-team control is usually adjacent on track (median separation of seconds). The primary contrast therefore compares teammates to drafting partners (see the hierarchy report).

## Official cross-check (sources kept distinct)

{md(OX)}

- **Where it's missing:** the best-lap comparison is 0 for qualifying sessions, because the official qualifying records carry no single-lap `BestSpeed` (only the four-lap `SpeedAvg` and per-lap `QualLap` fields).
- **Where it disagrees:** Fast Friday 2024 (6380: 14/29) and some 2025 practices (6651: 21/34; 6653: 14/34). The cause is not diagnosed; plausible explanations include laps missing from the Timing71 capture.
- **Car presence** agrees except where Timing71 captured fewer cars.
""")

    (OUT / "phase4f_dependence_report.md").write_text(f"""# V4 Phase 4F — Dependence Report

{md(DEP)}

- **Clusters:** there are only 15 primary sessions (independent clusters). The session bootstrap resamples those; intervals are wide and fragile.
- **Reuse:** a single car appears in up to {int(DEP.set_index('item').loc['max appearances of one car across comparisons','count'])} comparisons, and a single car-block in up to {int(DEP.set_index('item').loc['car-block reuse: max comparisons involving one car-block','count'])}.
- **Sample size:** none of the 92,893 raw same-team lap pairs is an independent observation. The effective sample is the session (15), then the block (209 eligible contrast blocks), then the car-block.
- **Not done:** no pair-level bootstrap and no p-values.
""")

    (OUT / "phase4f_cross_session_report.md").write_text(f"""# V4 Phase 4F — Cross-Session Persistence (exploratory)

- **Measure:** the per-car median leave-one-out team-relative deviation (comparable layer, 5 min), linked across session categories within the same year.
- **Coverage:** only pairs with ≥8 linked cars are summarised.
- **Interpretation limit:** this is not driver skill and not a car effect.

{md(CP.round(3))}

## Reading

- **Links through qualifying are impossible:** they have ≤3 linked cars, because teammates rarely share a 5-minute block in qualifying.
- **Practice → Carb Day and post-qualifying → Carb Day** (≈30 cars each):
  - post-qualifying → Carb Day is positive in all three years (ρ 0.23, 0.48, 0.44);
  - practice → Carb Day is inconsistent (0.17, −0.03, −0.37).
- **Practice → Fast Friday** is positive in 2023 (ρ 0.56, n = 10) and weak in 2024 (0.24, n = 8).
- **Overall:** at most weak-to-moderate, inconsistent persistence. No stable car or driver relative-to-team signal is established.

## Race

{md(RA)}

The race is structural only; no D values were computed. The 2023 race has no comparable-layer car-blocks (none of its 647 broad-layer laps passed the comparable-layer filters). The reason was not diagnosed in this phase.
""")


if __name__ == "__main__":
    main()
