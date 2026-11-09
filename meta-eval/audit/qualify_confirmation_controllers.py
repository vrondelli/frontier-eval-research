import datetime,hashlib,importlib.util,json,pathlib,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1];rows=[]
for name in ['run_confirmation_v2.py','run_confirmation_h6_v2.py']:
 spec=importlib.util.spec_from_file_location(name[:-3],ROOT/name);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 with tempfile.TemporaryDirectory(prefix='confirmation-controller-gate-')as folder:
  module.ROOT=pathlib.Path(folder)
  def fail(job):raise RuntimeError('synthetic controller gate')
  module.run=fail;receipt=module.safe_run(('fixture-model','H1',1,2))
  expected=module.ROOT/'runs/confirmation/fixture-model/H1/draw2/runtime-error.json'
  assert expected.exists()and receipt['status']=='runtime_error'and not(module.ROOT/'runs/screen').exists()
  rows.append({'script':name,'sha256':hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),'four_tuple_error_handler':'pass','correct_draw_receipt_path':True,'model_calls':0})
value={'amended_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'old_waiter_pids':[24308,34464],'old_waiters_stopped_after_verified_no_children':True,'confirmation_artifacts_before_amendment':False,'actor_attempts_restarted':0,'screen_controller_unchanged':True,'old_controller_files_preserved':True,'qualification':rows,'reason':'Original copied safe_run used three-value unpack and screen error path; new controllers preserve per-draw confirmation errors.'}
(ROOT/'audit/CONFIRMATION-CONTROLLER-AMENDMENT.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'controllers_qualified':len(rows),'model_calls':0}))
