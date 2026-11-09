import hashlib,json,pathlib,shutil
root=pathlib.Path(__file__).resolve().parent;archive=root/'release/eval-author-meta-eval.zip'
receipt=json.loads((root/'grades/release-verification/CANDIDATE-CLEAN-FINDINGS.json').read_text())
digest=hashlib.sha256(archive.read_bytes()).hexdigest();assert receipt['all_passed']and receipt['archive_sha256']==digest
backup=root/'release'/('verified-candidate-'+digest[:12]+'.zip')
if not backup.exists():shutil.copy2(archive,backup)
assert hashlib.sha256(backup.read_bytes()).hexdigest()==digest
value={'kind':'provisional_verified_backup_not_final_entry','archive':backup.name,'sha256':digest,'bytes':backup.stat().st_size,'proof':'grades/release-verification/CANDIDATE-CLEAN-FINDINGS.json','pending':'Finalcoachedresults andhumanreview notcontainedascomplete; finalZIPwillberebuilt.'}
(root/'release/CANDIDATE-DELIVERY.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(value))
