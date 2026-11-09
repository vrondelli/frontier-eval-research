"""Private-original custody census derived from the six fixed cohort policies."""
import csv,hashlib,io,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def expected_attempts():
    rows=[]
    def add(cohort,policy,model,case,folder,draw=None):
        rows.append({'attempt_id':cohort+'/'+model+'/'+case+('/draw'+str(draw)if draw else''),
                     'cohort':cohort,'policy':policy,'model':model,'case':case,'folder':folder})
    policy='protocol/RUN-POLICY.json';p=load(ROOT/policy)
    for case in p['screen']['case_ids']:
        for model in p['models']:add('screen',policy,model,case,f'runs/screen/{model}/{case}')
    for name,cohort,namespace in [('CONFIRMATION-H1-ADMISSION.json','confirmation_H1','confirmation'),
                                   ('CONFIRMATION-H6-ADMISSION.json','confirmation_H6','confirmation'),
                                   ('H1-BUDGET-DIAGNOSTIC-ADMISSION.json','budget_H1','budget-diagnostic')]:
        policy='protocol/'+name;p=load(ROOT/policy)
        for model in p['models']:
            for case in p['cases']:
                for draw in range(1,p.get('draws',p.get('additional_draws',0))+1):add(cohort,policy,model,case,f'runs/{namespace}/{model}/{case}/draw{draw}',draw)
    for name,cohort,namespace in [('CLEAN-HIT-DIAGNOSTIC-POLICY.json','clean_hit','clean_screen'),
                                ('COACHED-HIT-DIAGNOSTIC-POLICY.json','coached_hit','clean_screen_v2/coached')]:
        policy='protocol/'+name;p=load(ROOT/policy)
        for job in p['jobs_sequential']:add(cohort,policy,job['model'],job['case'],f'runs/{namespace}/{job["model"]}/{job["case"]}')
    return rows
def inventory(root):
    result={};links={}
    if root.is_symlink():return {},{'ROOT':str(root.readlink())}
    for path in root.rglob('*'):
        key=path.relative_to(root).as_posix()
        if path.is_symlink():links[key]=str(path.readlink())
        elif path.is_file():result[key]={'sha256':sha(path),'bytes':path.stat().st_size}
    return result,links
def main():
    expected=expected_attempts();assert len(expected)==31 and len({x['attempt_id']for x in expected})==31
    reviews=[]
    for entry in expected:
        folder=ROOT/entry['folder'];launch_path=folder/'launch.json';row=dict(entry)
        row['policy_sha256']=sha(ROOT/entry['policy'])
        if not launch_path.exists():row['status']='not_launched';reviews.append(row);continue
        launch=load(launch_path);recovery=load(folder/'RECOVERY.json')if(folder/'RECOVERY.json').exists()else None
        packet=ROOT/'packets'/('coached'if entry['cohort']=='coached_hit'else'primary')/entry['case']
        expected_input={p.relative_to(packet).as_posix():sha(p)for p in packet.rglob('*')if p.is_file()and not p.is_symlink()}
        if entry['cohort']in['clean_hit','coached_hit']:
            expected_input={k:v for k,v in expected_input.items()if k=='prompt.md'or k.startswith('input/')}
        initial=launch.get('input_inventory',{})
        row['initial_payload_matches_condition_packet']=initial==expected_input
        row['initial_unexpected_paths']=sorted(set(initial)-set(expected_input))
        row['staged_metadata_payload']=[k for k in initial if k in ['PROVENANCE.json','MANIFEST.json']]
        row['stdin_matches_newline_normalized_condition_prompt']=launch.get('prompt_sha256')==hashlib.sha256((packet/'prompt.md').read_text(encoding='utf-8').encode()).hexdigest()
        error=folder/'runtime-error.json';row.update(pid=launch.get('pid'),condition=launch.get('condition'),
            native_exit_code=launch.get('exit_code','not_persisted'),launch_sha256=sha(launch_path),
            recorded_process_status=launch.get('status','not_persisted'),raw_runtime_fault_retained=error.exists())
        transcript=folder/'transcript.jsonl';threads=[];terminal=[];last_message=None;invalid=0
        if transcript.exists():
            row['transcript_sha256']=sha(transcript)
            if'transcript_sha256'in launch:
                row['raw_transcript_hash_equals_recorded_field']=row['transcript_sha256']==launch['transcript_sha256']
                if launch.get('condition')in['coached_clean_capture_v2','clean_staging_capture_v2']:
                    row['recorded_prearchive_hash_basis']='UTF8stdout_text_before_Windows_CRLF_file_encoding'
                    row['transcript_matches_prearchive_hash']=hashlib.sha256(transcript.read_text(encoding='utf-8').encode()).hexdigest()==launch['transcript_sha256']
                else:
                    row['recorded_prearchive_hash_basis']='raw_file_bytes'
                    row['transcript_matches_prearchive_hash']=row['raw_transcript_hash_equals_recorded_field']
            else:row['transcript_matches_prearchive_hash']='no_prearchive_hash_recorded'
            with transcript.open(encoding='utf-8')as stream:
                for line in stream:
                    try:event=json.loads(line)
                    except ValueError:invalid+=1;continue
                    kind=event.get('type')
                    if kind=='thread.started':threads.append(event.get('thread_id'))
                    if kind in['turn.completed','turn.failed']:terminal.append(kind)
                    if kind=='item.completed'and event.get('item',{}).get('type')=='agent_message':last_message=event['item'].get('text')
        row.update(thread_ids=threads,native_terminal_events=terminal,invalid_json_lines=invalid)
        final=folder/'final.txt'
        row['final_present']=final.exists()
        if final.exists():
            row['final_sha256']=sha(final)
            row['final_matches_last_native_message']=(final.read_text(encoding='utf-8').strip()==last_message.strip())if last_message is not None else'no_native_message'
            if recovery and recovery.get('native_final_sha256'):row['final_matches_recovery_hash']=sha(final)==recovery['native_final_sha256']
        state=launch.get('status','running')
        if recovery:
            row['recovery_sha256']=sha(folder/'RECOVERY.json');row['recovery_native_status']=recovery.get('native_terminal_status','see_terminal_events')
            state='recovered_completed'if recovery.get('native_turn_completed_event')else'captured_snapshot_native_unknown'
        elif state=='running'and error.exists():state='runtime_error'
        if state=='completed'and'turn.completed'not in terminal:state='process_completed_without_completed_turn'
        row['status']=state
        delivery=folder/'delivery'
        if delivery.exists():
            actual,links=inventory(delivery);row['actual_regular_file_count']=len(actual);row['actual_symlinks']=links
            record=recovery.get('inventory')if recovery else launch.get('capture_inventory',launch.get('output_inventory'))
            expected_files={};expected_links={}
            if record:
                for name,value in record.items():
                    if isinstance(value,str):expected_files[name]=value
                    elif 'symlink'in value:expected_links[name]=value['symlink']
                    elif value.get('kind')=='symlink':expected_links[name]=value['target']
                    elif 'sha256'in value:expected_files[name]=value['sha256']
                expected_links.update(launch.get('output_symlinks',{}))
                missing=sorted(set(expected_files)-set(actual));extra=sorted(set(actual)-set(expected_files))
                modified=sorted(name for name in set(actual)&set(expected_files)if actual[name]['sha256']!=expected_files[name])
                row.update(expected_regular_file_count=len(expected_files),missing_expected_files=missing,
                           modified_expected_files=modified,extra_regular_files=extra,extra_cache_files=[x for x in extra if'__pycache__'in x or x.endswith('.pyc')],
                           all_recorded_file_bytes_match=not missing and not modified,
                           exact_regular_inventory_match=not missing and not modified and not extra,
                           symlinks_match_record=links==expected_links,
                           full_recorded_delivery_inventory_match=not missing and not modified and not extra and links==expected_links)
            else:row['delivery_inventory_binding']='no_output_inventory_or_recovery_record'
            row['input_deltas']={'modified':[name for name,value in initial.items()if name in actual and actual[name]['sha256']!=value],
                                 'missing':[name for name in initial if name not in actual],
                                 'added_regular_file_count':len(set(actual)-set(initial)),
                                 'interpretation':'Observed changes only. A violation requires the applicable public preservation rule; not assumed here.'}
        else:row['delivery_present']=False
        reviews.append(row)
    statuses={}
    for row in reviews:statuses[row['status']]=statuses.get(row['status'],0)+1
    failures=[r['attempt_id']for r in reviews if r.get('all_recorded_file_bytes_match')is False or r.get('symlinks_match_record')is False]
    extra=[{'attempt_id':r['attempt_id'],'extra_regular_files':r.get('extra_regular_files',[])}for r in reviews if r.get('extra_regular_files')]
    payload=[r['attempt_id']for r in reviews if r.get('initial_payload_matches_condition_packet')is False or r.get('stdin_matches_newline_normalized_condition_prompt')is False]
    thread_ids=[thread for r in reviews for thread in r.get('thread_ids',[])if thread]
    result={'schema_version':'eval-author-all-attempt-private-custody/v1','model_calls':0,'expected_attempts':len(expected),
            'attempts_derived_from_fixed_policies':True,'statuses':statuses,'bound_original_byte_failures':failures,
            'extra_delivery_files':extra,'condition_input_mismatches':payload,
            'actual_symlink_count':sum(len(r.get('actual_symlinks',{}))for r in reviews),
            'terminal_attempts_without_output_inventory_binding':[r['attempt_id']for r in reviews if r['status']not in['not_launched','running']and'all_recorded_file_bytes_match'not in r],
            'terminal_attempts_without_transcript':[r['attempt_id']for r in reviews if r['status']not in['not_launched','running']and'transcript_sha256'not in r],
            'recorded_thread_ids':len(thread_ids),'unique_thread_ids':len(set(thread_ids)),
            'final_text_mismatches':[r['attempt_id']for r in reviews if r.get('final_matches_last_native_message')is False],
            'invalid_transcript_json_cases':[r['attempt_id']for r in reviews if r.get('invalid_json_lines',0)],
            'prearchive_transcript_hash_mismatches':[r['attempt_id']for r in reviews if r.get('transcript_matches_prearchive_hash')is False],
            'raw_file_vs_recorded_text_hash_differences':[r['attempt_id']for r in reviews if r.get('raw_transcript_hash_equals_recorded_field')is False],
            'input_change_cases':[{'attempt_id':r['attempt_id'],'deltas':r['input_deltas']}for r in reviews if r.get('input_deltas',{}).get('modified')or r.get('input_deltas',{}).get('missing')],
            'attempts':reviews,
            'audit_scope':'Private original deliveries/transcripts. Public release has intentional memory redactions and cache exclusions; assess it with RELEASE-MANIFEST.json and PRIVACY-REDACTIONS.json instead of expecting identical file sets.',
            'terminal_census_complete':all(r['status']not in['not_launched','running']for r in reviews)}
    (ROOT/'grades/audit-review/ALL-ATTEMPT-CUSTODY.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Private-original attempt custody','',f'Expected attempts derived from fixed policies: **{len(expected)}**.',
           '',f'Statuses: `{json.dumps(statuses,sort_keys=True)}`.',
           '',f'Bound byte failures: {len(failures)}. Extra-file cases: {len(extra)}. Initial condition-payload mismatches: {len(payload)}.',
           '', 'This inventories private original evidence. Public ZIP memory redactions and cache exclusions are deliberate release transformations, verified by separate release manifests.',
           '', '| Attempt | Status | Bound bytes | Exact inventory | Input changes | Raw runtime fault |',
           '| --- | --- | --- | --- | ---: | --- |']
    for row in reviews:
        delta=row.get('input_deltas',{});changes=len(delta.get('modified',[]))+len(delta.get('missing',[]))
        lines.append(f'| {row["attempt_id"]} | {row["status"]} | {row.get("all_recorded_file_bytes_match","pending")} | {row.get("full_recorded_delivery_inventory_match","pending")} | {changes} | {row.get("raw_runtime_fault_retained",False)} |')
    lines+=['','Input changes are observations; a preservation violation requires the applicable public instruction. Unknown native turns remain unknown even when a stopped snapshot was recovered. Native exit codes absent from original receipts are never inferred.','']
    (ROOT/'grades/audit-review/ALL-ATTEMPT-CUSTODY.md').write_text('\n'.join(lines))
    print(json.dumps({k:v for k,v in result.items()if k not in['attempts','audit_scope']}))
if __name__=='__main__':main()
