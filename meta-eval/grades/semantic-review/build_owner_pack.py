"""Readable owner review index; pending review remains pending."""
import json,datetime,os
from pathlib import Path
B=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
names={'H1':'Ledger task and hidden status literal','H2':'Original rubric-author task','H3':'Intake-time prediction evaluation','H4':'Ferry code and own-test quality','H5':'Query semantics, work and isolation','H6':'Exact numeric export','H7':'Field evidence and output shape','H8':'Snapshot evidence discovery','H9':'Research synthesis and counts'}
models=['gpt-6.1-sol','gpt-6-astra'];rows=[]
def link(p,label):
 return '['+label+']('+os.path.relpath(p,HERE).replace('\\','/')+')' if p.exists() else label+' (pending)'
for case in names:
 packet=B/'packets/primary'/case;prov=json.loads((packet/'PROVENANCE.json').read_text())
 row={'case_id':case,'name':names[case],'condition':prov['condition_id'],'human_review_status':'pending','models':{},'semantic_reports':[]}
 for model in models:
  run=B/'runs/screen'/model/case;p=run/'launch.json';r=json.loads(p.read_text()) if p.exists() else {}
  recovery_path=run/'RECOVERY.json';recovery=json.loads(recovery_path.read_text(encoding='utf8'))if recovery_path.exists()else{}
  error_path=run/'runtime-error.json';runtime_error=json.loads(error_path.read_text(encoding='utf8'))if error_path.exists()else{}
  row['models'][model]={'status':recovery.get('recovered_status',r.get('status',runtime_error.get('status','in_progress' if p.exists() else 'not_started'))),'raw_controller_status':runtime_error.get('status',r.get('status')),'exit_code':r.get('exit_code',recovery.get('native_exit_code')),'native_turn_completed_event':recovery.get('native_turn_completed_event'),'delivery_custody_verified':recovery.get('delivery_custody_verified'),'formal_claim_eligible':r.get('formal_claim_eligible',False)}
 for p in HERE.glob(case+'*.json'):
  if p.name.endswith('INDEPENDENT.json') or p.name in [case+'-'+m+'.json' for m in models]:row['semantic_reports'].append(p.name)
 rows.append(row)
terminal_path=B/'runs/SCREEN-TERMINAL.json';terminal=json.loads(terminal_path.read_text(encoding='utf8'))if terminal_path.exists()else{}
results_path=B/'RESULTS.json';results=json.loads(results_path.read_text(encoding='utf8'))if results_path.exists()else{}
human_path=HERE/'HUMAN-REVIEW-STATUS.json';human=json.loads(human_path.read_text(encoding='utf8'))if human_path.exists()else{'status':'pending','human_review_completed':False}
now=datetime.datetime.now(datetime.timezone.utc).isoformat();(HERE/'OWNER-REVIEW-STATUS.json').write_text(json.dumps({'snapshot_utc':now,'reviewer_type':'AI_prepared_review_pack_not_human_review','human_review':human,'initial_screen_terminal':bool(terminal),'raw_terminal_scheduled':terminal.get('scheduled'),'cohorts':results.get('cohorts',[]),'cases':rows},indent=2)+'\n',encoding='utf8')
lines=['# Owner review pack: GPT-created evaluations','',f'Status snapshot: {now}. This is a reading index prepared by an AI reviewer. **Human review is pending for every case.** It does not certify all artifacts or replace raw results. Re-run `build_owner_pack.py` to refresh live attempt statuses.','',
'Start with '+link(B/'DESIGN.md','the design')+', '+link(B/'FREEZE.json','the frozen screen')+' and '+link(B/'protocol/RUN-POLICY.json','the run policy')+'. Inspect original/reconstructed instruction provenance before judging outcomes. An exact user prompt under a changed runtime is not a full-context replication.','',
'The two immediate review questions are: **H1:** do the actual solver-visible views require the success word `accepted`, and is rejecting otherwise correct `applied` behavior justified? **H6:** does the original exact-number contract permit the zero spelling `0e10000000000000000000`, with counts1and3, and should a grader accept a CLI that fails it? The evidence for both is explained below. Review those task meanings first; use the nine-case table as a reference.', '',
'**Review the task meanings and grading criteria now; final recurrence counts can wait.** All admitted author attempts have finished; human review of task meanings remains separate from approval of recurrence statistics. The original18-attempt controller is terminal. Its raw results retain13ordinary completions,3timeouts and2H9copy/archive errors. Both H9native final outputs were recovered without new actor calls, with completed-turn events and verified delivery custody; native exit codes were not persisted before the copy fault. See each recovery receipt. Fresh H1/H6 confirmations are terminal; their separate outcomes appear below. Human task-meaning and criterion review remains pending.','',
'| Case | Author prompt and exact input | Owner checks | Sol attempt | Astra attempt | AI semantic review | Human review |','| --- | --- | --- | --- | --- | --- | --- |']
for r in rows:
 c=r['case_id'];packet=B/'packets/primary'/c
 inp=link(packet/'prompt.md',c+' prompt')+'; '+link(packet/'PROVENANCE.json',r['condition'])+'; '+link(packet/'MANIFEST.json','input hashes')
 checks=B/'owner/cases'/c if (B/'owner/cases'/c).exists() else B/'owner/audit_cases'/c
 owner=link(checks,'controls')+'; '+link(B/('owner/audit_cases/check.py' if c in ['H8','H9'] else 'owner/check_cases.py'),'checker')+'; '+link(B/'owner/contracts'/(c+'.md'),'source-license matrix')
 state=[]
 for m in models:
  run=B/'runs/screen'/m/c;s=r['models'][m]['status'];entry=link(run/('RECOVERY.json'if(run/'RECOVERY.json').exists()else'launch.json'),s)
  if(run/'runtime-error.json').exists():entry+='; '+link(run/'runtime-error.json','raw copy error')
  if (run/'delivery').exists():entry+='; '+link(run/'delivery','delivery')
  if (run/'final.txt').exists():entry+='; '+link(run/'final.txt','final')
  state.append(entry)
 review='; '.join(link(HERE/p,p) for p in r['semantic_reports']) or 'Pending'
 lines.append('| '+c+' '+r['name']+' | '+inp+' | '+owner+' | '+state[0]+' | '+state[1]+' | '+review+' | **Pending** |')
lines += ['', '## Current fixed31-attempt result index', '',
'The owner explicitly said **“Not reviewed yet; keep building.”** No AI review or generated form supplies owner signoff. Original instruction accounting is one recovered exact-text job (H2), eight reconstructed jobs; none recreates the full historical session context. See '+link(B/'RESULTS.md','current results')+', '+link(B/'ADJUDICATION.md','adjudication')+' and '+link(HERE/'HUMAN-REVIEW-STATUS.json','actual human review status')+'.', '',
'| Cohort | Attempts | Capture status | Semantic status |', '|---|---:|---|---|']
for cohort in results.get('cohorts',[]):
 fmt=lambda d:'; '.join(str(v)+' '+k for k,v in d.items())
 lines.append('| '+cohort['id']+' | '+str(cohort['attempts'])+' | '+fmt(cohort['effective_status_counts'])+' | '+fmt(cohort['semantic_outcome_counts'])+' |')
lines += ['', 'Initial screen and each fresh condition stay separate. H1same-condition600s confirmations timed out3/3; the1200s budget diagnostic has three completed false rejections. H6same-condition confirmations have one fresh completed false green, one completed real-defect rejection and one capture with unknown native terminal. Do not pool these selected draws into a global reliability rate.', '',
'Clean H1 uses the same single-sentence instruction, with CRLF-to-LF normalization accounting for raw-file versus stdin hashes; it adds no quality boundary. Clean staging removes packet metadata. Coached staging adds an explicit quality checklist and remains separate. Native memory/context is possible in both conditions.', '',
'| Fresh attempt | Capture | Reviewed outcome | Evidence |','|---|---|---|---|']
for r in results.get('attempts',[]):
 if r['cohort']=='initial_screen':continue
 proof=r.get('review_evidence')or([r['launch']]if r.get('launch')else[])
 lines.append('| '+r['id']+' | '+r['effective_status']+' | '+r['semantic_outcome']+': '+r['semantic_summary']+' | '+'; '.join(link(B/p,p)for p in proof)+' |')
lines += ['', '## Two completed seed results to review', '',
'The completed Sol H1 eval rejects a correct `applied` Service while accepting the identical service after changing only that success literal to `accepted`. The operator README mentions `accepted`, but its own documented solver-only initial/final views and question command omit the literal. Review '+link(HERE/'H1-INDEPENDENT.json','the independent exposure analysis')+', '+link(HERE/'H1-SOL-LITERAL-PAIR.json','the full-grader paired replay')+' and '+link(B/'grades/root-review/H1-SOL-REPLAY.json','the separate five-control root replay')+'. The conclusion is one verified false rejection in a reconstructed-authoring Sol attempt. Astra H1 is a timeout snapshot and is not another completed failure.', '',
'The two staged views are created by '+link(B/'runs/screen/gpt-6.1-sol/H1/delivery/evaluation/protocol.py','the delivered protocol')+': initial_view sends original F1-F5 plus runtime limits; reveal sends original input/E1.md. Neither adds the success literal. '+link(B/'runs/screen/gpt-6.1-sol/H1/delivery/README.md','The delivered README')+' instructs the operator to send ONLY those views. Its separate accepted-only clarification would be legitimate if included in solver exposure; the documented views omit it. Paired full-grader result: applied => fail; accepted => pass; all other Service code identical.', '',
'**H6, Astra: a known-bad numeric CLI receives84/84.** The original public task allows exact integer-valued JSON number spellings. The small input token `0e10000000000000000000` denotes zero. Its singleton count must be1; a three-entry version must be3. The saved Decimal-based Luna CLI fails that input with `decimal.InvalidOperation`, while canonical0 returns the correct counts. The completed new Astra eval nevertheless accepts that same CLI on all84cases. Read '+link(B/'grades/root-review/H6-ASTRA-REPLAY.json','the independent root replay')+', '+link(B/'grades/owner-review/ASTRA-H6-PAIRED-REPRODUCER.json','the paired native reproducer')+' and '+link(B/'grades/owner-review/H6-REVIEW.md','the qualification review')+'. This is a coverage false green in one completed reconstructed-authoring attempt. Sol has a different symbolic-zero implementation; this evidence does not establish its failure. Fresh confirmations are separate and their final counts are not requested for approval here.', '',
'H2 reviewed outputs meet the checked original rubric-writing requirements. H3 label-lookup probes produce `fail` (Astra) or `needs_review` (Sol), so they do not show a completed semantic false pass. Both H3 packages disclose their unqualified OS isolation; a public train-file read alone is not private owner-label theft. See '+link(HERE/'CONTEXT-DEVIATIONS.json','H2 context deviations')+' and '+link(HERE/'H3-PRECONDITION.md','H3 timing interpretation')+'.', '',
'## Control qualifications you must preserve', '',
'- H4initial positives were not full-task gold: one alternate used standalone assertions despite the explicit unittest requirement, and the inherited production reference has newline/precision weaknesses. The frozen five controls are excluded for full-task judgments in '+link(B/'owner/ADJUDICATION.json','owner adjudication')+'. A separately labeled '+link(B/'owner/expansion-h4/MANIFEST.json','post-outcome successor')+' produced correct5/5finite verdicts for both new graders; do not call rejection of the old faulty positive a model failure.',
'- H6initial positives pass selected bounded probes but are not qualified for the full original numeric domain because they expand huge written exponents before count. They are excluded as full-task positive gold. The known-bad saved-CLI acceptance still supplies a valid negative coverage witness: it demonstrably fails a tiny licensed input. Broader positive acceptance stays unknown.',
'- '+link(B/'owner/semantic-successor/QUALIFICATION-PORTABLE.json','H2/H3successor component controls')+' qualify10/10selected controls after output inspection: two actual reviewed model artifacts and three clear mutants per case. This is post-outcome component evidence, not prospective gold or full-system/private-boundary qualification. Human review is still pending.',
'- H8formal228versus stored232snapshots and H9staged147regrade files versus150historical invocation events are different scopes. Source-license matrices explain the accepted alternatives. Raw duplicates and missing native exits must not be compressed into model failures.', '',
'## Human review procedure', '',
'1. Read the author prompt, input, condition provenance and delivered public task. Decide whether the check is licensed and whether an alternative output could be valid. Do not impose historical hidden literals or private rankings.',
'2. Inspect the owner reference and the exact positive/negative control. Replay the concrete witness in the qualified runtime; preserve instrument errors and timeouts as their own outcomes.',
'3. Inspect model transcript exposure and the finished files. Confirm the documented solver view contains every graded requirement; an operator README that is not sent is insufficient.',
'4. Confirm counts and claim scope: completed versus timeout; exact user instruction versus reconstructed condition; synthetic audit candidate versus actual observed model behavior; finite controls versus entire contract.',
'5. Record task-meaning and criterion decisions with specific evidence in a copy of `HUMAN-REVIEW-TEMPLATE.json`. Leave final confirmation counts and unsupported full-system claims pending. AI authors and reviewers do not satisfy human review by signing a form.', '',
'Current controls: '+link(B/'owner/cases/manifest.json','H1-H7 control manifest')+' and '+link(B/'owner/audit_cases/manifest.json','H8-H9 audit controls')+'. Expanded checks: '+link(B/'grades/owner-review/EXPANSION-STATUS.md','owner review status')+'. Evidence exposure/privacy: '+link(B/'grades/audit-review/METADATA-EXPOSURE.json','metadata exposure')+' and '+'`grades/audit-review/RELEASE-PRIVACY-CHECK.json` (external final-archive proof, bound by `release/DELIVERY.json`)'+'.']
(HERE/'OWNER-REVIEW-PACK.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
template=HERE/'HUMAN-REVIEW-TEMPLATE.json'
old=json.loads(template.read_text(encoding='utf8'))if template.exists()else{}
edited=any(old.get(k)for k in ['reviewer_name','reviewed_utc','independence_and_AI_use'])
for case in old.get('case_reviews',[]):
 for key,value in case.items():
  if key=='case_id':continue
  if isinstance(value,list)and value:edited=True
  elif isinstance(value,str)and value not in ['pending','not_applicable_no_seed_claim','unknown_not_requested_for_approval']:edited=True
untouched=not edited
if untouched:template.write_text(json.dumps({'status':'pending_actual_owner_review','reviewer_name':None,'reviewed_utc':None,'independence_and_AI_use':None,'requested_now':'Review original task meanings, licensed grading criteria, allowed alternatives and the H1/H6seed witnesses. Final confirmation counts are not being requested for approval.','final_count_review':'pending_actual_owner_review','case_reviews':[{'case_id':c,'decision':'pending','task_meaning':'pending','criterion_licenses':'pending','allowed_alternatives':'pending','positive_control_scope':'pending','negative_control_validity':'pending','exposure_and_condition':'pending','seed_witness_review':'pending'if c in ['H1','H6']else'not_applicable_no_seed_claim','full_system_qualification':'unknown_not_requested_for_approval','reproduction_receipts':[],'evidence_notes':[],'unresolved':[]} for c in names]},indent=2)+'\n',encoding='utf8')
print(json.dumps({'cases':len(rows),'human_review':'pending','statuses':{r['case_id']:{m:v['status'] for m,v in r['models'].items()} for r in rows}}))
