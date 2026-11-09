"""An always-reject grader cannot qualify through an all-negative surviving bank."""
import json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory(prefix='eval-partial-gate-')as temp:
    package=Path(temp);(package/'grade.py').write_text('import json\nprint(json.dumps({"pass": False}))\n')
    output=ROOT/'grades/audit-review/CURRENT-PARTIAL-GOLD-CHECK.json'
    result=subprocess.run([sys.executable,str(ROOT/'run_eval_current.py'),'score','--package',str(package),'--case','H6',
                           '--output',str(output),'--allow-unisolated-diagnostic'],capture_output=True,text=True)
    receipt=json.loads(output.read_text())
    assert result.returncode==2 and receipt['status']=='scored_partial_only'
    assert receipt['adjudicated_control_coverage']['H6']['admitted_positive_controls']==0
    print(json.dumps({'model_calls':0,'always_reject_cannot_qualify':True,'status':receipt['status']}))
