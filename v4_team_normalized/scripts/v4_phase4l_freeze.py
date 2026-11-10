"""V4 Phase 4L: freeze manifest (relative path, size, SHA-256, phase, role) for all V4 artifacts. No analysis."""
import hashlib, re, subprocess
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
V4 = REPO / "v4_team_normalized"
OUT = V4 / "output" / "phase4l"
EXCLUDE = {"output/phase4l/v4_final_manifest.csv", "output/phase4l/v4_final_manifest.sha256", "output/phase4l/v4_freeze_report.md", "output/phase4l/phase4l_checks_log.txt"}


def phase_of(rel):
    m = re.match(r"output/(phase\w+)/", rel)
    if m:
        return m.group(1)
    m = re.match(r"scripts/v4_(phase\w+?)_", rel)
    if m:
        return m.group(1)
    if rel.startswith("evidence/phase4e"):
        return "phase4e"
    if rel.startswith("evidence/entry_lists") or rel.startswith("manual/") or re.match(r"output/v4_", rel) or rel.startswith("scripts/v4_parse") or rel.startswith("scripts/v4_build"):
        return "phase1_2"
    return "v4"


def role_of(rel):
    n = rel.split("/")[-1]
    if rel.startswith("evidence/"):
        return "SOURCE_EVIDENCE"
    if rel.startswith("manual/"):
        return "MANUAL_RULES"
    if rel.startswith("scripts/"):
        return "CODE"
    if "freeze_record" in n or "input_verification" in n:
        return "FREEZE_RECORD"
    if re.search(r"spec|prespecified|pre_specification|tier_spec", n):
        return "PRE_REGISTRATION"
    if "/figures/" in rel:
        return "FIGURE"
    if rel.startswith("output/phase4l/"):
        return "SYNTHESIS"
    if n.endswith("checks_log.txt"):
        return "CHECK_LOG"
    if n.endswith(".md"):
        return "REPORT"
    if n.endswith(".csv"):
        return "RESULT_TABLE"
    return "OTHER"


def build():
    rows = []
    for p in sorted(V4.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts or p.name == ".DS_Store" or p.name.endswith(".pkl"):
            continue
        rel = str(p.relative_to(V4))
        if rel in EXCLUDE:
            continue
        rows.append(dict(relative_path="v4_team_normalized/" + rel, size_bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                         phase=phase_of(rel), artifact_role=role_of(rel)))
    return pd.DataFrame(rows)


def main():
    M = build()
    M.to_csv(OUT / "v4_final_manifest.csv", index=False)
    msha = hashlib.sha256((OUT / "v4_final_manifest.csv").read_bytes()).hexdigest()
    (OUT / "v4_final_manifest.sha256").write_text(f"{msha}  v4_team_normalized/output/phase4l/v4_final_manifest.csv\n")
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    byrole = M.groupby("artifact_role").agg(files=("relative_path", "size"), bytes=("size_bytes", "sum")).reset_index()
    byphase = M.groupby("phase").agg(files=("relative_path", "size"), bytes=("size_bytes", "sum")).reset_index()
    md = lambda d: "\n".join(["| " + " | ".join(d.columns) + " |", "|" + "|".join("---" for _ in d.columns) + "|"] + ["| " + " | ".join(map(str, r)) + " |" for r in d.itertuples(index=False)])
    (OUT / "v4_freeze_report.md").write_text(f"""# V4 Freeze Report

**Freeze record:**
- **Manifest:** `v4_final_manifest.csv`, {len(M)} files, {M.size_bytes.sum():,} bytes.
- **Manifest SHA-256:** `{msha}` (in `v4_final_manifest.sha256`).
- **Pre-freeze V4 HEAD:** `{head}`. The final commit is the "V4 final synthesis and freeze" commit that adds this manifest.

**Coverage:**
- **Included:** every file under `v4_team_normalized/` (evidence, manual rules, scripts, Phase 1–4L outputs, figures, README).
- **Excluded:** `__pycache__`, `.DS_Store`, the regenerable `_audit_cache.pkl`, and the four self-referential freeze files (`v4_final_manifest.csv`, `v4_final_manifest.sha256`, `v4_freeze_report.md`, `phase4l_checks_log.txt`).

## By role

{md(byrole)}

## By phase

{md(byphase)}

## Verification

`scripts/v4_phase4l_checks.py` recomputes every manifest hash. It also verifies:
- case labels and quoted numbers against their sources;
- FINAL_V2/V3 hashes, Phase 4A–4K immutability, and that the paper and original main are unchanged.

The results are in `phase4l_checks_log.txt`.

## Status

**Frozen:**
- V4 is an additive extension. It does not modify FINAL_V2/V3, the 41-transition core, V2 calibration, the V3 PIT architecture, production or scenario inference, the operational curve, or any existing frozen manifest.

**Not done:**
- No merge, no push, paper untouched.
""")
    print(len(M), msha)


if __name__ == "__main__":
    main()
