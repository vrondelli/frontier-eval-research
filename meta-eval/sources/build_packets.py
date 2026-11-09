"""Build source-bound reconstructed packets; never infer author prompts from solver prompts."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[4]
BASE=Path(__file__).resolve().parents[1]
if (BASE/'FREEZE.json').exists():raise SystemExit('Refusing packet rebuild after FREEZE.json; create a successor cut.')
HACK=ROOT/'research/hackathon'
FRONT=HACK/'frontier-hunt-20261106'
records=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf8')
def copy(src,dst):
 if src.is_dir():
  for p in src.rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts:copy(p,dst/p.relative_to(src))
 else:
  dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
  records.append({'source':str(src.relative_to(ROOT)).replace('\\','/'),'destination':str(dst.relative_to(BASE)).replace('\\','/'),'sha256':sha(src),'bytes':src.stat().st_size,'exposure':'author_public_input'})
jobs={
 'H1':('Build an evaluation for the ledger-admission task in input/E1.md.',[(HACK/'ten-task-benchmark-v1/questions/E1.md','E1.md'),(HACK/'ten-task-benchmark-v1/README.md','README.md')]),
 'H2':('Build an evaluation for the scoring-criteria task described in input/task.txt.',[(FRONT/'lane6-criteria-gaming/prompt.txt','task.txt'),(FRONT/'lane6-criteria-gaming/calibration','workspace')]),
 'H3':('Build an evaluation for the intake-time prediction task described in input/task.txt.',[(FRONT/'round3/temporal-leakage/prompt.txt','task.txt'),(FRONT/'round3/temporal-leakage/workspace_template','workspace')]),
 'H4':('Build an evaluation for the ferry-settlement task described in input/task.txt.',[(FRONT/'round10/v6-common-mode/prompt.txt','task.txt'),(FRONT/'round10/v6-common-mode/workspace_template','workspace')]),
 'H5':('Build an evaluation for the analytical query-engine task described in input/task.txt.',[(FRONT/'confirmation-candidates-20261108/g1f-query-optimizer/tasks/inventory-reservations-fresh-01/prompt.txt','task.txt'),(FRONT/'confirmation-candidates-20261108/g1f-query-optimizer/tasks/inventory-reservations-fresh-01/workspace_template','workspace')]),
 'H6':('Build an evaluation for the numeric export CLI task described in input/task.txt.',[(FRONT/'numeric-ambiguity-20261108/na01-runtime-numeric/prompts/warehouse-main-1.txt','task.txt'),(FRONT/'numeric-ambiguity-20261108/na01-runtime-numeric/templates/warehouse-main-1','workspace')]),
 'H7':('Build an evaluation for the report-extraction task described in input/task.txt.',[(FRONT/'round13/dh19-field-evidence/prompts/seal-inspection-main-1.txt','task.txt'),(FRONT/'round13/dh19-field-evidence/templates/seal-inspection-main-1','workspace')]),
 'H8':('Build an audit of the stored architecture-study sessions and snapshots represented in input/. Report the evidence coverage and any missing or inconsistent records.',[]),
 'H9':('Audit the Round-10 experiment evidence in input/ and write the research results and conclusions.',[])
}
provs=[]
for ident,(objective,inputs) in jobs.items():
 packet=BASE/'packets/primary'/ident;packet.mkdir(parents=True,exist_ok=True)
 (packet/'prompt.md').write_text(objective+'\n',encoding='utf8')
 for src,rel in inputs:copy(src,packet/'input'/rel)
 prov={'case_id':ident,'condition_id':'minimal_reconstruction','instruction_status':'original_eval_author_instruction_not_recovered','author_instruction':objective,'author_instruction_sha256':sha(packet/'prompt.md'),'exact_instruction_replication':False,'basis':'Saved original subject-facing task and public workspace; original eval-author conversational instruction has not been recovered.','instruction_changes':'Minimal newly written authoring request; no quality checklist, retrospective defect hint, positive/negative-control instruction, or coached directive added.','owner_only_withheld':['original grader','original reference','private probes','saved candidate answers','audit findings and labels'],'source_material_kind':'original_public_solver_task_plus_reconstructed_authoring_request','tool_context':'Original eval-author tool exposure not established. Runner must record new exposure and cannot claim same-context replication.'}
 if ident in ['H8','H9']:prov['source_material_kind']='audit_objective_reconstruction_and_source_receipts';prov['basis']='Reconstructed original audit/synthesis objective; source files below supply historical evidence, not the old audit answer.'
 write(packet/'PROVENANCE.json',prov);provs.append(prov)
# H8: source native session receipts and actual layout, without old audit answers.
arch=HACK/'architecture-oracle-validity-experiments-20261102';p8=BASE/'packets/primary/H8/input'
for p in arch.glob('NATIVE-*.json'):copy(p,p8/p.name)
for p in (arch/'r3').glob('NATIVE-*.json'):copy(p,p8/'r3'/p.name)
layout=[]
for runroot in [arch/'runs',arch/'r3/runs']:
 if not runroot.exists():continue
 for folder in runroot.iterdir():
  if not folder.is_dir():continue
  ep=folder/'episode.json'
  if ep.exists():copy(ep,p8/ep.relative_to(arch))
  stages=folder/'stages'
  candidates=[]
  if stages.exists():
   for st in stages.iterdir():
    if st.is_dir():candidates.extend([st,st/'snapshot'])
  candidates.append(folder/'final')
  for snap in candidates:
   m=snap/'manifest.json'
   if m.exists():
    copy(m,p8/m.relative_to(arch));layout.append({'root':str(snap.relative_to(arch)).replace('\\','/'),'workspace_exists':(snap/'workspace').is_dir(),'manifest_source_sha256':sha(m)})
write(p8/'snapshot-layout.json',{'reconstruction_notice':'Snapshot manifests copied byte-for-byte; workspace file bodies omitted. This packet tests discovery/accounting only and cannot support byte-integrity claims.','source_layout':layout})
# H9: raw per-episode grades, process receipts, finals and metadata. Do not copy syntheses.
p9=BASE/'packets/primary/H9/input'
files=subprocess.check_output(['rg','--files',str(FRONT/'round10')],text=True).splitlines()
for raw in files:
 p=Path(raw)
 if 'episodes' in p.parts and p.name in {'grade.txt','process.txt','last-message.txt','log.txt.meta','log.txt'}:
  copy(p,p9/p.relative_to(FRONT/'round10'))
# All actual copied source identities, plus packet-local generated files.
for ident in jobs:
 packet=BASE/'packets/primary'/ident
 local=[{'path':str(p.relative_to(packet)).replace('\\','/'),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(packet.rglob('*')) if p.is_file() and p.name!='MANIFEST.json']
 write(packet/'MANIFEST.json',{'case_id':ident,'condition_id':'minimal_reconstruction','files':local,'source_bindings':[r for r in records if r['destination'].startswith('packets/primary/'+ident+'/')]})
write(BASE/'sources/SOURCE-MANIFEST.json',{'generated_utc':datetime.now(timezone.utc).isoformat(),'source_files':records,'source_count':len(records),'total_bytes':sum(r['bytes'] for r in records),'original_evidence_modified':False})
write(BASE/'sources/INSTRUCTION-PROVENANCE.json',{'generated_utc':datetime.now(timezone.utc).isoformat(),'cases':provs,'exact_authoring_instructions_verified':0,'minimal_reconstructions':9,'recovery_scope':'Inspected saved DESIGN, task prompt and public-workspace artifacts. Subject-facing prompts are not promoted into original eval-authoring instructions. Broad session-archive recovery remains uncompleted; no claim of absence.','formal_claim_limit':'All nine current packets are reconstructed authoring conditions, not exact historical instruction replications.'})
print(json.dumps({'packets':len(provs),'source_files':len(records),'bytes':sum(r['bytes'] for r in records),'exact':0,'reconstructed':9}))
if (BASE/'sources/recover_h2_exact.py').exists():subprocess.run([sys.executable,str(BASE/'sources/recover_h2_exact.py')],check=True)
