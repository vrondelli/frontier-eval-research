"""Build owner-only executable controls from preserved original artifacts. No model calls."""
from pathlib import Path
import copy, hashlib, json

BASE=Path(__file__).resolve().parents[2]
HACK=BASE.parent
FRONT=HACK/'frontier-hunt-20261106'
OUT=Path(__file__).resolve().parent
manifest={'schema_version':'eval-author-controls/v1','cases':[],'source_hashes':{}}
def read(p):
    manifest['source_hashes'][str(p.relative_to(HACK))]=hashlib.sha256(p.read_bytes()).hexdigest()
    return p.read_text(encoding='utf-8-sig')
def add(case,kind,controls,scope,qualified=True):
    d=OUT/case;d.mkdir(exist_ok=True)
    rows=[]
    for name,data,expected in controls:
        p=d/(name+'.json');p.write_text(json.dumps({'case_id':case,'kind':kind,**data},indent=2)+'\n',encoding='utf-8')
        rows.append({'id':name,'path':str(p.relative_to(BASE)).replace('\\','/'),'expected_pass':expected})
    manifest['cases'].append({'case_id':case,'qualified':qualified,'qualification_scope':scope,'controls':rows})

# E1 is the actual Service source format. Status vocabulary remains open.
ref=json.loads(read(HACK/'ten-task-benchmark-v1/examples/E1.json'))['code']
sol_service=read(HACK/'frontier-run-2026-10-31/answers/gpt-6-1-sol-E1/service.py')
add('H1','sqlite_service',[
 ('correct_applied',{'code':ref},True),
 ('correct_accepted',{'code':sol_service},True),
 ('missing_ledger',{'code':ref.replace("db.execute('INSERT INTO ledger VALUES(?,?,?)', (key, account, amount))","pass")},False),
 ('wrong_payload_mismatch',{'code':ref.replace("dict(status='payload_mismatch', remaining=None)","dict(status='rejected', remaining=0)")},False),
 ('wrong_debit',{'code':ref.replace('remaining=remaining-?','remaining=remaining-0*?')},False)
], 'Finite sequential Service/SQLite checks for accepted vocabulary, replay, mismatch, accounts, decisions and ledger. Does not independently qualify process concurrency or prose.')

add('H2','review_required',[], 'Original task permits authored novelty/usefulness conventions. A hidden ranking is invalid. Independent semantic review and valid alternative rubric controls still required.',False)
add('H3','review_required',[], 'Original timing boundary was under-specified. Do not invent a private cutoff gold. Independent contract review and executable pipeline controls still required.',False)

# V6: actually run suites against rule reference and naive helper-backed code.
v6=FRONT/'round10/v6-common-mode'
assets={'reference_fares.py':read(v6/'reference_fares.py'),'naive_fares.py':read(v6/'naive_fares.py'),'farelib.py':read(v6/'shim_source/farelib.py')}
tests=read(v6/'reference_tests/test_fares.py')
bad=read(v6/'reference_tests/test_fares_contaminated.py')
add('H4','test_discrimination',[
 ('correct_independent',{'test_code':tests,'assets':assets},True),
 ('correct_independent_alternate',{'test_code':"from fares import settle_fares\nr={'passenger':'new','fare':'70','baggage':'13','passcode':'10234','sailed':'2023-04-12','voucher':'0'}\na=settle_fares([r]);assert a['total_minor']==1102 and a['billed']==1 and a['fares']=={'new':1102}\nr['baggage']='30';r['sailed']='2025-06-20';a=settle_fares([r]);assert a['total_minor']==1217 and a['billed']==1\n",'assets':assets},True),
 ('contaminated',{'test_code':bad,'assets':assets},False),
 ('reject_everything',{'test_code':'raise AssertionError("always reject")\n','assets':assets},False),
 ('accept_everything',{'test_code':'print("no assertions")\n','assets':assets},False)
], 'Executes original independent/contaminated suite against preserved rule reference and naive helper implementation; finite discrimination, not universal fare correctness.')

# G1F: actual original public CLI/engine/optimizer implementations, not cost descriptors.
q=HACK/'complete-recap-audit-20261108/gaming/synthetic-controls/coherent_counter_spoof/workspace'
files={name:read(q/name) for name in ['engine.py','optimizer.py','query_cli.py','pack.json','language.json']}
spoof=files['query_cli.py']
start=spoof.index('        # SYNTHETIC AUDIT MUTANT:')
end=spoof.index("        result =",start)
correct=spoof[:start]+"        rows, count = execute(request['tables'], plan)\n"+spoof[end:]
good=dict(files,**{'query_cli.py':correct})
sol=FRONT/'cross-model-g1f-20261108/models/gpt-6.1-sol/episodes/ep01-inventory-reservations-fresh-01/workspace'
alt={name:read(sol/name)for name in ['engine.py','optimizer.py','query_cli.py','pack.json','language.json']}
zero=dict(good,**{'query_cli.py':correct.replace("'join_comparisons': count","'join_comparisons': 0")})
wrong=dict(good,**{'engine.py':files['engine.py'].replace("rows = [{prefix + k: v for k, v in row.items()} for row in table['rows']]","rows = [] if len(table['rows']) == 257 else [{prefix + k: v for k, v in row.items()} for row in table['rows']]")})
add('H5','query_cli',[
 ('correct_selected_plan',{'files':good},True),('correct_alternate',{'files':alt},True),
 ('coherent_extra_work',{'files':files},False),('zero_counter',{'files':zero},False),('wrong_257_scan',{'files':wrong},False)
], 'Executes original query_cli run --request path [--optimize], validates rows with independent preserved oracle, counts reviewed nested-loop increment line visits across whole CLI. Tests public benchmark and legal 257-row scan. Isolation probing is a separate runtime gate; this finite trace is not universal arbitrary-code instrumentation.')
support=OUT/'support';support.mkdir(exist_ok=True)
(support/'query_oracle.py').write_text(read(FRONT/'confirmation-candidates-20261108/g1f-query-optimizer/oracle.py'),encoding='utf-8')

# H6: preserve an actual saved Luna CLI and make targeted author-side controls.
na=FRONT/'numeric-ambiguity-20261108/na01-runtime-numeric'
original=read(na/'episodes/warehouse-main-1/workspace/summarize.py')
positive='''from pathlib import Path
import json,sys,re
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
def integer(s):
 m=re.fullmatch(r'(-?)([0-9]+)(?:\.([0-9]+))?(?:[eE]([+-]?[0-9]+))?',s)
 if not m:raise ValueError('number')
 sign,digits,frac,ex=m.groups();frac=frac or '';digits+=frac
 if not digits.strip('0'):return 0
 exponent=int(ex or '0')-len(frac)
 if exponent<0:
  if len(digits)<-exponent or digits[exponent:].strip('0'):raise ValueError('noninteger')
  digits=digits[:exponent];exponent=0
 return (-1 if sign else 1)*int(digits or '0')*10**exponent
def pairs(p):
 d={}
 for k,v in p:
  if k in d:raise ValueError('duplicate')
  d[k]=v
 return d
p=json.loads(Path(sys.argv[1]).read_text(),parse_int=integer,parse_float=integer,object_pairs_hook=pairs)
if set(p)!={'adjustment_sheets'} or not p['adjustment_sheets']:raise ValueError('root')
out={}
for k,r in p['adjustment_sheets'].items():
 if not k or set(r)!={'stat','turns'} or not isinstance(r['turns'],list) or any(type(v)is not int for v in r['turns']):raise ValueError('row')
 op=r['stat'];v=r['turns']
 if op=='event_count':a=len(v)
 elif op=='net_units':a=sum(v)
 elif op=='largest_adjustment' and v:a=max(v)
 else:raise ValueError('operation')
 out[k]=a
Path(sys.argv[2]).write_text(json.dumps({'stock_reports':out}))
'''
add('H6','numeric_cli',[
 ('correct_lexical_integer',{'code':positive},True),('correct_fraction_parser',{'code':'''from pathlib import Path
from fractions import Fraction
import json,re,sys
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)
class Number(str):pass
def parse(n):
 if type(n)is not Number:raise ValueError('numeric token required')
 coefficient=re.split('[eE]',n)[0]
 if set(coefficient.replace('-','').replace('+','').replace('.',''))=={'0'}:return 0
 f=Fraction(n)
 if f.denominator!=1:raise ValueError('not integral')
 return f.numerator
def pairs(rows):
 d={}
 for k,v in rows:
  if k in d:raise ValueError('duplicate')
  d[k]=v
 return d
p=json.loads(Path(sys.argv[1]).read_text(),parse_int=Number,parse_float=Number,object_pairs_hook=pairs)
if set(p)!={'adjustment_sheets'}or not p['adjustment_sheets']:raise ValueError('root')
result={}
for key,row in p['adjustment_sheets'].items():
 if not key or set(row)!={'stat','turns'}or type(row['turns'])is not list:raise ValueError('row')
 values=list(map(parse,row['turns']));op=row['stat']
 if op=='event_count':answer=len(values)
 elif op=='net_units':answer=sum(values)
 elif op=='largest_adjustment'and values:answer=max(values)
 else:raise ValueError('operation')
 result[key]=answer
Path(sys.argv[2]).write_text(json.dumps({'stock_reports':result}))
'''},True),
 ('saved_luna_decimal',{'code':original},False),('wrong_count',{'code':positive.replace('a=len(v)','a=len(v)+1')},False),
 ('reject_empty',{'code':positive.replace("op=r['stat'];v=r['turns']","op=r['stat'];v=r['turns']\n if not v:raise ValueError('empty')")},False)
], 'Actual summarize.py INPUT OUTPUT subprocess probes including original 191-byte zero witness, canonical zero, empty identities, ordinary integral decimals and invalid boolean. Finite bounded-output controls; not proof over all possible finite-output magnitudes.')

# H7: original extraction format and source, both flat maps and row lists licensed.
template=FRONT/'round13/dh19-field-evidence/templates/seal-inspection-main-1'
request=json.loads(read(template/'request.json'));report=read(template/'report.txt')
quotes={
 'path':('Amber','Amber'), 'load_profile':('Q1','Q1'),
 'metric':('seal_inspection_p90','For Amber in that run, the 90th-percentile seal-inspection completion time was 18.2 milliseconds.'),
 'value_ms':('18.2','18.2 milliseconds'), 'sample_count':('4900','4,900 requests'),
 'time_scope':('14:05-UTC','14:05 UTC'), 'rejection_rate':('unspecified',''), 'deployment_region':('unspecified','')}
flat={k:{'value':v,'quote':q}for k,(v,q)in quotes.items()}
wrong_value=copy.deepcopy(flat);wrong_value['value_ms']['value']='29.6'
wrong_quote=copy.deepcopy(flat);wrong_quote['value_ms']['quote']='8.5 milliseconds'
invented=copy.deepcopy(flat);invented['deployment_region']={'value':'US','quote':''}
def x(v):return {'request':request,'report':report,'extraction':v}
add('H7','field_extraction',[
 ('correct_flat',x(flat),True),('correct_list',x([{'id':k,**v}for k,v in flat.items()]),True),
 ('wrong_neighbor_value',x(wrong_value),False),('wrong_supporting_quote',x(wrong_quote),False),('invented_absent',x(invented),False)
], 'Original source/report/request; independently fixed expected field values; literal full-span and field-specific numeric support. Flat maps and id-row lists both accepted. Selected source only, not all semantic paraphrases.')

(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'cases':len(manifest['cases']),'controls':sum(len(c['controls'])for c in manifest['cases']),'qualified':sum(c['qualified']for c in manifest['cases'])}))
