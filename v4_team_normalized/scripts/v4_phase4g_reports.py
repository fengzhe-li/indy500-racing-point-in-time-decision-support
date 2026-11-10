"""V4 Phase 4G: figures, future-evidence feasibility table and reports (reads Phase 4G outputs; descriptive only)."""
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "output" / "phase4g"
FIG = OUT / "figures"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 9, "legend.frameon": False})
DIAG = ("Phase 4G diagnostic · Timing71 archived live-feed records (third-party) · timing-sequence adjacency is a proxy, not tow · "
        "2023–24 primary; 2025 separate · Phase 4F CASE D unchanged")
POPC = {"A_PRIMARY_CONTROL": CAT[2], "B_RANDOM_PICK_EXPECTATION": INK2, "B_ELIGIBLE_CANDIDATES": INK2, "C1_TEAMMATE_OF_TARGET": CAT[1],
        "C2_ALL_TEAMMATES": CAT[3], "TEAM_BALANCED_DIFF": CAT[0], "ADJACENT_BLOCK_DIFF": CAT[6], "REWEIGHTED_DIFF": CAT[4]}
CUM = ["share_same_update", "share_le0_intervening", "share_le1_intervening", "share_le2_intervening", "share_le3_intervening", "share_le5_intervening"]
CUM_L = ["same\nupdate", "≤0\n(same upd.\nor consec.)", "≤1", "≤2", "≤3", "≤5"]


def md(df):
    f = lambda v: "" if (isinstance(v, float) and np.isnan(v)) else (f"{v:.3f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v))
    return "\n".join(["| " + " | ".join(map(str, df.columns)) + " |", "|" + "|".join("---" for _ in df.columns) + "|"]
                     + ["| " + " | ".join(f(v) for v in r) + " |" for r in df.itertuples(index=False)])


def save(fig, name, top=0.92):
    fig.tight_layout(rect=(0, 0.05, 1, top))
    fig.text(0.01, 0.01, DIAG, fontsize=6.3, color=INK2)
    fig.savefig(FIG / name, dpi=140, bbox_inches="tight")
    plt.close(fig)


FEAS = [
    dict(source="Timing71 analysis JSON (already retrieved, Phase 4E)", content_checked="cars.stints.laps: lapNumber, laptime, flag, driver, timestamp; state: final snapshot only; messages: pit/flag text",
         improves_on_proxy="NO", reason="Lap timestamps are feed-update times (~1.67 s cycle); no per-lap position, interval or gap history; final state only.",
         recoverable_without_large_ingestion="n/a (in hand)", status="IN_HAND"),
    dict(source="Timing71 full replay recordings of the live feed (same archive; not the analysis file)",
         content_checked="manifest.colSpec of the in-hand files lists Gap ('Gap to leader'), Int ('Interval to car in front'), T1S/T3S speed traps, State",
         improves_on_proxy="POSSIBLY", reason="A per-update Int column would give a feed-reported interval to the car in front, i.e. an observed ordering/gap field rather than a lap-line proxy. Replay file format, retention and coverage for 2023-2025 not verified in Phase 4G.",
         recoverable_without_large_ingestion="UNVERIFIED; would require a new retrieval and parser (not done in 4G)", status="DOCUMENTED_ONLY"),
    dict(source="INDYCAR official 'Section Results' / 'Top Section Times' PDFs (listed in official session-detail SessionReports for 2024 practice sessions)",
         content_checked="document names and URLs present in retrieved official JSON; PDFs not retrieved",
         improves_on_proxy="POSSIBLY", reason="Official section timing could give per-lap section times at several timing loops; whether it includes time-of-day per crossing (needed for ordering) is unverified.",
         recoverable_without_large_ingestion="UNVERIFIED; PDF table extraction for ~25 sessions", status="DOCUMENTED_ONLY"),
    dict(source="INDYCAR official session-detail records (already retrieved)", content_checked="per-car session summary: BestLapTime, BestSpeed, Gap, Difference, LapsComplete",
         improves_on_proxy="NO", reason="Session-level summaries only; no per-lap ordering.", recoverable_without_large_ingestion="n/a (in hand)", status="IN_HAND"),
    dict(source="Official race Lap Chart PDF", content_checked="listed for race sessions only", improves_on_proxy="NO (for practice)",
         reason="Race-only; race is outside Phase 4F/4G scope.", recoverable_without_large_ingestion="n/a", status="OUT_OF_SCOPE"),
    dict(source="Telemetry / transponder loop data, onboard video, team radio", content_checked="none", improves_on_proxy="YES in principle",
         reason="Would be needed to observe physical gaps, tow or aerodynamic interaction; not publicly available to this project.",
         recoverable_without_large_ingestion="NO", status="NOT_AVAILABLE"),
]


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(FEAS).to_csv(OUT / "future_evidence_feasibility.csv", index=False)
    ADS = pd.read_csv(OUT / "adjacency_distribution_summary.csv")
    TS = pd.read_csv(OUT / "timing_sequence_adjacency.csv", low_memory=False, dtype={"session_key": str})
    ST = pd.read_csv(OUT / "different_team_adjacency_strata.csv", dtype={"scope": str})
    NB = pd.read_csv(OUT / "negative_positive_block_diagnostics.csv", dtype={"session_key": str})
    RU = pd.read_csv(OUT / "control_reuse_audit.csv")
    DP = pd.read_csv(OUT / "design_population_comparison.csv")
    YA = pd.read_csv(OUT / "year_session_adjacency.csv")
    CE = pd.read_csv(OUT / "phase4g_case_evaluation.csv").set_index("criterion").value
    SC = pd.read_csv(OUT / "sequence_completeness.csv")
    RV = pd.read_csv(OUT / "reproduction_verification.csv")
    DV = pd.read_csv(OUT / "design_population_verification.csv")

    # 1 cumulative adjacency: A vs B expectation vs teammates
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.9), sharey=True)
    for ax, role in zip(axes, ["PRIMARY", "ERA_C_SECONDARY"]):
        a = ADS[(ADS.role == role) & (ADS.basis == "OBSERVED_FEED_SEQUENCE")].set_index("population")
        for p in ["A_PRIMARY_CONTROL", "B_RANDOM_PICK_EXPECTATION", "C1_TEAMMATE_OF_TARGET", "C2_ALL_TEAMMATES"]:
            ax.plot(range(len(CUM)), a.loc[p, CUM].values, marker="o", ms=5, lw=2, color=POPC[p], label=p.replace("_", " ").lower())
        ax.set_xticks(range(len(CUM)), CUM_L, fontsize=7)
        ax.set_xlabel("intervening lap-line records between target and comparator (lower-median target lap)")
        ax.set_title("2023–24 primary" if role == "PRIMARY" else "2025 secondary (separate)", loc="left", fontsize=9.5)
    axes[0].set_ylabel("cumulative share of pairs")
    axes[0].legend(fontsize=7.5)
    fig.suptitle("1. Selected different-team controls are more timing-adjacent than the pool they were drawn from", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig01_control_vs_candidate_adjacency.png")

    # 2 timestamp separation distribution
    P = TS[TS.role == "PRIMARY"]
    fig, ax = plt.subplots(figsize=(10, 3.6))
    for p in ["A_PRIMARY_CONTROL", "B_ELIGIBLE_CANDIDATES", "C1_TEAMMATE_OF_TARGET"]:
        x = P[P.population == p].carblock_time_sep_s.clip(upper=300)
        ax.hist(x, bins=np.arange(0, 305, 5), histtype="step", lw=1.8, density=True, color=POPC[p], label=f"{p.replace('_', ' ').lower()} (n={len(x)}, median {x.median():.1f} s)")
    ax.set_xlabel("car-block time separation from target (s) — the quantity nearest-time selection minimised")
    ax.set_ylabel("density")
    ax.legend(fontsize=7.5)
    ax.set_title("2. Timestamp separation, 2023–24 primary", loc="left", fontsize=10.5)
    save(fig, "fig02_timestamp_separation.png", top=0.97)

    # 3 D by sequence stratum
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True)
    order = ["SAME_UPDATE", "CONSECUTIVE", "BETWEEN_1_2", "BETWEEN_3_5", "BETWEEN_GT5"]
    for ax, role in zip(axes, ["PRIMARY", "ERA_C_SECONDARY"]):
        s = ST[(ST.role == role) & (ST.stratum_type == "SEQUENCE") & (ST.scope == "ALL")].set_index("stratum").loc[order]
        x = np.arange(len(order))
        ax.vlines(x, s.D_p25, s.D_p75, color=CAT[0], lw=6, alpha=0.35, label="pooled IQR")
        ax.plot(x, s.D_session_balanced_median, "o-", color=CAT[0], ms=7, lw=2, label="session-balanced median")
        for xi, (m, n) in enumerate(zip(s.D_session_balanced_median, s.n_pairs)):
            ax.annotate(f"{m:.2f}\nn={n}", (xi, m), textcoords="offset points", xytext=(8, -4), fontsize=7, color=INK2)
        ax.set_xticks(x, ["same\nupdate", "consecutive", "1–2\nbetween", "3–5\nbetween", ">5\nbetween"])
        ax.set_title("2023–24 primary" if role == "PRIMARY" else "2025 secondary (separate)", loc="left", fontsize=9.5)
    axes[0].set_ylabel("D = |Δ car-block speed| (mph)\ndifferent-team candidate pairs")
    axes[0].legend(fontsize=7.5, loc="upper left")
    fig.suptitle("3. Observed local performance difference by timing-sequence adjacency stratum (pre-declared strata)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig03_D_by_adjacency_stratum.png")

    # 4 / 5 adjacency by year and by category
    for fname, lvl, title in [("fig04_adjacency_by_year.png", "YEAR", "4. Adjacency by year"), ("fig05_adjacency_by_session_category.png", "CATEGORY", "5. Adjacency by session category")]:
        y = YA[YA.level == lvl].reset_index(drop=True)
        lab = [f"{textwrap.fill(str(s).replace('_', ' ').lower(), 14)}\n({'2025 sec.' if r.startswith('ERA') else '23–24'}; n={n})" for s, r, n in zip(y.scope, y.role, y.targets)]
        fig, ax = plt.subplots(figsize=(11 if lvl == "CATEGORY" else 8, 3.8))
        x = np.arange(len(y))
        for k, (col, nm, c) in enumerate([("A_share_no_intervening", "selected control", POPC["A_PRIMARY_CONTROL"]),
                                          ("B_expected_share_no_intervening", "random pick from pool", POPC["B_RANDOM_PICK_EXPECTATION"]),
                                          ("C1_share_no_intervening", "nearest teammate", POPC["C1_TEAMMATE_OF_TARGET"])]):
            ax.bar(x + (k - 1) * 0.26, y[col], width=0.24, color=c, label=nm)
        for xi, d in zip(x, y.phase4f_session_balanced_delta_reference):
            if not np.isnan(d):
                ax.annotate(f"4F Δ {d:+.2f}", (xi, 0.02), ha="center", fontsize=7, color=INK)
        ax.set_xticks(x, lab, fontsize=7)
        ax.set_ylabel("share with no intervening record\n(same update or consecutive)")
        ax.legend(fontsize=7.5, loc="upper right")
        ax.set_title(title + " (Phase 4F primary Δ shown for reference; not a causal link)", loc="left", fontsize=10)
        save(fig, fname, top=0.97)

    # 6 negative vs positive blocks
    b = NB[NB.level == "BLOCK"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    for ax, (col, lab) in zip(axes, [("share_controls_no_intervening", "share of controls with no\nintervening record"),
                                     ("median_control_lap_ts_sep_s", "median lap-level |Δts| to control (s)"),
                                     ("excess_no_intervening", "control no-intervening share\nminus pool expectation")]):
        data = [b[b.group == g][col].dropna().values for g in ["NEGATIVE", "ZERO", "POSITIVE"] if (b.group == g).any()]
        labs = [f"{g.lower()} Δ_block\n(n={int((b.group == g).sum())})" for g in ["NEGATIVE", "ZERO", "POSITIVE"] if (b.group == g).any()]
        ax.boxplot(data, tick_labels=labs, widths=0.5, medianprops=dict(color=CAT[1], lw=2), flierprops=dict(markersize=3))
        ax.set_ylabel(lab, fontsize=8)
    fig.suptitle("6. Phase 4F primary blocks with negative vs positive Δ_block: control-selection diagnostics only", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig06_negative_vs_positive_block_adjacency.png")

    # 7 design populations
    fig, ax = plt.subplots(figsize=(9, 3.9))
    for p in ["A_PRIMARY_CONTROL", "TEAM_BALANCED_DIFF", "REWEIGHTED_DIFF", "ADJACENT_BLOCK_DIFF", "C1_TEAMMATE_OF_TARGET"]:
        r = DP[DP.population == p].iloc[0]
        ax.plot(range(len(CUM)), r[CUM].values.astype(float), marker="o", ms=5, lw=2, color=POPC[p],
                label=f"{p.replace('_', ' ').lower()} (median sep {r.carblock_sep_s_median:.0f} s)")
    ax.set_xticks(range(len(CUM)), CUM_L, fontsize=7)
    ax.set_ylabel("cumulative share (weighted where the design weights)")
    ax.legend(fontsize=7.5)
    ax.set_title("7. Different-team comparison populations: primary nearest-time vs Phase 4F sensitivity designs", loc="left", fontsize=10)
    save(fig, "fig07_primary_vs_team_balanced_population.png", top=0.97)

    reports(ADS, ST, NB, RU, DP, YA, CE, SC, RV, DV)


def reports(ADS, ST, NB, RU, DP, YA, CE, SC, RV, DV):
    f3 = lambda v: f"{float(v):.3f}"
    obs = ADS[ADS.basis == "OBSERVED_FEED_SEQUENCE"]
    cols = ["role", "population", "n_pairs", "share_same_update", "share_consecutive_strict", "share_le0_intervening", "share_le1_intervening",
            "share_le2_intervening", "share_le3_intervening", "share_le5_intervening"]
    t_adj = obs[obs.population != "A_POOL_PERCENTILE_RANK"][cols]
    t_sep = obs[obs.population != "A_POOL_PERCENTILE_RANK"][["role", "population", "carblock_sep_s_p10", "carblock_sep_s_p25", "carblock_sep_s_median", "carblock_sep_s_p75",
                                                              "carblock_sep_s_p90", "lap_ts_sep_s_median", "intervening_p25", "intervening_median", "intervening_p75", "intervening_p90"]]
    der = ADS[ADS.basis != "OBSERVED_FEED_SEQUENCE"][cols]
    rank = ADS[ADS.population == "A_POOL_PERCENTILE_RANK"][["role", "basis", "intervening_p25", "intervening_median", "intervening_p75"]].rename(
        columns={"intervening_p25": "rank_p25", "intervening_median": "rank_median", "intervening_p75": "rank_p75"})
    strat = ST[ST.stratum_type.isin(["SEQUENCE", "TIMESTAMP_CARBLOCK_SEP"])][["role", "stratum_type", "stratum", "scope", "n_pairs", "n_sessions", "D_p25", "D_median", "D_p75", "D_session_balanced_median"]]
    wt = ST[ST.stratum_type == "WITHIN_TARGET_PAIRED"][["role", "scope", "n_pairs", "n_sessions", "D_median", "D_session_balanced_median", "share_positive"]]
    sess = ST[ST.stratum_type == "SESSION_CONTRAST"][["role", "scope", "n_no_intervening", "n_gt5", "D_median", "eligible_for_S2_session_rule"]].rename(columns={"scope": "session", "D_median": "D_gt5_minus_D_no_intervening"})
    grp = NB[NB.level == "GROUP_MEDIAN_OF_BLOCKS"][["group", "blocks", "sessions", "targets", "median_control_carblock_sep_s", "median_control_lap_ts_sep_s", "median_control_intervening",
                                                   "share_controls_no_intervening", "pool_expectation_no_intervening", "excess_no_intervening", "median_pool_size", "control_reuse_ratio"]]
    ya = YA[YA.level != "SESSION"][["role", "level", "scope", "targets", "A_share_no_intervening", "B_expected_share_no_intervening", "A_minus_B_expectation", "C1_share_no_intervening",
                                    "A_minus_C1_share_no_intervening", "A_median_carblock_sep_s", "C1_median_carblock_sep_s", "phase4f_session_balanced_delta_reference"]]
    ys = YA[YA.level == "SESSION"][["role", "scope", "targets", "A_share_no_intervening", "B_expected_share_no_intervening", "C1_share_no_intervening", "A_minus_C1_share_no_intervening",
                                    "phase4f_session_balanced_delta_reference"]]
    ru = RU[RU.level.isin(["OVERALL", "YEAR", "ADJACENCY_BY_REUSE"])].dropna(axis=1, how="all")
    rd = RU[RU.level == "REUSE_DISTRIBUTION"][["role", "scope", "unique_control_carblocks"]]
    dp = DP[["population", "n_pairs", "n_blocks", "weighted", "share_same_update", "share_le0_intervening", "share_le2_intervening", "share_le5_intervening", "carblock_sep_s_median",
             "lap_ts_sep_s_median", "intervening_median", "distinct_comparator_teams", "largest_single_comparator_team_share", "max_carblock_appearances", "median_carblock_appearances",
             "blocks_covered"]]
    ce = pd.DataFrame({"criterion": CE.index, "value": CE.values})
    sc = SC[["session_key", "role", "category", "lap_records", "distinct_feed_updates", "share_records_in_shared_update", "median_update_spacing_s", "share_records_after_capture_gap"]]
    Pp = obs[(obs.role == "PRIMARY")].set_index("population")
    s23 = ST[(ST.role == "PRIMARY") & (ST.stratum_type == "SEQUENCE") & (ST.scope == "ALL")].set_index("stratum").D_session_balanced_median

    rep1 = f"""# V4 Phase 4G — Control-Selection Report

**Pre-specification:** `phase4g_design_diagnostic_spec.md`, committed as `ffdfacd` before any adjacency computation. Its rules were applied without change. **Phase 4F CASE:** `{CE['phase4f_case_unchanged']}`. It is unchanged, and the Phase 4F files were verified against `phase4f_freeze_record.csv`.

**Source:** Timing71 archived recordings of the INDYCAR live timing feed (third-party). This is a design diagnostic. It is not a new hierarchy test and not a tow analysis.

## 1. Reproduction of the Phase 4F primary control selection (4G.4)

The Phase 4F nearest-time selection was re-implemented with full candidate pools retained. Every target, teammate, control, D value and time separation matches `phase4f/comparison_pairs.csv` exactly:

{md(RV)}

The Phase 4F sensitivity populations also reproduce Phase 4F:
- adjacent-block DIFF: n and session-balanced D;
- reweighted DIFF: n and weighted D;
- team-balanced DIFF: all 209 block values.

{md(DV)}

## 2. Is the selected control an unusual comparison population? (4G.6)

**Answer: yes.** In the 2023–24 primary:
- **Selected control:** {f3(Pp.loc['A_PRIMARY_CONTROL', 'share_le0_intervening'])} of controls have **no intervening lap-line record** between them and the target: they are in the same feed update, or they are consecutive observations.
- **Random pick from the same pool:** {f3(CE['S1_B_random_pick_expectation'])} would be expected.
- **Difference:** {f3(CE['S1_difference'])}, a ratio of {f3(CE['S1_ratio'])}.
- **Pool rank:** the selected control's median percentile rank of intervening records within its own pool is about 0.20 (0 = most adjacent in the pool; 0.5 = what a random pick gives).
- **Teammates:** the nearest teammate (C1) is also more adjacent than the pool ({f3(Pp.loc['C1_TEAMMATE_OF_TARGET', 'share_le0_intervening'])}), but less so than the selected control.

**Cumulative adjacency** (share of pairs; "≤k" = same update, or ≤k intervening records on the lower-median target lap):

{md(t_adj)}

**Separation quantiles** (car-block time separation and lap-level |Δts| in s; intervening records):

{md(t_sep)}

**Selected control's percentile rank within its pool:**

{md(rank)}

**Derived laptime-chain sensitivity** (not observed; it breaks feed-update ties using laptime chains):

{md(der)}

- On this basis the selected controls remain about 2.8× the pool expectation.
- The absolute difference ({f3(CE['agreement_derived_A_share_no_intervening'])} vs {f3(CE['agreement_derived_B_expectation'])}) falls below the 0.20 "substantial" threshold. It agrees in direction but not in magnitude class.
- It does not enter the case rule (spec §11).

## 3. Year and session category (4G.7)

{md(ya)}

**Per session** (Phase 4F session-median Δ shown only for reference):

{md(ys)}

**Readings** (descriptive, not causal):
- The selected control's excess adjacency over its pool is almost the same in 2023 ({f3(YA[(YA.level == 'YEAR') & (YA.scope == '2023')].A_minus_B_expectation.iloc[0])}) and 2024 ({f3(YA[(YA.level == 'YEAR') & (YA.scope == '2024')].A_minus_B_expectation.iloc[0])}). **Control adjacency by itself does not explain why 2024's primary Δ was negative.**
- What differs by year is how adjacent the *teammate* comparator is. The control-minus-teammate gap in the no-intervening share is:
  - 2023: {f3(YA[(YA.level == 'YEAR') & (YA.scope == '2023')].A_minus_C1_share_no_intervening.iloc[0])};
  - 2024: {f3(YA[(YA.level == 'YEAR') & (YA.scope == '2024')].A_minus_C1_share_no_intervening.iloc[0])};
  - 2025 (secondary): {f3(YA[(YA.level == 'YEAR') & (YA.scope == '2025')].A_minus_C1_share_no_intervening.iloc[0])}.
- That ordering matches the ordering of the Phase 4F primary Δ (+0.10, −0.21, −0.39).
- **Caveat:** these are three points. Per session the pattern is mixed. The largest negative sessions (6387, 6388) have large gaps, but 6207 and 6378 have gaps near 0 with Δ ≈ 0 and −0.21.
- **Session category:** all categories with many targets show the same excess adjacency of about 0.29–0.31. Fast Friday (19 targets) is too small to read.

## 4. Negative vs positive Phase 4F blocks (4G.9)

{md(grp)}

**Comparison:**
- **Negative-Δ blocks:**
  - selected controls are closer: a median car-block separation of {f3(grp.set_index('group').loc['NEGATIVE', 'median_control_carblock_sep_s'])} s vs {f3(grp.set_index('group').loc['POSITIVE', 'median_control_carblock_sep_s'])} s in positive blocks, and a lap-level |Δts| of {f3(grp.set_index('group').loc['NEGATIVE', 'median_control_lap_ts_sep_s'])} s vs {f3(grp.set_index('group').loc['POSITIVE', 'median_control_lap_ts_sep_s'])} s;
  - they more often have no intervening record ({f3(grp.set_index('group').loc['NEGATIVE', 'share_controls_no_intervening'])} vs {f3(grp.set_index('group').loc['POSITIVE', 'share_controls_no_intervening'])});
  - they come from somewhat larger pools (median {f3(grp.set_index('group').loc['NEGATIVE', 'median_pool_size'])} vs {f3(grp.set_index('group').loc['POSITIVE', 'median_pool_size'])}).
- **Excess adjacency over the pool expectation** differs less (median {f3(grp.set_index('group').loc['NEGATIVE', 'excess_no_intervening'])} vs {f3(grp.set_index('group').loc['POSITIVE', 'excess_no_intervening'])}).
- **Verdict:** negative blocks are associated with more extreme control adjacency, but the association is moderate, not decisive. Blocks were not redefined or discarded.

## 5. Control reuse (4G.10)

{md(ru)}

**Distribution of targets per control car-block:**

{md(rd)}

**Readings:**
- About half of targets share their control car-block with at least one other target. The maximum is 5 targets per control car-block.
- High-reuse controls (≥3 targets) are slightly more timing-adjacent than the rest.
- Reused controls are not independent evidence. The 1,937 primary comparisons rest on {int(RU[(RU.role == 'PRIMARY') & (RU.level == 'OVERALL')].unique_control_carblocks.iloc[0])} distinct control car-blocks.

## 6. Design populations: primary vs team-balanced / adjacent-block / reweighted (4G.11–4G.12)

{md(dp)}

**Nothing here is promoted to a primary result.** None of the three Phase 4F sensitivity designs takes the time-nearest different-team car within the target's own block. Team-balanced uses all cross-team pairs; adjacent-block takes the nearest car in the *next* block; reweighted keeps the primary pairs but reweights them to same-car separations. All three move the different-team population away from timing adjacency:

| Population | No-intervening share | Median car-block separation | Notes |
|---|---|---|---|
| Primary control | {f3(DP.set_index('population').loc['A_PRIMARY_CONTROL', 'share_le0_intervening'])} | 3 s | |
| Team-balanced (weighted) | {f3(DP.set_index('population').loc['TEAM_BALANCED_DIFF', 'share_le0_intervening'])} | 61 s | close to the pool expectation |
| Reweighted | {f3(DP.set_index('population').loc['REWEIGHTED_DIFF', 'share_le0_intervening'])} | | the weights concentrate on a few long-separation pairs |
| Adjacent-block | {f3(DP.set_index('population').loc['ADJACENT_BLOCK_DIFF', 'share_le0_intervening'])} | 147 s | the comparator is in the next block by construction |

**Other differences:**
- **Team representation is similar:** 12 control teams in the primary; the largest single-team share is 0.15–0.16, except in the reweighted population, where it is 0.28 because of weight concentration.
- **Reuse:** the team-balanced population reuses each car-block far more (median 13 appearances vs 1).
- **Block coverage:** the same 209 blocks, except adjacent-block (158).

So the sign difference between the Phase 4F primary and these sensitivities coincides with a large difference in the timing adjacency of the different-team comparator.

## 7. Mechanical case (spec §11)

{md(ce)}
"""
    rep2 = f"""# V4 Phase 4G — Timing-Sequence Adjacency Report

## What was reconstructed

**Sequence:**
- For each session, every Timing71 lap-line record (all cars, flags and laps) is placed in chronological order.
- **Feed timestamps are update times.** Distinct timestamps are never closer than about 1.5–1.7 s. In the long practice sessions, 54–78% of records share their timestamp with another car's record.
- **Order within one feed update is not observed** and was **not invented**. Such pairs are labelled `SAME_UPDATE` (order unobserved).

**Per target–comparator car-block pair:**
- each target lap is matched to the comparator's nearest lap in the block;
- the number of other records strictly between them is counted;
- the lower-median target lap gives the pair's category.

**Sequence completeness:**

{md(sc)}

- In practice-type sessions (2023–2025), about 1–16% of records follow a capture gap.
- Missing records would **understate** intervening counts, i.e. make pairs look more adjacent than they were. This affects all populations alike and does not favour the selected control.

## D by adjacency stratum (4G.8, different-team candidate pairs)

**Strata were fixed in the spec before D was seen.**

{md(strat)}

**Within-target paired diagnostic** (median D(>5 between) − median D(no intervening), per target, holding the block and target fixed):

{md(wt)}

**Per-session contrast** (primary and 2025):

{md(sess)}

**Readings:**
- **Primary, session-balanced median D:** same update {f3(s23['SAME_UPDATE'])}, consecutive {f3(s23['CONSECUTIVE'])}, 1–2 between {f3(s23['BETWEEN_1_2'])}, 3–5 between {f3(s23['BETWEEN_3_5'])}, >5 between {f3(s23['BETWEEN_GT5'])} mph.
- **Different-team cars that are timing-adjacent are more similar** in observed local performance than less-adjacent ones:
  - Δ_S2 = {f3(CE['S2_delta'])} mph;
  - positive in 2023 ({f3(CE['S2_2023_delta'])}) and 2024 ({f3(CE['S2_2024_delta'])});
  - positive in {f3(CE['S2_share_sessions_positive'])} of eligible sessions; the two exceptions are small sessions, 2024 Practice 1 and Fast Friday;
  - positive within target ({f3(CE['S2_within_target_sb_median'])});
  - also present in 2025 ({f3(CE['agreement_2025_S2_delta'])}).
- **The timestamp-bin gradient** (car-block median time, the Phase 4F bins) **is not monotone:** ≤5 s is lowest, but 5–15 s is higher than 15–60 s. Car-block median-time separation is a coarser proxy than lap-level sequence adjacency.

## Direction of dependence is not identified

- **One direction:** timing adjacency may reflect shared local on-track context that makes speeds similar.
- **The reverse direction:** two cars can only **stay** near-consecutive across several laps if their lap times are similar. Sustained adjacency is partly a *consequence* of similar speed.
- **Either way,** choosing the control by nearest car-block time conditions on a variable that is associated with the outcome D. That is the concrete control-selection property identified here.

## Observed vs not observed (4G.13)

**OBSERVED:** two cars' lap records appeared in the same Timing71 feed update, or with few intervening records. That means they crossed the timing line close together in time and order, at about 1.7 s feed resolution.

**NOT OBSERVED:**
- whether one car was physically towing another;
- the exact physical gap;
- the order within a feed update;
- the traffic configuration around the full lap;
- aerodynamic interaction;
- run purpose.

Timing-sequence adjacency is consistent with shared local on-track context but does not identify tow.
"""
    rep3 = f"""# V4 Phase 4G — Limitations Report

1. **Proxy only.** Timing-sequence adjacency is an on-track temporal adjacency proxy measured at the timing line. Timing-sequence adjacency is consistent with shared local on-track context but does not identify tow. No tow, traffic-group or aerodynamic label was created.
2. **Feed resolution.**
   - Timing71 timestamps are feed-update times (about 1.67 s cycle), not line-crossing times.
   - Order within an update is unobserved and was not invented.
   - The derived laptime-chain estimate is a labelled sensitivity. It agrees in direction (about 2.8× the pool expectation). On the derived basis, the absolute excess is {f3(CE['agreement_derived_A_share_no_intervening'])} − {f3(CE['agreement_derived_B_expectation'])} ≈ 0.16, below the "substantial" threshold of 0.20.
3. **Missing captures:** about 1–16% of records in practice-type sessions follow a capture gap, which would understate intervening counts.
4. **Direction of dependence:** adjacency and similar speed are mutually dependent (sustained adjacency requires similar lap times). Phase 4G shows that the primary control selection conditions on this association. It does not show which way the dependence runs.
5. **Mechanical case thresholds:**
   - The spec thresholds (0.20 absolute, ratio ≥ 2, 0.25 mph) were fixed before the results.
   - **2025 secondary:** the ratio is 1.99 (A {f3(CE['agreement_2025_A_share_no_intervening'])} vs E {f3(CE['agreement_2025_B_expectation'])}), just under 2. The absolute excess (about 0.32) and the D association (Δ_S2 {f3(CE['agreement_2025_S2_delta'])}) agree in direction. 2025 does not enter the case.
6. **Small effective sample:**
   - The adjacency–D association uses 10 primary sessions with eligible blocks.
   - The two sessions where it is not positive are small (2024 Practice 1, 2024 Fast Friday).
   - Pairs within a block share cars, and controls are reused (about half of targets share a control car-block). None of this is treated as independent.
7. **Year pattern:**
   - The selected control's excess adjacency over its pool is similar in 2023 and 2024.
   - The year ordering of the Phase 4F Δ matches the control-minus-teammate adjacency gap, but that is three points, and the per-session pattern is mixed.
   - No causal explanation of the year differences is claimed.
8. **What this does not do:**
   - no hierarchy retest;
   - no change to the Phase 4F CASE D label;
   - no model;
   - no team effects;
   - no team/driver ranking;
   - no 2025 or race pooling;
   - no new data ingested.
9. **External evidence** (`future_evidence_feasibility.csv`):
   - The Timing71 live-feed column spec includes an interval-to-car-in-front (`Int`) column. Full replay recordings *might* carry it per update, but that is unverified.
   - Official "Section Results" PDFs exist for practice sessions, but whether they carry per-crossing time of day is unverified.
   - Neither was retrieved in Phase 4G.
"""
    (OUT / "phase4g_control_selection_report.md").write_text(rep1)
    (OUT / "phase4g_adjacency_report.md").write_text(rep2)
    (OUT / "phase4g_limitations_report.md").write_text(rep3)


if __name__ == "__main__":
    main()
