#!/usr/bin/env python3
"""Build human catalogue and source excerpts from the preserved local archive.
No candidate programs, model calls or network requests are executed.
"""
from pathlib import Path
from campaign_context import CONTEXT
from reader_intros import INTROS
import datetime, hashlib, json, re, os
ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'research/hackathon'
def read_json(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def put(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding='utf-8')
def js(p, obj): put(p, json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
def cell(x): return str(x).replace('|',' / ').replace('\n',' ')
def status_text(s):
    return {'completed':'Completed','timeout':'Timed out','capture_unknown_native_terminal':'Completion unknown','recovered_completed_turn_delivery':'Completed; delivery recovered'}.get(s,s)
def title(s): return re.sub(r'-20\d{6}$','',s).replace('-', ' ').capitalize()
EARLY = read_json(ARCHIVE/'complete-recap-audit-20261108/EARLY-COVERAGE.json')
PROTO = read_json(ARCHIVE/'complete-recap-audit-20261108/R1-R10-PROTOCOL-LEDGER.json')
TRANS = read_json(ARCHIVE/'complete-recap-audit-20261108/FAILURE-TRANSITIONS.json')
META = read_json(ARCHIVE/'eval-author-meta-eval-20261108/RESULTS.json')
SCORES = read_json(ROOT/'meta-eval/grades/scored-v2-final/REPORT.json')
SOURCES=[]
def excerpt(rel, out=None):
    p=ARCHIVE/rel
    if not p.is_file(): return None
    b=p.read_bytes()
    if len(b)>700000: return None
    text=b.decode('utf-8-sig',errors='replace')
    # Retain text while making old relative links explicitly historical references.
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m: m.group(0) if re.match(r'https?://',m[2]) else f'{m[1]} (historical reference: `{m[2]}`)',text)
    text=text.replace('/home/vlad_/projects/engineer-assessment/','<original-workspace>/')
    out=out or f'evidence/source-text/{rel}'
    put(ROOT/out, f'> Archived source excerpt. Original location: `{rel}`. Relative links below describe original archive paths. This copy does not assert current live status.\n\n'+text)
    SOURCES.append({'source':rel,'original_sha256':hashlib.sha256(b).hexdigest(),'public':out,'public_sha256':hashlib.sha256((ROOT/out).read_bytes()).hexdigest(),'transformations':['historical relative links rendered as text','original workspace prefix generalized','UTF-8 re-encoding','provenance header']})
    return out
# Public machine ledgers preserve original bytes. They are snapshots, not new trials.
for rel in ['complete-recap-audit-20261108/EARLY-COVERAGE.json','complete-recap-audit-20261108/R1-R10-PROTOCOL-LEDGER.json','complete-recap-audit-20261108/FAILURE-TRANSITIONS.json','original-five-rerun-20261108/RESULTS.json','verification-eval-20261108/RESULTS.json']:
    dest=ROOT/'evidence/ledgers'/rel
    dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes((ARCHIVE/rel).read_bytes())
    SOURCES.append({'source':rel,'original_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'public':dest.relative_to(ROOT).as_posix(),'public_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'transformations':[]})
for name in ['SCORED-DELIVERY.json','SCORED-CLEAN-VERIFICATION.json','SCORED-PRIVACY-CHECK.json','SCORED-LINK-CHECK.json']:
    dest=ROOT/'releases'/name;dest.write_bytes((ARCHIVE/'eval-author-meta-eval-20261108/release'/name).read_bytes())

EXTRA={
 'audit': ('Which source paths and claims were checked during hackathon preparation?', 'Supporting audit records', 'Supporting records; not an additional model experiment.', 'Retains cross-cut audit material. Use campaign-specific audits for behavioral conclusions.', 'Do not count the audit directory as an assessed model cohort.'),
 'frontier-hunt-20261106': ('Can diverse programming, judgment and governance tasks expose repeatable failures?', 'Executed adaptive multi-round campaign', 'R1-R10: 67 protocol rows / 295 counted model episodes. Later rounds have separate denominators.', 'Real lying-helper errors recur across five cuts; many finite screens pass; several apparent hits are invalidated. Stronger-model query follow-up passes. See the round and transition ledgers.', 'Do not pool adaptive rounds, call finite passes universal correctness, or use Luna-heavy counts as frontier-tier breadth.'),
 'complete-recap-audit-20261108': ('Why did failures seem to disappear, and could the tests be gamed?', 'Independent retrospective audit', 'Historical cut: 46 packages; 45 earlier packages plus frontier hunt, not current 55.', 'Synthetic cost spoof passes the old grader, but inspected stronger-model implementations really reduce work. Failures recur; treatment changes and narrow endpoints explain many compressed no-hit labels.', 'Audit and scripted controls are not additional benchmark-subject attempts. Historical 46-directory coverage is not a current 55-directory claim.'),
 'eval-author-meta-eval-20261108': ('Can GPT build a trustworthy evaluator, and can an outer evaluator expose its defects?', 'Completed software; post-hoc scored research; human review incomplete', '31 attempts: 19 completed eval-author packages, 4 supplementary outputs, 7 timeouts, 1 unknown completion; 114 native check jobs.', 'Five H1 outputs reject a correct service under a hidden literal; three H6 outputs falsely accept a faulty CLI; two of those also reject equivalent legal output zero. Eight outputs overlap across these findings. Coached H1 fixes the literal while changing scope.', 'Unknowns remain weighted. No fully human-qualified pass, no pooled failure rate, no universal inability claim.'),
 'verification-eval-20261108': ('Can stronger models repair verification under explicit, public contracts?', 'Executed verification-repair benchmark', '30 attempts: 15 Astra + 15 Sol; 1,806 case decisions.', 'All 30 completed attempts pass. No qualified frontier failure in the frozen sample. File-dot ambiguity stays an unscored lead.', 'This is explicit verifier repair, a different task from independently authoring a complete eval.'),
 'original-failure-taskpack-20261108': ('Can original failure-producing tasks be reproduced without rewriting them as verifier repair?', 'Source-bound task preparation', 'Five original tasks; no new author trials in packaging.', 'Preserves numeric CLI, quote extraction, payroll SDK, query optimization and persistent no-tool diagnosis tasks, with private review material separated.', 'The interactive task requires actual adaptive feedback, not one-turn replay of a fixed transcript.'),
 'original-task-replays-20261108': ('Do stronger models repeat failures on original quotation and payroll tasks?', 'Executed original-task follow-up', 'Four fixed initial attempts, two models by two tasks; read the original per-task results for contract probes.', 'All four attempts pass their specific original quote/date-boundary checks. A later original-contract probe confirms a Sol payroll leading-zero bug. The independent subsequent recurrence belongs to original-five-rerun, not this cohort.', 'Do not collapse original frozen finite checks and later source-licensed probes into a single pass/fail percentage.'),
 'original-five-rerun-20261108': ('Do original production-task failures recur on stronger models under preserved public tasks?', 'Executed original-five comparison plus declared transport recovery', '14 started episodes: 10 initial, 2 interrupted instrument-unknown, 2 completed payroll recovery repetitions.', 'All ten initial tasks pass. A licensed leading-zero payroll probe confirms a prior Sol bug and recurs in one of two completed fresh Sol repetitions. The other repetition passes; Astra controls pass.', 'Windows/runtime changes are disclosed. The two interrupted attempts remain unknown. One of two selected repetitions is not a prevalence estimate.'),
 'exact-original-numeric-20261108': ('Does the historical exponent-zero failure persist on stronger models solving the original bounded warehouse task?', 'Executed stronger-model pilot', 'Two planned model attempts: Astra and Sol.', 'Both warehouse pilots pass the original zero witness; no model qualifies for the conditional energy replication.', 'These are current stronger-model successes on a selected mechanism; earlier bad Luna artifacts remain bad.'),
 'exact-original-numeric-replication-20261108': ('Would a qualified warehouse failure recur on an unchanged second original numeric surface?', 'Conditional protocol; not launched', 'Zero calls: neither pilot model met the qualifying condition.', 'The predeclared conditional energy replication correctly remains unlaunched.', 'A written plan is not a completed experiment or a negative model trial.')
}
# All source directories, including unrun preparation and duplicate exports, get a row.
entries={x['directory']:dict(x) for x in EARLY['entries']}
for name, (question,kind,counts,outcome,limits) in EXTRA.items():
    entries[name]={'directory':name,'kind':kind,'question':question,'local_counts_with_units':counts,'observed_outcome':outcome,'followup_comparability_and_limits':limits,'model_tool_condition':'See source and condition matrix; do not infer immutable serving weights.'}
all_names=sorted(p.name for p in ARCHIVE.iterdir() if p.is_dir())
unknown=sorted(set(all_names)-set(entries))
assert not unknown,unknown
assert set(entries)==set(all_names),(len(entries),len(all_names))
assert set(CONTEXT)==set(all_names),('Missing editorial context',sorted(set(all_names)-set(CONTEXT)))
QUESTIONS={
'adaptive-frontier-research-20261031':'Can a model choose diagnostic actions that preserve a feasible winning continuation?',
'readiness-study-20261031':'Do the planning failures persist on fresh instances, persistent interaction, or when computation is offered?',
'frontier-run-2026-10-31':'What happens when three model aliases answer the original ten-task benchmark without answering tools?',
'frontier-run-v2-2026-10-31':'What survives a clarified contract and harder successor tasks?',
'depot-direct-run-2026-10-31':'Does committing a direct schedule expose errors hidden by returning a search program?',
'submission-failure-audit-20261101':'Do earlier failures persist when ordinary persistent computation tools are allowed?',
'architecture-oracle-validity-experiments-20261102':'Do architectural structure and repair-first policies predict or improve later maintenance outcomes?',
'assessment-evidence-screen-20261102':'Can models solve explicit evidence, novelty, identification and repair tasks?',
'criteria-adversarial-pilot-20261101':'Can adversarial claims manipulate assessment criteria or expose unstable judgments?',
'semantic-invariance-pilot-20261101':'Do equivalent answers receive stable ratings while consequential changes alter them?',
'wording-ambiguity-isolation-pilot-20261101':'How much do wording and style change decisions under fixed scoring ideas?',
'anchor-causality-pilot-20261101':'Do rating anchors remove variability, and is apparent improvement causal?',
'anchor-batch-order-pilot-20261101':'Does batch position change criterion-focused ratings?',
'anchor-boundary-repair-pilot-20261101':'Do clearer anchor boundaries improve selected regressions and fresh comparisons?',
'practical-coding-pilot-20261101':'Do practical migration, publication and shared-policy tasks expose normal-tool failures?',
'long-horizon-coding-pilot-20261101':'Do successive changes accumulate regressions in small software lineages?',
'coupling-conflict-coding-pilot-20261102':'Do interacting policy changes break earlier requirements?',
'metadata-boundary-review-20261104':'Can human reviewers qualify metadata and authority boundaries?',
'coordinator-continuation-20261105':'Can a native coordinator continue the governance task under the historical constraints?',
'coordinator-continuation-r2-20261107':'What does a later coordinator do when the owner denies permission?',
}
for key,x in entries.items():
    if 'question' not in x:
        if key in QUESTIONS:x['question']=QUESTIONS[key]
        elif key.startswith(('c08','c09','goal-priority','governance','qualification-strategy')):x['question']='Does process or governance pressure displace the stated goal, and which historical conditions are reproduced?'
        elif 'benchmark' in key:x['question']='Can the benchmark tasks, references and package checks be prepared or validated?'
        elif 'design' in key or 'discovery' in key:x['question']='What study design or task family should be tested next?'
        elif 'report' in key or 'export' in key:x['question']='How can already collected evidence be packaged or explained without counting it again?'
        else:x['question']='What does this source campaign contribute to the evaluation research?'
    for field in ['kind','local_counts_with_units','observed_outcome','followup_comparability_and_limits']: x[field]=x[field].rstrip('.')
    candidates=[e['path'] for e in x.get('evidence',[]) if e['path'].endswith('.md')]
    # Newer final reports take precedence over intentionally frozen, stale READMEs.
    candidates += [f'{key}/{n}' for n in ['REPORT.md','PROGRAM-FINDINGS.md','RESULTS-REVIEW.md','FINDINGS.md','RESULTS.md','README.md','PLAN.md','POLICY.md','DESIGN.md']]
    source=next((p for p in candidates if (ARCHIVE/p).is_file()),None)
    if key=='frontier-hunt-20261106':source='complete-recap-audit-20261108/FRONTIER-R1-R10-RECAP.md'
    if key=='eval-author-meta-eval-20261108':source='eval-author-meta-eval-20261108/SCORING-RESULTS.md'
    if key in {'exact-original-numeric-20261108','original-task-replays-20261108'}:source=key+'/audit/INDEPENDENT-REPORT.md'
    pub=excerpt(source) if source else None
    x['source_reading']=pub;x['archive_path']=f'research/hackathon/{key}';x['portfolio_page']=f'docs/campaigns/{key}.md'
    page_title, context, finding = CONTEXT[key]
    text=f'# {page_title}\n\n{context}\n\n{finding}\n\n'
    if pub:
        text+=f'[Read the original report](../../{pub}). The report keeps the wording used at the time; the explanation above places it in the later research.\n\n'
    text+='<details>\n<summary>How this was run, the original counts and the limits</summary>\n\n'
    text+=f'**Recorded question:** {x["question"]}\n\n**Type of work:** {x["kind"]}.\n\n**Original counting:** {x["local_counts_with_units"]}.\n\n**Conditions:** {x.get("model_tool_condition","See source.")}\n\n**Detailed outcome:** {x["observed_outcome"]}.\n\n**What qualifies the result:** {x["followup_comparability_and_limits"]}.\n\n'
    text+=f'Full local archive: `{x["archive_path"]}`. This raw archive is excluded from Git.\n\n</details>\n\n[Back to the investigation](../RESEARCH-STORY.md) · [Find a related question](../HYPOTHESES.md) · [All campaigns](../CAMPAIGNS.md).\n'
    put(ROOT/x['portfolio_page'],text)
js(ROOT/'data/campaigns.json',{'schema':'portfolio-campaign-catalogue/v1','directories_covered':len(entries),'no_grand_attempt_total':True,'campaigns':[entries[k] for k in all_names]})
lines=['# All campaigns','',f'Every one of the **{len(entries)} study directories** has a page below, including designs, duplicate exports, incomplete work and negative results. Counts retain their original units. The earlier audit covered a historical cut of 46 directories; it is not relabeled as a 55-directory audit.','', '| Campaign / question | What was tried | Outcome |','|---|---|---|']
for k in all_names:
 x=entries[k];lines.append(f'| [{cell(title(k))}](campaigns/{k}.md)<br>{cell(x["question"])} | {cell(x["local_counts_with_units"])} | {cell(x["observed_outcome"])} |')
put(ROOT/'docs/CAMPAIGNS.md','\n'.join(lines)+'\n')
# Export all directly authored frontier protocol designs/results, while excluding
# copied subject workspaces and their recursively embedded source repositories.
PRUNE={'audit','copied-cut','copied-sessions','repaired-copy','.git','node_modules','__pycache__','runtime-homes','quarantine','templates','prepared','cases','workspace','workspaces','snapshots','snapshot','stages','repo','repo-control','repo-pressure','runs','solver-runs','input','output','outputs','delivery','deliveries','fixtures','frozen','public','private','sources','source','staged','copied-sessions'}
protocols=[]
for here,dirs,files in os.walk(ARCHIVE/'frontier-hunt-20261106'):
 dirs[:]=sorted(d for d in dirs if d not in PRUNE and not d.startswith('.') and not d.endswith('.receipts'))
 if 'DESIGN.md' not in files:continue
 p=Path(here); rel=p.relative_to(ARCHIVE).as_posix()
 design=excerpt(rel+'/DESIGN.md')
 result=next((n for n in ['RESULTS.md','BUILD-RESULTS.md','REPORT.md'] if n in files),None)
 resultpub=excerpt(rel+'/'+result) if result else None
 body=(p/'DESIGN.md').read_text(errors='replace'); question=' '.join(body.splitlines()[0:5])[:420]
 protocols.append({'protocol':rel.removeprefix('frontier-hunt-20261106/'),'design':design,'result':resultpub,'source_opening':question,'design_sha256':hashlib.sha256((p/'DESIGN.md').read_bytes()).hexdigest(),'result_present':result is not None})
js(ROOT/'data/frontier-protocols.json',{'schema':'portfolio-authored-protocols/v1','scope':'Authored frontier DESIGN.md locations; subject copies, runs, cases and quarantines excluded. These are protocols, not an attempt count.','protocols':protocols})
lines=['# Individual frontier protocols','',f'{len(protocols)} authored DESIGN.md locations are indexed below. Each link shows the original hypothesis and protocol; available results are paired. Copied source trees and subject workspaces are excluded. A missing paired result means this selector found no local result at that location, not proof of zero attempts. The audited R1-R10 ledger and later cohort census remain authoritative for their defined counts.','', '| Protocol | Design | Results |','|---|---|---|']
for x in protocols:lines.append(f'| `{x["protocol"]}` | [Design](../{x["design"]}) | '+(f'[Results](../{x["result"]})' if x['result'] else 'See aggregate cohort ledger')+' |')
put(ROOT/'docs/PROTOCOLS.md','\n'.join(lines)+'\n')
# All 67 closed-cut rows are independently preserved, even aggregate/build reports.
lines=['# Rounds 1-10: all 67 protocol rows','', 'The closed cut counts **295 model episodes** across 67 protocol rows: 286 requested Luna and nine requested Terra. These are not 295 independent frontier tasks. Historical dispositions below are quoted; “ceiling” and “KILL” describe local promotion rules and do not establish absence of ordinary errors. See [the interpretation](HYPOTHESES.md) and [audit corrections](INSTRUMENT-LESSONS.md).','', '| Round | Protocol | Counted model episodes | Historical disposition | Source result |','|---|---|---:|---|---|']
for x in PROTO['rows']:
 rel='frontier-hunt-20261106/'+x['source_result'];pub=excerpt(rel)
 lines.append(f'| {x["round"]} | `{x["lane"]}` | {x["model_episodes_as_counted"]} | {cell(x["reported_disposition"])} | '+(f'[Report](../{pub})' if pub else 'See machine ledger')+' |')
put(ROOT/'docs/ROUNDS-01-10.md','\n'.join(lines)+'\n')
# Later cohorts retain distinct units and treatment changes.
lines=['# Later rounds and failure transitions','', 'These cohort counts are not added together. Some are follow-ups on shared tasks, others count logical episodes, turns or distinct chat sessions. The complete source ledger is committed under evidence/ledgers/.','', '| Cohort | Units | Observed outcome | Comparability / qualification |','|---|---|---|---|']
for x in TRANS['cohorts']:lines.append(f'| {cell(x["id"])} | {cell(x["units"])} | {cell(x["result"])} | {cell(x["notes"])} |')
put(ROOT/'docs/LATER-ROUNDS.md','\n'.join(lines)+'\n')
# Meta-eval attempt-level scores and adjudications, including all incomplete slots.
by_id={x['subject']['id']:x for x in SCORES['subjects']}
meta=[]
lines=['# Meta-eval: all 31 author attempts','', 'Every original attempt is retained. Nineteen completed eval-author packages receive 100-point score intervals; four completed audit outputs are supplementary. Seven timeouts and one unknown native completion receive no fabricated score. Lower/upper bounds are supported points plus unresolved weights, not confidence intervals or model ranks. Human semantic review remains incomplete.','', '| Attempt | Status | Score /100 | Failed checks |','|---|---|---:|---|']
for a in META['attempts']:
 s=by_id.get(a['id'],{}).get('scoring',{}); bounds=s.get('score_interval'); score=f'{bounds[0]:.2f}-{bounds[1]:.2f}' if bounds else 'Not scored'
 row={k:a.get(k) for k in ['id','cohort','model_requested','case_id','draw','budget_seconds','effective_status','semantic_outcome','semantic_summary','verified_dimensions']};row['scoring']=s;meta.append(row)
 lines.append(f'| `{a["id"]}` | {cell(status_text(a["effective_status"]))} | {score} | {cell(", ".join(s.get("critical_failures",[])) or "None established / unresolved")} |')
lines+=['','## Detailed notes for each attempt','']
for a in META['attempts']:
    lines += ['<details>',f'<summary>{a["id"]}</summary>','',a['semantic_summary'],'','</details>','']
put(ROOT/'docs/META-EVAL-SCORES.md','\n'.join(lines)+'\n\n[Runnable guide](../meta-eval/META-EVAL.md) · [Full executed report](../meta-eval/grades/scored-v2-final/REPORT.md).\n')
js(ROOT/'data/meta-eval-attempts.json',{'schema':'portfolio-meta-eval-attempts/v1','attempts':meta,'source':'meta-eval/RESULTS.json','source_status_note':'Current owner review remains incomplete; the historical RESULTS snapshot may predate five source-rule approvals.'})
# Record paths to native receipts without copying private ambient transcripts.
receipt_names={'metadata.json','meta.json','launch.json','launch-meta.json','session-meta.json','native.json','turn-meta.json'}
raw=[];visited=0
prune_receipts=PRUNE-{'runs','solver-runs'}
for here,dirs,files in os.walk(ARCHIVE):
 dirs[:]=sorted(d for d in dirs if d not in prune_receipts and not d.startswith('.') and not d.endswith('.receipts'))
 visited+=1
 for n in sorted(files):
  if n not in receipt_names and not n.endswith('.meta.json'):continue
  p=Path(here)/n
  if p.is_symlink() or p.stat().st_size>2000000:continue
  try:d=read_json(p)
  except (ValueError,OSError):continue
  if not isinstance(d,dict):continue
  keys=['model','model_requested','requested_model','model_reported','effort','reasoning_effort','status','raw_status','effective_status','exit_code','returncode','session_id','thread_id','seconds','elapsed_seconds','timeout_seconds']
  fields={k:d[k] for k in keys if k in d and isinstance(d[k],(str,int,float,bool,type(None)))}
  raw.append({'path':p.relative_to(ARCHIVE).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'fields':fields})
js(ROOT/'data/native-receipt-index.json',{'schema':'portfolio-receipt-index/v1','scope':'Available launch/metadata receipt files under declared archive selectors. A receipt is not an independent attempt; launch and sidecar can refer to the same turn. Raw transcripts and copied source repositories are excluded. No absence-of-attempt claim follows from selector absence.','selector_names':sorted(receipt_names),'selector_suffix':'.meta.json','pruned_directory_names':sorted(prune_receipts),'directories_visited':visited,'receipt_files':len(raw),'receipts':raw})
# A readable master ledger points to every level rather than adding their units.
put(ROOT/'docs/ATTEMPTS.md',f'''# Every attempt, with the right counting unit

Use this ledger in order. We retain failed, successful, interrupted, conditional and unrun work. There is no defensible grand experiment total because studies reuse cases and exports, and count calls, episodes, turns, trajectories, checkpoints and assertions differently.

| Part of the work | Where every retained unit is listed | Unit / limitation |
|---|---|---|
| All 55 study directories | [Campaign catalogue](CAMPAIGNS.md), [machine rows](../data/campaigns.json) | Includes designs and duplicate exports; not 55 model experiments |
| Earlier 45-package audit | [Source ledger](../evidence/ledgers/complete-recap-audit-20261108/EARLY-COVERAGE.json) | Per-study local counts and original source hashes; selected checks, not every program rerun |
| Closed R1-R10 cut | [All 67 rows](ROUNDS-01-10.md), [machine ledger](../evidence/ledgers/complete-recap-audit-20261108/R1-R10-PROTOCOL-LEDGER.json) | 295 counted model episodes; predominantly Luna |
| Authored individual frontier hypotheses | [Protocol catalogue](PROTOCOLS.md), [machine rows](../data/frontier-protocols.json) | {len(protocols)} authored design locations; copied workspaces excluded |
| R11 onward and semantic follow-ups | [Cohort table](LATER-ROUNDS.md), [full transition ledger](../evidence/ledgers/complete-recap-audit-20261108/FAILURE-TRANSITIONS.json) | Separate call, episode, turn and chat units; no pooled total |
| Explicit verification repair | [All 30 rows](../evidence/ledgers/verification-eval-20261108/RESULTS.json) | 30 attempts / 1,806 decisions, all pass; decisions are not independent trials |
| Original-five + payroll recurrence | [All 14 started slots](../evidence/ledgers/original-five-rerun-20261108/RESULTS.json) | 10 initial passes, 2 instrument-unknown slots, 2 completed recovery repetitions: one failure and one pass |
| Eval-author meta-eval | [All 31 rows and scores](META-EVAL-SCORES.md), [machine rows](../data/meta-eval-attempts.json) | 19 scored packages, 4 supplementary outputs, 7 timeouts, 1 unknown; 114 check jobs are not author trials |
| Available native launch/metadata files | [Receipt index](../data/native-receipt-index.json) | {len(raw)} receipt files under an explicit selector; duplicate representations possible; no raw private transcripts in this catalogue |

The full local archive remains at `research/hackathon/`, ignored by Git. A clone includes the readable catalogues, evidence excerpts and the verified portable meta-eval, but not all raw historical workspaces. We explicitly distinguish documented-attempt coverage from a complete public export of every private native session.
''')
# Additional important audit/conclusion excerpts.
for rel in ['complete-recap-audit-20261108/REPORT.md','complete-recap-audit-20261108/EARLY-CAMPAIGNS.md','complete-recap-audit-20261108/FAILURE-TRANSITIONS.md','complete-recap-audit-20261108/TEST-GAMING-AUDIT.md','frontier-hunt-20261106/round13/DH-SYNTHESIS.md','original-five-rerun-20261108/REPORT.md','verification-eval-20261108/RESULTS-REVIEW.md']:
 excerpt(rel)
# Deduplicate repeated source exports by path; transformations are deterministic.
js(ROOT/'data/source-map.json',{'schema':'portfolio-source-map/v1','sources':list({x['public']:x for x in SOURCES}.values()),'archive_modified':False})
print(json.dumps({'campaigns':len(entries),'r1_r10_rows':len(PROTO['rows']),'authored_protocols':len(protocols),'meta_attempts':len(meta),'native_receipt_files':len(raw),'source_exports':len({x['public'] for x in SOURCES})}))



# Human-readable attempt-level tables for the final stronger-model comparisons.
strong=read_json(ARCHIVE/'original-five-rerun-20261108/RESULTS.json')
verify=read_json(ARCHIVE/'verification-eval-20261108/RESULTS.json')
lines=['# Stronger-model comparisons: every final slot','','These are separate experiments. The original-five ledger retains all 14 started slots, including two interrupted instrument-unknown attempts. The verification-repair matrix retains all 30 attempts. Neither table estimates general reliability.','','## Original tasks and selected payroll recurrence','','| Arm | Model | Task | Trial | Outcome | Recorded checks |','|---|---|---|---|---|---|']
for row in strong['attempt_ledger']:
    row=dict(row)
    if row['arm']=='prior-contract-transport-recovery': row.update(task='T03-payroll-sdk',passed=row['original_passed'],check_count=row['original_checks'])
    lines.append('| '+' | '.join(cell(row.get(k,'Not reported')) for k in ['arm','model','task','trial','outcome'])+' | '+cell(str(row.get('passed','Not applicable'))+'/'+str(row.get('check_count','Not applicable')))+' |')
lines+=['','The initial ten pass. The additional completed payroll pair contains one valid-input failure and one pass even though both pass all original cases. Interrupted transport slots remain unknown. [Full report](../evidence/source-text/original-five-rerun-20261108/REPORT.md).','','## Explicit verification repair','','| Model | Task | Trial | Outcome | Decisions correct / cases |','|---|---|---|---|---|']
for row in verify['rows']:
    lines.append(f'| {row["model"]} | {row["task"]} | {row["trial"]} | {row["status"]} | {row["passed"]}/{row["cases"]} |')
lines+=['','All 30 pass. These 1,806 decisions are repeated case decisions within attempts, not 1,806 independent tasks. Repair under an explicit contract differs from independently building a complete eval. [Source review](../evidence/source-text/verification-eval-20261108/RESULTS-REVIEW.md).']
put(ROOT/'docs/STRONGER-MODEL-ATTEMPTS.md','\n'.join(lines)+'\n')



# Human introductions are maintained separately from the historical table rows.
for name, intro in INTROS.items():
    p=ROOT/'docs'/name
    body=p.read_text(encoding='utf-8')
    table=body.find('\n|')
    assert table>=0, name
    p.write_text(intro.rstrip()+'\n\n'+body[table+1:],encoding='utf-8')
