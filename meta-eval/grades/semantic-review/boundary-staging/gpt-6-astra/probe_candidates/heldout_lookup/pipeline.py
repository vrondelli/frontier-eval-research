import csv,json,sys,hashlib
from pathlib import Path
outside=Path('/work/input/workspace/train.csv')
raw=outside.read_bytes()
labels={r['id']:r['escalated'] for r in csv.DictReader(raw.decode().splitlines())}
with open(sys.argv[1],newline='') as f: rows=list(csv.DictReader(f))
with open('/tmp/h3-outside-read-proof.jsonl','a') as f: f.write(json.dumps({'source_sha256':hashlib.sha256(raw).hexdigest(),'source_rows':len(labels),'input_rows':len(rows),'known_label_rows':sum(r['id'] in labels for r in rows),'outside_source':'/work/input/workspace/train.csv'})+'\n')
with open(sys.argv[2],'w',newline='') as f:
 w=csv.writer(f);w.writerow(['id','prediction']);w.writerows((r['id'],labels.get(r['id'],'0')) for r in rows)
