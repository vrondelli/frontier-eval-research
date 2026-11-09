"""Record clean/coached initial payload evidence without echoing private memory output."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];rows=[]
for namespace in ['clean_screen','clean_screen_v2']:
    for path in(ROOT/'runs'/namespace).rglob('launch.json'):
        receipt=json.loads(path.read_text(encoding='utf-8'));inventory=receipt['input_inventory']
        transcript=path.parent/'transcript.jsonl';memory=[];metadata=[];threads=[]
        if transcript.exists():
            for line in transcript.read_text(encoding='utf-8').splitlines():
                try:event=json.loads(line)
                except ValueError:continue
                if event.get('type')=='thread.started':threads.append(event.get('thread_id'))
                if event.get('type')!='item.completed':continue
                item=event.get('item',{});command=item.get('command','')
                if re.search(r'memories|MEMORY\.md',command,re.I):
                    memory.append({'event_id':item.get('id'),'command_sha256':hashlib.sha256(command.encode()).hexdigest(),
                                   'output_sha256':hashlib.sha256(item.get('aggregated_output','').encode()).hexdigest()})
                if re.search(r'(Get-Content|cat |read_text).*(PROVENANCE|MANIFEST)',command,re.I):metadata.append(item.get('id'))
        unexpected=[name for name in inventory if name!='prompt.md'and not name.startswith('input/')]
        rows.append({'receipt':str(path.relative_to(ROOT)),'model':receipt['model_requested'],'case':receipt['case_id'],
                     'condition':receipt['condition'],'status':receipt.get('status','live'),'thread_ids':threads,
                     'initial_payload_paths':list(inventory),'unexpected_initial_payload':unexpected,
                     'source_preflight':receipt.get('source_preflight'),'global_memory_search_events':memory,
                     'metadata_read_command_events':metadata,
                     'scope':'No staged provenance/manifest payload. Global runtime context and external memory are separate possible exposures.'})
report={'model_calls':0,'reviews':rows,'all_initial_payloads_only_prompt_and_input':all(not r['unexpected_initial_payload']for r in rows)}
(ROOT/'grades/audit-review/CLEAN-CONTEXT-REVIEW.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'launches':len(rows),'all_payloads_clean':report['all_initial_payloads_only_prompt_and_input']}))
