"""Read-only frozen-byte and initial actor exposure reconciliation."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    freeze=json.loads((ROOT/'FREEZE.json').read_text())
    mismatches=[]
    for path,expected in freeze['files'].items():
        p=ROOT/path
        if not p.is_file() or digest(p)!=expected:mismatches.append(path)
    exposure=[]
    for receipt_path in (ROOT/'runs/screen').glob('*/*/launch.json'):
        receipt=json.loads(receipt_path.read_text())
        case=receipt['case_id'];packet=ROOT/'packets/primary'/case
        expected={p.relative_to(packet).as_posix():digest(p)for p in packet.rglob('*')if p.is_file()and not p.is_symlink()}
        actual=receipt['input_inventory']
        exposure.append({'case_id':case,'model':receipt['model_requested'],
                         'matches_frozen_public_packet':actual==expected,
                         'unexpected_paths':sorted(set(actual)-set(expected)),
                         'missing_paths':sorted(set(expected)-set(actual)),
                         'differing_paths':sorted(k for k in set(actual)&set(expected)if actual[k]!=expected[k]),
                         'owner_payload_paths':[p for p in actual if p.startswith('owner/')or p.startswith('grades/')],
                         'source_only_copy_is_not_universal_read_isolation':True})
    report={'schema_version':'eval-author-freeze-review/v1','frozen_files_checked':len(freeze['files']),
            'frozen_byte_mismatches':mismatches,'actor_initial_exposure':exposure,
            'all_initial_copies_match':all(x['matches_frozen_public_packet']for x in exposure),
            'generation_boundary_scope':'Independent known-owner-UNC sentinel probe denied access; arbitrary host paths not proved.',
            'model_calls':0}
    out=ROOT/'grades/audit-review/FREEZE-EXPOSURE-REVIEW.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'frozen_files':len(freeze['files']),'mismatches':mismatches,
                      'launched':len(exposure),'all_initial_copies_match':report['all_initial_copies_match']}))
if __name__=='__main__':main()
