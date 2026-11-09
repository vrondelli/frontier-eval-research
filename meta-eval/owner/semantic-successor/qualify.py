import json,re,hashlib,csv,shutil,subprocess,datetime
from pathlib import Path
HERE=Path(__file__).resolve().parent;BASE=HERE.parents[1]
def h2(text):
 headings=re.findall(r'^## (.+)$',text,re.M);required=['Checks','Score mapping','Worked examples','Failure modes'];ordered=[h for h in headings if h in required]
 weights={int(m[0]):int(m[1])for m in re.findall(r'^\d+\.\s+\*\*C(\d+).*?(\d+) point',text,re.M)}
 ranges=[tuple(map(int,m))for m in re.findall(r'^\|\s*(\d+)\s*[-–]\s*(\d+)\s*\|\s*([0-3])\s*\|',text,re.M)]
 mapping={};overlap=False
 for lo,hi,score in ranges:
  for point in range(lo,hi+1):overlap=overlap or point in mapping;mapping[point]=score
 mapping_ok=bool(weights)and not overlap and all(x in mapping for x in range(sum(weights.values())+1))
 assigned={};declared_total=None;declared_scores=None
 for line in text.splitlines():
  if not line.startswith('|'):continue
  cells=[c.strip().replace('**','')for c in line.strip('|').split('|')]
  if len(cells)!=5:continue
  match=re.match(r'C(\d+)',cells[0])
  if match and all('YES'in c or'NO'in c for c in cells[1:]):assigned[int(match[1])]=['YES'in c for c in cells[1:]]
  if cells[0]=='Total':declared_total=[int(c)for c in cells[1:]]
  if cells[0]in ['Overall score','Score']:declared_scores=[int(c)for c in cells[1:]]
 actual=[sum(weights.get(k,0)*v[i]for k,v in assigned.items())for i in range(4)]
 return {'ordered_required_headings':ordered==required,'all_worked_checks':set(assigned)==set(weights)and bool(weights),'mapping_exhaustive_disjoint':mapping_ok,'worked_arithmetic':declared_total==actual,'worked_score_mapping':declared_scores is not None and all(mapping.get(t)==s for t,s in zip(actual,declared_scores)),'observed_totals':actual}
WRAPPER='''import json,subprocess,pathlib,sys
p=subprocess.run([sys.executable,sys.argv[1],'/work/owner_candidate','--output','/tmp/result.json'],text=True,capture_output=True,timeout=180)
q=pathlib.Path('/tmp/result.json')
print(json.dumps({'exit_code':p.returncode,'stderr':p.stderr,'result':json.loads(q.read_text())if q.exists()else None,'stdout':p.stdout if not q.exists()else ''}))
'''
def h3(c):
 delivery=BASE/c['source_delivery'];source=delivery/c['evaluator_relative_path'];assert hashlib.sha256(source.read_bytes()).hexdigest()==c['evaluator_sha256']
 workroot=HERE/'work';work=workroot/c['control_id'];work.mkdir(parents=True,exist_ok=False);shutil.copytree(delivery,work,dirs_exist_ok=True)
 try:
  file=work/c['evaluator_relative_path'];text=file.read_text(encoding='utf8');mutation=c['mutation']
  if mutation=='accuracy_floor':
   old='    # Small fresh-ID probes discourage simple historical-ID lookup.';assert old in text;text=text.replace(old,'    check("owner_added_quality_floor", result["metrics"].get("independent_holdout_accuracy", 0) >= .66, "Unlicensed mutant floor")\n'+old,1)
  elif mutation=='binary_check_removed':
   old='if any(r["prediction"] not in {"0", "1"} for r in outputs):';assert old in text;text=text.replace(old,'if False: # authored mutant omits binary validation',1)
  elif mutation=='manual_gate_removed':
   old='result["status"] = "fail" if any(not c["passed"] for c in result["checks"]) else "needs_review"';assert old in text;text=text.replace(old,'result["status"] = "fail" if any(not c["passed"] for c in result["checks"]) else "pass"',1)
  file.write_text(text,encoding='utf8')
  candidate=work/'owner_candidate';candidate.mkdir();ref=BASE/'runs/screen/gpt-6-astra/H3/delivery/reference'
  for name in ['pipeline.py','features.txt','REPORT.md']:shutil.copyfile(ref/name,candidate/name)
  if c['candidate']=='invalid_binary':(candidate/'pipeline.py').write_text('import csv,sys\nwith open(sys.argv[1],newline="") as f: rows=list(csv.DictReader(f))\nwith open(sys.argv[2],"w",newline="") as f:\n w=csv.writer(f);w.writerow(["id","prediction"]);w.writerows((r["id"],2)for r in rows)\n')
  if c['candidate']=='false_metric':
   p=candidate/'REPORT.md';p.write_text(p.read_text().replace('validation_accuracy: 0.604','validation_accuracy: 1.000',1))
  (work/'owner_wrapper.py').write_text(WRAPPER)
  linux='/home/vlad_/projects/engineer-assessment/'+work.resolve().relative_to(Path(r'\\wsl.localhost\Ubuntu-26.04\home\vlad_\projects\engineer-assessment')).as_posix()
  cmd=['wsl.exe','--distribution','Ubuntu-26.04','--user','vlad_','--exec','docker','run','--rm','--network','none','--read-only','--memory','512m','--cpus','1','--pids-limit','64','--tmpfs','/tmp:rw,noexec,nosuid,size=128m','-v',linux+':/work:rw','-w','/work','python:3.14-slim','python','/work/owner_wrapper.py','/work/'+c['evaluator_relative_path']]
  p=subprocess.run(cmd,text=True,capture_output=True,timeout=240)
  try:receipt=json.loads(p.stdout)
  except ValueError:return None,{'command':cmd,'docker_exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
  result=receipt.get('result')or{};machine_ok=bool(result.get('checks'))and all(x['passed']for x in result['checks'])
  if c['expected_conforms']:conforms=machine_ok and result.get('status')=='needs_review'
  elif mutation=='accuracy_floor':conforms=machine_ok
  elif mutation=='binary_check_removed':conforms=not machine_ok
  else:conforms=result.get('status')!='pass'
  return conforms,{'command':cmd,'docker_exit':p.returncode,'receipt':receipt,'source_code_sha256':c['evaluator_sha256'],'mutated_code_sha256':hashlib.sha256(text.encode()).hexdigest(),'machine_checks_all_pass':machine_ok,'overall_status':result.get('status'),'scope':'Component fidelity only; reviewed reference is safe authored fixture; no model calls or fullsystem acceptance.'}
 finally:
  assert work.resolve().is_relative_to(workroot.resolve());shutil.rmtree(work)
manifest=json.loads((HERE/'MANIFEST.json').read_text());rows=[]
for case in manifest['cases']:
 for name in case['controls']:
  c=json.loads((BASE/name).read_text(encoding='utf8'))
  try:
   if c['case_id']=='H2':ev=h2(c['text']);observed=all(v for k,v in ev.items()if k!='observed_totals')
   else:observed,ev=h3(c)
   rows.append({'case_id':c['case_id'],'control_id':c['control_id'],'expected_conforms':c['expected_conforms'],'observed_conforms':observed,'qualified':observed is c['expected_conforms'],'evidence':ev})
  except Exception as e:rows.append({'case_id':c['case_id'],'control_id':c['control_id'],'qualified':False,'error':repr(e)})
result={'condition':'post_outcome_semantic_control_successor','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_calls':0,'human_review':'pending','overall_native_eval_qualification':False,'all_component_controls_qualified':all(r['qualified']for r in rows),'receipts':rows}
(HERE/'QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps({'qualified':sum(r['qualified']for r in rows),'total':len(rows),'all_component_controls_qualified':result['all_component_controls_qualified']}))
