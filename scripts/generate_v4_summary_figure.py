#!/usr/bin/env python3
"""Presentation-only README graphic for the frozen V4 evidence extension.

Reads ALREADY-FROZEN Phase 4J outputs (tag V4_TEAM_NORMALIZED_FINAL) and draws them. No value is recomputed:
layer medians, contrasts and session-bootstrap intervals are copied from
v4_team_normalized/output/phase4j/hierarchy_summary_all_analyses.csv; leave-one-out signs from the frozen LOSO/LOTO tables.
The layout deliberately avoids implying the unsupported full same-car < same-team < different-team ordering.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P4J = ROOT / "v4_team_normalized" / "output" / "phase4j"
OUT = ROOT / "figures" / "portfolio"
BG, PANEL, INK, MUTED, CYAN, ORANGE, GREEN, RED, GRID = "#ffffff", "#f5f8fa", "#17232d", "#526672", "#168fa3", "#d87316", "#168a62", "#c94444", "#d6e0e5"


def frozen_values() -> dict:
    hs = pd.read_csv(P4J / "hierarchy_summary_all_analyses.csv").set_index("analysis")
    p, t2 = hs.loc["PRIMARY_TIER1_2023_2024"], hs.loc["TIER2_SENSITIVITY_2023_2024"]
    lo = pd.read_csv(P4J / "leave_one_session_out.csv").query("analysis == 'PRIMARY_TIER1_2023_2024'")
    lt = pd.read_csv(P4J / "leave_one_team_out.csv").query("analysis == 'PRIMARY_TIER1_2023_2024' and feasible")
    case = pd.read_csv(P4J / "case_evaluation.csv").set_index("criterion").value["PRIMARY_CASE"]
    n = int(p.evaluable_sessions)
    return dict(D_same_car=float(p.D_same_car), D_same_team=float(p.D_same_team), D_diff_team=float(p.D_diff_team),
                C1=float(p.C1), C1_lo=float(p.C1_boot_lo), C1_hi=float(p.C1_boot_hi), C1_pos=int(round(p.share_sessions_C1_pos * n)),
                C2=float(p.C2), C2_lo=float(p.C2_boot_lo), C2_hi=float(p.C2_boot_hi), C2_pos=int(round(p.share_sessions_C2_pos * n)),
                n=n, C1_status=p.C1_status, C2_status=p.C2_status, case=case, tier2_C2=float(t2.C2),
                C1_loso_all_pos=bool((lo.C1 > 0).all()), C1_loto_all_pos=bool((lt.C1 > 0).all()), C2_loto_flips=int((lt.C2 <= 0).sum()))


def main() -> None:
    v = frozen_values()
    assert v["C1_status"] == "POSITIVE_CONSISTENT" and v["C2_status"] == "INCONSISTENT" and v["case"] == "B"
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig = plt.figure(figsize=(13, 6.4), facecolor=BG)
    fig.text(0.035, 0.94, "V4 teammate-control evidence (frozen Phase 4J, pre-registered)", fontsize=17, fontweight="bold", color=INK)
    fig.text(0.035, 0.895, f"Restricted population: 2023–24 practice, frozen Class-A 5-min car-blocks, timing-adjacency common support, {v['n']} independent sessions",
             fontsize=10.5, color=MUTED)

    # Panel A: three value tiles, identical size and baseline (no bars, no staircase, no ordering arrows)
    fig.text(0.035, 0.815, "A  Observed dispersion D (session-balanced median |Δ speed|)", fontsize=12.5, fontweight="bold", color=INK)
    tiles = [("Same car", "local repeat,\nsame stint", v["D_same_car"]), ("Same team", "different car,\nsame 5-min block", v["D_same_team"]),
             ("Different team", "same 5-min block,\nsame adjacency stratum", v["D_diff_team"])]
    for i, (name, sub, val) in enumerate(tiles):
        x0 = 0.035 + i * 0.145
        ax = fig.add_axes([x0, 0.36, 0.13, 0.4])
        ax.set_facecolor(PANEL)
        for s in ax.spines.values():
            s.set_color(GRID)
        ax.set_xticks([]); ax.set_yticks([])
        ax.text(0.5, 0.80, name, ha="center", fontsize=13, fontweight="bold", color=INK, transform=ax.transAxes)
        ax.text(0.5, 0.70, sub, ha="center", va="top", fontsize=8.5, color=MUTED, transform=ax.transAxes, linespacing=1.3)
        ax.text(0.5, 0.33, f"{val:.2f}", ha="center", fontsize=28, fontweight="bold", color=CYAN, transform=ax.transAxes)
        ax.text(0.5, 0.17, "mph", ha="center", fontsize=11, color=MUTED, transform=ax.transAxes)
    fig.text(0.035, 0.315, "Tiles are summaries, not a ranking; read the contrasts in panel B.", fontsize=9.5, color=MUTED, style="italic")

    # Panel B: pre-registered contrasts with frozen session-bootstrap intervals
    ax = fig.add_axes([0.52, 0.36, 0.44, 0.4])
    fig.text(0.52, 0.815, "B  Pre-registered contrasts (95% session-bootstrap interval)", fontsize=12.5, fontweight="bold", color=INK)
    rows = [(1.25, "C1  same team − same car", v["C1"], v["C1_lo"], v["C1_hi"], GREEN,
             f"ROBUST within restricted population · {v['C1_pos']}/{v['n']} sessions positive\nall leave-one-session-out and leave-one-team-out estimates positive"),
            (0, "C2  different team − same team", v["C2"], v["C2_lo"], v["C2_hi"], RED,
             f"NOT ROBUST · {v['C2_pos']}/{v['n']} sessions positive · {v['C2_loto_flips']} team removal flips sign\nTier 2 sensitivity = {v['tier2_C2']:+.2f} mph")]
    for y, lab, c, lo_, hi_, col, note in rows:
        ax.plot([lo_, hi_], [y, y], color=col, lw=3, solid_capstyle="butt")
        ax.plot([lo_, lo_], [y - 0.08, y + 0.08], color=col, lw=2)
        ax.plot([hi_, hi_], [y - 0.08, y + 0.08], color=col, lw=2)
        ax.plot(c, y, "o", ms=11, color=col, zorder=3)
        box = dict(facecolor=BG, edgecolor="none", pad=1.5)
        ax.text(-0.95, y + 0.2, lab, fontsize=11, fontweight="bold", color=INK, va="bottom", bbox=box)
        ax.text(hi_ + 0.05, y, f"{c:+.2f} mph\n[{lo_:+.2f}, {hi_:+.2f}]", ha="left", va="center", fontsize=9.5, color=col, fontweight="bold", bbox=box)
        ax.text(-0.95, y - 0.2, note, fontsize=8.3, color=MUTED, va="top", linespacing=1.35, bbox=box)
    ax.axvline(0, color=INK, lw=1)
    ax.set_xlim(-0.95, 2.45)
    ax.set_ylim(-0.75, 1.75)
    ax.set_yticks([])
    ax.set_xlabel("mph", color=MUTED)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_facecolor(BG)

    fig.text(0.035, 0.17, "Full same-car < same-team < different-team hierarchy NOT established.", fontsize=13.5, fontweight="bold", color=RED)
    fig.text(0.035, 0.12, f"Pre-registered Phase 4J — CASE {v['case']} (partial). Exact-car control robustly reduces dispersion vs same-team different-car comparison;",
             fontsize=10.5, color=INK)
    fig.text(0.035, 0.085, "shared team identity showed no stable additional reduction vs different-team comparison. Empirical control hierarchy, not a causal team effect.",
             fontsize=10.5, color=INK)
    fig.text(0.035, 0.03, "Source: v4_team_normalized/output/phase4j/hierarchy_summary_all_analyses.csv (tag V4_TEAM_NORMALIZED_FINAL). "
             "Lap data: third-party archived recording of the INDYCAR live timing feed (Timing71).", fontsize=8, color=MUTED)
    fig.savefig(OUT / "v4-control-evidence-summary.png", dpi=150, facecolor=BG)
    plt.close(fig)
    pd.DataFrame([v]).to_csv(OUT / "v4-control-evidence-summary_plotting_data.csv", index=False)
    print("wrote figures/portfolio/v4-control-evidence-summary.png")


if __name__ == "__main__":
    main()
