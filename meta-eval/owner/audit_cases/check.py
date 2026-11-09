"""Independent semantic oracle for source-derived H8/H9 controls."""
import json
import sys
from pathlib import Path

def check(value):
    data, result = value['input'], value['candidate_response']
    if value['case_id']=='H8':
        paths=result.get('checked_paths',[])
        return (result.get('complete') is True and result.get('checked_count')==data['expected_turn_count']
                and len(paths)==len(set(paths))==len(data['expected_snapshot_paths'])
                and set(paths)==set(data['expected_snapshot_paths']))
    if value['case_id']=='H9':
        events=data['events']
        return (result.get('grader_invocations')==len(events) and
                result.get('grader_exit_1')==sum(e['grader_exit']==1 for e in events))
    raise ValueError('unsupported case')

if __name__=='__main__':
    value=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    print(json.dumps({'pass':check(value),'reason':'independent exact source-derived check'}))
