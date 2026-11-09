"""Current owner scoring successor: honor adjudications; preserve frozen runtime."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import run_eval as frozen

ROOT=Path(__file__).resolve().parent

def validate_package(path):
    path=Path(path)
    if path.is_symlink()or any(p.is_symlink()for p in path.rglob('*')):
        raise ValueError('Delivered package symlink refused before any copy or container mount')

def security_self_check(output):
    with tempfile.TemporaryDirectory(prefix='eval-current-security-')as tmp:
        tmp=Path(tmp);owner=tmp/'owner-marker';owner.write_text('harmless owner sentinel')
        package=tmp/'subject';package.mkdir();(package/'escape-link').symlink_to(owner)
        try:validate_package(package);symlink_refused=False
        except ValueError:symlink_refused=True
        root_link=tmp/'subject-link';root_link.symlink_to(package,target_is_directory=True)
        try:validate_package(root_link);root_symlink_refused=False
        except ValueError:root_symlink_refused=True
        try:frozen.materialize({'case_id':'H5','files':{'../escape.py':'print(1)'}},tmp/'candidate');traversal_refused=False
        except ValueError:traversal_refused=True
        result={'model_calls':0,'symlink_refused':symlink_refused,'root_symlink_refused':root_symlink_refused,
                'materialized_path_traversal_refused':traversal_refused,'owner_marker_unchanged':owner.read_text()=='harmless owner sentinel'}
        frozen.dump(output,result)
        print(json.dumps(result));return 0 if all(result[k]for k in result if k!='model_calls')else 1

def option(name):
    if name in sys.argv:
        index=sys.argv.index(name)
        if index+1>=len(sys.argv):raise ValueError(name+' requires a value')
        value=sys.argv[index+1];del sys.argv[index:index+2];return value
    return None

def main():
    if '--security-self-check'in sys.argv:
        output=Path(sys.argv[sys.argv.index('--output')+1]);return security_self_check(output)
    successor_path=option('--successor-controls')
    writable_copy='--writable-disposable-copy'in sys.argv
    if writable_copy:sys.argv.remove('--writable-disposable-copy')
    original_execute=frozen.execute
    def execute(command,*args,**kwargs):
        if writable_copy and command and command[0]=='docker':
            for part in command:
                if isinstance(part,str)and part.startswith('type=bind,source=')and ',target=/subject'in part:
                    source=Path(part.split('source=',1)[1].split(',target=',1)[0])
                    if source.name!='subject'or not source.parent.name.startswith('eval-author-score-'):
                        raise ValueError('Writable subject mount must be the disposable runtime copy')
                    source.chmod(0o777)
                    for p in source.rglob('*'):p.chmod(0o777 if p.is_dir()else 0o666)
            command=[part.replace(',target=/subject,readonly',',target=/subject')if isinstance(part,str)else part for part in command]
        return original_execute(command,*args,**kwargs)
    frozen.execute=execute
    scoring='score'in sys.argv
    output=Path(sys.argv[sys.argv.index('--output')+1])if '--output'in sys.argv else None
    if scoring and '--package'in sys.argv:
        try:validate_package(sys.argv[sys.argv.index('--package')+1])
        except ValueError as error:
            if output:frozen.dump(output,{'status':'unqualified','formal_eligible':False,'reason':str(error)})
            return 2
    adjudication_path=ROOT/'owner/ADJUDICATION.json'
    if scoring and not adjudication_path.exists():
        if output:frozen.dump(output,{'status':'unqualified','formal_eligible':False,'reason':'Owner adjudication receipt unavailable'})
        return 2
    adjudication=json.loads(adjudication_path.read_text(encoding='utf-8'))if scoring else{}
    excluded=adjudication.get('excluded_controls',[])
    original_manifests=frozen.manifests
    adapter_supplied='--adapter'in sys.argv
    selected_case=sys.argv[sys.argv.index('--case')+1]if '--case'in sys.argv else None
    if scoring and adapter_supplied and selected_case in ['H8','H9']:
        frozen.dump(output,{'status':'semantic_review_required','formal_eligible':False,
                            'reason':'Native historical audit reports require staged-input semantic review; narrow JSON diagnostics are not full report gold.'})
        return 2
    def excluded_control(case,control):
        return any(item.get('case_id')==case['case_id']and
                   (item.get('control_id')==control.get('id')or item.get('path')==control.get('path'))
                   for item in excluded)
    def manifests():
        rows=[]
        for path,case in original_manifests():
            clone=copy.deepcopy(case)
            clone['controls']=[c for c in clone['controls']if not excluded_control(clone,c)]
            if adapter_supplied and clone['case_id']in['H8','H9']:clone['controls']=[]
            if clone['controls']:rows.append((path,clone))
        if successor_path:
            path=Path(successor_path).resolve();bank=json.loads(path.read_text(encoding='utf-8'))
            if bank.get('status')!='post_outcome_owner_correction':raise ValueError('Successor bank must disclose post-outcome status')
            controls=[]
            for index,c in enumerate(bank['cases']):
                controls.append({'id':'successor-'+str(index),'path':str((path.parent/c['path']).resolve()),'expected_pass':c['expected_pass']})
            rows.append((path,{'case_id':'H4','condition':'post_outcome_owner_correction','controls':controls}))
        return rows
    frozen.manifests=manifests
    original_materialize=frozen.materialize
    def materialize(value,destination):
        if value['case_id']=='H1':
            original_materialize(value,destination)
            answer=destination/'answer.json';document=json.loads(answer.read_text(encoding='utf-8'))
            document['explanation']='Owner-authored control artifact. Evaluate its behavior independently; this adapter text is not evidence of correctness.'
            answer.write_text(json.dumps(document),encoding='utf-8')
            return destination
        if value['case_id']!='H4':return original_materialize(value,destination)
        if not successor_path:raise ValueError('Initial H4 controls excluded from complete-task scoring; complete successor candidate required')
        public=ROOT/'packets/primary/H4/input/workspace'
        validate_package(public)
        shutil.copytree(public,destination)
        (destination/'fares.py').write_text(value['assets']['reference_fares.py'],encoding='utf-8')
        (destination/'test_fares.py').write_text(value['test_code'],encoding='utf-8')
        destination.chmod(0o755)
        for p in destination.rglob('*'):p.chmod(0o755 if p.is_dir()else 0o644)
        return destination
    frozen.materialize=materialize
    try:status=frozen.main()
    except ValueError as error:
        if output:frozen.dump(output,{'status':'unqualified','reason':str(error),'formal_eligible':False,
                                     'excluded_owner_controls':excluded,
                                     'owner_adjudication_sha256':hashlib.sha256(adjudication_path.read_bytes()).hexdigest()})
        return 2
    if scoring and output and output.exists():
        result=json.loads(output.read_text(encoding='utf-8'))
        result['owner_adjudication_sha256']=hashlib.sha256(adjudication_path.read_bytes()).hexdigest()
        result['excluded_owner_controls']=excluded
        result['subject_disposable_copy_writable']=writable_copy
        coverage={}
        for check in result.get('checks',[]):
            case=check['case_id'];counts=coverage.setdefault(case,{'admitted_positive_controls':0,'admitted_negative_controls':0})
            counts['admitted_positive_controls'if check['expected_pass']else'admitted_negative_controls']+=1
        for case,counts in coverage.items():
            counts['both_control_directions_present']=counts['admitted_positive_controls']>0 and counts['admitted_negative_controls']>0
            counts['owner_case_policy']=adjudication.get('native_case_policy',{}).get(case,{})
        result['adjudicated_control_coverage']=coverage
        if coverage and not all(item['both_control_directions_present']for item in coverage.values()):
            result['status']='scored_partial_only'
            result['complete_eval_acceptance_decision']='unknown_missing_admitted_positive_or_negative_gold'
            if status==0:status=2
        result['owner_control_condition']='post_outcome_owner_correction'in str(successor_path)if successor_path else 'initial_bank_minus_adjudicated_exclusions'
        if successor_path:
            result['owner_control_condition']='explicit_post_outcome_owner_correction'
            result['successor_bank_sha256']=hashlib.sha256(Path(successor_path).read_bytes()).hexdigest()
        frozen.dump(output,result)
    return status

if __name__=='__main__':raise SystemExit(main())
