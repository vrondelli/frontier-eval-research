import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
ROOT=BASE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
errors=[];files=0;sources=0
for case in [f'H{i}' for i in range(1,10)]:
 packet=BASE/'packets/primary'/case
 m=json.loads((packet/'MANIFEST.json').read_text(encoding='utf8'))
 prov=json.loads((packet/'PROVENANCE.json').read_text(encoding='utf8'))
 expected='exact_original' if case=='H2' else 'minimal_reconstruction'
 if prov['condition_id']!=expected:errors.append(case+': wrong provenance claim')
 if case!='H2' and prov['exact_instruction_replication']:errors.append(case+': unsupported exact claim')
 for row in m['files']:
  p=packet/row['path'];files+=1
  if not p.is_file() or sha(p)!=row['sha256']:errors.append(case+': packet mismatch '+row['path'])
 for row in m['source_bindings']:
  p=ROOT/row['source'];sources+=1
  if not p.is_file() or sha(p)!=row['sha256']:errors.append(case+': source mismatch '+row['source'])
result={'status':'pass' if not errors else 'fail','packets':9,'packet_files_checked':files,'source_bindings_checked':sources,'errors':errors,'scope':'Current copied byte custody and honest reconstructed-instruction labels; not semantic task or grader qualification.'}
(BASE/'sources/PACKET-VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result));raise SystemExit(bool(errors))
