#!/usr/bin/env python3
"""Verify a staged portfolio checkout; no commit or model call is made."""
from pathlib import Path
import datetime,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
records=[]
def run(label,args,cwd=ROOT):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True)
 item={'name':label,'command':args,'cwd':str(cwd.relative_to(ROOT)),'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 records.append(item)
 print(label+': '+('PASS' if p.returncode==0 else 'FAIL'),flush=True)
 if p.returncode:print(p.stdout,p.stderr);raise SystemExit(p.returncode)
 return p
run('portfolio coverage and identities',[sys.executable,'tools/validate_portfolio.py'])
run('limited publication pattern scan',[sys.executable,'tools/scan_publication.py'])
run('meta-eval unit tests',[sys.executable,'-m','unittest','discover','-s','meta_eval/tests','-v'],ROOT/'meta-eval')
run('declared runtime',[sys.executable,'run_meta_eval.py','doctor'],ROOT/'meta-eval')
run('31 records and 114 receipts',[sys.executable,'validate_meta_eval_report.py','grades/scored-v2-final/REPORT.json','--all-existing'],ROOT/'meta-eval')
# Materialize the actual staged set; ignored archive cannot accidentally rescue it.
subprocess.run([sys.executable,'tools/stage_portfolio.py'],cwd=ROOT,check=True,capture_output=True)
tree=subprocess.check_output(['git','write-tree'],cwd=ROOT,text=True).strip()
base=ROOT/'.local';base.mkdir(exist_ok=True)
clone=base/('verified-checkout-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f'))
clone.mkdir();assert clone.resolve().is_relative_to(base.resolve())
subprocess.run(['git','checkout-index','--all','--prefix='+str(clone)+'/'],cwd=ROOT,check=True)
assert not (clone/'research').exists()
run('staged checkout without raw archive',[sys.executable,'tools/validate_portfolio.py'],clone)
run('staged checkout execution receipt completeness',[sys.executable,'validate_meta_eval_report.py','grades/scored-v2-final/REPORT.json','--all-existing'],clone/'meta-eval')
proof={'schema':'portfolio-checkout-verification/v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_passed':True,'verified_index_tree':tree,'raw_archive_absent_from_checked_clone':True,'model_calls':0,'new_native_subject_trials':0,'full_114_job_replay_repeated_now':False,'note':'This migration rechecks identities, original unit tests/runtime and all retained execution receipts; historical 114-job cold replay is bound by releases/SCORED-CLEAN-VERIFICATION.json. The proof file itself is added after the checked tree to avoid self-reference.','checks':records}
(ROOT/'data/PORTFOLIO-VERIFICATION.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Wrote data/PORTFOLIO-VERIFICATION.json; no commit or push.',flush=True)
