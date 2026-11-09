"""Build a small standalone archive without caches, credentials or release recursion."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile
import zipfile
import subprocess
import sys
import os
from release_privacy import sanitize
from release_nested import inspect_zip

ROOT=Path(__file__).resolve().parent
if os.name=='nt'and not str(ROOT).startswith('\\\\?\\'):
    ROOT=Path('\\\\?\\UNC\\'+str(ROOT)[2:])if str(ROOT).startswith('\\\\')else Path('\\\\?\\'+str(ROOT))
EXCLUDED_DIRS={'.git','__pycache__','.pytest_cache','.mypy_cache','node_modules','.venv','venv','release','.codex'}
EXCLUDED_NAMES={'auth.json','credentials.json','.env','id_rsa','id_ed25519'}
ALLOWED_TOP={'owner','packets','sources','runs','grades','protocol','audit','submission','meta_eval'}
EXTERNAL_PROOF_PATHS={'completion-audit.json','completion-audit.md','build-state.json',
                      'grades/audit-review/release-privacy-check.json','grades/release-verification/final-clean-findings.json'}
DEVELOPMENT_PREFIXES={'grades/meta-eval-pilot','grades/meta-eval-adapter-check',
                      'grades/meta-eval-v2-executed','grades/scored-v2-results','grades/meta-eval-calibration'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'release/eval-author-meta-eval.zip');p.add_argument('--verify',action='store_true');a=p.parse_args()
    members=[];excluded=[];redactions=[];nested_reviews=[]
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():continue
        rel=path.relative_to(ROOT)
        if any(rel.as_posix().lower().startswith(prefix+'/')for prefix in DEVELOPMENT_PREFIXES):
            excluded.append({'path':rel.as_posix(),'reason':'superseded_meta_eval_development_run_preserved_locally'});continue
        if rel.as_posix()=='meta_eval/controls/H1/wrong_B_reply.json':
            excluded.append({'path':rel.as_posix(),'reason':'superseded_development_control_source_only_v2_retained'});continue
        if rel.as_posix().lower()in EXTERNAL_PROOF_PATHS:
            excluded.append({'path':rel.as_posix(),'reason':'external_final_or_operational_proof_avoids_archive_hash_cycle'});continue
        model_zip=path.suffix.lower()=='.zip'and rel.parts[0]=='runs'and'delivery'in rel.parts
        if (path.is_symlink() or any(x.lower() in EXCLUDED_DIRS for x in rel.parts) or path.name.lower() in EXCLUDED_NAMES
            or (path.name.lower().startswith('.env') and path.name.lower()!='.env.example')
            or path.suffix in {'.pyo','.pdf','.mp4','.png'} or(path.suffix.lower()=='.zip'and not model_zip)or (len(rel.parts)>1 and rel.parts[0] not in ALLOWED_TOP)):
            reason=('symlink_not_dereferenced'if path.is_symlink()else'nested_archive_omitted_sources_retained'if path.suffix=='.zip'
                    else'cache_local_environment_or_credential_file'if any(x.lower()in EXCLUDED_DIRS for x in rel.parts)or path.name.lower()in EXCLUDED_NAMES or path.name.lower().startswith('.env')
                    else'noncode_media_or_outside_release_scope')
            excluded.append({'path':rel.as_posix(),'reason':reason});continue
        data=path.read_bytes()
        if model_zip:
            try:
                clean,review=inspect_zip(data);review['path']=rel.as_posix();nested_reviews.append(review)
            except (ValueError,zipfile.BadZipFile,RuntimeError)as error:
                excluded.append({'path':rel.as_posix(),'reason':'nested_archive_unqualified:'+str(error),'original_sha256':hashlib.sha256(data).hexdigest()});continue
            if review['changes']:
                redactions.append({'path':rel.as_posix(),'original_sha256':review['original_sha256'],
                                   'sanitized_sha256':review['public_sha256'],'events':[{'nested_archive_changes':review['changes']}]})
            members.append((rel.as_posix(),clean));continue
        if re.search(rb'sk-(?:proj-)?[A-Za-z0-9_-]{32,}',data):
            raise RuntimeError('Potential credential in '+rel.as_posix())
        clean,events=sanitize(rel.as_posix(),data)
        if events:
            redactions.append({'path':rel.as_posix(),'original_sha256':hashlib.sha256(data).hexdigest(),
                               'sanitized_sha256':hashlib.sha256(clean).hexdigest(),'events':events})
        members.append((rel.as_posix(),clean))
    privacy={'schema_version':'eval-author-release-redactions/v1','original_logs_modified':False,
             'transcript_policy':'Public archive contains sanitized transcript copies, not complete raw transcripts. Exact originals remain local.',
             'redactions':redactions}
    members.append(('PRIVACY-REDACTIONS.json',(json.dumps(privacy,indent=2)+'\n').encode()))
    members.append(('NESTED-ARCHIVE-REVIEW.json',(json.dumps({'model_delivered_archives':nested_reviews,
                    'policy':'Intended model ZIPs preserved byte-for-byte when bounded scan needs no change; sanitization/exclusion explicit and original hashes retained.'},indent=2)+'\n').encode()))
    members.append(('RELEASE-EXCLUSIONS.json',(json.dumps({'schema_version':'eval-author-release-exclusions/v1',
                    'private_originals_preserved':True,'excluded':excluded,
                    'note':'Intended model-delivered ZIPs are retained after bounded nested scans. Other duplicate archives, caches and unsafe/private payloads are explicitly omitted. Public file sets intentionally differ from private raw inventories.'},indent=2)+'\n').encode()))
    members.append(('SCORING-POLICY.json',(json.dumps({'default_scorer':'run_meta_eval.py',
                    'native_control_adapter':'run_eval_current.py',
                    'score_registry':'meta_eval/CHECK-REGISTRY.json',
                    'default_author_runner':'run_clean_screen_v2.py',
                    'historical_author_runner':'run_screen.py is retained only for original screen reproduction',
                    'owner_adjudication':'owner/ADJUDICATION.json',
                    'frozen_runtime':'run_eval.py is retained only for original receipt reproduction',
                    'successor_controls':'explicit opt-in; post-outcome correction is a separate condition'},indent=2)+'\n').encode()))
    manifest={'schema_version':'eval-author-release/v1','files':[{'path':name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}for name,data in members],
              'excluded_count':len(excluded),'model_results_included':any(name.startswith('runs/screen/')for name,_ in members),
              'transcripts_sanitized':True,'redacted_file_count':len(redactions)}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as archive:
        for name,data in members:archive.writestr(name,data)
        archive.writestr('RELEASE-MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    if a.output.stat().st_size>50_000_000:raise RuntimeError('Archive exceeds50MB')
    if a.verify:
        with tempfile.TemporaryDirectory(prefix='eval-release-clean-')as temp:
            extracted=Path('\\\\?\\'+temp)if os.name=='nt'else Path(temp)
            try:
                with zipfile.ZipFile(a.output)as archive:archive.extractall(extracted)
                result=subprocess.run([sys.executable,'-B',str(extracted/'verify_release.py')],capture_output=True,text=True)
            finally:
                # Exact directory created above, never an interpolated workspace target.
                import shutil
                if extracted.is_dir():shutil.rmtree(extracted)
            print(result.stdout,result.stderr)
            if result.returncode:raise RuntimeError('Clean verification failed')
    print(json.dumps({'archive':str(a.output),'bytes':a.output.stat().st_size,'files':len(members),'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()}))

if __name__=='__main__':main()
