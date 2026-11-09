"""Independent paired literal intervention on the unchanged completed Sol H1 eval."""
import json,hashlib,subprocess,tempfile
from pathlib import Path
B=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
P=B/'runs/screen/gpt-6.1-sol/H1/delivery'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={p.relative_to(P).as_posix():sha(p) for p in P.rglob('*') if p.is_file()}
original=json.loads((B/'owner/cases/H1/correct_applied.json').read_text())['code']
assert "status = 'applied' if changed else 'rejected'" in original
normalized=original.replace("status = 'applied' if changed else 'rejected'","status = 'accepted' if changed else 'rejected'")
base=['bwrap','--die-with-parent','--unshare-all','--cap-drop','ALL','--clearenv','--ro-bind','/usr','/usr','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--symlink','usr/bin','/bin','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8']
code="import json;from evaluation.grader import grade; c=json.load(open('/control.json'));r=grade({'task_id':'E1','code':c['code'],'explanation':'Independent AI-reviewer synthetic paired control; source behavior differs only in success status literal.'});print(json.dumps(r))"
receipts=[]
with tempfile.TemporaryDirectory(prefix='h1-independent-pair-') as temp:
 for name,source in [('applied',original),('accepted',normalized)]:
  control=Path(temp)/(name+'.json');control.write_text(json.dumps({'code':source}))
  cmd=base+['--ro-bind',str(P),'/subject','--ro-bind',str(control),'/control.json','--chdir','/subject','/usr/bin/python3','-B','-c',code]
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
  r={'success_literal':name,'control_code_sha256':hashlib.sha256(source.encode()).hexdigest(),'exit_code':p.returncode,'stderr':p.stderr,'command':cmd}
  try:r['grade']=json.loads(p.stdout)
  except ValueError:r['stdout']=p.stdout
  receipts.append(r)
after={p.relative_to(P).as_posix():sha(p) for p in P.rglob('*') if p.is_file()}
result={'kind':'independent_literal_only_paired_full_grader_replay','reviewer_type':'AI_reviewer_not_human','model':'gpt-6.1-sol','case_id':'H1','one_literal_intervention':True,'package_unchanged':before==after,'receipts':receipts}
(OUT/'H1-SOL-LITERAL-PAIR.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'package_unchanged':before==after,'grades':[{k:r[k]for k in ['success_literal','exit_code']}|{'formal_status':r.get('grade',{}).get('formal_status')} for r in receipts]}))
