"""V4 Phase 4H: figures and reports (reads Phase 4H outputs only; descriptive)."""
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "output" / "phase4h"
FIG = OUT / "figures"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 9, "legend.frameon": False})
DIAG = ("Phase 4H measurement-validity audit · Timing71 archived live-feed laps (third-party); official QualLap1–4 anchor 2023–24 qualifying · "
        "no hierarchy recomputed · 2025 separate · Phase 4F D / 4G A unchanged")
CLASSES = ["A_PERFORMANCE_COMPARABLE", "B_PLAUSIBLY_PERFORMANCE_COMPARABLE", "C_RUN_STATE_AMBIGUOUS", "D_CLEARLY_NON_COMPARABLE", "E_INPUT_INSUFFICIENT"]
CLS_C = dict(zip(CLASSES, [CAT[2], CAT[0], CAT[3], CAT[7], "#9a9892"]))
CLS_L = dict(zip(CLASSES, ["A performance-comparable", "B plausibly comparable", "C run-state ambiguous", "D clearly non-comparable", "E input insufficient"]))


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
    P = pd.read_csv(OUT / "practice_lap_inventory.csv", dtype={"session_key": str, "car": str}, low_memory=False)
    Q = pd.read_csv(OUT / "qualifying_performance_reference.csv", dtype={"session_key": str, "car": str}, low_memory=False)
    RC = pd.read_csv(OUT / "run_state_classification.csv", dtype={"session_key": str})
    CAL = pd.read_csv(OUT / "qualifying_calibration.csv")
    RA = pd.read_csv(OUT / "classification_rule_audit.csv")
    PA = pd.read_csv(OUT / "phase4f_population_run_state_audit.csv")
    AD = pd.read_csv(OUT / "adjacency_run_state_audit.csv")
    SD = pd.read_csv(OUT / "practice_speed_distribution.csv")
    CE = pd.read_csv(OUT / "case_evaluation.csv").set_index("criterion").value
    P["yg"] = np.where(P.year == 2025, "2025 secondary", "2023–24 primary")
    nd = P[~P.D.astype(bool)]
    T = {k: float(CE[k]) for k in ["T_steady_95", "T_steady_100", "T_level_95", "T_level_100"]}

    # 1 qualifying vs practice speed
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.8), sharey=True)
    for ax, yg in zip(axes, ["2023–24 primary", "2025 secondary"]):
        x = nd[nd.yg == yg].speed_mph
        ax.hist(x, bins=np.arange(200, 238, 0.5), density=True, histtype="stepfilled", alpha=0.35, color=CAT[0], label=f"practice, at-speed non-D laps (n={len(x)})")
        if yg.startswith("2023"):
            qq = Q[Q.provenance == "OFFICIAL_ANCHORED"].speed_mph
            lab = f"official qualifying timed laps 2023–24 (n={len(qq)})"
        else:
            qq = Q[(Q.year == 2025) & (Q.flag.astype(str).str.lower() == "green") & Q.attempt_len.isin([4, 5])].speed_mph
            lab = f"2025 qualifying green laps in 4/5-lap runs (inferred; n={len(qq)})"
        ax.hist(qq, bins=np.arange(200, 238, 0.5), density=True, histtype="step", lw=2, color=CAT[1], label=lab)
        ax.set_xlabel("lap speed (mph)")
        ax.set_title(yg, loc="left", fontsize=9.5)
        ax.legend(fontsize=7.2, loc="upper left")
    axes[0].set_ylabel("density")
    fig.suptitle("1. Qualifying timed laps vs practice laps (different aero/boost regimes; levels are not assumed to transfer)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig01_qualifying_vs_practice_speed.png")

    # 2 / 3 deficits
    for fname, col, title, tl in [("fig02_practice_deficit_to_session_best.png", "deficit_to_session_best", "2. Practice laps: deficit to the car's session-best lap", None),
                                  ("fig03_practice_deficit_to_stint_best.png", "deficit_to_stint_best", "3. Practice laps: deficit to the car's stint-best lap", None)]:
        fig, ax = plt.subplots(figsize=(10, 3.6))
        for k, yg in enumerate(["2023–24 primary", "2025 secondary"]):
            x = nd[nd.yg == yg][col].clip(upper=0.10) * 100
            ax.hist(x, bins=np.arange(0, 10.1, 0.1), density=True, histtype="step", lw=1.8, color=CAT[k], label=f"{yg} at-speed non-D laps (median {x.median():.2f}%)")
        qd = Q[Q.provenance == "OFFICIAL_ANCHORED"].dev_from_attempt_fastest * 100
        ax.axvline(qd.quantile(.95), color=CAT[1], ls="--", lw=1.4, label=f"official qualifying: 95th pct deficit to attempt-fastest lap ({qd.quantile(.95):.2f}%)")
        ax.set_xlabel("deficit (%) — 10% shown as upper bin")
        ax.set_ylabel("density")
        ax.legend(fontsize=7.5)
        ax.set_title(title, loc="left", fontsize=10.5)
        save(fig, fname, top=0.97)

    # 4 representative trajectories: deterministic = the 6 longest stints in the largest 2024 practice-type session
    sk = P[P.year == 2024].session_key.value_counts().index[0]
    s = P[P.session_key == sk]
    top = s.groupby(["source_id", "car", "stint"]).size().sort_values(ascending=False).head(6).index
    fig, axes = plt.subplots(2, 3, figsize=(13, 6), sharey=True)
    for ax, key in zip(axes.flat, top):
        h = s[(s.source_id == key[0]) & (s.car == key[1]) & (s.stint == key[2])].sort_values("lap_in_stint")
        ax.plot(h.lap_in_stint + 1, h.speed_mph.clip(lower=195), color=INK2, lw=1, zorder=1)
        for c in CLASSES:
            hh = h[h.cls == c]
            ax.scatter(hh.lap_in_stint + 1, hh.speed_mph.clip(lower=195), s=18, color=CLS_C[c], zorder=2, label=CLS_L[c])
        ax.set_title(f"car {key[1]}, stint {key[2]} ({len(h)} laps)", loc="left", fontsize=8.5)
        ax.set_xlabel("lap position in stint")
    axes[0, 0].set_ylabel("lap speed (mph; <195 clipped)")
    axes[1, 0].set_ylabel("lap speed (mph; <195 clipped)")
    hl = axes[0, 0].get_legend_handles_labels()
    fig.legend(*hl, loc="upper right", bbox_to_anchor=(1.0, 0.95), fontsize=7.5, ncol=5)
    fig.suptitle(f"4. Within-stint trajectories: the 6 longest stints of session {sk} (deterministic selection)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig04_within_stint_trajectories.png", top=0.9)

    # 5 lap position vs speed
    fig, ax = plt.subplots(figsize=(10, 3.8))
    for k, yg in enumerate(["2023–24 primary", "2025 secondary"]):
        g = P[P.yg == yg].assign(pos=lambda d: (d.lap_in_stint + 1).clip(upper=20)).groupby("pos").speed_mph
        med, lo, hi = g.median(), g.quantile(.25), g.quantile(.75)
        ax.fill_between(med.index + (k - 0.5) * 0.15, lo, hi, color=CAT[k], alpha=0.18)
        ax.plot(med.index + (k - 0.5) * 0.15, med, "o-", color=CAT[k], ms=4, lw=1.8, label=f"{yg}: median (band = IQR), all records")
    ax.set_ylim(150, 232)
    ax.set_xlabel("lap position in stint (20 = 20+)")
    ax.set_ylabel("lap speed (mph)")
    ax.legend(fontsize=7.5, loc="lower right")
    ax.set_title("5. Lap position within stint vs speed (position 1 = pit-exit lap; stint length varies)", loc="left", fontsize=10.5)
    save(fig, "fig05_lap_position_vs_speed.png", top=0.97)

    # 6 composition by session category
    c = RC[RC.level == "CATEGORY"].copy()
    lab = [f"{textwrap.fill(r.category.replace('_', ' ').lower(), 14)}\n({'2025' if r.yr_group.startswith('2025') else '23–24'}; n={int(r.n_laps)})" for r in c.itertuples(index=False)]
    fig, ax = plt.subplots(figsize=(12, 4.2))
    bottom = np.zeros(len(c))
    for cl in CLASSES:
        vals = c[f"share_all_{cl[0]}"].values
        ax.bar(range(len(c)), vals, bottom=bottom, color=CLS_C[cl], label=CLS_L[cl], edgecolor=SURFACE, lw=1)
        bottom += vals
    ax.set_xticks(range(len(c)), lab, fontsize=7)
    ax.set_ylabel("share of all lap records")
    ax.legend(fontsize=7.5, ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.13))
    ax.set_title("6. Run-state composition by session category", loc="left", fontsize=10.5, pad=24)
    save(fig, "fig06_run_state_by_session_category.png", top=0.95)

    # 7 adjacency vs run-state matching
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.9))
    order = ["SAME_UPDATE", "CONSECUTIVE", "BETWEEN_1_2", "BETWEEN_3_5", "BETWEEN_GT5"]
    xl = ["same\nupdate", "consec.", "1–2", "3–5", ">5"]
    for k, role in enumerate(["PRIMARY", "ERA_C_SECONDARY"]):
        a = AD[(AD.role == role) & (AD.table == "MATCH_BY_ADJACENCY")].set_index("stratum").loc[order]
        axes[0].plot(range(5), a.share_matched, "o-", color=CAT[k], lw=2, label=f"{'2023–24' if role == 'PRIMARY' else '2025'}: same car-block class")
        axes[0].plot(range(5), a.share_both_AB, "s--", color=CAT[k], lw=1.4, label=f"{'2023–24' if role == 'PRIMARY' else '2025'}: both A or B")
        for sub, m in [("RUNSTATE_MATCHED", "o-"), ("RUNSTATE_MISMATCHED", "^:"), ("BOTH_A", "s--")]:
            axes[1].plot(range(5), a[f"D_sb_median_{sub}"], m, color=CAT[k], lw=1.6, ms=5,
                         label=f"{'2023–24' if role == 'PRIMARY' else '2025'}: {sub.lower().replace('_', ' ')}")
    for ax in axes:
        ax.set_xticks(range(5), xl)
        ax.set_xlabel("timing-sequence adjacency stratum (Phase 4G, different-team pool pairs)")
    axes[0].set_ylabel("share of pairs")
    axes[1].set_ylabel("session-balanced median D (mph)")
    axes[0].legend(fontsize=7)
    axes[1].legend(fontsize=6.5, ncol=2)
    fig.suptitle("7. Timing adjacency vs run-state matching; the adjacency–D gradient within run-state subsets (descriptive; no mediation claim)", x=0.01, ha="left", fontsize=10)
    save(fig, "fig07_adjacency_vs_run_state.png")

    # 8 Phase 4F target / control composition
    pa = PA[PA.population != "ALL_COMPARABLE_CARBLOCKS"].copy()
    fig, ax = plt.subplots(figsize=(11, 3.9))
    cols = [("share_both_A", "both A"), ("share_both_AB", "both A/B"), ("share_matched", "same class (any)"), ("share_involves_C_ambiguous", "involves C (ambiguous)"),
            ("share_involves_D_or_E", "involves D/E")]
    x = np.arange(len(pa))
    for k, (col, nm) in enumerate(cols):
        ax.bar(x + (k - 2) * 0.16, pa[col], width=0.15, color=CAT[k], label=nm)
    ax.set_xticks(x, [f"{textwrap.fill(p.replace('_', ' ').lower(), 16)}\n({'2025' if r.startswith('ERA') else '23–24'})" for p, r in zip(pa.population, pa.role)], fontsize=7)
    ax.set_ylabel("share of pairs")
    ax.legend(fontsize=7.5, ncol=5, loc="upper center", bbox_to_anchor=(0.5, 1.12))
    ax.set_title("8. Run-state composition of the Phase 4F/4G comparison populations (car-block modal class)", loc="left", fontsize=10.5, pad=22)
    save(fig, "fig08_phase4f_population_run_state.png", top=0.95)

    reports(P, Q, RC, CAL, RA, PA, AD, SD, CE, T)


def reports(P, Q, RC, CAL, RA, PA, AD, SD, CE, T):
    f3 = lambda v: f"{float(v):.3f}"
    pc = lambda v: f"{100 * float(v):.1f}%"
    o = Q[Q.provenance == "OFFICIAL_ANCHORED"]
    qref = o.groupby("year").agg(attempts=("attempt_id", "nunique"), laps=("laptime", "size"), speed_min=("speed_mph", "min"), speed_median=("speed_mph", "median"),
                                 speed_max=("speed_mph", "max"), within_range_median=("within_attempt_rel_range", "median"), within_range_max=("within_attempt_rel_range", "max"),
                                 dev_fastest_p90=("dev_from_attempt_fastest", lambda s: s.quantile(.9)),
                                 share_monotone_decline=("sequential_pattern", lambda s: (s == "---").mean())).reset_index()
    qall = Q.drop_duplicates("attempt_id").groupby(["year", "session_key", "attempt_len"]).size().unstack(fill_value=0).reset_index()
    qall.columns = [str(c) if not isinstance(c, str) else c for c in qall.columns]
    sd = SD[SD.level == "YEAR"][["layer", "year", "n_laps", "speed_min", "speed_p5", "speed_p25", "speed_p50", "speed_p75", "speed_p95", "speed_max", "def_session_best_p50",
                                  "def_session_best_p90", "def_stint_best_p50", "def_stint_best_p90", "within_stint_range_median", "share_def_session_best_gt_2pct"]]
    sdc = SD[(SD.level == "CATEGORY") & (SD.layer == "NON_D")][["role", "category", "n_laps", "speed_p10", "speed_p50", "speed_p90", "def_session_best_p50", "def_stint_best_p50",
                                                                 "within_stint_range_median", "within_car_iqr_median"]]
    cal = CAL[["reference_group", "in_sample", "attempts", "laps", "retention_A", "retention_AB", "share_C", "share_D", "share_E", "attempt_coherence_same_class", "within_attempt_rel_range_median", "note"]]
    ra = RA
    rcy = RC[RC.level.isin(["YEAR", "CATEGORY", "STINT_POSITION"])][["level", "yr_group", "year", "category", "lap_position", "n_laps", "n_nonD", "share_all_D", "share_nonD_A",
                                                                     "share_nonD_B", "share_nonD_C", "share_nonD_E", "share_nonD_AB"]]
    rcs = RC[RC.level == "SESSION"][["yr_group", "session_key", "category", "n_laps", "share_all_D", "share_nonD_A", "share_nonD_B", "share_nonD_C", "share_nonD_E", "share_nonD_AB"]]
    rct = RC[RC.level == "TEAM_COVERAGE_ONLY_ALPHABETICAL"][["yr_group", "canonical_engineering_team", "n_laps", "share_nonD_AB", "share_nonD_C"]]
    pa = PA[PA.population != "ALL_COMPARABLE_CARBLOCKS"][["role", "population", "n_pairs", "share_matched", "share_mismatched", "share_both_A", "share_both_AB", "share_involves_C_ambiguous",
                                                           "share_involves_D_or_E", "target_share_A", "comparator_share_A"]]
    pcb = PA[PA.population == "ALL_COMPARABLE_CARBLOCKS"][["role", "n_pairs", "carblock_share_A", "carblock_share_B", "carblock_share_C", "carblock_share_D", "carblock_share_E"]].rename(columns={"n_pairs": "car_blocks"})
    am = AD[AD.table == "MATCH_BY_ADJACENCY"][["role", "stratum", "n_pairs", "share_matched", "share_both_A", "share_both_AB", "share_involves_C", "D_sb_median_ALL", "D_sb_median_RUNSTATE_MATCHED",
                                                 "n_RUNSTATE_MATCHED", "D_sb_median_RUNSTATE_MISMATCHED", "D_sb_median_BOTH_A", "n_BOTH_A"]]
    ag = AD[AD.table == "ADJACENCY_GRADIENT_WITHIN_SUBSET"][["role", "stratum", "n_pairs", "n_no_intervening", "n_gt5", "D_sb_no_intervening", "D_sb_gt5", "gradient_gt5_minus_no_intervening"]]
    qn = AD[AD.table == "QUALIFYING_NEGATIVE_CONTROL"][["role", "n_pairs", "n_no_intervening", "n_gt5", "qualifying_carblocks", "blocks_with_2plus_cars", "identifiable", "note"]]
    ce = pd.DataFrame({"criterion": CE.index, "value": CE.values})
    g = ag.set_index(["role", "stratum"]).gradient_gt5_minus_no_intervening
    ra_i = RA.set_index("item").value
    a_prim = PA[(PA.role == "PRIMARY") & (PA.population == "A_PRIMARY_CONTROL")].iloc[0]
    nd_share = RC[(RC.level == "YEAR_GROUP") & (RC.yr_group == "2023_2024_PRIMARY")].iloc[0]

    rep1 = f"""# V4 Phase 4H — Performance-Lap / Run-State Validity Report

**Pre-specification:** `phase4h_performance_validity_spec.md`, committed as `a56b4dd` before any classification, calibration or population audit. Its rules were applied without change.

**Prior results:** Phase 4F (`81455f3`, CASE **{CE['phase4f_case_unchanged']}**) and Phase 4G (`d903148`, CASE **{CE['phase4g_case_unchanged']}**) are unchanged and verified against `phase4h_freeze_record.csv`.

**Sources:**
- Lap records: **Timing71 archived recordings of the INDYCAR live timing feed (third-party)**.
- Official INDYCAR session details (2023–2024 only) anchor the official QualLap1–4 values.

**Scope:** a measurement-validity audit. No hierarchy was recomputed.

## Headline

**Measurement-validity CASE {CE['MEASUREMENT_VALIDITY_CASE']}: practice is unsuitable for a performance hierarchy.** Under the committed rules:
- The qualifying-calibrated classifier passes its out-of-year calibration: {pc(CE['C1_2024_official_retention_A'])} of 2024 official qualifying laps are retained.
- But only **{pc(CE['S_AB_nonD_2023_2024'])}** of at-speed 2023–24 practice laps (non-D) fall inside the qualifying envelope (class A or B).
- **{pc(CE['S_C_nonD'])}** are run-state ambiguous and {pc(CE['S_E_nonD'])} are input-insufficient.

**Gate:** {CE['phase4i_gate']}. Phase 4F and 4G stand as evidence that raw practice observations are not clean performance measurements. Phase 4I is not run.

## 1. Qualifying performance reference (4H.2)

**Official attempts matched to Timing71:** {ra_i['official attempts matched to Timing71 4-lap runs']} of {ra_i['official attempts in records (2023-2024)']} official QualLap1–4 records (2023–2024) matched an exact run of 4 consecutive Timing71 laps (`OFFICIAL_ANCHORED`). The unmatched records correspond to capture gaps.

{md(qref)}

**Structure of the official attempts:**
- Laps decline almost monotonically within an attempt ("---" pattern in most attempts).
- The within-attempt relative range is tiny (median 0.4–0.6%; max {pc(o.within_attempt_rel_range.max())}).

**Timing71 qualifying attempts by length** (a maximal timestamp-coherent run):

{md(qall)}

**Structural findings:**
- **2023–2024:** Timing71 qualifying captures record only timed laps. Warm-up laps are absent. Of the 92 one-lap "attempts", 38% re-post the previous lap time at the start of the next run (a feed artifact); the rest are isolated captured laps or partial captures.
- **2025:** the captures record a **yellow-flag warm-up lap** before each run, so runs appear as 5 laps. The pre-specified exactly-4-lap attempt definition therefore captures only fragments in 2025, and C2 fails mechanically.
- **2025 post-hoc description** (not a criterion): on the green laps 2–5 of these runs, the classifier retains {pc(CAL.set_index('reference_group').retention_A.get('2025_WARMUP_PLUS_4|timed laps 2-5 (post-hoc descriptive; not a criterion)', np.nan))} as A. The yellow warm-up laps are all D.
- **2025 has no official anchor**; its qualifying reference is inferred only.

## 2. Raw practice speed distribution (4H.4)

{md(sd)}

**By category** (non-D laps):

{md(sdc)}

**Evidence for multiple run states in practice** (descriptive, not causal):
- **All records:** heavily multimodal. Pit/out/in-laps and slow laps pull the p25 down to about 160–210 mph.
- **Non-D at-speed laps, deficit to the car's session best:** the median is 2.5–2.8% (about 6 mph).
  - 65–69% of at-speed laps are more than 2% below the car's own session best.
  - In official qualifying, the deficit to the attempt's fastest lap has a p90 of about 0.6%.
- **Within one stint:** the at-speed range is typically about 8 mph (median within-stint range of non-D laps).
- **Stint position:** the first lap is the pit-exit lap; lap 2 and the penultimate lap are slower on average (fig05).

## 3. Classifier and calibration (4H.5–4H.7)

**Thresholds** (2023 official attempts, n = {CE['n_2023_official_attempts']}):
- T_steady: 95th pct {f3(T['T_steady_95'])}, max {f3(T['T_steady_100'])} (relative range of a 4-lap window);
- T_level: 95th pct {f3(T['T_level_95'])}, max {f3(T['T_level_100'])} (window median vs the car's best steady window).

{md(cal)}

**Calibration criteria:**
- **C1 (2024 official, out-of-year):** A {pc(CE['C1_2024_official_retention_A'])}, A∪B {pc(CE['C1_2024_official_retention_AB'])} → **{'PASS' if str(CE['C1_pass']) == 'True' else 'FAIL'}**.
- **C2 (2025 inferred 4-lap):** A∪B {pc(CE['C2_2025_inferred_retention_AB'])} → **{'PASS' if str(CE['C2_pass']) == 'True' else 'FAIL'}**. The cause is structural (§1).

**Negative references:**
- **Qualifying:** known non-performance laps are **not recorded** in 2023–24 captures, so no qualifying negative reference exists there. In 2025, the observed yellow warm-up laps are all rejected (D), but only through the flag.
- **Practice proxies:** build laps (position 2), pre-in-laps and restart laps are classified A in only 3–9% of cases, vs 9–13% for interior laps.

**Classifier rule audit:**

{md(ra)}

## 4. Practice run-state composition (4H.8)

{md(rcy)}

**Per session:**

{md(rcs)}

**Coverage by team** (alphabetical; not a ranking):

{md(rct)}

## 5. Measurement-validity case (spec §9)

{md(ce)}
"""
    rep2 = f"""# V4 Phase 4H — Run-State Report (Phase 4F/4G population audit)

## Evidence tiers

| Tier | Contents |
|---|---|
| **Directly observed** | lap flag; pit exit/entry feed messages (practice stint starts matched {pc(ra_i['stint start matched to pit-exit message (practice stints)'])}; ends {pc(ra_i['stint end matched to pit-entry message (practice stints with endTime)'])}; qualifying stints {pc(ra_i['qualifying stints start matched to pit-exit message'])}, i.e. not pit-bounded); lap time; feed-update timestamp |
| **Inferred proxy** | out/in-laps at unmatched stint boundaries; build, pre-in and restart laps; capture gaps; steady-state windows; level vs the car's own best |
| **Unknown** | fuel, tyres, setup, boost within session, run purpose, tow/traffic, driver intent |

## Phase 4F car-blocks and comparison populations (4H.9)

The class of each Phase 4F comparable-layer car-block is its modal lap class.

{md(pcb)}

{md(pa)}

**Readings:**
- About {pc(a_prim.share_involves_C_ambiguous)} of the Phase 4F primary target–control pairs involve at least one run-state-ambiguous car-block.
- Only {pc(a_prim.share_both_A)} are A on both sides, and {pc(a_prim.share_both_AB)} are A/B on both sides.
- "Same class" ({pc(a_prim.share_matched)}) is mostly C = C, which is uninformative because C is the residual category.
- Teammate, pool and team-balanced populations look the same.
- **Most of the observed dispersion in Phases 4F/4G is therefore measured on car-blocks whose run state cannot be established.**

## Timing adjacency vs run state (4H.8)

{md(am)}

**Adjacency gradient** (D(>5 between) − D(no intervening)) within run-state subsets:

{md(ag)}

**Readings** (descriptive; no mediation claimed):
- **Adjacent pairs share a run-state class more often:** in 2023–24, {pc(AD[(AD.role == 'PRIMARY') & (AD.stratum == 'SAME_UPDATE')].share_matched.iloc[0])} for same-update pairs vs {pc(AD[(AD.role == 'PRIMARY') & (AD.stratum == 'BETWEEN_GT5')].share_matched.iloc[0])} for pairs more than 5 records apart. So *adjacency → similar run state → lower D* is plausible as part of the picture.
- **The Phase 4G gradient does not disappear when the coarse class is held equal:**
  - within matched pairs: {f3(g[('PRIMARY', 'RUNSTATE_MATCHED|ALL')])} mph;
  - within mismatched pairs: {f3(g[('PRIMARY', 'RUNSTATE_MISMATCHED|ALL')])} mph;
  - within both-A pairs: {f3(g[('PRIMARY', 'BOTH_A|ALL')])} mph (n = {int(ag.set_index(['role', 'stratum']).n_pairs[('PRIMARY', 'BOTH_A|ALL')])} pairs; small).
- **But the classifier leaves about 75% of car-blocks in the residual C class.** Holding "C = C" equal does not hold run state equal.
- **Conclusion:** the data cannot separate a pure adjacency phenomenon from run-state matching. The Phase 4G association is **materially compatible** with run-state composition and is not identified as a pure adjacency effect.

## Qualifying negative control (4H.10)

{md(qn)}

**NOT IDENTIFIABLE.** Indianapolis qualifying is run one car at a time, so different-team cars almost never share a 5-min block with laps in either adjacency stratum. No comparison was manufactured.
"""
    rep3 = f"""# V4 Phase 4H — Limitations Report

1. **Source semantics differ by session type.**
   - In practice, Timing71 stints are pit-bounded for most stints (feed pit messages).
   - In qualifying they are not, and only timed laps are recorded (2023–24). 2025 captures add a yellow warm-up lap.
   - The Phase 4E "first lap of stint = out-lap" rule therefore removes a *timed* lap in qualifying. This is recorded, not corrected; Phase 4E and 4F are unchanged.
2. **Qualifying is a different regime.** It has different boost, trim and single-car running. Only *shape* (steadiness) and *relative level* (vs the car's own best) were calibrated; absolute qualifying speed was never used as a cutoff. Whether qualifying steadiness is the right envelope for practice performance laps is an assumption, and it cannot be verified with these data.
3. **The class A rule is narrow by construction.** T_level comes from attempt-to-attempt variation in qualifying ({f3(T['T_level_95'])} at the 95th percentile). The pre-specified thresholds were not re-tuned. A looser rule would retain more practice laps, but no source-independent justification for any looser value exists, and choosing one after seeing practice shares would be outcome-driven.
4. **Run purpose, fuel, tyres, setup, tow and traffic are unobserved.** Even class A laps are only "qualifying-like steady windows near the car's own best". They are not verified push laps.
5. **Car-block labels are coarse.** The modal-lap class of a 5-min car-block collapses mixed blocks. The residual C class is heterogeneous, so "matched C = C" is not run-state matching.
6. **2025:**
   - There is no official anchor.
   - The pre-specified 4-lap attempt definition misses the 2025 warm-up + 4 structure, so C2 fails for structural reasons. A post-hoc description is reported, and it does not enter the case.
   - 2025 practice is reported separately. It agrees in direction (A∪B {pc(CE['agreement_2025_S_AB_nonD'])} of non-D laps).
7. **Capture gaps** make about {pc(nd_share.share_nonD_E)} of at-speed 2023–24 laps input-insufficient (no valid 4-lap window).
8. **The qualifying negative control is not identifiable** (single-car structure).
9. **What this does not do:**
   - no hierarchy recomputation;
   - no team effects;
   - no ranking;
   - no tow or traffic claims;
   - no model;
   - no change to Phase 4A–4G;
   - no pooling of 2025 or race.
"""
    (OUT / "phase4h_performance_validity_report.md").write_text(rep1)
    (OUT / "phase4h_run_state_report.md").write_text(rep2)
    (OUT / "phase4h_limitations_report.md").write_text(rep3)


if __name__ == "__main__":
    main()
