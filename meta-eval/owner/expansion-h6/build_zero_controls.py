from pathlib import Path
import hashlib,importlib.util,json
B=Path(__file__).resolve().parent;ROOT=B.parents[1];source=ROOT/'owner/cases/H6/correct_lexical_integer.json';base=json.loads(source.read_text());code=base['code']
output=code.replace("Path(sys.argv[2]).write_text(json.dumps({'stock_reports':out}))","Path(sys.argv[2]).write_text('{\"stock_reports\":{'+','.join(json.dumps(k)+':'+('0e10000000000000000000' if v==0 else str(v)) for k,v in out.items())+'}}')")
assert output!=code
wrong=code.replace("p=json.loads(Path(sys.argv[1]).read_text(),", "raw=Path(sys.argv[1]).read_text()\nif '0e10000000000000000000' in raw:raise ValueError('written exponent outside implementation range')\np=json.loads(raw,")
assert wrong!=code
rows=[]
for name,c,expected in [('legal_zero_output',output,True),('zero_input_only_rejection',wrong,False)]:
 p=B/(name+'.json');p.write_text(json.dumps({'case_id':'H6','kind':'numeric_cli','code':c},indent=2)+'\n');rows.append({'id':name,'path':str(p.relative_to(ROOT)).replace('\\','/'),'expected_pass':expected})
spec=importlib.util.spec_from_file_location('owner_checks',ROOT/'owner/check_cases.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);receipts=[]
for r in rows:
 actual,evidence=mod.check_h6(json.loads((ROOT/r['path']).read_text()));receipts.append({'control':r['id'],'expected':r['expected_pass'],'observed':actual,'qualified':actual==r['expected_pass'],'evidence':evidence})
(B/'QUALIFICATION.json').write_text(json.dumps({'all_qualified':all(r['qualified']for r in receipts),'receipts':receipts},indent=2)+'\n')
(B/'MANIFEST.json').write_text(json.dumps({'status':'post_outcome_diagnostic','reason':'Test published exact-integer spelling equivalence on input and output after finding new grader usesDecimal and omits written-exponentzero. These are authoredcontrols, not subjectmodel outcomes.','cases':rows},indent=2)+'\n')
(B/'FREEZE.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in B.iterdir()if p.is_file()and p.name!='FREEZE.json'}},indent=2)+'\n')
