import json,hashlib,shutil
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parents[2]
if (BASE/'FREEZE.json').exists():raise SystemExit('Refusing prompt recovery rewrite after FREEZE.json; create a successor cut.')
session=Path(r'\\wsl.localhost\Ubuntu-26.04\home\vlad_\.codex\sessions\2026\11\06\rollout-2026-11-06T20-06-46-01a1b31d-558f-79b2-b531-b53d8111c68d.jsonl')
original=ROOT/'research/hackathon/frontier-hunt-20261106/lane6-criteria-gaming'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
texts=[]
for line in session.open(encoding='utf8'):
 r=json.loads(line);q=r.get('payload',{})
 if r.get('type')=='response_item' and q.get('type')=='message' and q.get('role')=='user':
  t='\n'.join(c.get('text','') for c in q.get('content',[]) if isinstance(c,dict))
  if t.startswith('You are designing scoring criteria'):texts.append(t)
assert len(texts)==1
text=texts[0];assert text.strip()==(original/'prompt.txt').read_text(encoding='utf8').strip()
packet=BASE/'packets/primary/H2';archive=BASE/'packets/archive/H2-minimal-reconstruction'
assert packet.resolve().is_relative_to(BASE.resolve()) and archive.resolve().is_relative_to(BASE.resolve())
archive.parent.mkdir(parents=True,exist_ok=True)
if not archive.exists():shutil.move(str(packet),str(archive))
elif packet.exists():shutil.rmtree(packet)
packet.mkdir(parents=True,exist_ok=True);(packet/'input').mkdir(exist_ok=True)
(packet/'prompt.md').write_text(text,encoding='utf8')
bindings=[]
for src in sorted((original/'calibration').glob('CAL-*.txt')):
 dst=packet/'input'/src.name;shutil.copyfile(src,dst)
 bindings.append({'source':src.relative_to(ROOT).as_posix(),'destination':dst.relative_to(BASE).as_posix(),'sha256':sha(src),'bytes':src.stat().st_size,'exposure':'author_public_input'})
prov={'case_id':'H2','condition_id':'exact_original','instruction_status':'exact_original_direct_rubric_authoring_user_instruction_recovered','exact_instruction_replication':True,'same_full_context':False,'authoring_level':'The original task directly asks GPT to author scoring criteria; it does not ask it to build a software evaluator of criteria authors.','author_instruction_sha256':sha(packet/'prompt.md'),'original_prompt_file':(original/'prompt.txt').relative_to(ROOT).as_posix(),'original_prompt_file_sha256':sha(original/'prompt.txt'),'recovered_session_id':'01a1b31d-558f-79b2-b531-b53d8111c68d','session_source_sha256':sha(session),'text_match':'Exact recovered user instruction equals saved prompt.txt after stripping trailing whitespace and decoding line endings. Actor receives recovered text unchanged.','available_materials':['CAL-A.txt','CAL-B.txt','CAL-C.txt','CAL-D.txt'],'runtime_context_limit':'Original user instruction recovered; full system/developer/runtime context not reproduced. New runner must record its own model, effort, tools and sandbox.','owner_only_withheld':['old grader','reference criteria','bank labels','prior candidate outputs','audit findings'],'archive':'packets/archive/H2-minimal-reconstruction'}
(packet/'PROVENANCE.json').write_text(json.dumps(prov,indent=2)+'\n')
files=[{'path':p.relative_to(packet).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(packet.rglob('*')) if p.is_file() and p.name!='MANIFEST.json']
(packet/'MANIFEST.json').write_text(json.dumps({'case_id':'H2','condition_id':'exact_original','files':files,'source_bindings':bindings,'instruction_binding':{'session_id':prov['recovered_session_id'],'recovered_text_sha256':sha(packet/'prompt.md'),'original_prompt_file':prov['original_prompt_file'],'original_prompt_file_sha256':prov['original_prompt_file_sha256']}},indent=2)+'\n')
p=BASE/'sources/SOURCE-MANIFEST.json';m=json.loads(p.read_text());m['source_files']=[r for r in m['source_files'] if not r['destination'].startswith('packets/primary/H2/')]+bindings;m['source_count']=len(m['source_files']);m['total_bytes']=sum(r['bytes'] for r in m['source_files']);p.write_text(json.dumps(m,indent=2)+'\n')
p=BASE/'sources/INSTRUCTION-PROVENANCE.json';m=json.loads(p.read_text());m['cases']=[prov if c['case_id']=='H2' else c for c in m['cases']];m['exact_authoring_instructions_verified']=1;m['minimal_reconstructions']=8;m['formal_claim_limit']='H2 replays exact recovered direct rubric-authoring user instruction under new runtime context; other eight cases retain reconstructed authoring instructions.';p.write_text(json.dumps(m,indent=2)+'\n')
print(json.dumps({'case':'H2','condition':'exact_original','unchanged_user_prompt':True,'input_files':4,'archived_reconstruction':True}))
