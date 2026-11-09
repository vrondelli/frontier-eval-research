"""Portable native recipes for the immutable historical deliveries."""
import copy
import json
from pathlib import Path
import re

from .core import sha
from .runtime import docker_command

OLD_ROOT = "/home/vlad_/projects/engineer-assessment/research/hackathon/eval-author-meta-eval-20261108"


def read(root, path):
    return json.loads((root / path).read_text(encoding="utf-8-sig"))


def relocate(command, root):
    command = list(command)
    if command and command[0] == "wsl.exe":
        command = command[command.index("--exec") + 1:]
    return [s.replace(OLD_ROOT, str(root)) for s in command]


def recipe(command, root, name, **extra):
    return {"name": name, "command": relocate(command, root), **extra}


def h6_profile(attempt):
    cohort = attempt["cohort"]
    if cohort == "initial_screen" and attempt["model_requested"] == "gpt-6.1-sol":
        return {"module": "evaluate", "cases": "make_cases", "cases_module": "evaluate", "call": "e.evaluate([sys.executable,str(script)],cwd=script.parent)", "key": "success", "judge": "judge_output", "path": False, "string_expected": True}
    if cohort == "H6_same_condition_confirmation":
        if attempt["draw"] == "draw2":
            return {"module": "evaluate", "cases_module": "cases", "cases": "build_cases", "call": "e.run_suite([sys.executable,str(script)],script.parent)", "key": "all_passed", "judge": "check_output", "path": True, "string_expected": True}
        return {"module": "run_eval", "cases_module": "cases", "cases": "build_cases", "call": "e.evaluate(script)", "key": "all_passed", "judge": "judge", "path": False}
    if cohort == "selected_hit_clean_staging":
        return {"module": "evaluate", "cases_module": "evaluate", "cases": "cases", "call": "e.evaluate(script)", "key": "passed", "judge": "judge", "path": True}
    return {"module": "evaluate", "cases_module": "cases", "cases": "build_cases", "call": "e.run_suite(script,work_dir='/tmp')", "key": "all_passed", "judge": "judge", "path": False}


def build(root, attempt, image):
    """Recipes never import prior verdicts. Only owner-side invocation mappings reused."""
    package = root / attempt["directory"] / "delivery"
    result = {"id": attempt["id"], "case_id": attempt["case_id"], "cohort": attempt["cohort"],
              "model": attempt["model_requested"], "native_status": attempt["effective_status"],
              "package": str(package.relative_to(root)), "jobs": [], "review_evidence": attempt["review_evidence"],
              "historical_verified_dimensions": attempt["verified_dimensions"]}
    if result["native_status"] not in {"completed", "recovered_completed_turn_delivery"}:
        return result
    case = result["case_id"]
    if case in {"H8", "H9"}:
        result["supplementary"] = True
        return result
    jobs = result["jobs"]
    model, cohort = result["model"], result["cohort"]
    if case == "H1":
        if cohort == "initial_screen":
            path = "grades/root-review/H1-SOL-REPLAY.json"
        elif cohort == "H1_budget_diagnostic":
            path = f"grades/owner-review/H1-BUDGET-{attempt['draw']}-FULL.json"
        elif cohort == "selected_hit_clean_staging":
            path = "grades/owner-review/H1-CLEAN-FULL.json"
        else:
            path = "grades/owner-review/H1-COACHED-FULL.json"
        source = read(root, path)
        source_rows = source.get("rows", source.get("checks"))
        for row in source_rows:
            expected = row.get("expected_pass", row.get("expected_after_public_vocabulary_mapping"))
            jobs.append(recipe(row["command"], root, row["control"], kind="control", expected=expected,
                               family="baseline", mapping_source=path, mapping_sha256=sha(root / path)))
        base = next(row for row in source_rows if row["control"] == "correct_accepted")
        command = relocate(base["command"], root)
        control = str(root / "meta_eval/controls/H1/wrong_B_reply_v2.json")
        original = str(root / "owner/cases/H1/correct_accepted.json")
        command = [v.replace(original, control) for v in command]
        jobs.append({"name": "wrong_B_reply_sibling", "command": command, "kind": "control", "expected": False, "family": "sibling"})
        references = {
            "initial_screen": "examples/reference_service.py",
            "selected_hit_clean_staging": "tests/fixtures/reference_service.py",
            "selected_hit_coached_staging": "e1eval/reference.py",
        }
        ref = references.get(cohort)
        if cohort == "H1_budget_diagnostic":
            ref = {"draw1": None, "draw2": "controls/reference.py", "draw3": "tests/fixtures/reference.py"}[attempt["draw"]]
            if ref is None:
                candidates = list(package.rglob("*service*.py"))
                ref = str(candidates[0].relative_to(package)) if candidates else None
        if ref and (package / ref).is_file():
            result["reference"] = ref
            code = """import json,runpy
from pathlib import Path
m=runpy.run_path('/checker.py');ok,ev=m['check_h1']({'code':Path('/reference.py').read_text()});print(json.dumps({'ok':ok,'evidence':ev}))
"""
            jobs.append({"name": "independent_reference_core", "kind": "reference_core", "command": docker_command([(package / ref, "/reference.py"), (root / "owner/check_cases.py", "/checker.py")], code, image)})
            code = """import importlib.util,json,multiprocessing,sqlite3,tempfile
spec=importlib.util.spec_from_file_location('owner_checked_reference','/reference.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=[]
for repeat in range(3):
 with tempfile.TemporaryDirectory()as folder:
  path=folder+'/db';m.Service(path);ctx=multiprocessing.get_context('fork');gate=ctx.Barrier(2);q=ctx.Queue()
  def worker(key):
   try:
    s=m.Service(path);gate.wait(timeout=6);r=s.apply({'key':key,'account':'A','amount':60});q.put({'key':key,'reply':r})
   except Exception as e:q.put({'key':key,'error':repr(e)})
  processes=[ctx.Process(target=worker,args=(key,))for key in ['x','y']]
  for p in processes:p.start()
  replies=[q.get(timeout=10)for _ in processes]
  for p in processes:p.join(timeout=6)
  ok=all('reply'in r for r in replies)
  if ok:
   accepted=sum(r['reply']['status']in ['accepted','applied']for r in replies);ok=accepted==1 and all(r['reply']['remaining']==40 for r in replies)
   ok=ok and all(m.Service(path).apply({'key':r['key'],'account':'A','amount':60})==r['reply']for r in replies)
  with sqlite3.connect(path)as db:ok=ok and db.execute("select remaining from accounts where account='A'").fetchone()[0]==40 and db.execute('select count(*)from ledger').fetchone()[0]==1
  rows.append({'pass':ok,'replies':replies})
print(json.dumps({'ok':all(r['pass']for r in rows),'repetitions':rows}))
"""
            jobs.append({"name": "independent_reference_concurrency", "kind": "reference_boundary", "command": docker_command([(package / ref, "/reference.py")], code, image)})
    elif case == "H4":
        path = f"grades/owner-review/{model}-H4-SUCCESSOR.json"
        for row in read(root, path)["rows"]:
            jobs.append(recipe(row["command"], root, row["control"], kind="control", expected=row["expected_pass"], family="baseline", mapping_source=path))
    elif case == "H7":
        prefix = "sol" if model == "gpt-6.1-sol" else "astra"
        adapter = read(root, f"grades/adapters/{prefix}-H7.json")
        initial = next(c for c in read(root, "owner/cases/manifest.json")["cases"] if c["case_id"] == "H7")["controls"]
        sibling = read(root, "owner/expansion-h7/MANIFEST.json")["controls"]
        for family, controls in [("baseline", initial), ("sibling", sibling)]:
            for control in controls:
                source = root / control["path"]
                values = {"case_file": "/control.json", "package_dir": "/subject", "candidate_dir": "/candidate"}
                command = docker_command([(package, "/subject"), (source, "/control.json")], "", image)
                command = command[:command.index("-c") - 2] + [v.format(**values) for v in adapter["command"]]
                jobs.append({"name": source.stem, "kind": "control", "expected": control["expected_pass"], "family": family, "command": command})
        result["reference"] = "evaluation/reference.json"
    elif case == "H6":
        profile = h6_profile(attempt)
        result["h6_profile"] = profile
        negatives = next(c for c in read(root, "owner/cases/manifest.json")["cases"] if c["case_id"] == "H6")["controls"]
        negatives = [c for c in negatives if not c["expected_pass"]]
        for control in negatives:
            code = """import importlib,json,os,shutil,sys
from pathlib import Path
c=json.load(open('/control.json'));shutil.copytree('/subject','/tmp/eval');Path('/tmp/candidate').mkdir();script=Path('/tmp/candidate/summarize.py');script.write_text(c['code']);sys.path.insert(0,'/tmp/eval/evaluation');os.chdir('/tmp');e=importlib.import_module(MODULE);r=CALL;print(json.dumps({'pass_verdict':r[KEY],'report':r}))
""".replace("MODULE", repr(profile["module"])).replace("CALL", profile["call"]).replace("KEY", repr(profile["key"]))
            jobs.append({"name": control["id"], "kind": "control", "expected": False,
                         "family": "baseline" if "luna" in control["id"] else "sibling",
                         "command": docker_command([(package, "/subject"), (root / control["path"], "/control.json")], code, image)})
        expected = "'0'" if profile.get("string_expected") else "0"
        raw = '{"adjustment_sheets":{"zero":{"stat":"event_count","turns":[]}}}'
        code = """import importlib,json,sys
from pathlib import Path
sys.path.insert(0,'/subject/evaluation');e=importlib.import_module(MODULE)
Case=getattr(e,'Case',None)
if Case is None:Case=importlib.import_module('cases').Case
case=Case('owner-empty-count','owner',RAW,{'zero':EXPECTED});rows=[]
for token in ['0','0e10000000000000000000']:
 out='{"stock_reports":{"zero":'+token+'}}';p=Path('/tmp/output.json');p.write_text(out)
 r=getattr(e,JUDGE)(case,0,OUTPUT)
 accepted=(r is None)if JUDGE in ['judge_output','check_output']else r[0]
 rows.append({'token':token,'accepted':accepted,'detail':r})
print(json.dumps({'rows':rows}))
""".replace("MODULE", repr(profile["module"])).replace("RAW", repr(raw.encode() if profile.get("string_expected") or cohort == "selected_hit_clean_staging" else raw)).replace("EXPECTED", expected).replace("JUDGE", repr(profile["judge"])).replace("OUTPUT", "p" if profile["path"] else "out.encode()")
        jobs.append({"name": "legal_output_pair", "kind": "output_pair", "command": docker_command([(package, "/subject")], code, image)})
        code = """import importlib,json,sys
sys.path.insert(0,'/subject/evaluation');m=importlib.import_module(MODULE);cases=getattr(m,FUNCTION)();rows=[]
for c in cases:
 raw=next(getattr(c,n)for n in ['raw','data','payload']if hasattr(c,n))
 if c.expected is None:raw=''
 rows.append({'name':c.name,'raw':raw.decode('utf8')if isinstance(raw,bytes)else raw,'expected':None if c.expected is None else {str(k):str(v)for k,v in c.expected.items()}})
print(json.dumps({'cases':rows}))
""".replace("MODULE", repr(profile["cases_module"])).replace("FUNCTION", repr(profile["cases"]))
        jobs.append({"name": "export_reference_cases", "kind": "numeric_reference", "command": docker_command([(package, "/subject")], code, image)})
    elif case == "H3":
        reference = root / "runs/screen/gpt-6-astra/H3/delivery/reference"
        module = "evaluation/evaluate.py" if model == "gpt-6.1-sol" else "evaluate.py"
        code = """import json,subprocess,sys,shutil
from pathlib import Path
shutil.copytree('/subject','/tmp/eval');shutil.copytree('/candidate','/tmp/candidate')
p=subprocess.run([sys.executable,'/tmp/eval/MODULE','/tmp/candidate','--output','/tmp/result.json'],capture_output=True,text=True,timeout=120)
q=Path('/tmp/result.json');print(json.dumps({'native_exit':p.returncode,'report':json.loads(q.read_text())if q.exists()else None,'stderr':p.stderr}))
""".replace("MODULE", module)
        jobs.append({"name": "feature_free_reference_probe", "kind": "hybrid", "command": docker_command([(package, "/subject"), (reference, "/candidate")], code, image)})

    # The author's own verification suite is a distinct execution, with no owner bank mounted.
    tests = [p for p in package.rglob("test*.py") if "input" not in p.parts and "__pycache__" not in p.parts]
    selftest = package / "evaluation/selftest.py"
    if tests or selftest.is_file():
        if selftest.is_file():
            invocation = ["evaluation/selftest.py"]
        elif case == "H1" and cohort == "selected_hit_coached_staging":
            invocation = ["-m", "unittest", "e1eval.test_eval"]
        elif (package / "test_evaluation.py").is_file():
            invocation = ["test_evaluation.py"]
        elif case == "H4":
            invocation = ["evaluation/test_evaluation.py"]
        else:
            testdir = "tests" if any(p.parent == package / "tests" for p in tests) else "evaluation/tests" if any(p.parent == package / "evaluation/tests" for p in tests) else "evaluation" if all(p.parent == package / "evaluation" for p in tests) else "."
            invocation = ["-m", "unittest", "discover", "-s", testdir, "-p", "test*.py"]
        bootstrap = """import json,runpy,sys,unittest
from pathlib import Path
events={'unittest_cases_entered':0,'native_grader_calls':0}
case_code=unittest.TestCase.run.__code__
def observe(frame,event,arg):
 if event=='call':
  if frame.f_code is case_code:events['unittest_cases_entered']+=1
  if frame.f_code.co_filename.startswith('/tmp/eval/')and frame.f_code.co_name in ['grade','evaluate','run_suite']:events['native_grader_calls']+=1
sys.argv=INVOCATION;status=0;sys.setprofile(observe)
try:
 if sys.argv[0]=='-m':
  module=sys.argv[1];sys.argv=sys.argv[1:];runpy.run_module(module,run_name='__main__',alter_sys=True)
 else:runpy.run_path(sys.argv[0],run_name='__main__')
except SystemExit as e:status=e.code or 0
finally:
 sys.setprofile(None);Path('/tmp/owner-verification-events.json').write_text(json.dumps(events))
raise SystemExit(status)
""".replace("INVOCATION", repr(invocation))
        inner = """import json,os,shutil,subprocess,sys
shutil.copytree('/subject','/tmp/eval');os.chdir('/tmp/eval');env=dict(os.environ);env['PYTHONPATH']='/tmp/eval:/tmp/eval/evaluation'
p=subprocess.run([sys.executable,'-B','-c',BOOTSTRAP],capture_output=True,text=True,env=env,timeout=180)
report=Path('/tmp/eval/evaluation/selftest-report.json')
events=Path('/tmp/owner-verification-events.json')
print(json.dumps({'native_exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'observed_execution_events':json.loads(events.read_text())if events.exists()else None,'verification_report':json.loads(report.read_text())if report.exists()else None}))
""".replace("BOOTSTRAP", repr(bootstrap)).replace("import json,os,shutil,subprocess,sys", "import json,os,shutil,subprocess,sys\nfrom pathlib import Path")
        if case == "H1":
            command = ["bwrap", "--die-with-parent", "--unshare-all", "--ro-bind", "/usr", "/usr", "--symlink", "usr/lib", "/lib", "--symlink", "usr/lib64", "/lib64", "--symlink", "usr/bin", "/bin", "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp", "--clearenv", "--setenv", "PATH", "/usr/bin:/bin", "--ro-bind", str(package), "/subject", "--chdir", "/tmp", "/usr/bin/python3", "-B", "-c", inner]
        else:
            command = docker_command([(package, "/subject")], inner, image)
        jobs.append({"name": "author_verification", "kind": "selftests", "command": command, "timeout": 210})
    for job in jobs:
        job["command"] = [image if v == "python:3.14-slim" else v for v in job["command"]]
    return result
