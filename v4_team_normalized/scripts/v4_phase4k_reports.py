"""V4 Phase 4K: figures and reports (support/identifiability only; reads Phase 4K outputs)."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "output" / "phase4k"
FIG = OUT / "figures"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "text.color": INK, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 9, "legend.frameon": False})
DIAG = ("Phase 4K feasibility audit (spec dae6856) · no predictions, errors or fitting · Tier 1 class-A car-blocks, 2023–24 primary; 2025 and Tier 2 separate · "
        "Timing71 archived live-feed (third-party)")
PC = {"PRIMARY_TIER1_2023_2024": CAT[0], "TIER2_2023_2024_EXTENDED": CAT[1], "TIER1_2025_SECONDARY": CAT[2]}


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
    EV = pd.read_csv(OUT / "target_prediction_events.csv", dtype={"session_key": str})
    TS = pd.read_csv(OUT / "teammate_signal_support.csv", dtype={"session_key": str})
    PS = pd.read_csv(OUT / "placebo_signal_support.csv", dtype={"session_key": str})
    ATT = pd.read_csv(OUT / "event_attrition.csv")
    DEP = pd.read_csv(OUT / "event_overlap_dependence.csv")
    HZ = pd.read_csv(OUT / "horizon_structure.csv")
    CV = pd.read_csv(OUT / "session_team_coverage.csv", dtype={"key": str})
    PH = pd.read_csv(OUT / "physical_input_support.csv")
    MF = pd.read_csv(OUT / "model_free_support.csv")
    T2 = pd.read_csv(OUT / "tier2_feasibility.csv")
    R5 = pd.read_csv(OUT / "replication_2025_feasibility.csv")
    CE = pd.read_csv(OUT / "case_evaluation.csv")
    P = EV[EV.cutoff == "PRIMARY"]
    lv = ["F0", "F1", "F2", "F3", "F4", "F5"]

    # 1 attrition
    fig, ax = plt.subplots(figsize=(9, 3.8))
    for pop, c in PC.items():
        for cut, ls in [("PRIMARY", "-"), ("CONSERVATIVE", ":")]:
            a = ATT[(ATT.population == pop) & (ATT.cutoff == cut)].set_index("level").reindex(lv)
            ax.plot(range(6), a.events, "o" + ls, color=c, lw=1.8, label=f"{pop.lower()} · {cut.lower()} cutoff")
            if cut == "PRIMARY":
                for i, v in enumerate(a.events):
                    ax.annotate(str(int(v)), (i, v), xytext=(4, 3), textcoords="offset points", fontsize=7, color=c)
    ax.set_xticks(range(6), ["F0\nevent", "F1\n+physics", "F2\n+teammate obs", "F3\n+teammate move", "F4\n+placebo move", "F5\n+no leakage"])
    ax.set_ylabel("prediction events")
    ax.legend(fontsize=6.8)
    ax.set_title("1. Nested feasibility attrition F0 → F5", loc="left", fontsize=10.5)
    save(fig, "fig01_attrition.png", top=0.97)

    # 2 / 3 coverage
    for fname, level, title in [("fig02_events_by_session.png", "SESSION", "2. Primary events by session"), ("fig03_events_by_target_team.png", "TARGET_TEAM_ALPHABETICAL", "3. Primary events by target team (coverage only; alphabetical; not a ranking)")]:
        c = CV[(CV.population == "PRIMARY_TIER1_2023_2024") & (CV.level == level)]
        fig, ax = plt.subplots(figsize=(11, 3.8))
        x = np.arange(len(c))
        for k, f in enumerate(["F0", "F3", "F4", "F5"]):
            ax.bar(x + (k - 1.5) * 0.2, c[f], width=0.19, color=CAT[k], label=f)
        ax.set_xticks(x, c.key.str.replace("_", " ").str.lower(), rotation=30 if level != "SESSION" else 0, ha="right" if level != "SESSION" else "center", fontsize=7.5)
        ax.set_ylabel("events")
        ax.legend(fontsize=7.5)
        ax.set_title(title, loc="left", fontsize=10.5)
        save(fig, fname, top=0.97)

    # 4-6 distributions
    for fname, data, xl, title, logx in [
            ("fig04_target_horizon.png", [(P.horizon_s, "F0"), (P[P.F5].horizon_s, "F5")], "t1 − prediction_time (s)", "4. Target horizon (prediction_time = first eligible lap of t1)", False),
            ("fig05_teammate_signal_age.png", [(TS.age_s, "all teammate movements"), (TS[TS.event_id.isin(P[P.F5].event_id)].age_s, "F5 events")], "prediction_time − s1 availability (s, log)", "5. Teammate signal age", True),
            ("fig06_teammate_movement_interval.png", [(TS.interval_s, "all teammate movements"), (TS[TS.event_id.isin(P[P.F5].event_id)].interval_s, "F5 events")], "s1 − s0 (s, log)", "6. Teammate movement interval", True)]:
        fig, ax = plt.subplots(figsize=(9, 3.4))
        for k, (d, lab) in enumerate(data):
            d = pd.Series(d).dropna()
            if logx:
                bins = np.logspace(np.log10(max(d.min(), 1)), np.log10(max(d.max(), 10)), 30) if len(d) else 10
            else:
                bins = np.arange(0, 160, 5)
            ax.hist(d, bins=bins, histtype="step", lw=2, color=CAT[k], label=f"{lab} (n={len(d)}, median {d.median():.0f} s)")
        if logx:
            ax.set_xscale("log")
        ax.set_xlabel(xl)
        ax.set_ylabel("count")
        ax.legend(fontsize=7.5)
        ax.set_title(title, loc="left", fontsize=10.5)
        save(fig, fname, top=0.97)

    # 7 teammate vs placebo coverage
    fig, ax = plt.subplots(figsize=(9, 3.6))
    pops = list(PC)
    x = np.arange(len(pops))
    for k, (col, lab) in enumerate([("F2", "prior teammate obs"), ("F3", "teammate movement"), ("F4", "+ comparable placebo movement"), ("F5", "+ leakage-free")]):
        ax.bar(x + (k - 1.5) * 0.2, [int(EV[(EV.population == p) & (EV.cutoff == "PRIMARY")][col].sum()) for p in pops], width=0.19, color=CAT[k], label=lab)
    ax.set_xticks(x, [p.lower().replace("_", " ") for p in pops], fontsize=8)
    ax.set_ylabel("events")
    ax.legend(fontsize=7.5)
    ax.set_title("7. Teammate vs structurally comparable placebo support", loc="left", fontsize=10.5)
    save(fig, "fig07_teammate_vs_placebo_support.png", top=0.97)

    # 8 reuse
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.6))
    for ax, (df, keys, lab) in zip(axes, [(TS, ["teammate_car", "s0_cb", "s1_cb"], "teammate movement"), (PS, ["placebo_car", "q0_cb", "q1_cb"], "placebo movement")]):
        for k, lvl in enumerate(["F3", "F4", "F5"]):
            ids = P[P[lvl]].event_id
            d = df[df.event_id.isin(ids)].groupby(keys).event_id.nunique() if len(df) else pd.Series(dtype=int)
            if len(d):
                vc = d.value_counts().sort_index()
                ax.plot(vc.index, vc.values, "o-", color=CAT[k], label=f"{lvl} (n signals={len(d)}, max reuse {d.max()})")
        ax.set_xlabel(f"events using the same {lab}")
        ax.set_ylabel("number of signals")
        ax.legend(fontsize=7.5)
    fig.suptitle("8. Reuse of predictor signals across events (primary)", x=0.01, ha="left", fontsize=10.5)
    save(fig, "fig08_reuse_dependence.png")

    reports(EV, TS, PS, ATT, DEP, HZ, CV, PH, MF, T2, R5, CE)


def reports(EV, TS, PS, ATT, DEP, HZ, CV, PH, MF, T2, R5, CE):
    ce = CE
    cv = CE.set_index("criterion").value
    P = EV[EV.cutoff == "PRIMARY"]
    f4 = P[P.F4]
    att = ATT
    rep1 = f"""# V4 Phase 4K — Point-in-Time Teammate Prediction Feasibility Report

**Pre-specification:** `phase4k_prediction_feasibility_spec.md`, committed as **`dae6856`** before any event count. Its rules were applied without change.

**What was not done:**
- no prediction, error, fitting, λ or predictor comparison;
- Δv_target was never computed;
- Phase 4J (FINAL, CASE B) is unchanged and not revisited.

## Headline: primary feasibility CASE {cv['PRIMARY_FEASIBILITY_CASE']} (weak support)

**Phase 4L:** {cv['phase4l_gate']}.

**Primary population:** Tier 1 (class A), 2023–24, the 8 Phase 4I-supported practice sessions.
- **F0:** {int(P.F0.sum())} canonical target events (one per future target observation), from {P.target_car.nunique()} target cars, {P.target_team.nunique()} teams and {P.session_key.nunique()} sessions.
- **F5** (leakage-free, with a structurally comparable different-team placebo): **{int(P.F5.sum())} events**, from {int(cv['S5'])} sessions, {int(cv['K5'])} teams and {int(cv['C5'])} cars.

**Why F5 is small:**
- Of the 22 F4 events, 14 fail because the frozen class-A label of t0 **cannot be confirmed point-in-time**.
- The Phase 4H rule needs 4-lap windows that extend after t0. For same-stint targets those windows run into t1's own laps.
- The F5 survivors are therefore mostly cross-stint events with long baselines: median t0→t1 about 35 min.
- **Under the conservative cutoff** (prediction at t0's completion), F5 = 0 in every population. At t0's completion its own label can never be confirmed.

## Attrition

{md(att)}

## Physical inputs and forecast vintages

{md(PH)}

**Readings:**
- Every event has realised PTSC track and ambient readings at t0 and t1, so the frozen β is mechanically applicable to all F1 events. It is **not** validated for practice.
- **Resolved change:** only {int(P.physical_resolved_change.sum())} of {len(P)} events have a *measured* physical change (distinct 15-min readings). The rest share one reading, so Δ = 0 at archive resolution.
- **Genuine forecast vintages: 0.** None exist in the frozen evidence. Any later experiment would condition on the **realised** environment and would not be a deployable forecast.

## Model-free support

{md(MF)}

## Case evaluation

{md(ce)}

## Phase 4L gate

**CASE C:** a Phase 4L predictive experiment is **not justified**. Phase 4L is not run.

The Tier 2 extended population reaches the B thresholds (36 F5 events, 8 sessions). By pre-registration it is secondary and **cannot rescue** the Tier 1 primary.
"""
    rep2 = f"""# V4 Phase 4K — Chronology / Leakage Report

## Information cutoff

**Primary cutoff:**
- `prediction_time` = the timestamp of t1's first eligible lap. Every predictor input must be **strictly earlier**.
- Records in the same feed update as the first outcome lap (equal timestamp) are never treated as prior. No within-update order is invented.

**Conservative cutoff (sensitivity):** `prediction_time` = t0's completion.

## Label leakage (the binding constraint)

**The issue:** Phase 4H class labels are retrospective. They use 4-lap windows that can extend after a lap, and the car's session-best steady level.

**Point-in-time confirmation:**
- Each predictor-side car-block (t0, s0, s1, q0, q1) was **re-confirmed** with the *unchanged* rule and thresholds, using only laps before the cutoff.
- This removes selection leakage for the predictor side.

**F4 events:**
- t0 confirmable: {int(f4.t0_pit_confirmed.fillna(False).astype(bool).sum())} of {len(f4)}.
- Each of those had at least one fully confirmable teammate/placebo combination.

**Outcome labels (t1) remain retrospective.** The target population is defined ex post, and eligibility depends on t1's level relative to the session best. This applies equally to P0–P3, but it is a real selection on the outcome.

## Horizons

{md(HZ)}

**Horizon structure:**
- The target horizon (t1 − `prediction_time`) is short by construction: the median F5 value is about 60 s.
- The baseline interval (t1 − t0) is bimodal: adjacent blocks (about 80–100 s) or cross-stint (tens of minutes).
- The teammate signal age has a median of 15–40 min, so teammate movements are often not recent.
"""
    rep3 = f"""# V4 Phase 4K — Dependence Report

{md(DEP)}

**Readings:**
- One canonical event per future target outcome, by construction; no outcome is shared.
- Teammate-movement reuse is up to 6 at F3, falls to 1 at F5, and placebo reuse is at most 2.
- The dependence problem is less reuse than **scarcity**: 8 primary F5 events, with up to 37.5% from one session.

## Coverage (coverage only; not a ranking)

{md(CV[CV.population == 'PRIMARY_TIER1_2023_2024'])}
"""
    rep4 = f"""# V4 Phase 4K — Limitations Report

1. **Retrospective eligibility.** The frozen Phase 4H class A is not a point-in-time label. Confirming it with information before the cutoff is the main source of attrition, and it makes the conservative cutoff structurally empty.
2. **Selection on the outcome.** t1 must be class A, which depends on its level relative to the session best.
3. **No forecast vintages.** Any experiment would use realised PTSC readings. The 15-min readings leave most short-horizon events with zero measured physical change.
4. **Frozen β.** It comes from 2020–2024 formal qualifying (four-lap attempts) and is not validated for practice car-block movements.
5. **Placebo comparability.** It is structural only: the same 5-min block for s1, the same block gap and the same stint status. It is not balanced on timing adjacency, which is recorded but not required.
6. **Teammate signal age.** Signals are often old (median 15–40 min), so the "movement" they carry may predate the target's run.
7. **Tier 2 and 2025 are secondary.**

   | Population | Label | F5 events | Sessions |
   |---|---|---|---|
   | Tier 2 | {T2.set_index('item').value.get('feasibility_case_same_rules')} | {T2.set_index('item').value.get('N5')} | {T2.set_index('item').value.get('S5')} |
   | 2025 | {R5.set_index('item').value.get('feasibility_case_same_rules')} | {R5.set_index('item').value.get('N5')} | {R5.set_index('item').value.get('S5')} |

   Neither changes the primary.
8. **No predictive claim of any kind** is made in Phase 4K.
"""
    for n, r in [("phase4k_prediction_feasibility_report.md", rep1), ("phase4k_chronology_leakage_report.md", rep2), ("phase4k_dependence_report.md", rep3), ("phase4k_limitations_report.md", rep4)]:
        (OUT / n).write_text(r)


if __name__ == "__main__":
    main()
