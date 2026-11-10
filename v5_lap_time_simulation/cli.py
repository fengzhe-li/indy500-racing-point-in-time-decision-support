"""Command-line entry point: python -m v5_lap_time_simulation.cli"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import run_analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reproducible V5 quasi-steady Indy 500 lap simulation")
    parser.add_argument("--data-dir", type=Path, default=Path("data/canonical/v1"),
                        help="directory containing attempts.csv and attempt_laps.csv")
    parser.add_argument("--output-dir", type=Path, default=Path("v5_lap_time_simulation/output"))
    args = parser.parse_args()
    result = run_analysis(args.output_dir, args.data_dir)
    print(json.dumps({"output_dir": str(args.output_dir), "baseline": result["baseline"],
                      "validation": result["validation"]}, indent=2))


if __name__ == "__main__":
    main()
