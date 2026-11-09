#!/usr/bin/env python3
"""Offline, limited high-confidence secret/media scan. Prints no matching values."""
from pathlib import Path
import io,json,re,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
# Git's own ignore implementation defines the publication candidate set.
files=subprocess.check_output(['git','-C',str(ROOT),'ls-files','--cached','--others','--exclude-standard','-z']).decode().split('\0')
files=sorted(set(x for x in files if x))
patterns={
'openai_secret':re.compile(rb'\bsk-(?:proj-|svcacct-)[A-Za-z0-9_-]{36,}'),
'github_secret':re.compile(rb'\b(?:ghp_|gho_|ghu_|ghs_|github_pat_)[A-Za-z0-9_]{30,}'),
'aws_access_key':re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
'private_key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
'google_api_key':re.compile(rb'\bAIza[A-Za-z0-9_-]{35}\b'),
}
findings=[];checked=0;zip_entries=0;skipped=[]
def scan(label,raw,depth=0):
 global checked,zip_entries
 checked+=1
 for rule,rx in patterns.items():
  if rx.search(raw):findings.append({'path':label,'rule':rule})
 if raw.startswith(b'PK\x03\x04') and depth<4:
  try:
   with zipfile.ZipFile(io.BytesIO(raw)) as z:
    for item in z.infolist():
     if item.is_dir():continue
     if item.file_size>100_000_000:skipped.append(label+'!'+item.filename);continue
     zip_entries+=1;scan(label+'!'+item.filename,z.read(item),depth+1)
  except zipfile.BadZipFile:findings.append({'path':label,'rule':'malformed_zip'})
for rel in files:
 p=ROOT/rel
 if p.is_symlink():findings.append({'path':rel,'rule':'publication_symlink'});continue
 if not p.is_file():continue
 if p.suffix.lower() in {'.mp4','.webm','.wav','.mp3','.pfx','.p12','.pem','.key'}:findings.append({'path':rel,'rule':'media_or_key_requires_review'})
 if p.stat().st_size>100_000_000:skipped.append(rel);continue
 scan(rel,p.read_bytes())
result={'schema':'portfolio-pattern-scan/v1','candidate_files':len(files),'content_objects_scanned':checked,'nested_zip_entries_scanned':zip_entries,'findings':findings,'skipped':skipped,'all_patterns_clear':not findings and not skipped,'scope':'Limited offline secret/media patterns, not a universal privacy or rights audit. Full raw archive ignored. No matching values printed.'}
print(json.dumps(result,indent=2))
sys.exit(0 if not findings and not skipped else 1)
