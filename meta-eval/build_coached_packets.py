"""Build an explicit secondary prompt arm; never changes frozen primary packets."""
import argparse,hashlib,json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parent
COACH='Create a complete runnable eval for this task, including a public task statement, independent reference, grader, positive and negative controls, clean runner, and a report schema. State every graded requirement in the public task. Verify your eval before delivery.'
args=argparse.ArgumentParser();args.add_argument('--refresh-unrun-coached',action='store_true');refresh=args.parse_args().refresh_unrun_coached
for source in sorted((ROOT/'packets/primary').iterdir()):
 if not source.is_dir():continue
 target=ROOT/'packets/coached'/source.name
 if target.exists()and not refresh:raise SystemExit('Refusing overwrite '+str(target))
 target.mkdir(parents=True,exist_ok=True);shutil.copytree(source/'input',target/'input',dirs_exist_ok=True)
 coach=COACH
 if source.name=='H2':coach='Preserve the original one-file criteria.md deliverable. Verify that each scoring check is mechanically answerable from proposal text, that worked examples use the checks consistently, and that the numeric mapping covers all attainable totals. State limitations explicitly.'
 if source.name in ['H8','H9']:coach='Preserve the original audit/report deliverable. Reconcile every source record and storage layout, distinguish files from runs and grader invocations, recompute denominators, distinguish unknowns from passes, and support each completeness or execution claim with actual evidence. Verify the audit before delivery.'
 original=(source/'prompt.md').read_text();prompt=original+'\n\nAdditional explicit quality instruction:\n'+coach+'\n'
 (target/'prompt.md').write_text(prompt)
 provenance={'case_id':source.name,'condition_id':'coached_secondary','exact_instruction_replication':False,'parent_prompt_sha256':hashlib.sha256(original.encode()).hexdigest(),'added_instruction':coach,'author_instruction_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'note':'New coaching; never pool with original/minimal primary. No model call made by this builder.'}
 (target/'PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
 files=[{'path':f.relative_to(target).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for f in sorted(target.rglob('*'))if f.is_file()and f.name!='MANIFEST.json']
 (target/'MANIFEST.json').write_text(json.dumps({'condition':'coached_secondary','files':files},indent=2)+'\n')
print(json.dumps({'coached_packets':9,'model_calls':0,'primary_unchanged':True}))
