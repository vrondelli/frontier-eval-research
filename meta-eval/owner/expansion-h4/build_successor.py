from pathlib import Path
import hashlib,importlib.util,json
B=Path(__file__).resolve().parent;ROOT=B.parents[1]
initial=ROOT/'owner/cases/H4';rows=[]
for path in sorted(initial.glob('*.json')):
    c=json.loads(path.read_text());c['assets']['reference_fares.py']=(B/'fare_exact.py').read_text()
    if path.stem=='correct_independent_alternate':
        c['test_code']="""import unittest
from fares import settle_fares
class Independent(unittest.TestCase):
 def test_fraction_ceiling(self):
  record={'passenger':'new','fare':'70','baggage':'13','passcode':'10234','sailed':'2023-04-12','voucher':'0'}
  result=settle_fares([record]);self.assertEqual(result['total_minor'],1102);self.assertEqual(result['fares'],{'new':1102})
 def test_cutoff_inclusive(self):
  record={'passenger':'cutoff','fare':'70','baggage':'30','passcode':'10234','sailed':'2025-06-20','voucher':'0'}
  result=settle_fares([record]);self.assertEqual(result['total_minor'],1217);self.assertEqual(result['billed'],1)
if __name__=='__main__':unittest.main()
"""
    out=B/path.name;out.write_text(json.dumps(c,indent=2)+'\n');rows.append({'path':out.name,'expected_pass':path.stem.startswith('correct_')})
(B/'MANIFEST.json').write_text(json.dumps({'status':'post_outcome_owner_correction','cases':rows,'original_bank_unchanged':True,'reason':'Original alternate positive violated required unittest format; inherited reference had final-newline and decimal-precision weaknesses. New controls are diagnostics, not blind preregistered holdouts.'},indent=2)+'\n')
spec=importlib.util.spec_from_file_location('owner_checks',ROOT/'owner/check_cases.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
qualification=[]
for row in rows:
    actual,evidence=mod.check_h4(json.loads((B/row['path']).read_text()));qualification.append({'control':row['path'],'expected':row['expected_pass'],'observed':actual,'qualified':actual==row['expected_pass'],'evidence':evidence})
(B/'QUALIFICATION.json').write_text(json.dumps({'all_qualified':all(r['qualified']for r in qualification),'rows':qualification},indent=2)+'\n')
(B/'FREEZE.json').write_text(json.dumps({'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in B.iterdir()if p.is_file()and p.name!='FREEZE.json'}},indent=2)+'\n')
