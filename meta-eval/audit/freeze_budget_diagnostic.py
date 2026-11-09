import datetime,hashlib,importlib.util,json,pathlib,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1];script=ROOT/'run_h1_budget_diagnostic.py'
spec=importlib.util.spec_from_file_location('budget_controller',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
with tempfile.TemporaryDirectory(prefix='budget-controller-gate-')as folder:
 module.ROOT=pathlib.Path(folder)
 def fail(job):raise RuntimeError('synthetic budget controller gate')
 module.run=fail;result=module.safe_run(('fixture-model','H1',1200,2))
 assert result['status']=='runtime_error'and(module.ROOT/'runs/budget-diagnostic/fixture-model/H1/draw2/runtime-error.json').exists()
files=['run_h1_budget_diagnostic.py','protocol/H1-BUDGET-DIAGNOSTIC-ADMISSION.json','packets/primary/H1/prompt.md','packets/primary/H1/MANIFEST.json']
record={'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'condition':'post_screen_budget_diagnostic_1200s','draws':3,'model':'gpt-6.1-sol','case':'H1','four_tuple_error_gate':'pass','model_calls_in_gate':0,'files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in files}}
target=ROOT/'H1-BUDGET-DIAGNOSTIC-FREEZE.json'
if target.exists():raise SystemExit('Refusing overwrite')
target.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'frozen_files':len(files),'gate':'pass'}))
