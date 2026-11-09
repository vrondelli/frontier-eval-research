"""Replay the saved Sol-created E1 grader in a nested Linux filesystem sandbox."""
import argparse,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parent
def inventory(p):return {f.relative_to(p).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for f in p.rglob('*')if f.is_file()and not f.is_symlink()and '__pycache__'not in f.parts}
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,default=ROOT/'replays/H1-SOL-REPLAY.json');a=p.parse_args()
 package=ROOT/'runs/screen/gpt-6.1-sol/H1/delivery';before=inventory(package);rows=[]
 manifest=json.loads((ROOT/'owner/cases/manifest.json').read_text());case=next(c for c in manifest['cases']if c['case_id']=='H1')
 for control in case['controls']:
  source=ROOT/control['path']
  script="import json;from evaluation.grader import grade;c=json.load(open('/control.json'));print(json.dumps(grade({'task_id':'E1','code':c['code'],'explanation':'Owner-authored executable control; prose is independently reviewed.'})))"
  cmd=['bwrap','--die-with-parent','--unshare-all','--cap-drop','ALL','--clearenv','--ro-bind','/usr','/usr','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--symlink','usr/bin','/bin','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8','--ro-bind',str(package),'/subject','--ro-bind',str(source),'/control.json','--chdir','/subject','/usr/bin/python3','-B','-c',script]
  result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
  report=json.loads(result.stdout)if result.returncode==0 else {}
  status=report.get('formal_status');valid=status in ('pass','fail');actual=status=='pass'if valid else None
  rows.append({'control':control['id'],'expected_pass':control['expected_pass'],'actual_pass':actual,'valid':valid,'command':cmd,'exit_code':result.returncode,'report':report,'stderr':result.stderr})
 result={'kind':'independent_root_full_grader_replay','model':'gpt-6.1-sol','case_id':'H1','condition':'minimal_reconstruction_with_metadata_context','package_unchanged':before==inventory(package),'package_hashes':before,'checks':rows,'false_rejects':sum(r['valid']and r['expected_pass']and not r['actual_pass']for r in rows),'false_accepts':sum(r['valid']and not r['expected_pass']and r['actual_pass']for r in rows),'invalid':sum(not r['valid']for r in rows),'interpretation':'Original E1 and solver-only staged views omit required accepted literal; supplied owner reference returning applied is rejected despite correct task behavior.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k]for k in ['false_rejects','false_accepts','invalid','package_unchanged']}))
 return 0 if result['false_rejects']==1 and result['false_accepts']==0 and result['invalid']==0 and result['package_unchanged']else 1
if __name__=='__main__':raise SystemExit(main())
