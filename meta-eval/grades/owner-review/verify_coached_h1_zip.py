from pathlib import Path,PurePosixPath
import hashlib,json,zipfile
B=Path(__file__).resolve().parents[2];package=B/'runs/clean_screen_v2/coached/gpt-6.1-sol/H1/delivery';archive=package/'e1-eval.zip'
rows=[];unsafe=[];manifest_checks={}
with zipfile.ZipFile(archive)as z:
 for item in z.infolist():
  if item.is_dir():continue
  name=PurePosixPath(item.filename)
  if name.is_absolute()or'..'in name.parts or'\\'in item.filename:unsafe.append(item.filename);continue
  raw=z.read(item);p=package.joinpath(*name.parts);source_name=item.filename
  if not p.is_file()and len(name.parts)>1 and name.parts[0]=='e1-eval':p=package.joinpath(*name.parts[1:]);source_name='/'.join(name.parts[1:])
  sha=hashlib.sha256(raw).hexdigest();rows.append({'zip_member':item.filename,'workspace_relative':source_name,'bytes':len(raw),'zip_sha256':sha,'workspace_exists':p.is_file(),'matches_graded_workspace':p.is_file()and hashlib.sha256(p.read_bytes()).hexdigest()==sha})
 archive_manifest=json.loads(z.read('MANIFEST.json'))
 for name,digest in archive_manifest['sha256'].items():manifest_checks[name]=hashlib.sha256(z.read(name)).hexdigest()==digest
 manifest_checks['exact_payload_member_set']=set(archive_manifest['sha256'])==set(z.namelist())-{'MANIFEST.json'}
required=['TASK.md','README.md','e1eval/grader.py','e1eval/oracle.py','e1eval/runner.py','e1eval/worker.py','input/E1.md','input/README.md']
required_checks={name:any(r['workspace_relative']==name and r['matches_graded_workspace']for r in rows)for name in required}
result={'kind':'coached_h1_intended_zip_to_graded_workspace_binding','archive':str(archive.relative_to(B)),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'unsafe_entries':unsafe,'required_checks':required_checks,'all_required_match':all(required_checks.values()),'all_zip_files_match_workspace':all(r['matches_graded_workspace']for r in rows),'all_payload_files_match_graded_workspace':all(r['matches_graded_workspace']for r in rows if r['zip_member']!='MANIFEST.json'),'generated_manifest_checks':manifest_checks,'generated_manifest_valid':all(manifest_checks.values()),'rows':rows,'scope':'SHA256 comparison of every archived file against immutable workspace; no extra native replay needed when task/grader/runtime/input bytes match. Archive-only generated manifest is independently hash-checked and is the sole extra metadata file, not an executable mismatch.'}
(B/'grades/owner-review/H1-COACHED-ZIP-BINDING.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='rows'}))
