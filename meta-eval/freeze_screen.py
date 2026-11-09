"""Freeze an exploratory reconstructed-instruction screen after offline gates."""
import datetime,hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
def read(p):return json.loads((ROOT/p).read_text())
q=read('owner/cases/ROOT-LINUX-QUALIFICATION.json')
assert q['all_implemented_controls_qualified']
p=read('sources/PACKET-VALIDATION.json');assert p['status']=='pass'
s=read('owner/runtime/ISOLATED-SELF-CHECK.json');assert s['correct']==s['total'] and s['invalid']==0
files={}
for rel in ['packets/primary','owner/cases','owner/audit_cases','owner/runtime','protocol','sources']:
 for f in (ROOT/rel).rglob('*'):
  if f.is_file()and '__pycache__'not in f.parts and not f.is_symlink():files[f.relative_to(ROOT).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
for name in ['run_eval.py','run_screen.py','DESIGN.md']:
 files[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
record={'schema_version':'eval-author-screen-freeze/v1','frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'qualification':'exploratory_mixed_instruction_screen','exact_authoring_instruction_claim':'per_packet_only; H2 recovered text, full context differs','generation_owner_boundary':'known_owner_UNC_sentinel_denied; general_read_isolation_unproven','human_review':'pending','screen_policy':read('protocol/RUN-POLICY.json'),'implemented_control_gate':True,'source_custody_gate':True,'docker_runtime_gate':True,'unqualified_semantic_cases':['H2','H3','H8_native_report'],'files':files}
target=ROOT/'FREEZE.json'
if target.exists():raise SystemExit('Refusing to overwrite existing freeze')
target.write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'frozen_files':len(files),'qualification':record['qualification']}))
