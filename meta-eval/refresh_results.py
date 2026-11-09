"""Refresh the fixed 31-attempt synthesis from receipts; makes no model calls.

Optional grades/RESULTS-SUCCESSOR-ADJUDICATIONS.json has {"attempts": [{"id":
<an id in RESULTS.json>, "outcome": ..., "summary": ..., "evidence": [<relative
paths>]}]}. Verified defect judgments require completed attempts. Terminal
timeouts/capture incidents can receive explicit unknown/no-model-verdict labels.
This separates semantic adjudication from transport completion.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parent
MODELS = ['gpt-6.1-sol', 'gpt-6-astra']


def read(rel, default=None):
    path = ROOT / rel
    return json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else default


def source(rel):
    path = ROOT / rel
    return {'path': rel, 'exists': path.exists(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None}


def link(rel):
    return f'[{rel}]({rel})'


def native_usage(directory):
    path = ROOT / directory / 'transcript.jsonl'
    events = []
    if path.exists():
        with path.open(encoding='utf-8-sig', errors='replace') as handle:
            for line_number, line in enumerate(handle, 1):
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get('type') == 'turn.completed':
                    events.append({'line': line_number, 'usage': event.get('usage', {})})
    return {'source': directory + '/transcript.jsonl' if path.exists() else None,
            'turn_completed_events': events,
            'usage_known': bool(events) and all(bool(e['usage']) for e in events),
            'usd_cost': None, 'cost_status': 'not reported; no inferred pricing'}


def attempt(cohort, model, case, directory, draw=None, seconds=600):
    rel = directory + '/launch.json'
    launch = read(rel, {})
    runtime = read(directory + '/runtime-error.json')
    recovery = read(directory + '/RECOVERY.json')
    raw = launch.get('status')
    # Original screen copy faults were persisted in the cohort terminal, not launch.
    terminal_name = {'initial_screen': 'SCREEN-TERMINAL.json',
                     'H1_same_condition_confirmation': 'CONFIRMATION-TERMINAL.json',
                     'H6_same_condition_confirmation': 'CONFIRMATION-H6-TERMINAL.json',
                     'H1_budget_diagnostic': 'BUDGET-H1-TERMINAL.json'}.get(cohort)
    if raw is None and terminal_name:
        terminal = read('runs/' + terminal_name, {})
        for result in terminal.get('results', []):
            if result.get('case_id') == case and result.get('model_requested') == model:
                if draw and draw not in json.dumps(result):
                    continue
                raw = result.get('status')
                break
    effective = raw or ('running_or_capture_pending' if launch else 'not_launched')
    if cohort == 'initial_screen' and case == 'H9' and recovery:
        if recovery.get('native_turn_completed_event') is True:
            effective = 'recovered_completed_turn_delivery'
    if cohort == 'H6_same_condition_confirmation' and draw == 'draw1' and recovery:
        effective = 'capture_unknown_native_terminal'
    if raw is None and runtime and not recovery:
        effective = 'runtime_error'
    return {'id': '/'.join(filter(None, [cohort, model, case, draw])), 'cohort': cohort,
            'model_requested': model, 'case_id': case, 'draw': draw,
            'budget_seconds': seconds, 'raw_status': raw, 'effective_status': effective,
            'seconds': launch.get('seconds'), 'exit_code': launch.get('exit_code'),
            'launch': rel if launch else None, 'directory': directory,
            'runtime_error_receipt': directory + '/runtime-error.json' if runtime else None,
            'recovery_receipt': directory + '/RECOVERY.json' if recovery else None,
            'native_usage': native_usage(directory),
            'semantic_outcome': 'pending_review', 'semantic_summary': 'No terminal semantic adjudication imported yet.',
            'review_evidence': []}


def judge(row, outcome, summary, evidence):
    missing = [p for p in evidence if not (ROOT / p).exists()]
    if missing:
        row['review_missing_evidence'] = missing
        return
    row.update(semantic_outcome=outcome, semantic_summary=summary, review_evidence=evidence)


def build():
    index = read('protocol/COHORT-INDEX.json')
    rows = []
    for n in range(1, 10):
        for model in MODELS:
            rows.append(attempt('initial_screen', model, f'H{n}', f'runs/screen/{model}/H{n}'))
    for case, model in [('H1', MODELS[0]), ('H6', MODELS[1])]:
        for n in range(1, 4):
            rows.append(attempt(case + '_same_condition_confirmation', model, case,
                                f'runs/confirmation/{model}/{case}/draw{n}', f'draw{n}'))
    for n in range(1, 4):
        rows.append(attempt('H1_budget_diagnostic', MODELS[0], 'H1',
                            f'runs/budget-diagnostic/{MODELS[0]}/H1/draw{n}', f'draw{n}', 1200))
    for cohort, condition in [('selected_hit_clean_staging', 'primary'), ('selected_hit_coached_staging', 'coached')]:
        for case, model, cap in [('H1', MODELS[0], 1200), ('H6', MODELS[1], 600)]:
            directory = f'runs/clean_screen_v2/{condition}/{model}/{case}'
            legacy = f'runs/clean_screen/{model}/{case}'
            if condition == 'primary' and (ROOT / legacy / 'launch.json').exists():
                directory = legacy
            rows.append(attempt(cohort, model, case, directory, seconds=cap))
    assert len(rows) == index['planned_author_attempts'] == 31
    for row in rows:
        case, model, cohort = row['case_id'], row['model_requested'], row['cohort']
        if cohort == 'initial_screen':
            if case == 'H1' and model == MODELS[0]:
                judge(row, 'verified_false_reject', 'Correct applied-status Service rejected; accepted-only grading literal omitted from the package\'s documented solver views. Literal-only paired replay changes FAIL to PASS.',
                      ['grades/semantic-review/H1-INDEPENDENT.json', 'grades/semantic-review/H1-SOL-LITERAL-PAIR.json', 'grades/owner-review/sol-H1-FULL-BWRAP.json'])
            elif case == 'H1':
                judge(row, 'timeout_snapshot_diagnostic_only', '600s timeout. Snapshot shows related staged-view issue; not a second completed author failure.', ['grades/owner-review/H1-REVIEW.md'])
            elif case == 'H2':
                judge(row, 'no_objective_defect_established', 'Exact recovered rubric instruction text, changed runtime/context. Required headings, score mapping, worked arithmetic and calibration reviewed; valid alternative criteria preserved.', [f'grades/semantic-review/H2-{model}.json'])
            elif case == 'H3':
                judge(row, 'no_objective_defect_established_scoped', 'Task semantics reviewed. Intake-window ambiguity and missing OS isolation disclosed. Public-training-label lookup probe did not establish private-label theft or a semantic false pass.', [f'grades/semantic-review/H3-{model}.json', 'grades/semantic-review/H3-TIMING-WITNESS.json'])
            elif case == 'H4':
                judge(row, 'no_defect_on_post_outcome_successor_controls', 'Original five full-task controls invalidated. Both delivered graders distinguish all five separately qualified successor controls; finite post-outcome evidence only.', ['grades/owner-review/H4-REVIEW.md', f'grades/owner-review/{model}-H4-SUCCESSOR.json'])
            elif case == 'H5':
                judge(row, 'timeout_snapshot_diagnostic_only', '600s timeout. Restricted benchmark-only snapshot probe accepts a coherent underreported-work fixture. Full-suite completed failure not established.', ['grades/owner-review/H5-REVIEW.md', f'grades/owner-review/{model}-H5-BENCHMARK-SNAPSHOT.json'])
            elif case == 'H6' and model == MODELS[1]:
                judge(row, 'verified_false_green_and_isolated_false_reject', 'Actual historical bad CLI passes 84/84 new checks but fails tiny legal exponent-zero input. Separate legal-zero OUTPUT notation is falsely rejected by output parser; not an extra author attempt.', ['grades/owner-review/ASTRA-H6-PAIRED-REPRODUCER.json', 'grades/semantic-review/H6-INDEPENDENT.json', 'grades/semantic-review/H6-OUTPUT-ZERO-PAIR.json'])
            elif case == 'H6':
                judge(row, 'no_established_failure_on_licensed_witness', 'Symbolic parser handles the decisive zero family. Original finite positive controls are not full-domain gold and their rejection is excluded.', ['grades/owner-review/H6-REVIEW.md', 'owner/ADJUDICATION.json'])
            elif case == 'H7':
                judge(row, 'no_defect_on_selected_controls', 'All five selected extraction controls classified correctly. Universal paraphrase coverage and prose/tool behavior remain outside this finite result.', ['grades/owner-review/H7-REVIEW.md'])
            elif case == 'H8':
                judge(row, 'no_material_defect_established_scoped', 'Both delivered auditors distinguish 232 stored turns from 228 formal turns; original plus two mutations per model replayed correctly. Missing workspace bodies limit semantic certificates.', ['grades/audit-review/H8-SEMANTIC-REVIEW.md', 'grades/audit-review/H8-INDEPENDENT-REPLAY.json'])
            elif case == 'H9':
                judge(row, 'no_material_defect_established_recovered', 'Native turn completed; delivery recovered after UNC MAXPATH copy fault. Native exit code unpersisted. Accurate staged 147-unit/150-session accounting and regenerated auditor output; not full R10 153-call gold.', ['grades/audit-review/H9-SEMANTIC-REVIEW.md', 'grades/audit-review/H9-INDEPENDENT-REPLAY.json', row['directory'] + '/RECOVERY.json'])
        elif cohort == 'H1_same_condition_confirmation':
            judge(row, 'timeout_no_completed_recurrence_verdict', 'All three 600s fresh attempts timed out. Draws1/3 snapshots omit the grader literal; draw2 explicitly publishes it. No completed recurrence or disappearance rate.', ['grades/owner-review/H1-CONFIRMATION-REVIEW.json'])
        elif cohort == 'H6_same_condition_confirmation':
            review = read('grades/owner-review/H6-CONFIRMATION-REVIEW.json', {})
            item = next((d for d in review.get('draws', []) if d['draw'] == row['draw']), None)
            if item:
                outcome = {'draw1': 'capture_unknown_no_model_verdict', 'draw2': 'known_bad_rejected_distinct_defect', 'draw3': 'verified_fresh_false_green'}[row['draw']]
                judge(row, outcome, item.get('adjudication', item.get('reason', '')), ['grades/owner-review/H6-CONFIRMATION-REVIEW.json'])
        elif cohort == 'H1_budget_diagnostic':
            review = read('grades/owner-review/H1-BUDGET-NATIVE-SUMMARY.json', {})
            item = next((d for d in review.get('draws', []) if d['draw'] == row['draw']), None)
            if item and item.get('attempt_status') == 'completed' and item.get('false_rejects') == 1:
                judge(row, 'verified_false_reject', 'Completed 1200s-cap author: correct applied-status control rejected; all five controls valid. Staged views omit required accepted literal. Actual runtime under600s does not merge this selected new-cap cohort with prior600s timeouts.', ['grades/owner-review/H1-BUDGET-NATIVE-SUMMARY.json', f'grades/owner-review/H1-BUDGET-{row["draw"]}-FULL.json', 'grades/owner-review/H1-BUDGET-REVIEW.md'])
    overrides = read('grades/RESULTS-SUCCESSOR-ADJUDICATIONS.json', {'attempts': []})
    by_id = {r['id']: r for r in rows}
    for item in overrides.get('attempts', []):
        row = by_id[item['id']]
        if row['cohort'] not in ['selected_hit_clean_staging', 'selected_hit_coached_staging']:
            raise ValueError('Successor override may not rewrite discovery/confirmation: ' + item['id'])
        if row['effective_status'] != 'completed':
            terminal_unknowns = ['timeout', 'runtime_error', 'capture_unknown_native_terminal']
            unknown_outcomes = ['timeout_no_completed_model_verdict', 'incomplete_timeout_no_completed_verdict', 'capture_unknown_no_model_verdict', 'runtime_error_no_model_verdict']
            if row['effective_status'] not in terminal_unknowns or item['outcome'] not in unknown_outcomes or item.get('verified_dimensions'):
                raise ValueError('Noncompleted successor requires an explicit terminal unknown/no-model-verdict: ' + item['id'])
        if not item.get('evidence') or any(not (ROOT / p).exists() for p in item['evidence']):
            raise ValueError('Missing successor adjudication evidence: ' + item['id'])
        judge(row, item['outcome'], item['summary'], item['evidence'])
        if item.get('additional_outcomes'):
            row['additional_semantic_outcomes'] = item['additional_outcomes']
        if item.get('verified_dimensions'):
            row['verified_dimensions'] = item['verified_dimensions']
    for row in rows:
        dimensions = set(row.get('verified_dimensions', []))
        outcome = row['semantic_outcome']
        if row['case_id'] == 'H1' and outcome in ['verified_false_reject', 'verified_false_rejection']:
            dimensions.add('hidden_required_status_literal_false_reject')
        if row['case_id'] == 'H6':
            if outcome in ['verified_false_green_and_isolated_false_reject', 'verified_fresh_false_green', 'verified_false_acceptance']:
                dimensions.add('actual_bad_numeric_cli_false_green')
            if outcome == 'verified_false_green_and_isolated_false_reject' or 'verified_false_rejection' in row.get('additional_semantic_outcomes', []):
                dimensions.add('legal_numeric_output_false_reject')
        row['verified_dimensions'] = sorted(dimensions)
    cohorts = []
    for c in index['cohorts']:
        selected = [r for r in rows if r['cohort'] == c['id']]
        usage_totals = Counter()
        for row in selected:
            for event in row['native_usage']['turn_completed_events']:
                usage_totals.update({k:v for k,v in event['usage'].items() if isinstance(v, int)})
        cohorts.append({**c, 'effective_status_counts': dict(Counter(r['effective_status'] for r in selected)),
                        'raw_status_counts': dict(Counter(r['raw_status'] or 'not_persisted' for r in selected)),
                        'semantic_outcome_counts': dict(Counter(r['semantic_outcome'] for r in selected)),
                        'all_terminal_capture': all(r['effective_status'] in ['completed', 'timeout', 'runtime_error', 'recovered_completed_turn_delivery', 'capture_unknown_native_terminal'] for r in selected),
                        'usage_reported_attempts': sum(r['native_usage']['usage_known'] for r in selected),
                        'native_reported_usage_field_sums': dict(usage_totals),
                        'verified_defect_output_count': sum(bool(r['verified_dimensions']) for r in selected),
                        'verified_dimension_occurrences': dict(Counter(d for r in selected for d in r['verified_dimensions'])),
                        'all_semantically_adjudicated': all(r['semantic_outcome'] != 'pending_review' for r in selected)})
    human = read('grades/semantic-review/HUMAN-REVIEW-STATUS.json', {'status': 'pending', 'human_review_completed': False})
    owner_adjudication = read('owner/ADJUDICATION.json', {})
    result = {'schema_version': 'eval-author-results/v1', 'refreshed_utc': datetime.now(timezone.utc).isoformat(),
              'planned_author_attempts': 31, 'no_pooled_rate': True,
              'software_runs_and_adjudications_complete': all(c['all_terminal_capture'] and c['all_semantically_adjudicated'] for c in cohorts),
              'formal_human_qualification_complete': human.get('human_review_completed', False),
              'release_delivery_status': 'See COMPLETION-AUDIT.json for current exact-archive verification; research runs, software delivery and human qualification are separate.',
              'human_review': human, 'review_kind': 'AI semantic review plus executable independent replay; no human signoff',
              'owner_instrument_audit': {'source': 'owner/ADJUDICATION.json',
                                        'excluded_full_task_control_count': len(owner_adjudication.get('excluded_controls', [])),
                                        'excluded_controls': owner_adjudication.get('excluded_controls', []),
                                        'recorded_build_incidents': owner_adjudication.get('build_incidents', []),
                                        'scope': 'Research/owner-instrument defects are retained separately from fresh author-attempt verdicts. This is the cited sidecar inventory, not an exhaustive historical incident count.'},
              'source_instruction_fidelity': {'exact_recovered_text_jobs': ['H2'], 'reconstructed_jobs': ['H1','H3','H4','H5','H6','H7','H8','H9'], 'exact_original_session_replication': False},
              'usage_policy': 'Sum only actual turn.completed usage fields. Missing terminal usage is unknown, never zero. Cached/reasoning fields are retained as reported, not added again to parent fields. No USD cost inferred.',
              'cohorts': cohorts, 'attempts': rows,
              'scope_limits': [
                  'Conditional hit selection; no estimate of general model reliability or an unavoidable frontier limitation.',
                  'Native model aliases are not immutable weight identities; native memory/context remains possible.',
                  'Initial packet MANIFEST/PROVENANCE metadata was supplied and some read; no proven owner-bank read, no cryptographic context confinement.',
                  'Clean staging removes packet metadata only; coached staging adds an explicit new quality checklist. Neither is pooled with original/minimal prompts.',
                  'Clean H1 visible instruction is the same single sentence as primary. Raw-file versus stdin SHA differences reflect CRLF-to-LF normalization, not an appended instruction; this is text fidelity, not byte-for-byte full-session replication.',
                  'H4 original five full-task controls and H6 two full-domain positive labels are excluded by owner/ADJUDICATION.json; frozen old receipts preserved.',
                  'H2/H3 ten semantic successor controls and H4 corrected successor bank were created post-outcome, with component/finite qualification only.',
                  'H5 timeout snapshot benchmark diagnostic is not a completed author verdict or full-suite false green.',
                  'H6 enormous nonzero output resource ambiguity is separate from decisive short zero/count witnesses.',
                  'H8 stored232/formal228 and H9 staged147/150 are distinct populations; historical full R10 153 calls are not staged gold.',
                  'Human task-meaning and criterion review is explicitly pending.'],
              'pending': [r['id'] + ': ' + r['effective_status'] + ', ' + r['semantic_outcome'] for r in rows if r['semantic_outcome'] == 'pending_review'],
              'source_receipts': []}
    paths = {'protocol/COHORT-INDEX.json', 'protocol/RUN-POLICY.json', 'owner/ADJUDICATION.json',
             'grades/semantic-review/HUMAN-REVIEW-STATUS.json', 'grades/audit-review/METADATA-EXPOSURE.json',
             'grades/owner-review/EXPOSURE-PATH-CENSUS.json', 'owner/semantic-successor/QUALIFICATION-PORTABLE.json'}
    for row in rows:
        paths.update(row['review_evidence'])
        paths.update(p for p in [row['launch'], row['runtime_error_receipt'], row['recovery_receipt']] if p)
        if row['native_usage']['source']: paths.add(row['native_usage']['source'])
    if (ROOT / 'grades/RESULTS-SUCCESSOR-ADJUDICATIONS.json').exists(): paths.add('grades/RESULTS-SUCCESSOR-ADJUDICATIONS.json')
    result['source_receipts'] = [source(p) for p in sorted(paths)]
    return result


def render(result):
    text = ['# Results', '', 'This fixed cut schedules **31 author attempts in six separate cohorts**. The initial screen produced two independently verified defect families: H1 hidden grading literal in the delivered solver views, and H6 failure to detect an actual bad numeric CLI. These are bounded construction failures under the recorded conditions. Human review is pending.', '',
            f'Refreshed {result["refreshed_utc"]}. Transport status and semantic outcome are separate. No pooled rate is calculated.', '',
            '| Cohort | Planned | Current capture status | Semantic outcomes |', '|---|---:|---|---|']
    for c in result['cohorts']:
        fmt = lambda d: '; '.join(f'{v} {k}' for k,v in d.items())
        text.append(f'| {c["id"]} | {c["attempts"]} | {fmt(c["effective_status_counts"])} | {fmt(c["semantic_outcome_counts"])} |')
    text += ['', 'The initial18 comprise **13 ordinary completed deliveries, two H9 recovered completed-turn deliveries, and three timeouts**. H9 raw copy errors remain retained; recovered custody does not recover an unpersisted native exit code. All initial launch receipts retain `formal_claim_eligible:false`.', '',
             'H1 same-condition600s confirmations have zero completed outputs and three timeouts. Its separate1200s-cap diagnostic has three completed, independently false-rejecting graders. They finished in495–539s, but the selected budget condition remains separate; this does not establish a causal budget effect. H6 same-condition600s confirmations have two completed outputs and one capture with unknown native terminal: one completed grader catches a distinct real defect (92/93), and one freshly false-greens the actual bad CLI (126/126).', '',
             '## Initial screen by task and model', '', '| Task | Model | Capture | Adjudication | Evidence |', '|---|---|---|---|---|']
    for row in result['attempts']:
        if row['cohort'] == 'initial_screen':
            text.append(f'| {row["case_id"]} | {row["model_requested"]} | {row["effective_status"]} | {row["semantic_summary"]} | ' + ' '.join(link(p) for p in row['review_evidence']) + ' |')
    text += ['', '## Fresh confirmation and diagnostic attempts', '', '| Condition / draw | Model / task | Capture | Adjudication | Evidence |', '|---|---|---|---|---|']
    for row in result['attempts']:
        if row['cohort'] != 'initial_screen':
            evidence = row['review_evidence'] or ([row['launch']] if row['launch'] else [])
            text.append(f'| {row["cohort"]} {row["draw"] or ""} | {row["model_requested"]} {row["case_id"]} | {row["effective_status"]} | {row["semantic_summary"]} | ' + ' '.join(link(p) for p in evidence) + ' |')
    text += ['', '## Interpretation and remaining work', '']
    text += ['Verified occurrences by separate condition (one author output may show multiple dimensions; this is not a pooled rate):', '',
             '| Cohort | Completed outputs with verified defects | Verified dimensions |', '|---|---:|---|']
    for c in result['cohorts']:
        dims = '; '.join(f'{v} {k}' for k,v in c['verified_dimension_occurrences'].items()) or 'None established'
        text.append(f'| {c["id"]} | {c["verified_defect_output_count"]} | {dims} |')
    text += ['']
    text += ['- ' + s for s in result['scope_limits']]
    text += ['', 'Pending attempt adjudications:', '']
    text += ['- ' + p for p in result['pending']] or ['None.']
    text += ['', 'Human review remains pending even when every automated run is terminal. Goal completion and final release qualification are not asserted by this report. ' + link('ADJUDICATION.md') + ' records criteria and invalidated controls. ' + link('RESULTS.json') + ' carries per-attempt status and SHA-256 receipt identities.', '',
             '## Recorded resource use', '',
             'Only native `turn.completed` usage receipts are summed. Missing usage on timeout/capture error is unknown. Cached input and reasoning output are retained as reported fields and are not added again to input/output totals. Dollar cost was not reported and is not inferred.', '',
             '| Cohort | Attempts with usage | Reported input tokens | Reported cached input tokens | Reported output tokens | Reported reasoning output tokens |',
             '|---|---:|---:|---:|---:|---:|']
    for c in result['cohorts']:
        u = c['native_reported_usage_field_sums']
        text.append(f'| {c["id"]} | {c["usage_reported_attempts"]}/{c["attempts"]} | {u.get("input_tokens", "unknown")} | {u.get("cached_input_tokens", "unknown")} | {u.get("output_tokens", "unknown")} | {u.get("reasoning_output_tokens", "unknown")} |')
    text += ['',
             'Refresh with `python3 refresh_results.py`. This command performs no actor calls and never fills missing semantic judgments from successful process exit.']
    return '\n'.join(text) + '\n'


def adjudication(result):
    text = '''# Adjudication

This is an AI review and executable replay record, not human signoff. The owner explicitly said “Not reviewed yet; keep building.” Task-meaning review remains pending in [HUMAN-REVIEW-STATUS.json](grades/semantic-review/HUMAN-REVIEW-STATUS.json). Current per-attempt outcomes and pending runs are regenerated in [RESULTS.md](RESULTS.md) and [RESULTS.json](RESULTS.json).

## What counts as an observed construction failure

The licensed task meaning must support the witness, the delivered evaluator must be terminal and unchanged, and the result must be reproduced using the evaluator's actual interface. A timeout snapshot, missing instrument feature, theoretical file read, invalid positive control, or successful process exit alone does not meet that standard. New controls and diagnostics remain explicitly post-outcome. These criteria establish dimensions of eval quality, not universal correctness of the entire evaluation system.

**H1, Sol initial completed output:** original E1 requires the error spelling `payload_mismatch` but does not prescribe a success spelling. The new operator README introduces `accepted`, which could be a legitimate clarification if transmitted. Its documented staging procedure instead sends only its initial/final views, and those views use original E1 without the new literal; the benchmark question does likewise. The actual native grader rejects a correct `applied` implementation. Changing only success spelling to `accepted` changes FAIL to PASS. This is a concrete mismatch between the package's own solver exposure and grading, not a claim that authors may never clarify an interface. See [independent review](grades/semantic-review/H1-INDEPENDENT.json), [literal-only pair](grades/semantic-review/H1-SOL-LITERAL-PAIR.json), and [five-control native replay](grades/owner-review/sol-H1-FULL-BWRAP.json).

Three fresh600s H1 confirmations all timed out and are not completed failures or clean negatives. Three separately admitted1200s-cap diagnostic outputs completed and each falsely rejects the valid alternative while distinguishing the other controls; their own staged views omit the new literal. Actual runtimes under600s do not change the condition admission. See [budget summary](grades/owner-review/H1-BUDGET-NATIVE-SUMMARY.json) and [source/view review](grades/owner-review/H1-BUDGET-REVIEW.md). The fresh draw1 literal pair, when available, is a further causal diagnostic, not an extra author attempt.

**H6, Astra initial completed output:** the exact preserved historical Luna numeric CLI passes all84 checks of the newly authored eval, yet fails a191-byte legal input containing mathematical zero encoded as `0e10000000000000000000`. The task explicitly accepts exact integral JSON number encodings. The CLI errors with Decimal.InvalidOperation instead of producing counts1/3; replacing only the zero spelling with canonical zero succeeds. Both actual candidate and frozen source identity are bound by [paired reproducer](grades/owner-review/ASTRA-H6-PAIRED-REPRODUCER.json) and [independent clauses/review](grades/semantic-review/H6-INDEPENDENT.json). This is a coverage false green on an actually bad implementation, not proof that any finite suite can detect every defect.

A separate isolated seed grader probe submits legal zero OUTPUT exponent notation instead of canonical zero for the same tiny expected result. The new judge rejects the former with Decimal.InvalidOperation and accepts the latter. The original output contract explicitly permits integral exponent notation. This is a valid-result parser false reject, not a universally correct full CLI positive and not an extra model attempt. See [output pair](grades/semantic-review/H6-OUTPUT-ZERO-PAIR.json). Huge nonzero expanded sums and maxima are resource-ambiguous and are excluded from this decisive tiny-zero witness.

Of the three fresh same-condition H6 draws, draw1 is a recovered stable snapshot with unknown native terminal, draw2 rejects the actual bad candidate on a distinct huge-nonzero timeout case (92/93), and completed draw3 accepts it126/126 while the tinyzero witness still fails. That is one fresh completed recurrence among two completed confirmations, with one unknown retained. It does not prove the seed output-parser defect recurs. See [confirmation adjudication](grades/owner-review/H6-CONFIRMATION-REVIEW.json).

## Excluded and narrowed claims

- H2: both exact-text rubric jobs have no established objective defect. Alternative criteria are valid; no hidden novelty ranking is imposed. Changed CAL layout, normalized newlines and runtime/context remain disclosed.
- H3: both delivered intake-policy evaluators have no established objective defect under a literal reading. The30-minute timing boundary is ambiguous. Public train-label access is not private holdout theft; the synthetic lookup probe did not establish a full semantic false pass. Missing OS sandbox was disclosed by the authors and is not a full-positive claim.
- H4: all five original complete-candidate controls are excluded as full-task gold. The standalone-assert alternative violates the original unittest requirement, and inherited production reference precision/newline defects confound all wrappers. Corrected source-derived successor controls were built after outputs were seen. Both new graders classify all five successor controls correctly; this is finite post-outcome evidence.
- H5: both author attempts timed out. Restricted benchmark-only snapshot probes accept a coherent fixture doing180 actual work while reporting30. This identifies an instrument gap in incomplete output, not a completed author failure or full-suite false green. Earlier adapter/precondition failures remain incidents, not verdicts.
- H6: two frozen positive controls are only finite-probe correct and expand huge exponents before count. They are excluded as full-domain positive gold. Their rejection is not a model false reject. The actual bad candidate's independently established failure still licenses the coverage dimension.
- H7: five selected extraction controls are correctly distinguished by both graders. This is not universal paraphrase/prose qualification.
- H8: both auditors correctly account for182 stored sessions and232 turns versus180 formal sessions and228 turns, and pass six selected original/mutation replays. Missing workspace bodies limit semantic verification.
- H9: both native turns completed and their deliveries were recovered from UNC copy faults; native exit codes remain unpersisted. Staged147 logical units and150 session logs are correctly distinguished. Full historical R10 totals153 calls/150 invocations are a different population. Regenerated auditor outputs and retained limitations support no material failure on the staged task. One initial owner replay artifact was overwritten after a permission fix; that custody limitation is disclosed in the replay review.

The frozen original controls and their raw receipts are preserved. [owner/ADJUDICATION.json](owner/ADJUDICATION.json) lists exclusions; [run_eval_current.py](run_eval_current.py) applies the sidecar while the old scorer remains historical. [Source-license contracts](owner/contracts/README.md) distinguish original clauses, alternatives and post-outcome judgments. The ten H2/H3 [semantic successor controls](owner/semantic-successor/README.md) are scoped component controls, not prospective or fully isolated system qualification.

## Instruction and context limits

Only H2 recovers exact original author instruction text; eight jobs use explicitly reconstructed authoring instructions and preserved source tasks. None recreates the full original session context. The initial author workspaces supplied MANIFEST/PROVENANCE metadata, and actual reads are recorded. Native memory context is possible and observed; no owner-bank read was proved, and context confinement is unproven. Clean staging removes packet metadata but retains native memory context. The coached arm explicitly adds a stronger checklist and is a separate secondary condition. See [metadata exposure](grades/audit-review/METADATA-EXPOSURE.json), [path census](grades/owner-review/EXPOSURE-PATH-CENSUS.json), and [fixed31-attempt cohort index](protocol/COHORT-INDEX.json).

The evidence supports concrete, reproducible failures to construct trustworthy eval components under recorded conditions, including fresh recurrence. It does not establish that either model cannot build an eval, that every explored hypothesis failed, that models cheated, or that this is an unavoidable frontier limitation. General reliability rates require a different prospective design. Human criterion approval remains pending.
'''
    text += '\n## Clean and coached successor adjudications\n\n'
    text += 'These four selected attempts change the exposure condition and are reported separately. The clean arm keeps the same visible minimal author instruction and removes packet metadata. H1 also uses the separately admitted1200s budget. The coached arm adds an explicit checklist. Neither arm recreates the historical session or independently identifies a causal coaching effect.\n\n'
    for row in result['attempts']:
        if row['cohort'] not in ['selected_hit_clean_staging', 'selected_hit_coached_staging']:
            continue
        text += f'**{row["cohort"]}, {row["model_requested"]}, {row["case_id"]}:** {row["effective_status"]}; {row["semantic_outcome"]}. {row["semantic_summary"]} '
        text += ' '.join(link(p) for p in row['review_evidence']) + '\n\n'
    text += 'A published success literal that is actually sent to the solver can legitimately close the H1 witness. Coached H1 chooses final-answer-only evaluation and explicitly provides its new TASK contract; measuring staged adaptation and preserving original scope are separate questions. Two correct strategies passing finite controls does not prove universal eval quality.\n'
    return text


def main():
    result = build()
    (ROOT / 'RESULTS.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
    (ROOT / 'RESULTS.md').write_text(render(result), encoding='utf8')
    (ROOT / 'ADJUDICATION.md').write_text(adjudication(result), encoding='utf8')
    print(json.dumps({'attempts': len(result['attempts']), 'pending_semantic_reviews': len(result['pending']),
                      'cohorts': [{k:c[k] for k in ['id','effective_status_counts']} for c in result['cohorts']],
                      'human_review_completed': result['human_review'].get('human_review_completed', False)}))


if __name__ == '__main__':
    main()
