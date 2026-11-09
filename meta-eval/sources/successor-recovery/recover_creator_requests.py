"""Targeted creator-message recovery; never modifies the frozen screen packets."""
import json,subprocess,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOTS=[Path(r'C:\Users\vlad_\.codex\sessions\2026\11'),Path(r'\\wsl.localhost\Ubuntu-26.04\home\vlad_\.codex\sessions\2026\11')]
TERMS=['g1f-query-optimizer','na01-runtime-numeric','audit_execution','NA01']
cutoff='2026-11-09T01:35:00'
found=[];scans=[]
for root in ROOTS:
 cmd=['rg','-l','-g','*.jsonl']
 for term in TERMS:cmd+=['-e',term]
 cmd+=[str(root)]
 r=subprocess.run(cmd,capture_output=True,text=True)
 files=r.stdout.splitlines();scans.append({'root':str(root),'files_matched':len(files),'rg_exit':r.returncode})
 for file in files:
  source=Path(file);digest=None
  with source.open(encoding='utf8') as stream:
   for number,line in enumerate(stream,1):
    if not any(t.lower() in line.lower() for t in TERMS):continue
    try:record=json.loads(line);p=record.get('payload',{})
    except ValueError:continue
    if record.get('timestamp','')[:19]>=cutoff:continue
    typ=p.get('type');role=p.get('role');author=p.get('author');recipient=p.get('recipient')
    if not ((typ=='message' and role=='user') or typ=='agent_message'):continue
    text='\n'.join(x.get('text','') for x in p.get('content',[]) if isinstance(x,dict))
    if not text or not any(t.lower() in text.lower() for t in TERMS):continue
    if text.startswith(('# AGENTS','<codex_internal_context','<external_codex')):continue
    # Keep candidates; do not assert an assignment is a creator task without semantic review.
    if digest is None:digest=hashlib.sha256(source.read_bytes()).hexdigest()
    found.append({'timestamp':record.get('timestamp'),'source_file':str(source),'source_file_sha256':digest,'line':number,'payload_type':typ,'role':role,'author':author,'recipient':recipient,'text':text,'classification':'unreviewed_creator_request_candidate'})
out={'status':'candidate_recovery_not_prompt_promotion','cutoff_utc':cutoff,'search_terms':TERMS,'scans':scans,'candidate_messages':found,'claim_limit':'These are source messages, not automatically exact authoring instructions; each requires identity and exposure review before a successor cut.'}
(OUT/'CREATOR-REQUEST-CANDIDATES.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'scans':scans,'candidate_messages':len(found)}))
