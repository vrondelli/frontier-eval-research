import json,subprocess,pathlib,sys
cmd=[sys.executable,sys.argv[1],'/work/probe_candidates/heldout_lookup','--output','/tmp/evaluation.json']
p=subprocess.run(cmd,text=True,capture_output=True,timeout=180)
out={'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
q=pathlib.Path('/tmp/evaluation.json')
if q.exists():out['evaluation_result']=json.loads(q.read_text())
q=pathlib.Path('/tmp/h3-outside-read-proof.jsonl')
out['outside_read_proofs']=[json.loads(l) for l in q.read_text().splitlines()] if q.exists() else []
print(json.dumps(out))
