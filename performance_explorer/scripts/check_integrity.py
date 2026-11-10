"""Read-only frozen/hash audit. Writes a report only beneath performance_explorer."""
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V4_REF = 'fe65ddf73a4de6b9c645de74830c8db7b88d64cb'
BASE = 'f15a323199a56fe7130ebf0db97c954787bbd90b'
MAIN_REF = 'de49616eda74224e1f07475c24e40eb6b9486f58'

def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)

def file_checks(entries):
    mismatches=[]
    for path,expected in entries:
        file=ROOT/path
        actual=hashlib.sha256(file.read_bytes()).hexdigest() if file.exists() else None
        if actual != expected:
            baseline=subprocess.run(['git','show',f'{BASE}:{path}'],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
            mismatches.append({'path':path,'expected':expected,'actual':actual,
                               'unchanged_since_original_explorer':file.exists() and baseline.returncode==0 and baseline.stdout==file.read_bytes()})
    return dict(checked=len(entries),matched=len(entries)-len(mismatches),mismatches=mismatches)

def main():
    manifest=json.loads((ROOT/'weather/output/final_integration/indy500_final_v2_freeze_manifest.json').read_text())
    report={'v2_final_manifest':file_checks([(r['path'],r['sha256']) for r in manifest['artifacts'].values()])}
    lines=(ROOT/'v3_point_in_time/output/qa/v2_pre_implementation_hashes.txt').read_text().splitlines()
    report['v2_pre_implementation']=file_checks([(line.split('  ',1)[1],line.split('  ',1)[0]) for line in lines if line.strip()])
    for phase in [2,3,4]:
        path=ROOT/f'v3_point_in_time/output/phase{phase}_freeze/phase{phase}_hashes.csv'
        entries=list(csv.DictReader(path.open()))
        report[f'v3_phase{phase}']=file_checks([(
            'v3_point_in_time/output/phase2_freeze/phase2_case_table.csv' if r['path']=='phase2_case_table.csv (frozen copy)' else r['path'],
            r['sha256']) for r in entries])
    # Verify V4 against committed objects on the verified target-main history.
    # It is not materialized on this older feature base and is never checked out or modified.
    v4_manifest='v4_team_normalized/output/phase4l/v4_final_manifest.csv'
    entries=list(csv.DictReader(io.StringIO(git('show',f'{V4_REF}:{v4_manifest}').decode())))
    refs=''.join(f"{V4_REF}:{r['relative_path']}\n" for r in entries)
    stream=io.BytesIO(subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=refs.encode(),stdout=subprocess.PIPE,check=True).stdout)
    mismatches=[]
    for r in entries:
        header=stream.readline().decode().split();size=int(header[2]);blob=stream.read(size);stream.read(1)
        actual=hashlib.sha256(blob).hexdigest()
        if actual!=r['sha256']:mismatches.append({'path':r['relative_path'],'expected':r['sha256'],'actual':actual,'existing_in_verified_main':True})
    report['v4_target_main_manifest']=dict(ref=V4_REF,checked=len(entries),matched=len(entries)-len(mismatches),mismatches=mismatches)
    # Every non-Explorer tracked file must equal the merged main baseline (except Explorer's own workflow).
    tree=git('ls-tree','-rz',MAIN_REF).split(b'\0');checked=0;changed=[]
    for item in tree:
        if not item:continue
        metadata,raw_path=item.split(b'\t',1);path=raw_path.decode();sha=metadata.decode().split()[2]
        if path.startswith('performance_explorer/'):continue
        file=ROOT/path
        if not file.exists():changed.append(path);continue
        blob=file.read_bytes();actual=hashlib.sha1(f'blob {len(blob)}\0'.encode()+blob).hexdigest();checked+=1
        if sha!=actual:changed.append(path)
    report['non_explorer_worktree']=dict(baseline=MAIN_REF,checked=checked,changed=changed)
    source=json.loads((ROOT/'performance_explorer/contracts/v5-replay-1/SOURCE.json').read_text())
    report['v5_pinned_artifacts']=file_checks([('performance_explorer/'+p,r['sha256']) for p,r in source['files'].items()])
    v6source=json.loads((ROOT/'performance_explorer/contracts/v6-replay-2/SOURCE.json').read_text())
    report['v6_pinned_artifacts']=file_checks([('performance_explorer/'+p,r['sha256']) for p,r in v6source['files'].items()])
    (ROOT/'performance_explorer/audit/frozen_integrity.json').write_text(json.dumps(report,indent=2)+'\n')
    for name,result in report.items():print(name,json.dumps(result))
    if changed or any(r['mismatches'] for k,r in report.items() if k!='non_explorer_worktree'):
        raise SystemExit(1)
if __name__=='__main__':main()
