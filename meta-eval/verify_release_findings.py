"""Replay saved-artifact failure exhibits after clean ZIP extraction; no model calls."""
import argparse,hashlib,json,pathlib,stat,subprocess,sys,tempfile,zipfile
def main():
 p=argparse.ArgumentParser();p.add_argument('archive',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
 checks=[];before_sha=hashlib.sha256(a.archive.read_bytes()).hexdigest()
 with tempfile.TemporaryDirectory(prefix='eval-findings-clean-')as folder:
  root=pathlib.Path(folder)
  with zipfile.ZipFile(a.archive)as archive:
   for entry in archive.infolist():
    target=(root/entry.filename).resolve()
    if not target.is_relative_to(root)or stat.S_ISLNK(entry.external_attr>>16):raise ValueError('Unsafe archive member')
   archive.extractall(root)
  for script in ['verify_release.py','reproduce_h1.py','reproduce_h6.py','reproduce_h6_confirmation.py']:
   result=subprocess.run([sys.executable,'-B',str(root/script)],cwd=root,capture_output=True,text=True,timeout=300)
   checks.append({'script':script,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
 unchanged=before_sha==hashlib.sha256(a.archive.read_bytes()).hexdigest()
 report={'archive_sha256':before_sha,'archive_unchanged_during_verification':unchanged,'clean_extraction':True,'model_calls':0,'checks':checks,'all_passed':unchanged and all(c['exit_code']==0 for c in checks),'scope':'Saved immutable grader exhibits and owner checks; not fresh model inference or universal program proof.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'all_passed':report['all_passed'],'checks':len(checks),'model_calls':0}))
 return 0 if report['all_passed']else 1
if __name__=='__main__':raise SystemExit(main())
