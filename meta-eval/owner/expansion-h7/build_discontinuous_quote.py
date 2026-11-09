from pathlib import Path
import copy,hashlib,importlib.util,json
B=Path(__file__).resolve().parent;ROOT=B.parents[1];source=ROOT/'owner/cases/H7/correct_flat.json';correct=json.loads(source.read_text());bad=copy.deepcopy(correct)
components=['Amber lane seal inspections','90th-percentile seal-inspection completion time'];quote=' '.join(components);assert all(c in bad['report']for c in components)and quote not in bad['report']
bad['extraction']['metric']['quote']=quote
rows=[]
for name,doc,expected in [('literal_positive',correct,True),('discontinuous_components',bad,False)]:
 p=B/(name+'.json');p.write_text(json.dumps(doc,indent=2)+'\n');rows.append({'id':name,'path':str(p.relative_to(ROOT)).replace('\\','/'),'expected_pass':expected})
spec=importlib.util.spec_from_file_location('owner_checks',ROOT/'owner/check_cases.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
receipts=[]
for row in rows:
 actual,evidence=mod.check_h7(json.loads((ROOT/row['path']).read_text()));receipts.append({'control':row['id'],'expected':row['expected_pass'],'observed':actual,'qualified':actual==row['expected_pass'],'evidence':evidence})
(B/'QUALIFICATION.json').write_text(json.dumps({'all_qualified':all(r['qualified']for r in receipts),'components_literal':True,'whole_quote_literal':False,'components':components,'whole_quote':quote,'source_clause':'Every other quote must be one exact contiguous source span that supports THAT corresponding field value.','receipts':receipts},indent=2)+'\n')
(B/'MANIFEST.json').write_text(json.dumps({'status':'posthoc_component_probe','case_id':'H7','controls':rows,'known_family':'NA05component-only validation missed whole-quote contiguity; recreated on originalH7source. No newmodelattempts.'},indent=2)+'\n')
(B/'FREEZE.json').write_text(json.dumps({'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in B.iterdir()if p.is_file()and p.name!='FREEZE.json'}},indent=2)+'\n')
