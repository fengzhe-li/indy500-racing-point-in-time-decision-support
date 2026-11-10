#!/usr/bin/env python3
"""Validate public claims, figure links and selected frozen source hashes."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"PASS  {message}")


def main() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    all_image_refs = re.findall(r"!\[[^]]*\]\(([^)]+)\)", readme)
    # Remote badges (e.g. GitHub Actions status badges) are not local figure
    # files and are not expected to resolve on disk; only local figure paths
    # are checked here.
    image_refs = [ref for ref in all_image_refs if not ref.startswith(("http://", "https://"))]
    require(bool(image_refs), "README contains figures")
    missing = [ref for ref in image_refs if not (ROOT / ref).is_file()]
    require(not missing, f"all {len(image_refs)} README local figure references resolve")

    core = json.loads((ROOT / "r5_2/manual/probabilistic_physics_core_v1.json").read_text())
    require(abs(core["mean_core"]["full_data_huber_coefficients"]["delta_track_temp_c"] + 0.03482532976361639) < 1e-12, "frozen track coefficient matches README")
    require(abs(core["mean_core"]["full_data_huber_coefficients"]["delta_air_temp_c"] - 0.18239338404039918) < 1e-12, "frozen ambient coefficient matches README")

    final = json.loads((ROOT / "weather/output/final_integration/indy500_final_v2_freeze_manifest.json").read_text())
    require(final["version"] == "FINAL_V2" and final["status"] == "FINAL_FROZEN", "FINAL_V2 manifest is frozen")
    for item in final.get("artifacts", {}).values():
        if isinstance(item, dict) and "path" in item and "sha256" in item:
            path = ROOT / item["path"]
            require(path.is_file() and sha256(path) == item["sha256"], f"frozen hash: {item['path']}")

    section = json.loads((ROOT / "weather/output/v2b_section_mechanism/v2b_freeze_manifest_v1.json").read_text())
    require(section["scope"]["final_physics_core_transitions"] == 41, "FINAL_V2 contains 41 transitions")
    require(section["scope"]["linked_with_usable_section_evidence"] == 39, "section linkage is 39/41")

    samples = pd.read_csv(ROOT / "weather/output/v2_future_track/future_track_samples_with_solar_v1.csv")
    require(len(samples) == 656, "future-state sample interface has 656 rows")

    stress = json.loads((ROOT / "weather/output/v2e_scenario_stress_test/v2e_freeze_manifest_v1.json").read_text())
    require(stress["scenario_design"]["total_scenarios"] == 135, "stress test has 135 scenarios")
    require(stress["principal_findings"]["120_min_p_improve_range"] == [0.20552, 0.6704], "120-minute probability range matches README")

    ext = json.loads((ROOT / "r6_regime_extension/output/external_regime_inference_backtest_2025_v2/external_regime_inference_backtest_2025_metrics_v2.json").read_text())
    require(ext["extended_validation"]["n"] == 15, "external sample has 15 cases")
    require(ext["product_subset"]["n"] == 4, "production-boundary external subset has 4 cases")
    require(abs(ext["extended_validation"]["mae_mph"] - 0.49160020387931286) < 1e-12, "external MAE matches README")
    require(abs(ext["extended_validation"]["direction_accuracy"] - 0.4666666666666667) < 1e-12, "external directional accuracy matches README")

    # V4 (additive, frozen): README numbers must match the frozen Phase 4J/4H/4K/registry outputs; C2 must not be presented as robust
    v4 = ROOT / "v4_team_normalized/output"
    hs = pd.read_csv(v4 / "phase4j/hierarchy_summary_all_analyses.csv").set_index("analysis").loc["PRIMARY_TIER1_2023_2024"]
    require(pd.read_csv(v4 / "phase4j/case_evaluation.csv").set_index("criterion").value["PRIMARY_CASE"] == "B", "V4 Phase 4J primary case is B")
    require(hs.C1_status == "POSITIVE_CONSISTENT" and hs.C2_status == "INCONSISTENT", "V4 C1 robust / C2 not robust in frozen source")
    for label, val in [("0.37 mph", hs.D_same_car), ("1.23 mph", hs.D_same_team), ("1.09 mph", hs.D_diff_team), ("+0.70 mph", hs.C1), ("+0.20 mph", hs.C2)]:
        require(f"{val:+.2f} mph" == label or f"{val:.2f} mph" == label, f"V4 value {label} matches frozen Phase 4J source")
        require(label in readme, f"README states V4 value {label}")
    for lo, hi, text in [(hs.C1_boot_lo, hs.C1_boot_hi, "[+0.09, +1.72]"), (hs.C2_boot_lo, hs.C2_boot_hi, "[−0.53, +0.53]")]:
        require(f"[{lo:+.2f}, {hi:+.2f}]".replace("-", "−") == text and text in readme, f"README V4 interval {text} matches frozen source")
    h4 = pd.read_csv(v4 / "phase4h/case_evaluation.csv").set_index("criterion").value
    require(f"{100 * float(h4['S_A_nonD_2023_2024']):.1f}%" == "8.1%" and "**8.1%**" in readme, "V4 Class-A share matches README")
    att = pd.read_csv(v4 / "phase4k/event_attrition.csv").query("population == 'PRIMARY_TIER1_2023_2024' and cutoff == 'PRIMARY'").set_index("level").events
    require(int(att["F0"]) == 113 and int(att["F5"]) == 8 and "**113**" in readme and "only **8**" in readme, "V4 Phase 4K attrition matches README")
    require("**not established**" in readme and "C2 = different team − same team = +0.20 mph** [−0.53, +0.53]. **Not robust" in readme, "README states full hierarchy not established and C2 not robust")
    require("not** evidence that teammate predictive value is zero" in readme, "README does not present Phase 4K as zero teammate value")

    banned = ["predicts queue duration", "optimal wait recommendation", "autonomous race-strategy system"]
    require(not any(term in readme.lower() for term in banned), "README avoids prohibited strategy claims")
    print("\nPORTFOLIO_INTEGRITY_PASS")


if __name__ == "__main__":
    main()
