"""Post-initial-freeze E1 process overlap diagnostic, using the original Service API.
Only run trusted authored controls here; production grader execution needs Docker.
"""
import argparse,json,sqlite3,subprocess,sys,tempfile,time
from pathlib import Path
WORKER='''import json,sys,time
from pathlib import Path
from service import Service
s=Service(sys.argv[1]);key=sys.argv[2];Path('ready-'+key).write_text('ready')
while not Path('GO').exists():time.sleep(.005)
print(json.dumps(s.apply({'key':key,'account':'A','amount':60})))
'''
def run(code):
 receipts=[]
 with tempfile.TemporaryDirectory(prefix='owner-e1-process-')as folder:
  p=Path(folder);(p/'service.py').write_text(code);(p/'worker.py').write_text(WORKER)
  # Idempotent initialization before simultaneous calls is permitted.
  init=subprocess.run([sys.executable,'-c',"from service import Service;Service('db')"],cwd=p,capture_output=True,text=True,timeout=6)
  if init.returncode:return False,{'initialization':init.stderr}
  for trial in range(3):
   # Each declared repetition has a fresh store.
   db=p/('db'+str(trial));subprocess.run([sys.executable,'-c',"from service import Service;import sys;Service(sys.argv[1])",str(db)],cwd=p,check=True,capture_output=True,timeout=6)
   for marker in ['GO','ready-k1','ready-k2']:
    (p/marker).unlink(missing_ok=True)
   children=[subprocess.Popen([sys.executable,'worker.py',str(db),key],cwd=p,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)for key in ['k1','k2']]
   until=time.monotonic()+6
   while not all((p/('ready-'+key)).exists()for key in ['k1','k2']):
    if time.monotonic()>until:
     for c in children:c.kill();c.communicate()
     return False,{'error':'worker readiness timeout'}
    time.sleep(.01)
   (p/'GO').write_text('go');results=[]
   for child in children:
    out,err=child.communicate(timeout=6);results.append({'exit':child.returncode,'stdout':out,'stderr':err})
   try:
    replies=[json.loads(r['stdout'])for r in results];statuses=[r['status']for r in replies]
    valid=sum(s in ['applied','accepted']for s in statuses)==1 and statuses.count('rejected')==1
    replay_script="from service import Service;import json,sys;s=Service(sys.argv[1]);print(json.dumps([s.apply({'key':k,'account':'A','amount':60})for k in ['k1','k2']]))"
    replay=subprocess.run([sys.executable,'-c',replay_script,str(db)],cwd=p,capture_output=True,text=True,timeout=6)
    valid=valid and json.loads(replay.stdout)==replies
    con=sqlite3.connect(db)
    try:
     remaining=con.execute("SELECT remaining FROM accounts WHERE account='A'").fetchone()[0];ledger=con.execute('SELECT count(*) FROM ledger').fetchone()[0]
    finally:con.close()
    valid=valid and remaining==40 and ledger==1
    receipts.append({'trial':trial,'pass':valid,'replies':replies,'remaining':remaining,'ledger_rows':ledger,'processes':results})
   except Exception as e:receipts.append({'trial':trial,'pass':False,'error':repr(e),'processes':results})
 return all(r['pass']for r in receipts),receipts
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('artifact',type=Path);a.add_argument('--out',type=Path);n=a.parse_args();doc=json.loads(n.artifact.read_text());ok,evidence=run(doc['code']);result={'pass':ok,'evidence':evidence,'scope':'three overlapping independent-process60-unit pairs and process replay, original E1 F1-F5'};raw=json.dumps(result,indent=2)+'\n'
 if n.out:n.out.write_text(raw)
 else:print(raw)
 raise SystemExit(0 if ok else 1)
