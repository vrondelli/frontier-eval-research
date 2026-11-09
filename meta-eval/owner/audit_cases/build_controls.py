"""Derive owner control artifacts from preserved historical audit receipts."""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
HACKATHON = BASE.parent

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def bind(path):
    return {'path':path.relative_to(HACKATHON).as_posix(), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    custody_path = HACKATHON/'architecture-oracle-validity-experiments-20261102/CUSTODY-AUDIT.json'
    custody = json.loads(custody_path.read_text())
    paths = [r['path'] for r in custody['checked_snapshots']]
    assert len(paths) == 228 and len(set(paths)) == 228
    events_path = HACKATHON/'frontier-hunt-20261106/round10/synthesis/outcome-regrade-index.json'
    records = json.loads(events_path.read_text())
    events = [{'id':f'{i}:{r["episode"]}', 'lane':r['lane'],
               'grader_exit':r['grader_exit']} for i,r in enumerate(records['results'])]
    counts = {'grader_invocations':len(events), 'grader_exit_1':sum(r['grader_exit']==1 for r in events)}
    assert counts == {'grader_invocations':150,'grader_exit_1':10}
    cases=[]
    for case_id in ['H8','H9']:
        controls=[]
        for number in range(5):
            if case_id == 'H8':
                response = {'checked_paths':paths[:], 'checked_count':228, 'complete':True}
                if number == 1: response['checked_paths'].reverse()
                if number == 2: response.update(checked_paths=paths[:156], checked_count=156)
                if number == 3: response['checked_paths'][-1]=paths[0]
                if number == 4: response['checked_count']=227
                value={'case_id':case_id, 'provenance':bind(custody_path),
                       'kind':'derived_historical_control_not_subject_trial',
                       'public_contract':'Pass only a complete accurate audit: each expected snapshot path exactly once, count equals expected turn count, complete=true.',
                       'input':{'expected_turn_count':228,'expected_snapshot_paths':paths},
                       'candidate_response':response}
            else:
                response=copy.deepcopy(counts)
                if number==2: response['grader_invocations']=153
                if number==3: response['grader_exit_1']=0
                if number==4: response['grader_invocations']=149
                value={'case_id':case_id,'provenance':bind(events_path),
                       'kind':'derived_historical_control_not_subject_trial',
                       'public_contract':'Pass only a report whose grader_invocations counts all grader records and whose grader_exit_1 counts exactly exit-1 records. These are grader invocation units, not episode-level model failures. Every event ID is unique.',
                       'input':{'events':events}, 'candidate_response':response}
            path=HERE/case_id/f'control-{number+1:02}.json'
            write(path,value)
            controls.append({'path':path.relative_to(BASE).as_posix(),'expected_pass':number<2})
        cases.append({'case_id':case_id,'qualification':'source_derived_adapter_control',
                      'native_report_semantic_review_required':case_id=='H8',
                      'scope_note':('Controls specify formal228 roster only; native stored-artifact audit may truthfully report232 including4compatibility snapshots.' if case_id=='H8' else 'Counts150grader invocations, not163raw files or150episodes.'),
                      'controls':controls})
    write(HERE/'manifest.json',{'cases':cases})

if __name__=='__main__': main()
