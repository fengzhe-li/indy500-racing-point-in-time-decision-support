"""Read-only canonical audit; writes only Explorer artifacts. No V5 imports."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / 'data/canonical/v1'
FILES = ['attempts.csv', 'attempt_laps.csv', 'qualifying_events.csv',
         'field_evidence_links.csv', 'evidence_items.csv', 'sources.csv', 'attempt_sections.csv']

def read(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def positive(value):
    try:
        number = float(value)
        return number if math.isfinite(number) and number > 0 else None
    except (ValueError, TypeError):
        return None

def exclusion(attempt, laps):
    """Result validity is independent of knowledge of chronological attempt order."""
    if attempt['result_status'] != 'VALID_RETAINED':
        return 'status_' + attempt['result_status'].lower()
    if attempt['attempt_class'] != 'A_COMPLETE':
        return 'not_complete_attempt'
    if len(laps) != 4 or {l['lap_number'] for l in laps} != {'1', '2', '3', '4'}:
        return 'missing_or_duplicate_lap_number'
    if any(l['lap_completion_status'] != 'COMPLETE' for l in laps):
        return 'incomplete_lap'
    if any(positive(l['lap_time_seconds']) is None or positive(l['lap_speed_mph']) is None for l in laps):
        return 'invalid_lap_timing'
    total, speed = positive(attempt['four_lap_total_seconds']), positive(attempt['four_lap_average_speed_mph'])
    if total is None or speed is None:
        return 'invalid_aggregate_timing'
    if abs(sum(float(l['lap_time_seconds']) for l in laps) - total) > .0005:
        return 'inconsistent_total_time'
    if abs(36000 / total - speed) > .001:
        return 'inconsistent_aggregate_speed'
    if any(abs(9000 / float(l['lap_time_seconds']) - float(l['lap_speed_mph'])) > .001 for l in laps):
        return 'inconsistent_lap_speed'
    return None

def build():
    tables = {name: read(CANONICAL / name) for name in FILES}
    attempts, laps = tables['attempts.csv'], tables['attempt_laps.csv']
    ids = [a['attempt_id'] for a in attempts]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate attempt IDs')
    lap_ids = [l['attempt_lap_id'] for l in laps]
    if len(lap_ids) != len(set(lap_ids)):
        raise ValueError('Duplicate lap IDs')
    grouped = defaultdict(list)
    for lap in laps:
        if lap['attempt_id'] not in set(ids):
            raise ValueError('Orphan lap join')
        grouped[lap['attempt_id']].append(lap)
    events = {e['session_id']: e for e in tables['qualifying_events.csv']}
    evidence = {e['evidence_item_id']: e for e in tables['evidence_items.csv']}
    links = defaultdict(list)
    for link in tables['field_evidence_links.csv']:
        links[(link['entity_table'], link['entity_id'], link['field_name'])].append(link)
    panel = read(ROOT / 'r4/output/r4p1_attempt_four_lap_panel_v1.csv')
    if set(ids) != {p['attempt_id'] for p in panel}:
        raise ValueError('r4p1 / canonical attempt ID mismatch')
    old = json.loads((ROOT / 'performance_explorer/contracts/historical-selection-f15a323.json').read_text())
    old_ids = set(old['attemptIds'])
    rows, ledger = [], []
    for attempt in attempts:
        event = events[attempt['session_id']]
        if event['session_id'] != f"INDY500_DAY1_{event['year']}":
            raise ValueError('Unexpected session: explicit selection policy required')
        attempt_laps = grouped[attempt['attempt_id']]
        reason = exclusion(attempt, attempt_laps)
        v5 = (sum(l['lap_completion_status'] == 'COMPLETE' for l in attempt_laps) == 4
              and positive(attempt['four_lap_total_seconds']) is not None
              and positive(attempt['four_lap_average_speed_mph']) is not None)
        ledger.append(dict(year=int(event['year']), attempt_id=attempt['attempt_id'],
                           result_status=attempt['result_status'], source_locator=attempt['source_native_locator'],
                           v5_population=v5, old_explorer=attempt['attempt_id'] in old_ids,
                           missing_attempt_index=not attempt['car_attempt_index'], retained=reason is None,
                           exclusion_reason=reason or ''))
        if reason:
            continue
        attempt_laps.sort(key=lambda l: int(l['lap_number']))
        source_ids = set()
        for table, entity, field in [('ATTEMPTS',attempt['attempt_id'],'four_lap_total_seconds'),
                                     ('ATTEMPTS',attempt['attempt_id'],'four_lap_average_speed_mph')] + [
                                     ('ATTEMPT_LAPS',l['attempt_lap_id'],'lap_time_seconds') for l in attempt_laps]:
            raw = [link for link in links[(table,entity,field)] if link['value_classification']=='RAW_OBSERVED']
            if not raw:
                raise ValueError(f'No observed timing provenance for {entity} {field}')
            source_ids.update(evidence[link['evidence_item_id']]['source_id'] for link in raw)
        idx = attempt['car_attempt_index']
        if idx and (not positive(idx) or not float(idx).is_integer()):
            raise ValueError('Invalid attempt ordinal')
        rows.append(dict(year=int(event['year']), sessionId=attempt['session_id'],
                         attemptId=attempt['attempt_id'], carNumber=attempt['car_number'],
                         driver=attempt['driver_name'], team=attempt['team_name'],
                         attempt=int(float(idx)) if idx else None, attemptOrderQuality=attempt['car_attempt_order_quality'],
                         resultStatus=attempt['result_status'], sourceLocator=attempt['source_native_locator'],
                         averageSpeedMph=float(attempt['four_lap_average_speed_mph']),
                         totalSeconds=float(attempt['four_lap_total_seconds']),
                         lapTimesS=[float(l['lap_time_seconds']) for l in attempt_laps],
                         lapSpeedsMph=[float(l['lap_speed_mph']) for l in attempt_laps],
                         timingBasis='official_recorded_lap_duration', lapSpeedBasis='derived_from_recorded_lap_time',
                         source='data/canonical/v1/attempts.csv + attempt_laps.csv', sourceIds=sorted(source_ids)))
    rows.sort(key=lambda r:(r['year'],r['driver'],r['attempt'] or 0,r['attemptId']))
    if old_ids != {r['attemptId'] for r in rows if r['attempt'] is not None}:
        raise ValueError('Legacy selection discrepancy beyond the known attempt-order exclusion')
    yearly = []
    for year in sorted({l['year'] for l in ledger}):
        subset = [l for l in ledger if l['year']==year]
        counts = Counter(l['exclusion_reason'] for l in subset if not l['retained'])
        yearly.append(dict(year=year,source_rows=len(subset), r4p1_rows=sum(p['year']==str(year) for p in panel),
                           v5_complete=sum(l['v5_population'] for l in subset),
                           old_explorer=sum(l['old_explorer'] for l in subset),
                           retained_rows=sum(l['retained'] for l in subset),
                           recovered_unknown_order=sum(l['retained'] and l['missing_attempt_index'] for l in subset),
                           excluded_rows=sum(counts.values()), exclusions=dict(sorted(counts.items()))))
    sources = [{k:s[k] for k in ['source_id','source_uri','content_hash','evidence_quality']}
               for s in tables['sources.csv'] if s['source_id'] in {sid for r in rows for sid in r['sourceIds']}]
    manifest = {str((CANONICAL/f).relative_to(ROOT)):hashlib.sha256((CANONICAL/f).read_bytes()).hexdigest() for f in FILES}
    data = dict(schemaVersion='1.1.0',dataset='canonical-v1-retained-four-lap-attempts',
                dataKind='observed_official_timing_summary',sourceFile='data/canonical/v1/attempts.csv + attempt_laps.csv',
                recordCount=len(rows),sources=sources,sourceHashes=manifest,rows=rows)
    audit = dict(years=yearly,attempt_ids_unique=True,lap_ids_unique=True,orphan_laps=0,
                 r4p1_canonical_ids_equal=True,sourceHashes=manifest,
                 max_time_sum_error_s=max(abs(sum(r['lapTimesS'])-r['totalSeconds']) for r in rows))
    return data, audit, ledger

def artifacts():
    data,audit,ledger=build()
    def csv_text(rows):
        import io
        stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows);return stream.getvalue()
    return {
        'frontend/src/data/historical-attempts-v1.json':json.dumps(data,indent=2,ensure_ascii=False)+'\n',
        'audit/historical_audit.json':json.dumps(audit,indent=2)+'\n',
        'audit/historical_audit.csv':csv_text([{**r,'exclusions':json.dumps(r['exclusions'],sort_keys=True)} for r in audit['years']]),
        'audit/attempt_selection.csv':csv_text(ledger),
    }

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    for relative,text in artifacts().items():
        path=ROOT/'performance_explorer'/relative
        if args.check:
            if not path.exists() or path.read_bytes()!=text.encode():
                raise SystemExit(f'Stale generated artifact: {path}')
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(text.encode())
    print('Historical export and audit are current.' if args.check else 'Wrote historical export and audit.')
