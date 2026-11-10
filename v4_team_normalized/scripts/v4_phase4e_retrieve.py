"""V4 Phase 4E step 2: documented retrieval of the two small source sets listed in source_inventory.csv.

  (a) Timing71 analysis JSON (lap-level, timestamped) for every 2018-2025 Indy 500 session in the archive listing;
  (b) INDYCAR EventsSessionDetails JSON for 2018-2025 Indy 500 sessions not already preserved locally.

Replay ZIPs and official PDFs are NOT retrieved. Every file gets a manifest row (URL, UTC time, bytes, SHA-256).
"""
import hashlib
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
EVID = REPO / "v4_team_normalized" / "evidence" / "phase4e"
UA = {"User-Agent": "Mozilla/5.0 (research audit; V4 Phase 4E)", "Accept": "application/json"}


def fetch(url, path):
    q = urllib.parse.quote(url, safe=":/?=&")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(q, headers=UA), timeout=60) as r:
                b = r.read()
                status = r.status
            path.write_bytes(b)
            return dict(url=url, local_path=str(path.relative_to(REPO)), http_status=status, bytes=len(b),
                        sha256=hashlib.sha256(b).hexdigest(), retrieved_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"), error="")
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            time.sleep(2 + 2 * attempt)
    return dict(url=url, local_path="", http_status=None, bytes=0, sha256="", retrieved_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"), error=err)


def main():
    rows = []
    t71dir = EVID / "timing71_analysis"
    t71dir.mkdir(parents=True, exist_ok=True)
    cand = pd.read_csv(REPO / "v4_team_normalized/output/phase4e/inputs/timing71_indy500_candidates_head_probe.csv")
    for r in cand.itertuples(index=False):
        safe = str(r.id).replace(":", "_")
        rows.append(dict(source_set="TIMING71_ANALYSIS", source_id=f"T71_ARCHIVE_{r.id}", year=int(r.year), session=r.description,
                         **fetch(r.analysisFilename, t71dir / f"{int(r.year)}_{safe}_analysis.json")))
        time.sleep(0.2)
    offdir = EVID / "official_session_details"
    offdir.mkdir(parents=True, exist_ok=True)
    inv = pd.read_csv(REPO / "v4_team_normalized/output/phase4e/source_inventory.csv", low_memory=False)
    need = inv[inv.source_id.str.startswith("INDYCAR_SESSION_DETAILS_") & (inv.local.astype(str) == "False")]
    for r in need.itertuples(index=False):
        sid = int(r.official_session_id)
        rows.append(dict(source_set="INDYCAR_SESSION_DETAILS", source_id=r.source_id, year=int(r.year), session=r.session,
                         **fetch(f"https://www.indycar.com/api/results/EventsSessionDetails?id={sid}", offdir / f"{int(r.year)}_session_{sid}_raw.json")))
        time.sleep(0.5)
    man = pd.DataFrame(rows)
    man.to_csv(EVID / "retrieval_manifest.csv", index=False)
    print(man.groupby(["source_set"]).agg(files=("url", "size"), ok=("error", lambda s: int((s == "").sum())), mb=("bytes", lambda s: round(s.sum() / 1e6, 2))))
    print(man[man.error != ""][["source_id", "error"]].to_string())


if __name__ == "__main__":
    main()
