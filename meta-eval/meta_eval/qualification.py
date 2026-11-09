"""Good/broken eval calibration with owner expectations outside subject processes."""
import json
from pathlib import Path
from .core import CHECKS, dump, inventory
from .generic import run_manifest
from .runtime import docker_command, execute_isolated


def native_call(module, expression):
    return "import importlib.util,json\ns=importlib.util.spec_from_file_location('subject_module','/subject/"+module+".py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);value="+expression+";print(json.dumps({'value':value}))"


def qualify(root, output, image):
    output=output.resolve();output.mkdir(parents=True,exist_ok=True);fixtures=output/'fixtures';rows=[]
    canary=output/'private-owner-canary.txt';canary.write_text('controlled synthetic owner-only canary\n')
    modes=['good_add','good_inverse','always_pass','always_fail','wrong_reference','common_mode_bug','hidden_rule','scope_deleted','fake_runner','false_measurement','false_report','outer_frame_tamper']
    for mode in modes:
        package=fixtures/mode;package.mkdir(parents=True,exist_ok=True)
        task='Given integers a and b, accept an answer equal to their mathematical sum. Return a boolean.'
        grader="def grade(c):\n return type(c['answer'])is int and c['answer']==c['a']+c['b']\n"
        if mode=='good_inverse':grader="def grade(c):\n return type(c['answer'])is int and c['answer']-c['a']==c['b']\n"
        if mode=='always_pass':grader='def grade(c):\n return True\n'
        if mode=='always_fail':grader='def grade(c):\n return False\n'
        if mode=='common_mode_bug':grader="def grade(c):\n return c['answer']==c['a']+c['b']+1\n"
        if mode=='hidden_rule':grader="def grade(c):\n return c.get('secret_tag')=='yes' and c['answer']==c['a']+c['b']\n"
        if mode=='outer_frame_tamper':grader="def grade(c):\n import inspect\n for frame in inspect.stack():\n  if 'checks'in frame.frame.f_locals:frame.frame.f_locals['checks'].clear()\n return True\n"
        if mode=='scope_deleted':task='Return a label.'
        reference='def solve(a,b):\n return a+b\n'if mode not in ['wrong_reference','common_mode_bug']else'def solve(a,b):\n return a+b+1\n'
        (package/'TASK.md').write_text(task);(package/'grader.py').write_text(grader);(package/'reference.py').write_text(reference)
        controls=[{'candidate':{'a':2,'b':3,'answer':5},'expected':True},{'candidate':{'a':2,'b':3,'answer':6},'expected':False}]
        dump(package/'controls.json',controls)
        runner="import json\nfrom pathlib import Path\nfrom grader import grade\nc=json.loads(Path(__file__).with_name('controls.json').read_text());print(json.dumps({'results':[grade(x['candidate'])for x in c]}))\n"
        if mode=='fake_runner':runner="import json\nprint(json.dumps({'results':[False,True]}))\n"
        (package/'runner.py').write_text(runner)
        dump(package/'report.json',{'controls_executed':999 if mode=='false_measurement'else 2,'correct_control_verdicts':999 if mode=='false_report'else 2,'all_controls_correct':True})
        candidates=[('baseline',{'a':2,'b':3,'answer':5}),('alternative',{'a':-7,'b':7,'answer':0}),('fault',{'a':2,'b':3,'answer':6}),('sibling',{'a':-7,'b':7,'answer':1}),('own_positive',controls[0]['candidate']),('own_negative',controls[1]['candidate'])]
        jobs=[{'id':name,'code':native_call('grader','m.grade('+repr(c)+')')}for name,c in candidates]
        jobs.extend([{'id':'reference_core','code':native_call('reference','m.solve(2,3)')},{'id':'reference_boundary','code':native_call('reference','m.solve(-7,7)')},
          {'id':'runner','code':"import json,subprocess,sys\np=subprocess.run([sys.executable,'-B','/subject/runner.py'],capture_output=True,text=True,timeout=5);print(json.dumps({'value':json.loads(p.stdout)['results']}))"},
          {'id':'sandbox','code':"import json\nfrom pathlib import Path\nprint(json.dumps({'value':Path("+repr(str(canary))+').exists()}))'}])
        def aggregate(identifier,operation,**kwargs):jobs.append({'id':identifier,'kind':'aggregate','operation':operation,**kwargs})
        aggregate('grader_invoked','observations_valid',observations=['baseline','alternative','fault','sibling'])
        aggregate('runner_consistent','runner_matches',observations=['own_positive','own_negative'],runner='runner')
        aggregate('task_fidelity','text_contains',file='TASK.md',required=['a','b','answer','integers','sum'])
        aggregate('rule_public','token_exposure',code_file='grader.py',public_file='TASK.md',token='secret_tag')
        aggregate('own_executed','observations_valid',observations=['own_positive','own_negative'])
        aggregate('own_labels_correct','labels_match',observations=['own_positive','own_negative'],labels=[True,False])
        for identifier,metric,field in [('measurement','count','controls_executed'),('numeric_claim','correct_count','correct_control_verdicts'),('conclusion','all_correct','all_controls_correct')]:
            aggregate(identifier,'report_matches',observations=['own_positive','own_negative'],labels=[True,False],file='report.json',metric=metric,field=field)
        mappings={'A1':('grader_invoked',True),'A2':('runner_consistent',True),'B1':('task_fidelity',True),'B2':('rule_public',True),'C1':('reference_core',5),'C2':('reference_boundary',0),'D1':('baseline',True),'D2':('alternative',True),'E1':('fault',False),'E2':('sibling',False),'F1':('sandbox',False),'F2':('measurement',True),'G1':('own_executed',True),'G2':('own_labels_correct',True),'H1':('numeric_claim',True),'H2':('conclusion',True)}
        manifest={'schema_version':'meta-eval-owner-manifest/v1','package_hashes':inventory(package),'owner_qualification_complete':False,'jobs':jobs,'checks':[{'id':key,'job':mappings[key][0],'pointer':'/value','expected':mappings[key][1],'obligation':'Explicit synthetic calibration: '+description}for key,_,description in CHECKS]}
        manifest_path=fixtures/(mode+'-owner-manifest.json');dump(manifest_path,manifest)
        scored=run_manifest(root,package,manifest_path,output/'executions'/mode,image,calibration=True)
        failed={c['id']for c in scored['checks']if c['status']=='fail'}
        target={'always_pass':'E1','always_fail':'D1','wrong_reference':'C1','common_mode_bug':'C1','hidden_rule':'B2','scope_deleted':'B1','fake_runner':'A2','false_measurement':'F2','false_report':'H1','outer_frame_tamper':'E1'}.get(mode)
        passed=not failed and scored['scoring']['score_interval']==[100,100]if target is None else target in failed and bool(scored['scoring']['critical_failures'])
        rows.append({'fixture':mode,'expected_target_failure':target,'observed_failures':sorted(failed),'score_interval':scored['scoring']['score_interval'],'calibration_passed':passed});print(json.dumps(rows[-1]),flush=True)
    domain_rows=[]
    from .engine import ensure_controls
    ensure_controls(root)
    for task,path,expected in [('H1','owner/cases/H1/correct_accepted.json',True),('H1','meta_eval/controls/H1/wrong_B_reply_v2.json',False),('H6','owner/cases/H6/saved_luna_decimal.json',False)]:
        code="import json,runpy\nm=runpy.run_path('/checker.py');c=json.load(open('/control.json'));ok,ev=m['CHECKS']["+repr(task)+"](c);print(json.dumps({'observed_pass':ok,'evidence':ev}))"
        receipt=execute_isolated(docker_command([(root/'owner/check_cases.py','/checker.py'),(root/path,'/control.json')],code,image),root,60)
        actual=(receipt.get('decoded')or{}).get('observed_pass');domain_rows.append({'task':task,'control':path,'expected_pass':expected,'observed_pass':actual,'qualified':actual is expected});dump(output/(task+'-'+Path(path).stem+'.json'),receipt)
    result={'schema_version':'meta-eval-executable-calibration/v2','model_calls':0,'all_passed':all(r['calibration_passed']for r in rows)and all(r['qualified']for r in domain_rows),'fixtures':rows,'domain_control_qualification':domain_rows,'comparison_boundary':'Owner expected values and aggregate score checks remain in host process. Subject modules receive one candidate/input at a time in isolated child containers.','scope':'Framework and finite detector calibration, not full seven-domain oracle or human-review certification.'}
    dump(output/'QUALIFICATION.json',result);return 0 if result['all_passed']else 1
