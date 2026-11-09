"""Distinguish raw Windows line endings from changed author instructions."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(value):return hashlib.sha256(value).hexdigest()
rows=[]
for model,case in [('gpt-6.1-sol','H1'),('gpt-6-astra','H6')]:
    source=ROOT/'packets/primary'/case/'prompt.md';raw=source.read_bytes();normalized=source.read_text(encoding='utf-8').encode()
    launch=json.loads((ROOT/'runs/clean_screen'/model/case/'launch.json').read_text())
    delivered=ROOT/'runs/clean_screen'/model/case/'delivery/prompt.md'
    rows.append({'model':model,'case':case,'raw_prompt_sha256':sha(raw),'raw_CRLF_sequences':raw.count(b'\r\n'),
                 'raw_last_bytes_hex':raw[-8:].hex(),'normalized_stdin_sha256':sha(normalized),
                 'recorded_actual_stdin_sha256':launch['prompt_sha256'],
                 'actual_stdin_equals_newline_normalized_original':sha(normalized)==launch['prompt_sha256'],
                 'delivered_prompt_raw_identical':delivered.read_bytes()==raw if delivered.exists()else'not_yet_captured',
                 'boundary_instruction_added':False,'source_instruction_text':normalized.decode()})
policy=json.loads((ROOT/'protocol/CLEAN-HIT-DIAGNOSTIC-POLICY.json').read_text())
result={'model_calls':0,'prompt_comparisons':rows,
        'clean_runner_current_sha256':sha((ROOT/'run_clean_screen.py').read_bytes()),
        'clean_runner_frozen_sha256':policy['files']['run_clean_screen.py'],
        'explanation':'Windows text-mode read normalizesCRLF toLF before stdin; source payload rawhash and stdintexthash may differ with identical instruction text.',
        'coached_comparison':'Coachedfreeze verifies newline-normalized primary text plus the explicitqualitysentence and whitespace separators only; input files identical.',
        'other_condition_changes':'Metadata removed; H1clean timeout1200 differs from initialscreen600. These remain separateconditions.'}
(ROOT/'grades/audit-review/PROMPT-BYTE-RECONCILIATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'all_observed_stdin_hashes_match_normalized_source':all(r['actual_stdin_equals_newline_normalized_original']for r in rows),
                  'frozen_runner_unchanged':result['clean_runner_current_sha256']==result['clean_runner_frozen_sha256']}))
