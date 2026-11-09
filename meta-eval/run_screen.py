"""Fixed native author screen. Run Windows-native; creates fresh workspaces and immutable copies."""
import argparse, concurrent.futures, datetime, hashlib, json, os, pathlib, shutil, subprocess, tempfile, time
ROOT=pathlib.Path(__file__).resolve().parent
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def inv(p):return {f.relative_to(p).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file() and not f.is_symlink()}
def run(job):
 model,case,cap=job;packet=ROOT/'packets/primary'/case
 out=ROOT/'runs/screen'/model/case
 if out.exists():raise RuntimeError('Refusing to overwrite '+str(out))
 out.mkdir(parents=True)
 work=pathlib.Path(tempfile.mkdtemp(prefix='eval-author-'+case+'-'))/'workspace'
 shutil.copytree(packet,work)
 prompt=(packet/'prompt.md').read_text(encoding='utf-8')
 cli=shutil.which('codex.exe') or shutil.which('codex')
 if cli is None:raise RuntimeError('Codex executable unavailable; no author call made')
 cmd=[cli,'-c','windows.sandbox=mxc','exec','--json','--skip-git-repo-check','-C',str(work),'-s','workspace-write','-m',model,'-c','model_reasoning_effort="high"','-o',str(out/'final.txt'),'-']
 provenance=json.loads((packet/'PROVENANCE.json').read_text(encoding='utf-8'))
 receipt={'case_id':case,'model_requested':model,'condition':provenance['condition_id'],'exact_instruction_replication':provenance['exact_instruction_replication'],'command':cmd,'workspace':str(work),'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'input_inventory':inv(work),'generation_owner_boundary':'unproven; exposure must be audited','formal_claim_eligible':False}
 write(out/'launch.json',receipt)
 runtimebin=work.parent/'runtimebin';runtimebin.mkdir()
 (runtimebin/'python3.cmd').write_text('@"'+os.sys.executable+'" %*\r\n',encoding='utf-8')
 env=os.environ.copy();env['PATH']=str(runtimebin)+os.pathsep+str(pathlib.Path(os.sys.executable).parent)+os.pathsep+env.get('PATH','')
 receipt['python_runtime']=os.sys.version;receipt['python_executable']=os.sys.executable;receipt['local_python3_alias']=str(runtimebin/'python3.cmd')
 t=time.monotonic();proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace',env=env)
 receipt['pid']=proc.pid;write(out/'launch.json',receipt)
 try:stdout,stderr=proc.communicate(prompt,timeout=cap);status='completed'
 except subprocess.TimeoutExpired:
  subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True);stdout,stderr=proc.communicate();status='timeout'
 (out/'transcript.jsonl').write_text(stdout,encoding='utf-8');(out/'stderr.txt').write_text(stderr,encoding='utf-8')
 shutil.copytree(work,out/'delivery',symlinks=True)
 receipt.update(status=status,exit_code=proc.returncode,seconds=time.monotonic()-t,end_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),output_inventory=inv(out/'delivery'))
 write(out/'launch.json',receipt)
 print(json.dumps({'model':model,'case':case,'status':status,'exit':proc.returncode}),flush=True)
 return receipt
def safe_run(job):
 try:return run(job)
 except Exception as exc:
  model,case,_=job;out=ROOT/'runs/screen'/model/case
  receipt_path=out/'launch.json'
  receipt=json.loads(receipt_path.read_text(encoding='utf-8')) if receipt_path.exists() else {'case_id':case,'model_requested':model}
  receipt.update(status='runtime_error',runtime_error=str(exc),formal_claim_eligible=False)
  write(out/'runtime-error.json',receipt)
  print(json.dumps({'model':model,'case':case,'status':'runtime_error','error':str(exc)}),flush=True)
  return receipt
def main():
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--models',nargs='+',default=['gpt-6.1-sol','gpt-6-astra']);p.add_argument('--cases',nargs='+',default=['H'+str(i)for i in range(1,10)]);p.add_argument('--workers',type=int,default=4);p.add_argument('--timeout',type=int,default=600);a=p.parse_args()
 jobs=[(m,c,a.timeout) for c in a.cases for m in a.models]
 if not a.execute:print(json.dumps({'scheduled':len(jobs),'jobs':jobs,'executed':False}));return
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers)as pool:
  results=list(pool.map(safe_run,jobs))
 write(ROOT/'runs/SCREEN-TERMINAL.json',{'scheduled':len(jobs),'results':results})
if __name__=='__main__':main()
