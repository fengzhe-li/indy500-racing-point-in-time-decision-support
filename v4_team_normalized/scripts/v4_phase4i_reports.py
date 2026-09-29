"""V4 Phase 4I: figures and reports (reads Phase 4I outputs only; support structure; no hierarchy outcome)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "output" / "phase4i"
FIG = OUT / "figures"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 9, "legend.frameon": False})
DIAG = ("Phase 4I support audit · frozen Phase 4H classes (Tier 1 = A↔A; Tier 2 = A/B↔A/B) · Timing71 archived live-feed (third-party) · "
        "no between-car D computed · 2025 separate")
TC = {"TIER1_STRICT": CAT[2], "TIER2_EXTENDED": CAT[0]}
ADJ = ["SAME_UPDATE", "CONSECUTIVE", "BETWEEN_1_2", "BETWEEN_3_5", "BETWEEN_GT5"]


def md(df):
    f = lambda v: "" if (isinstance(v, float) and np.isnan(v)) else (f"{v:.3f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))
    return "\n".join(["| " + " | ".join(map(str, df.columns)) + " |", "|" + "|".join("---" for _ in df.columns) + "|"]
                     + ["| " + " | ".join(f(v) for v in r) + " |" for r in df.itertuples(index=False)])


def save(fig, name, top=0.92):
    fig.tight_layout(rect=(0, 0.05, 1, top))
    fig.text(0.01, 0.01, DIAG, fontsize=6.3, color=INK2)
    fig.savefig(FIG / name, dpi=140, bbox_inches="tight")
    plt.close(fig)


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    T1 = pd.read_csv(OUT / "tier1_strict_support.csv", dtype={"session_key": str})
    T2 = pd.read_csv(OUT / "tier2_extended_support.csv", dtype={"session_key": str})
    TS = pd.concat([T1, T2], ignore_index=True)
    SCS = pd.read_csv(OUT / "same_car_support.csv")
    STS = pd.read_csv(OUT / "same_team_support.csv", dtype={"session_key": str})
    DTS = pd.read_csv(OUT / "different_team_candidate_support.csv")
    CSS = pd.read_csv(OUT / "common_support_by_session.csv", dtype={"session_key": str})
    CSB = pd.read_csv(OUT / "common_support_by_block.csv", dtype={"session_key": str})
    AD = pd.read_csv(OUT / "adjacency_support.csv")
    DEP = pd.read_csv(OUT / "reuse_dependence_audit.csv")
    ERA = pd.read_csv(OUT / "year_era_support.csv")
    PS = pd.read_csv(OUT / "performance_scale_reference.csv")
    CE = pd.read_csv(OUT / "case_evaluation.csv")
    WB = pd.read_csv(OUT / "within_block_pairs.csv", dtype={"session_key": str})

    ses = TS[TS.level == "SESSION"].copy()
    order = ses[ses.tier == "TIER2_EXTENDED"].sort_values(["yr_group", "session_key"]).session_key.tolist()
    lab = {r.session_key: f"{r.session_key}\n{r.category[:12].lower()}" for r in ses.itertuples(index=False)}

    # 1 eligible observations by session
    fig, ax = plt.subplots(figsize=(13, 3.9))
    x = np.arange(len(order))
    for k, t in enumerate(["TIER1_STRICT", "TIER2_EXTENDED"]):
        s = ses[ses.tier == t].set_index("session_key").reindex(order)
        ax.bar(x + (k - 0.5) * 0.38, s.eligible_carblocks, width=0.36, color=TC[t], label=f"{t}: eligible car-blocks")
    ax.axvline(len(ses[(ses.tier == "TIER2_EXTENDED") & (ses.yr_group != "2025_SECONDARY")]) - 0.5, color=INK2, ls="--", lw=1)
    ax.text(len(ses[(ses.tier == "TIER2_EXTENDED") & (ses.yr_group != "2025_SECONDARY")]) - 0.4, ax.get_ylim()[1] * 0.92, "2025 secondary →", fontsize=8, color=INK2)
    ax.set_xticks(x, [lab[s] for s in order], fontsize=6.5)
    ax.set_ylabel("eligible car-blocks (5-min)")
    ax.legend(fontsize=7.5)
    ax.set_title("1. Eligible observations by session (2023–24 primary | 2025 secondary)", loc="left", fontsize=10.5)
    save(fig, "fig01_eligible_by_session.png", top=0.97)

    # 2 Tier 1 vs Tier 2
    yg = TS[(TS.level == "YEAR_GROUP")]
    mets = ["eligible_laps", "eligible_carblocks", "same_car_local_pairs", "same_car_cross_run_pairs", "same_team_pairs", "diff_team_pairs"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8), sharex=True)
    for ax, g in zip(axes, ["2023_2024_PRIMARY", "2025_SECONDARY"]):
        for k, t in enumerate(["TIER1_STRICT", "TIER2_EXTENDED"]):
            r = yg[(yg.tier == t) & (yg.yr_group == g)].iloc[0]
            v = [r[m] for m in mets]
            ax.barh(np.arange(len(mets)) + (k - 0.5) * 0.38, v, height=0.36, color=TC[t], label=t)
            for i, vv in enumerate(v):
                ax.annotate(f"{int(vv)}", (vv, i + (k - 0.5) * 0.38), xytext=(3, -3), textcoords="offset points", fontsize=7)
        ax.set_xscale("log")
        ax.set_yticks(range(len(mets)), [m.replace("_", " ") for m in mets])
        ax.set_title(g.replace("_", " ").lower(), loc="left", fontsize=9.5)
    axes[0].legend(fontsize=7.5)
    fig.suptitle("2. Tier 1 (A↔A) vs Tier 2 (A/B↔A/B) support (log scale; counts, not outcomes)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig02_tier1_vs_tier2_support.png")

    # 3 three layers by session
    fig, axes = plt.subplots(2, 1, figsize=(13, 6.2), sharex=True)
    for ax, t in zip(axes, ["TIER1_STRICT", "TIER2_EXTENDED"]):
        s = ses[ses.tier == t].set_index("session_key").reindex(order)
        for k, (col, nm) in enumerate([("same_car_local_pairs", "same-car local repeat"), ("same_team_pairs", "same-team pairs"), ("diff_team_pairs", "different-team candidate pairs")]):
            ax.bar(x + (k - 1) * 0.27, s[col].fillna(0) + 0.0, width=0.25, color=CAT[k], label=nm)
        ax.set_yscale("symlog", linthresh=1)
        ax.set_ylabel(f"{t}\npairs (symlog)")
    axes[0].legend(fontsize=7.5, ncol=3)
    axes[1].set_xticks(x, [lab[s] for s in order], fontsize=6.5)
    fig.suptitle("3. The three comparison layers by session", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig03_layers_by_session.png")

    # 4 common support by session
    fig, axes = plt.subplots(2, 1, figsize=(13, 6.2), sharex=True)
    for ax, t in zip(axes, ["TIER1_STRICT", "TIER2_EXTENDED"]):
        s = CSS[CSS.tier == t].set_index("session_key").reindex(order)
        for k, (col, nm) in enumerate([("blocks_ST_DT", "blocks with same-team & diff-team"), ("blocks_SC_ST", "blocks with same-car & same-team"), ("blocks_ALL3", "blocks with all three")]):
            ax.bar(x + (k - 1) * 0.27, s[col], width=0.25, color=CAT[k + 3], label=nm)
        for xi, ok in zip(x, s.all_three_layers_block_scale):
            ax.annotate("✓" if ok else "✗", (xi, ax.get_ylim()[1] * 0.85 if ax.get_ylim()[1] else 1), ha="center", fontsize=9, color=CAT[2] if ok else CAT[7])
        ax.set_ylabel(f"{t}\nblocks")
    axes[0].legend(fontsize=7.5, ncol=3, loc="lower left", bbox_to_anchor=(0.0, 1.02))
    axes[1].set_xticks(x, [lab[s] for s in order], fontsize=6.5)
    fig.suptitle("4. Common support by session (✓ = session has all three layers at block scale)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig04_common_support_by_session.png")

    # 5 same-team time separation
    fig, ax = plt.subplots(figsize=(10, 3.6))
    p = WB[WB.yr_group == "2023_2024_PRIMARY"]
    for t, ls in [("TIER1_STRICT", "-"), ("TIER2_EXTENDED", "--")]:
        for layer, c in [("SAME_TEAM", CAT[1]), ("DIFF_TEAM", CAT[0])]:
            v = p[(p.tier == t) & (p.layer == layer)].time_sep_s
            ax.hist(v, bins=np.arange(0, 305, 15), histtype="step", lw=1.8, ls=ls, density=True, color=c, label=f"{t} {layer.lower()} (n={len(v)}, median {v.median():.0f} s)")
    ax.set_xlabel("time separation between eligible car-blocks in the same 5-min block (s)")
    ax.set_ylabel("density")
    ax.legend(fontsize=7)
    ax.set_title("5. Same-team pair time separation (different-team candidates for reference), 2023–24", loc="left", fontsize=10.5)
    save(fig, "fig05_same_team_time_separation.png", top=0.97)

    # 6 adjacency support by layer
    a = AD[(AD.table == "ADJACENCY_DISTRIBUTION")]
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True)
    for ax, g in zip(axes, ["2023_2024_PRIMARY", "2025_SECONDARY"]):
        keys = [(t, l) for t in ["TIER1_STRICT", "TIER2_EXTENDED"] for l in ["SAME_TEAM", "DIFF_TEAM"]]
        bottom = np.zeros(len(keys))
        for k, c in enumerate(ADJ):
            v = np.array([a[(a.tier == t) & (a.layer == l) & (a.yr_group == g) & (a.stratum == c)].share.sum() for t, l in keys])
            ax.bar(range(len(keys)), v, bottom=bottom, color=CAT[k], label=c.lower().replace("_", " "), edgecolor=SURFACE)
            bottom += v
        bal = AD[(AD.table == "BALANCE_FEASIBILITY") & (AD.stratum == "ALL") & (AD.yr_group == g)].set_index("tier").share_ge1_same_stratum_candidate
        for i, (t, l) in enumerate(keys):
            if l == "SAME_TEAM" and t in bal:
                ax.annotate(f"balance-feasible\n{bal[t]:.0%}", (i, 1.01), ha="center", fontsize=6.8)
        ax.set_xticks(range(len(keys)), [f"{t.split('_')[0].lower()}\n{l.lower().replace('_', ' ')}" for t, l in keys], fontsize=7.5)
        ax.set_ylim(0, 1.15)
        ax.set_title(g.replace("_", " ").lower(), loc="left", fontsize=9.5)
    axes[0].set_ylabel("share of pairs by Phase 4G adjacency stratum")
    axes[1].legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1.0))
    fig.suptitle("6. Timing-sequence adjacency support by comparison layer (no outcome)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig06_adjacency_support.png")

    # 7 reuse / concentration
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8))
    for t, ls in [("TIER1_STRICT", "-"), ("TIER2_EXTENDED", "--")]:
        for layer, c in [("SAME_TEAM", CAT[1]), ("DIFF_TEAM", CAT[0])]:
            w = p[(p.tier == t) & (p.layer == layer)]
            use = pd.concat([w.cb_a, w.cb_b]).value_counts().sort_values()
            axes[0].step(use.values, np.arange(1, len(use) + 1) / len(use), where="post", color=c, ls=ls, lw=1.8, label=f"{t} {layer.lower()}")
        st = STS[(STS.tier == t) & (STS.yr_group == "2023_2024_PRIMARY") & (STS.layer == "SAME_TEAM_CONCENTRATION_BY_TEAM_ALPHABETICAL")].share.sort_values(ascending=False).cumsum()
        ss = STS[(STS.tier == t) & (STS.yr_group == "2023_2024_PRIMARY") & (STS.layer == "SAME_TEAM_CONCENTRATION_BY_SESSION")].share.sort_values(ascending=False).cumsum()
        axes[1].plot(range(1, len(st) + 1), st.values, "o" + ls, color=TC[t], label=f"{t}: by team")
        axes[1].plot(range(1, len(ss) + 1), ss.values, "s" + ls, color=TC[t], alpha=0.6, label=f"{t}: by session")
    axes[0].set_xlabel("pairs a car-block participates in")
    axes[0].set_ylabel("cumulative share of car-blocks")
    axes[0].legend(fontsize=6.8)
    axes[1].set_xlabel("number of teams / sessions (largest contributors first; unnamed)")
    axes[1].set_ylabel("cumulative share of same-team pairs")
    axes[1].axhline(0.5, color=INK2, lw=0.8, ls=":")
    axes[1].legend(fontsize=6.8)
    fig.suptitle("7. Reuse and concentration of support, 2023–24 (support volume only; not performance)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig07_reuse_concentration.png")

    # 8 performance scale
    ps = PS.copy()
    ps["val"] = ps.median_sd_mph.fillna(ps.median_abs_delta_mph)
    ps = ps[ps.val.notna()]
    fig, ax = plt.subplots(figsize=(10, 3.8))
    y = np.arange(len(ps))
    ax.scatter(ps.val, y, color=CAT[0], s=40, zorder=3, label="median SD (or median |Δ| consecutive laps)")
    ax.scatter(ps.median_range_mph, y, color=CAT[1], marker="D", s=30, zorder=3, label="median within-unit range")
    ax.set_xscale("log")
    ax.set_yticks(y, [f"{r.reference.replace('_', ' ').lower()} [{r.scope}]" for r in ps.itertuples(index=False)], fontsize=7)
    ax.set_xlabel("mph (log)")
    ax.legend(fontsize=7.5, loc="lower right")
    ax.set_title("8. Empirical measurement scale (qualifying; same car only; recorded precision)", loc="left", fontsize=10.5)
    save(fig, "fig08_performance_scale_reference.png", top=0.97)

    reports(TS, SCS, STS, DTS, CSS, CSB, AD, DEP, ERA, PS, CE)


def reports(TS, SCS, STS, DTS, CSS, CSB, AD, DEP, ERA, PS, CE):
    ce = CE.copy()
    case = CE[CE.criterion == "SUPPORT_CASE"].value.iloc[0]
    lv = CE[CE.criterion == "LEVEL"].set_index(["tier", "yr_group"]).value
    yg = TS[TS.level.isin(["YEAR_GROUP", "YEAR"])][["tier", "level", "yr_group", "year", "eligible_laps", "eligible_carblocks", "cars", "teams", "sessions", "blocks",
                                                   "carblocks_with_2plus_laps", "same_car_local_pairs", "same_car_cross_run_pairs", "same_car_cross_session_pairs", "same_team_pairs", "diff_team_pairs"]]
    cat = TS[TS.level == "CATEGORY"][["tier", "yr_group", "category", "eligible_laps", "eligible_carblocks", "cars", "sessions", "same_team_pairs", "diff_team_pairs", "same_car_local_pairs"]]
    ses = TS[TS.level == "SESSION"][["tier", "yr_group", "session_key", "category", "eligible_laps", "eligible_carblocks", "cars", "teams", "same_team_pairs", "diff_team_pairs",
                                     "same_car_local_pairs", "same_car_cross_run_pairs"]]
    scs = SCS
    sts = STS[STS.layer == "SAME_TEAM"].drop(columns=[c for c in ["team", "share", "session_key", "teams"] if c in STS])
    stc = STS[STS.layer != "SAME_TEAM"][["tier", "yr_group", "layer", "team", "session_key", "pairs", "share"]]
    dts = DTS
    css = CSS[["tier", "yr_group", "session_key", "category", "eligible_blocks", "blocks_SC", "blocks_ST", "blocks_DT", "blocks_ST_DT", "blocks_SC_ST", "blocks_ALL3",
               "all_three_layers_block_scale", "all_three_layers_session_scale", "same_team_pairs", "diff_team_pairs", "teams_in_same_team_pairs"]]
    cbs = CSB.groupby(["tier", "yr_group"]).agg(blocks=("block", "size"), blocks_ST_DT=("ST_DT", "sum"), blocks_SC_ST=("SC_ST", "sum"), blocks_ALL3=("ALL3", "sum"),
                                               blocks_with_ptsc=("ptsc_readings", lambda s: int((s > 0).sum()))).reset_index()
    bal = AD[AD.table == "BALANCE_FEASIBILITY"][["tier", "yr_group", "stratum", "pairs", "share_ge1_same_stratum_candidate", "share_ge3_same_stratum_candidate", "share_any_candidate"]]
    adj = AD[AD.table == "ADJACENCY_DISTRIBUTION"].pivot_table(index=["tier", "yr_group", "layer"], columns="stratum", values="share").reset_index()
    comp = AD[AD.table.str.startswith("TIER2_COMPOSITION")][["table", "yr_group", "layer", "stratum", "pairs", "share"]]
    dep = DEP[["tier", "yr_group", "population", "raw_pairs", "unique_laps", "unique_carblocks", "unique_cars", "unique_car_pairs", "unique_teams", "unique_team_years", "unique_sessions",
               "max_carblock_reuse", "median_carblock_reuse", "share_pairs_involving_reused_carblock", "max_share_pairs_touching_one_carblock",
               "share_edges_touching_top5pct_degree_nodes", "graph_components", "largest_component_share_of_nodes"]]
    era = ERA
    ps = PS
    g = lambda t, y, m: CE[(CE.tier == t) & (CE.yr_group == y) & (CE.criterion == m)].value.iloc[0]
    t1p = TS[(TS.level == "YEAR_GROUP") & (TS.tier == "TIER1_STRICT") & (TS.yr_group == "2023_2024_PRIMARY")].iloc[0]
    t2p = TS[(TS.level == "YEAR_GROUP") & (TS.tier == "TIER2_EXTENDED") & (TS.yr_group == "2023_2024_PRIMARY")].iloc[0]
    st1 = sts[(sts.tier == "TIER1_STRICT") & (sts.yr_group == "2023_2024_PRIMARY")].iloc[0]
    st2 = sts[(sts.tier == "TIER2_EXTENDED") & (sts.yr_group == "2023_2024_PRIMARY")].iloc[0]

    rep1 = f"""# V4 Phase 4I — Post-Validity Support Report

**Pre-specification:** `phase4i_support_audit_spec.md`, committed as `ccb06c6` before any support count. Its rules were applied without change.

**Frozen inputs:**
- the Phase 4H classes, used exactly (classifier and thresholds unchanged);
- Phase 4F **D**, Phase 4G **A** and Phase 4H **D**, all unchanged.

**Source:** Timing71 archived recordings of the INDYCAR live timing feed (third-party).

**No between-car speed difference (D) was computed.** No hierarchy direction, estimator or control selection.

## Headline: support CASE {case}

| Tier | 2023–24 primary | 2025 (separate) |
|---|---|---|
| Tier 1 (A↔A) | **{lv[('TIER1_STRICT', '2023_2024_PRIMARY')]}** | {lv[('TIER1_STRICT', '2025_SECONDARY')]} |
| Tier 2 (A/B↔A/B) | **{lv[('TIER2_EXTENDED', '2023_2024_PRIMARY')]}** | {lv[('TIER2_EXTENDED', '2025_SECONDARY')]} |

- **Why not CASE A:** Tier 1 misses STRONG only on blocks with all three layers ({g('TIER1_STRICT', '2023_2024_PRIMARY', 'M3')} vs the pre-set ≥ 30).
- **What CASE B means:** a Phase 4J may be justified only within the explicitly supported, restricted population (§ Gate).

**The support is multi-session and multi-team, but small in absolute terms.**
- **Tier 1** has **{int(st1.pairs)} same-team pairs** (primary):
  - from {int(st1.independent_car_pairs)} distinct car-pairs, {int(st1.distinct_teams)} teams and {int(st1.sessions)} sessions;
  - largest team share {st1.max_team_share:.2f}; largest session share {st1.max_session_share:.2f}.
- **Tier 2** has **{int(st2.pairs)} pairs**:
  - from {int(st2.independent_car_pairs)} car-pairs, {int(st2.distinct_teams)} teams and {int(st2.sessions)} sessions.

## 1. Eligible observations (4I.3)

- **Tier 1, 2023–24:** {int(t1p.eligible_laps)} A laps in {int(t1p.eligible_carblocks)} eligible car-blocks ({int(t1p.cars)} cars, {int(t1p.teams)} teams, {int(t1p.sessions)} sessions, {int(t1p.blocks)} blocks).
- **Tier 2, 2023–24:** {int(t2p.eligible_laps)} A/B laps in {int(t2p.eligible_carblocks)} car-blocks.

{md(yg)}

**By category:**

{md(cat)}

**By session:**

{md(ses)}

## 2. Same-car support (4I.6): subtypes kept separate

{md(scs)}

**Readings:**
- **Local repeats** (same stint, different car-blocks) are mostly adjacent 5-min blocks, about 80–100 s apart.
- **Cross-run repeats** are about 1 h apart.
- **Cross-session repeats** are days apart.
- **Within-car-block lap repeats** are numerous.
- These are different evidential structures and are not pooled.

## 3. Same-team / different-car support (4I.7)

{md(sts)}

**Concentration** (teams alphabetical; support volume only, not performance):

{md(stc)}

## 4. Different-team candidate universe (4I.8): no comparator selected

{md(dts)}

## 5. Case evaluation (spec §10)

{md(ce)}

## Gate (4I.15)

**CASE B.**

**What a Phase 4J could address:** at most the **restricted population audited here**:
- 2023–2024 primary practice-type sessions only;
- the frozen Phase 4H Tier 1 (A↔A) as the high-confidence tier;
- Tier 2 (A/B) reported separately, never merged;
- same-car local repeats, same-team pairs and different-team candidates within the same 5-min blocks.

**Limits on that population:**
- The same-team layer rests on a few dozen pairs from about 9–10 teams.
- Adjacency balancing is feasible for only about 57% (Tier 1) to 61% (Tier 2) of same-team pairs. It is infeasible for same-feed-update pairs.
- A Phase 4J must be separately pre-specified, adjacency-aware (Phase 4G), and must not generalise beyond this support, to other years (2018–2022), to raw practice, or to race.

**Phase 4J is not run.**
"""
    rep2 = f"""# V4 Phase 4I — Common-Support Report

## Sessions (block scale and session scale)

{md(css)}

## Blocks

{md(cbs)}

**Coverage:**
- Every eligible block has PTSC weather readings available (availability only; no coefficients).
- All three layers in the *same* 5-min block is rarer than per-session coexistence, so support is reported at both scales.

## Adjacency support (4I.9): Phase 4G strata; no new threshold

{md(adj)}

**Balance feasibility:** does ≥1 different-team eligible candidate exist in the same block with the same adjacency stratum as the teammate?

{md(bal)}

- **Feasible:** in the >5-intervening stratum.
- **Weak:** in the closest strata.
- **Tier 1 same-update pairs:** no same-stratum candidate (0/12 orientations).

## Tier 2 composition (4I.10)

{md(comp)}

About two-thirds of Tier 2 pairs involve at least one B or mixed car-block. Tier 2 is therefore **not** equivalent in evidential quality to Tier 1.
"""
    rep3 = f"""# V4 Phase 4I — Dependence Report

{md(dep)}

**Readings:**
- Raw pair counts overstate independent evidence.
- **Different-team candidates:** over 90% of pairs involve a car-block used more than once (maximum reuse 9 in Tier 1, 14 in Tier 2).
- **Same-team pairs:** reuse is low (maximum 3).
- **Same-car cross-session pairs:** almost all involve reused car-blocks.
- **Graph:** it fragments into many small components (largest component < 10% of nodes). Support is spread across blocks rather than dominated by a few hub observations.
- **Independent clusters:** the sessions (≤ 11 primary).
- No "effective N" formula is used.
"""
    rep4 = f"""# V4 Phase 4I — Limitations Report

## Era coverage (4I.12)

{md(era)}

**What the eras contribute:**
- **2018–2022:** the eight-year registry and longitudinal team identity. These years provide **no lap-level eligible evidence**: 2018–2021 have stint-level timestamps only, 2022 has session-level records only, and the Phase 4H classifier is not projected backwards.
- **2023–2025:** all hierarchy-relevant support. 2023–2024 is primary; 2025 is secondary and separate.

## Measurement scale (4I.13; descriptive)

{md(ps)}

**Readings:**
- **Qualifying within-attempt SD:** about 0.4–0.6 mph (0.16–0.25%).
- **Class-A same-car within-car-block SD:** about 0.5–0.6 mph.
- **Consecutive-lap |Δ|:** median about 0.5 mph (about 0.09 s of lap time).
- **Same-car cross-session SD of session medians:** 2.7 mph (2023–24) and 5.3 mph (2025). Session conditions and run programmes change more than local repeat noise.
- **Recorded precision** (0.0006 mph) is not limiting.
- No minimum meaningful difference and no power calculation.

## Limitations

1. **Tier 1 is strict by construction.** Phase 4H class A is narrow and was not loosened, so absolute support is small, especially for same-team pairs.
2. **Tier 2 is lower quality.** It mixes A and B; about two-thirds of its pairs involve B or mixed car-blocks.
3. **Adjacency.** Common support within the closest adjacency strata (same update / consecutive) is sparse. A future adjacency-balanced design would lose most of those strata.
4. **Unobserved variables.** Run purpose, fuel, tyres, tow and traffic remain unobserved even for class A.
5. **Session clusters.** There are only 11 primary sessions (8 in 2025), so between-session dependence dominates.
6. **Scope.** Support counts do not imply a detectable or meaningful hierarchy effect, and no outcome was examined.
"""
    for n, r in [("phase4i_support_report.md", rep1), ("phase4i_common_support_report.md", rep2), ("phase4i_dependence_report.md", rep3), ("phase4i_limitations_report.md", rep4)]:
        (OUT / n).write_text(r)


if __name__ == "__main__":
    main()
