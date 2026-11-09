"""Audit visible metadata/read evidence in completed native transcripts."""
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
rows=[]
for receipt_path in (ROOT/'runs/screen').glob('*/*/launch.json'):
    receipt=json.loads(receipt_path.read_text())
    transcript=receipt_path.parent/'transcript.jsonl'
    row={'model':receipt['model_requested'],'case_id':receipt['case_id'],
         'metadata_files_supplied':[p for p in receipt['input_inventory']if p in ['PROVENANCE.json','MANIFEST.json']],
         'status':receipt.get('status','live'), 'completed_transcript_available':transcript.exists(),
         'metadata_name_visible_events':[], 'possible_metadata_content_read_events':[],
         'confirmed_provenance_content_events':[]}
    if transcript.exists():
        for line in transcript.read_text(encoding='utf-8').splitlines():
            try:event=json.loads(line)
            except ValueError:continue
            if event.get('type')!='item.completed':continue
            item=event.get('item',{});command=item.get('command','');output=item.get('aggregated_output','')
            if any(name in output for name in ['PROVENANCE.json','MANIFEST.json']):
                row['metadata_name_visible_events'].append({'id':item.get('id'),'command':command})
            if re.search(r'(Get-Content|type |cat |read_text|read_bytes).*(PROVENANCE|MANIFEST)',command,re.I) or any(marker in output for marker in ['owner_only_withheld','instruction_status','No coached checklist','no coached checklist']):
                row['possible_metadata_content_read_events'].append({'id':item.get('id'),'command':command,'output_excerpt':output[:1200]})
            if any(marker in output for marker in ['"owner_only_withheld"','"instruction_status"']):
                row['confirmed_provenance_content_events'].append({'id':item.get('id'),'command':command})
    row['interpretation']='Metadata was available even without observed read. Pattern search cannot prove no access. It is added context beyond the short author instruction.'
    rows.append(row)
report={'schema_version':'eval-author-metadata-exposure/v1','frozen_packets_changed':False,'model_calls':0,
        'case_reviews':rows,'successor_requirement':'Stage prompt.md and input/ only, keep provenance/manifest outside actor workspace; label separate successor condition.'}
(ROOT/'grades/audit-review/METADATA-EXPOSURE.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'launched':len(rows),'completed_transcripts':sum(r['completed_transcript_available']for r in rows),
                  'possible_metadata_reads':sum(bool(r['possible_metadata_content_read_events'])for r in rows),
                  'confirmed_provenance_content_reads':sum(bool(r['confirmed_provenance_content_events'])for r in rows)}))
