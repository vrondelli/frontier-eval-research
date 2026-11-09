"""Verify sanitization provenance and absence of observed memory-registry output lines."""
import hashlib
import json
from pathlib import Path
import re
import zipfile
import io

ROOT=Path(__file__).resolve().parents[2]
archive_path=ROOT/'release/eval-author-meta-eval.zip'
private_lines=set()
for transcript in (ROOT/'runs').rglob('transcript.jsonl'):
    for line in transcript.read_text(encoding='utf-8').splitlines():
        try:event=json.loads(line)
        except ValueError:continue
        item=event.get('item',{})
        if not re.search(r'memories|MEMORY\.md',item.get('command',''),re.I):continue
        for fragment in item.get('aggregated_output','').splitlines():
            fragment=fragment.strip()
            if re.match(r'^\d+[:-]',fragment)and len(fragment)>60:private_lines.add(fragment)
with zipfile.ZipFile(archive_path)as archive:
    names=archive.namelist();privacy=json.loads(archive.read('PRIVACY-REDACTIONS.json'))
    mismatches=[]
    for record in privacy['redactions']:
        source=ROOT/record['path']
        if hashlib.sha256(source.read_bytes()).hexdigest()!=record['original_sha256']:mismatches.append(record['path']+':original')
        if hashlib.sha256(archive.read(record['path'])).hexdigest()!=record['sanitized_sha256']:mismatches.append(record['path']+':sanitized')
    leaks=[];nested_errors=[];nested_hash_mismatches=[]
    if'NESTED-ARCHIVE-REVIEW.json'in names:
        nested_review=json.loads(archive.read('NESTED-ARCHIVE-REVIEW.json'))
        for record in nested_review['model_delivered_archives']:
            if hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest()!=record['original_sha256']:nested_hash_mismatches.append(record['path']+':original')
            if hashlib.sha256(archive.read(record['path'])).hexdigest()!=record['public_sha256']:nested_hash_mismatches.append(record['path']+':public')
    def strings(node):
        if isinstance(node,str):yield node
        elif isinstance(node,dict):
            for value in node.values():yield from strings(value)
        elif isinstance(node,list):
            for value in node:yield from strings(value)
    def content(name,data,depth=0):
        try:yield name,data.decode('utf-8')
        except UnicodeDecodeError:pass
        if name.lower().endswith('.zip'):
            if depth>=3:nested_errors.append(name+':depth_limit');return
            try:
                with zipfile.ZipFile(io.BytesIO(data))as nested:
                    infos=nested.infolist()
                    if len(infos)>5000 or sum(i.file_size for i in infos)>100_000_000:raise ValueError('member/size limit')
                    for member in infos:
                        if not member.is_dir():yield from content(name+'!/'+member.filename,nested.read(member),depth+1)
            except (ValueError,RuntimeError,zipfile.BadZipFile)as error:nested_errors.append(name+':'+str(error))
    texts=[]
    for name in names:texts.extend(content(name,archive.read(name)))
    for name,text in texts:
        corpus=[text]
        try:corpus.extend(strings(json.loads(text)))
        except ValueError:
            for line in text.splitlines():
                try:corpus.extend(strings(json.loads(line)))
                except ValueError:pass
        for fragment in private_lines:
            if any(fragment in item for item in corpus):leaks.append({'path':name,'private_line_sha256':hashlib.sha256(fragment.encode()).hexdigest()})
report={'schema_version':'eval-author-release-privacy-check/v1','archive_sha256':hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        'redacted_files':len(privacy['redactions']),'redaction_hash_mismatches':mismatches,
        'nested_archive_hash_mismatches':nested_hash_mismatches,'nested_archive_scan_errors':nested_errors,
        'observed_private_memory_lines_checked':len(private_lines),'observed_private_line_leaks':leaks,
        'original_logs_changed_by_packaging':False,
        'scope':'Targeted observed-memory-output check, not universal confidential-data detection.'}
(ROOT/'grades/audit-review/RELEASE-PRIVACY-CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
raise SystemExit(bool(mismatches or leaks or nested_errors or nested_hash_mismatches))
