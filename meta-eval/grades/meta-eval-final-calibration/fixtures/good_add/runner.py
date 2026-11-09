import json
from pathlib import Path
from grader import grade
c=json.loads(Path(__file__).with_name('controls.json').read_text());print(json.dumps({'results':[grade(x['candidate'])for x in c]}))
