"""Offline proof that intended ZIPs survive and unsafe/private members are explicit."""
import io,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from release_nested import inspect_zip
def make(entries):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w')as archive:
        for name,data in entries.items():archive.writestr(name,data)
    return stream.getvalue()
benign=make({'safe.py':'print(1)'})
copy,review=inspect_zip(benign);assert copy==benign and not review['changes']
event=json.dumps({'type':'item.completed','item':{'id':'m1','type':'command_execution','command':'read MEMORY.md','aggregated_output':'unrelated private text'}})+'\n'
dirty=make({'../escape':'unsafe','.env':'not-public','log.jsonl':event,'safe.py':'print(1)'})
clean,changed=inspect_zip(dirty)
with zipfile.ZipFile(io.BytesIO(clean))as archive:
    assert '../escape'not in archive.namelist()and'.env'not in archive.namelist()
    assert b'unrelated private text'not in archive.read('log.jsonl')and archive.read('safe.py')==b'print(1)'
artifact=ROOT/'runs/clean_screen_v2/coached/gpt-6.1-sol/H1/delivery/e1-eval.zip'
actual,actual_review=inspect_zip(artifact.read_bytes());assert actual==artifact.read_bytes()
report={'model_calls':0,'benign_zip_byte_exact':True,'unsafe_paths_and_private_environment_omitted':True,
        'memory_output_sanitized':True,'actual_coached_model_zip_review':actual_review,
        'actual_model_zip_preserved_byte_exact':True,'synthetic_changes':changed['changes']}
(ROOT/'grades/audit-review/NESTED-RELEASE-SELF-CHECK.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'model_calls':0,'all_checks_pass':True,'actual_zip_members':actual_review['members'],'actual_zip_unchanged':True}))
