"""Explicit post-outcome semantic/component controls; original frozen banks unchanged."""
import json,hashlib,datetime,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;BASE=HERE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf8')
models=['gpt-6.1-sol','gpt-6-astra'];cases=[]
h2=[]
for model in models:
 src=BASE/'runs/screen'/model/'H2/delivery/criteria.md'
 c={'case_id':'H2','control_id':'positive-'+model,'kind':'reviewed_rubric_mechanical_component','source_path':src.relative_to(BASE).as_posix(),'source_sha256':sha(src),'text':src.read_text(encoding='utf8'),'expected_conforms':True,'manual_judgment':'The AI semantic review accepts the declared novelty operationalization as a valid alternative; no private CAL ranking. Human review pending.','public_license':'Original H2 Checks/Score mapping/Worked examples/Failure modes deliverable requirements.'}
 p=HERE/'H2'/(c['control_id']+'.json');write(p,c);h2.append(p)
source=json.loads(h2[0].read_text(encoding='utf8'));text=source['text']
mutations=[('missing-required-heading',text.replace('## Failure modes','## Limitations',1),'DELIVERABLE requires exact Failure modes heading.'),('mapping-gap',text.replace('| 0-1 | 0 |','| 0-0 | 0 |',1),'Score mapping must cover every possible point total with no gaps or overlaps.'),('worked-arithmetic',text.replace('| **Total** | **5** |','| **Total** | **6** |',1),'Worked examples must apply each check and give the resulting total and mapped score.')]
for ident,changed,license in mutations:
 assert changed!=text,ident
 c={**source,'control_id':ident,'kind':'authored_post_outcome_rubric_mutant','text':changed,'expected_conforms':False,'public_license':license,'mutation_source_sha256':source['source_sha256']}
 p=HERE/'H2'/(ident+'.json');write(p,c);h2.append(p)
cases.append({'case_id':'H2','controls':[p.relative_to(BASE).as_posix()for p in h2],'scope':'Deterministic headings, weights, range coverage and worked arithmetic for the two known reviewed formats; novelty/usefulness construct validity remains manual.'})
h3=[]
for model in models:
 rel='evaluation/evaluate.py'if model=='gpt-6.1-sol'else'evaluate.py';src=BASE/'runs/screen'/model/'H3/delivery'/rel
 c={'case_id':'H3','control_id':'positive-'+model,'kind':'reviewed_eval_semantic_component','source_delivery':(src.parent.parent if model=='gpt-6.1-sol'else src.parent).relative_to(BASE).as_posix(),'evaluator_relative_path':rel,'evaluator_sha256':sha(src),'mutation':None,'candidate':'correct_reference','expected_conforms':True,'qualification_dimension':'Machine contract checks and conservative needs_review status only; no OS sandbox/full-system/human-review acceptance.','public_license':'H3 original named CLI/output/feature/holdout requirements; no numeric accuracy floor.'}
 p=HERE/'H3'/(c['control_id']+'.json');write(p,c);h3.append(p)
ref=BASE/'runs/screen/gpt-6-astra/H3/delivery/reference'
reference={p.name:{'source_path':p.relative_to(BASE).as_posix(),'sha256':sha(p)}for p in ref.iterdir()if p.is_file()}
base=json.loads(h3[1].read_text(encoding='utf8'))
mutants=[('unlicensed-accuracy-floor','accuracy_floor','correct_reference','The original task states no minimum accuracy; a feature-free valid baseline must not fail solely for independent score below.66.'),('missing-binary-output-check','binary_check_removed','invalid_binary','Deliverable1 requires literal0/1 predictions; a constant2 pipeline violates that explicit contract.'),('automatic-accept-with-false-metric','manual_gate_removed','false_metric','Deliverable3 requires honest held-out validation. Numeric formatting alone cannot establish honesty; reference split actual483/800 is not1.000.')]
for ident,mutation,candidate,license in mutants:
 c={**base,'control_id':ident,'kind':'authored_post_outcome_eval_component_mutant','mutation':mutation,'candidate':candidate,'expected_conforms':False,'public_license':license}
 p=HERE/'H3'/(ident+'.json');write(p,c);h3.append(p)
cases.append({'case_id':'H3','controls':[p.relative_to(BASE).as_posix()for p in h3],'reference_candidate':reference,'scope':'Actual delivered evaluators run on safe authored candidates in disposable Docker. Positives qualify specific semantic components only. Unknown overall review and disclosed missing OSsandbox remain unknown.'})
manifest={'schema_version':'post-outcome-semantic-controls/v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'condition':'post_outcome_semantic_control_successor','model_calls':0,'original_frozen_banks_modified':False,'human_review':'pending','cases':cases}
write(HERE/'MANIFEST.json',manifest)
files=[p for p in HERE.rglob('*')if p.is_file()and p.name not in ['FREEZE.json','QUALIFICATION.json']and'work'not in p.parts and'__pycache__'not in p.parts]
write(HERE/'FREEZE.json',{'condition':manifest['condition'],'scope':'Frozen after native output inspection; before this successor qualification. Never prospective actor gold.','files_sha256':{p.relative_to(HERE).as_posix():sha(p)for p in files}})
print(json.dumps({'H2_controls':len(h2),'H3_controls':len(h3),'condition':manifest['condition']}))
