"""Current-state owner-review matrix. Pending rows are never invented verdicts."""
from pathlib import Path
import collections,datetime,json
B=Path(__file__).resolve().parents[2]
screen=json.loads((B/'runs/SCREEN-CENSUS.json').read_text());confirm=json.loads((B/'runs/CONFIRMATION-CENSUS.json').read_text());successor=json.loads((B/'grades/RESULTS-SUCCESSOR-ADJUDICATIONS.json').read_text());adopt={r['id']:r for r in successor['attempts']}
rows=[]
def add(cohort,model,case,draw,status,condition,evidence,assessment,scope,source=None):
 r={'id':'/'.join(str(x)for x in [cohort,model,case,draw]if x is not None),'cohort':cohort,'model':model,'case_id':case,'draw':draw,'native_status':status,'condition':condition,'owner_assessment':assessment,'scope':scope,'evidence':evidence,'human_expert_review_complete':False}
 if source:r['source_receipt']=source
 r['completed_defect_demonstrated']=status in ['completed','recovered_completed']and assessment in ['verified_false_rejection','verified_false_acceptance']
 rows.append(r)
for r in screen['rows']:
 m,c,s=r['model'],r['case'],r['status'];e=[];scope='Finite screen conditions; not universal correctness.'
 if c=='H1':a='verified_false_rejection'if m=='gpt-6.1-sol'else'incomplete_snapshot_false_rejection';e=['grades/owner-review/H1-REVIEW.md','grades/owner-review/sol-H1-FULL-BWRAP.json'if m=='gpt-6.1-sol'else'grades/owner-review/astra-H1-SNAPSHOT-BWRAP.json']
 elif c in ['H2','H3']:
  p=B/'grades/semantic-review'/(c+'-'+m+'.json');doc=json.loads(p.read_text());a=doc['judgment'];e=[str(p.relative_to(B)).replace('\\','/')];scope='Independent model semantic review; human expert signoff remains pending.'
 elif c=='H4':a='no_verified_defect_on_corrected_posthoc_controls';e=['grades/owner-review/H4-REVIEW.md','owner/ADJUDICATION.json'];scope='Original positives invalid; post-outcome successor diagnostic5/5, separate from frozen bank.'
 elif c=='H5':a='incomplete_snapshot_measurement_gap';e=['grades/owner-review/H5-REVIEW.md'];scope='Timeout snapshots accept coherent extra-work probe on selected native benchmark cases only.'
 elif c=='H6':
  a='verified_false_acceptance'if m=='gpt-6-astra'else'known_bad_rejected_overall_positive_qualification_unknown';e=['grades/owner-review/H6-REVIEW.md','grades/owner-review/astra-H6-FULL-GRADE.json'if m=='gpt-6-astra'else'grades/owner-review/sol-H6-FULL-GRADE-RAW.json','owner/ADJUDICATION.json'];scope='Coverage dimension; initial full-task positives excluded. Tiny zero/count input is unambiguous.'
 elif c=='H7':a='no_verified_defect_on_finite_and_posthoc_contiguity_controls';e=['grades/owner-review/H7-REVIEW.md'];scope='Frozen5controls plus separately labeled2contiguity controls; selected original source.'
 elif c in ['H8','H9']:a='no_verified_defect_on_staged_subset';e=['grades/audit-review/'+c+'-SEMANTIC-REVIEW.md'];scope='Subset reconstruction with independent Docker replay; absent full original inputs/context limit claims.'
 else:raise ValueError(c)
 add('screen',m,c,None,s,r['condition'],e,a,scope,'runs/SCREEN-CENSUS.json')
for r in confirm['rows']:
 m,c,d,s=r['model'],r['case'],r['draw'],r['status']
 if c=='H1':a='incomplete_snapshot_or_scope_change_only';e=['grades/owner-review/H1-CONFIRMATION-REVIEW.json'];scope='Three600second timeouts, no completed-failure denominator.'
 elif d==3:a='verified_false_acceptance';e=['grades/owner-review/H6-CONFIRM-draw3.json'];scope='Actual unchanged bad saved CLI accepted126/126.'
 elif d==2:a='actual_known_bad_candidate_rejected';e=['grades/owner-review/H6-CONFIRM-draw2.json'];scope='92/93; distinct huge-nonzero-exponent timeout catches bad program, does not prove zero-family coverage.'
 else:a='native_terminal_unknown_recovered_snapshot';e=['runs/confirmation/gpt-6-astra/H6/draw1/RECOVERY.json'];scope='Verified232file snapshot custody, but no final/terminal event/native exit; not completed pass/failure.'
 add('confirmation',m,c,'draw'+str(d),s,r.get('condition'),e,a,scope,'runs/CONFIRMATION-CENSUS.json')
for d in ['draw1','draw2','draw3']:
 p=B/'runs/budget-diagnostic/gpt-6.1-sol/H1'/d/'launch.json';r=json.loads(p.read_text());e=['grades/owner-review/H1-BUDGET-'+d+'-FULL.json','grades/owner-review/H1-BUDGET-REVIEW.md']
 add('budget_diagnostic','gpt-6.1-sol','H1',d,r['status'],r.get('condition'),e,'verified_false_rejection','Separate1200capcohort, actual495–539seconds. Native5controls each; all3ownsolverviews omit literal.',str(p.relative_to(B)).replace('\\','/'))
for cohort,folder in [('selected_hit_clean_staging','clean_screen'),('selected_hit_coached_staging','clean_screen_v2/coached')]:
 for m,c in [('gpt-6.1-sol','H1'),('gpt-6-astra','H6')]:
  id='/'.join([cohort,m,c]);p=B/'runs'/folder/m/c/'launch.json';r=json.loads(p.read_text())if p.exists()else{};s=r.get('status','pending_terminal_receipt'if r else'not_started');v=adopt.get(id)
  add(cohort,m,c,None,s,r.get('condition',cohort),v['evidence']if v else[],v['outcome']if v else'not_yet_adjudicated',v['summary']if v else'No owner verdict until terminal capture and independent native scoring.',str(p.relative_to(B)).replace('\\','/')if p.exists()else None)
assert len(rows)==31,len(rows)
counts=dict(collections.Counter(r['native_status']for r in rows));doc={'schema_version':'eval-author-owner-review-matrix/v1','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'planned_rows':31,'status_counts':counts,'no_pooled_failure_rate':True,'human_review_complete':False,'owner_sidecar':'owner/ADJUDICATION.json','notes':['Context/provenance/metadata exposure and original/reconstructed/coached conditions remain separate.','completed_defect_demonstrated denotes a checked dimension, not whole-domain binary completeness.','Raw score false-reject counts require sidecar exclusions; superseded owner incidents never become subject failures.'],'attempts':rows}
(B/'grades/owner-review/FINAL-OWNER-MATRIX.json').write_text(json.dumps(doc,indent=2)+'\n')
md=['# Owner-review matrix','',f'Current state:31planned rows. Native statuses: `{json.dumps(counts,sort_keys=True)}`. No pooled reliability rate is justified. Human expert review remains pending; this ledger records independent agent/owner checks and exact evidence scopes.','', '| Cohort | Model | Job/draw | Native status | Owner finding |','| --- | --- | --- | --- | --- |']
for r in rows:md.append('| '+ ' | '.join([r['cohort'],r['model'],r['case_id']+('/'+r['draw']if r['draw']else''),r['native_status'],r['owner_assessment']])+' |')
md+=['','Each row’s scope and evidence paths are in [FINAL-OWNER-MATRIX.json](FINAL-OWNER-MATRIX.json). Completed defects are measured dimensions; untested full-goal correctness remains unknown. See [owner exclusions](../../owner/ADJUDICATION.json) before interpreting raw scores.']
(B/'grades/owner-review/FINAL-OWNER-MATRIX.md').write_text('\n'.join(md)+'\n');print(json.dumps({'rows':len(rows),'statuses':counts}))
