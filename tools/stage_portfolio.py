#!/usr/bin/env python3
"""Stage the curated portfolio and every exact release member for review.
Frozen subject .gitignore files must not hide hash-bound release evidence.
No commit, remote, push or archive mutation is performed.
"""
from pathlib import Path
import hashlib,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1]
zpath=ROOT/'releases/eval-author-meta-eval-scored-v2.zip'
assert hashlib.sha256(zpath.read_bytes()).hexdigest()=='fb4fca7b22311573f65337f83fb17ad63fa0cce4225505f2727ffc6506cf1c45'
paths=['README.md','AGENTS.md','AI-ASSISTANCE.md','RIGHTS.md','.gitignore','.gitattributes','docs','data','evidence','releases','tools']
subprocess.run(['git','-C',str(ROOT),'add','--',*paths],check=True)
with zipfile.ZipFile(zpath) as z:
 members=[]
 for info in z.infolist():
  if info.is_dir():continue
  p=Path(info.filename)
  assert not p.is_absolute() and '..' not in p.parts
  member='meta-eval/'+info.filename
  assert (ROOT/member).is_file(),member
  members.append(member)
subprocess.run(['git','--literal-pathspecs','-C',str(ROOT),'add','--force','--pathspec-from-file=-','--pathspec-file-nul'],input=('\0'.join(members)+'\0').encode(),check=True)
print(f'Staged curated files plus all {len(members)} exact release files. No commit or push.')
