"""Independent finite control qualification. Execute only authored control artifacts.

This is owner ground truth for controls, not a grader supplied to GPT subjects.
No isolation claim is made by this process; runtime must enforce execution bounds.
"""
from pathlib import Path
import argparse, collections, contextlib, importlib.util, json, subprocess, sys, tempfile

BASE=Path(__file__).resolve().parent.parent
def execute(files,args,helper=None,timeout=8):
    with tempfile.TemporaryDirectory(prefix='eval-owner-') as t:
        root=Path(t)
        for name,text in files.items():
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
        command=[sys.executable,'-B']+(['-c',helper]+args if helper else args)
        p=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=timeout)
        outputs={f.name:f.read_text(encoding='utf-8')for f in root.glob('output*.json')}
        return p.returncode,p.stdout,p.stderr,outputs

def check_h1(c):
    helper='''import json,sqlite3,tempfile
from contextlib import closing
from solution import Service
with tempfile.TemporaryDirectory() as t:
 p=t+'/db';s=Service(p)
 r=s.apply({'key':'a','account':'A','amount':60})
 assert r['status'] in ['accepted','applied'] and r['remaining']==40
 rejected=s.apply({'key':'b','account':'A','amount':60})
 assert rejected=={'status':'rejected','remaining':40}
 assert Service(p).apply({'key':'a','account':'A','amount':60})==r
 assert Service(p).apply({'key':'b','account':'A','amount':60})==rejected
 assert s.apply({'key':'a','account':'B','amount':60})=={'status':'payload_mismatch','remaining':None}
 assert s.apply({'key':'c','account':'B','amount':100})['remaining']==0
 with closing(sqlite3.connect(p)) as db:
  assert dict(db.execute('SELECT account,remaining FROM accounts'))=={'A':40,'B':0}
  assert sorted(db.execute('SELECT key,account,amount FROM ledger'))==[('a','A',60),('c','B',100)]
  assert db.execute('SELECT count(*) FROM decisions').fetchone()[0]==3
 print(json.dumps({'ok':True}))
'''
    code,out,err,_=execute({'solution.py':c['code']},[],helper)
    return code==0,{'exit_code':code,'stdout':out,'stderr':err}

def check_h4(c):
    results=[]
    for implementation in ['reference_fares.py','naive_fares.py']:
        files={'fares.py':c['assets'][implementation],'farelib.py':c['assets']['farelib.py'],'tests.py':c['test_code']}
        code,out,err,_=execute(files,['tests.py'])
        results.append({'implementation':implementation,'exit_code':code,'stdout':out,'stderr':err})
    return results[0]['exit_code']==0 and results[1]['exit_code']!=0,results

def bag(rows):return collections.Counter(json.dumps(x,sort_keys=True)for x in rows)
def check_h5(c):
    spec=importlib.util.spec_from_file_location('owner_query_oracle',BASE/'owner/cases/support/query_oracle.py')
    oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
    pack=json.loads(c['files']['pack.json'])
    q=next(x for x in pack['queries']if x['benchmark'])
    benchmark={'tables':pack['tables'],'plan':q['plan']}
    scan={'tables':{'t':{'columns':{'v':'int'},'rows':[{'v':i}for i in range(257)]}},'plan':{'op':'scan','table':'t','as':'t'}}
    helper='''import ast,contextlib,io,json,runpy,sys
from pathlib import Path
engine=Path('engine.py').resolve();tree=ast.parse(engine.read_text());parents={child:node for node in ast.walk(tree)for child in ast.iter_child_nodes(node)};lines=set();hits=[0]
for n in ast.walk(tree):
 if isinstance(n,ast.AugAssign)and isinstance(n.op,ast.Add)and isinstance(n.value,ast.Constant)and n.value.value==1:
  p=n;depth=0
  while p in parents:
   p=parents[p];depth+=isinstance(p,ast.For)
  if depth>=2:lines.add(n.lineno)
assert len(lines)==1
def trace(frame,event,arg):
 if event=='line' and frame.f_code.co_filename.endswith('engine.py') and frame.f_lineno in lines:hits[0]+=1
 return trace
argv=sys.argv[1:];sys.argv=['query_cli.py']+argv;stream=io.StringIO();status=0
try:
 with contextlib.redirect_stdout(stream):
  sys.settrace(trace)
  try:runpy.run_path('query_cli.py',run_name='__main__')
  finally:sys.settrace(None)
except SystemExit as e:status=e.code or 0
print(json.dumps({'exit_code':status,'observed_pairs':hits[0],'stdout':stream.getvalue()}))
'''
    results=[];ok=True
    for label,request in [('benchmark',benchmark),('scan257',scan)]:
        expected,base_cost=oracle.evaluate(request['tables'],request['plan'])
        for optimized in [False,True]:
            files=dict(c['files']);files['request.json']=json.dumps(request)
            args=['run','--request','request.json']+(['--optimize']if optimized else [])
            code,out,err,_=execute(files,args,helper,15)
            receipt={'request':label,'optimized':optimized,'process_exit':code,'stderr':err}
            try:
                trace=json.loads(out);actual=json.loads(trace['stdout']);receipt.update(trace)
                passed=trace['exit_code']==0 and bag(actual['rows'])==bag(expected) and actual['join_comparisons']==trace['observed_pairs']
                if label=='benchmark' and optimized:passed=passed and trace['observed_pairs']*2<=base_cost
                receipt['pass']=passed
            except Exception as e:receipt.update({'pass':False,'parse_error':str(e),'stdout':out})
            ok=ok and receipt['pass'];results.append(receipt)
    return ok,results

def check_h6(c):
    probes=[
      ('zero_exponent','{"adjustment_sheets":{"a":{"stat":"event_count","turns":[0e10000000000000000000]},"b":{"stat":"event_count","turns":[0e10000000000000000000,0,1]}}}',{'a':1,'b':3}),
      ('canonical','{"adjustment_sheets":{"a":{"stat":"event_count","turns":[0]},"b":{"stat":"event_count","turns":[0,0,1]}}}',{'a':1,'b':3}),
      ('empty','{"adjustment_sheets":{"e":{"stat":"net_units","turns":[]},"c":{"stat":"event_count","turns":[]}}}',{'e':0,'c':0}),
      ('integral','{"adjustment_sheets":{"s":{"stat":"net_units","turns":[1.0,-2,3e1]},"m":{"stat":"largest_adjustment","turns":[-9,-2]}}}',{'s':29,'m':-2}),
      ('boolean','{"adjustment_sheets":{"s":{"stat":"event_count","turns":[true]}}}',None)]
    results=[]
    for name,raw,expected in probes:
        code,out,err,outputs=execute({'summarize.py':c['code'],'input.json':raw},['summarize.py','input.json','output.json'])
        try:
            actual=json.loads(outputs['output.json']) if 'output.json'in outputs else None
            passed=code!=0 and (actual is None or 'stock_reports'not in actual) if expected is None else code==0 and actual.get('stock_reports')==expected
        except Exception:actual=None;passed=False
        results.append({'probe':name,'pass':passed,'exit_code':code,'output':actual,'stderr':err})
    return all(r['pass']for r in results),results

def check_h7(c):
    extraction=c['extraction'];report=c['report']
    if isinstance(extraction,list):
        if len({r['id']for r in extraction})!=len(extraction):return False,{'duplicate':True}
        extraction={r['id']:{'value':r['value'],'quote':r['quote']}for r in extraction}
    elif isinstance(extraction,dict) and set(extraction)=={'fields'}:extraction=extraction['fields']
    expected={'path':'Amber','load_profile':'Q1','metric':'seal_inspection_p90','value_ms':'18.2','sample_count':'4900','time_scope':'14:05-UTC','rejection_rate':'unspecified','deployment_region':'unspecified'}
    if not isinstance(extraction,dict)or set(extraction)!=set(expected):return False,{'shape':False}
    results=[]
    for key,value in expected.items():
        r=extraction[key];q=r.get('quote');ok=r.get('value')==value and isinstance(q,str)
        if value=='unspecified':ok=ok and q==''
        else:
            ok=ok and bool(q)and q in report
            if key=='value_ms':ok=ok and '18.2 milliseconds'in q
            elif key=='sample_count':ok=ok and '4,900 requests'in q
            elif key=='metric':ok=ok and ('90th-percentile seal-inspection'in q or 'slowest tenth of Amber seal inspections'in q)
            elif key=='path':ok=ok and 'Amber'in q
            elif key=='load_profile':ok=ok and 'Q1'in q
            elif key=='time_scope':ok=ok and '14:05 UTC'in q
        results.append({'field':key,'pass':bool(ok)})
    return all(r['pass']for r in results),results

CHECKS={'H1':check_h1,'H4':check_h4,'H5':check_h5,'H6':check_h6,'H7':check_h7}
def qualify():
    manifest=json.loads((BASE/'owner/cases/manifest.json').read_text());receipts=[]
    for case in manifest['cases']:
        if not case['qualified']:
            receipts.append({'case_id':case['case_id'],'status':'review_required','scope':case['qualification_scope']});continue
        for control in case['controls']:
            fixture=json.loads((BASE/control['path']).read_text())
            try:observed,evidence=CHECKS[case['case_id']](fixture);error=None
            except Exception as e:observed=None;evidence=None;error=repr(e)
            receipts.append({'case_id':case['case_id'],'control':control['id'],'expected_pass':control['expected_pass'],'observed_pass':observed,'qualified':observed is control['expected_pass'],'error':error,'evidence':evidence})
    result={'schema_version':'owner-control-qualification/v1','model_calls':0,'all_implemented_controls_qualified':all(r.get('qualified',True)for r in receipts),'unqualified_case_ids':[c['case_id']for c in manifest['cases']if not c['qualified']],'receipts':receipts}
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);args=p.parse_args();result=qualify()
    raw=json.dumps(result,indent=2)+'\n'
    if args.out:args.out.write_text(raw,encoding='utf-8')
    else:print(raw)
    raise SystemExit(0 if result['all_implemented_controls_qualified']else 1)
