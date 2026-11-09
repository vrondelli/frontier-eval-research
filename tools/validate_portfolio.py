#!/usr/bin/env python3
"""Check portfolio coverage, provenance, links and immutable bundle contents.
Works without the ignored historical archive; never executes candidate code.
"""
from pathlib import Path
import hashlib,json,re,sys,zipfile
from urllib.parse import unquote
ROOT=Path(__file__).resolve().parents[1]
load=lambda p:json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
failures=[];checks=[]
def check(name,condition):
 (checks if condition else failures).append(name)
c=load('data/campaigns.json');p=load('data/frontier-protocols.json');a=load('data/meta-eval-attempts.json');m=load('data/MIGRATION.json')
check('55 unique campaign directories',len(c['campaigns'])==len({x['directory'] for x in c['campaigns']})==55)
check('campaigns match exact migration directory census',set(x['directory'] for x in c['campaigns'])==set(x for x in m['original_top_level_entries'] if not x.endswith(('.md','.json','.py'))))
check('151 unique authored frontier protocol designs',len(p['protocols'])==len({x['protocol'] for x in p['protocols']})==151)
r=load('evidence/ledgers/complete-recap-audit-20261108/R1-R10-PROTOCOL-LEDGER.json')
check('67 protocol rows / 295 counted episodes',len(r['rows'])==67 and sum(x['model_episodes_as_counted'] for x in r['rows'])==295)
check('31 unique meta-eval attempt slots',len(a['attempts'])==len({x['id'] for x in a['attempts']})==31)
check('19 scored packages',sum(bool(x['scoring'].get('score_interval')) for x in a['attempts'])==19)
for x in a['attempts']:
 s=x['scoring']
 if not s.get('score_interval'):continue
 lo,hi=s['score_interval'];check('score accounting: '+x['id'],abs(lo-s['points_observed_pass'])<1e-6 and abs(hi-lo-s['points_unresolved'])<1e-6 and abs(s['points_observed_pass']+s['points_observed_fail']+s['points_unresolved']-100)<1e-6 and not s['qualified'])
orig=load('evidence/ledgers/original-five-rerun-20261108/RESULTS.json')
check('14 original-five started episodes retained',orig['total_started_episodes_retained']==14)
ver=load('evidence/ledgers/verification-eval-20261108/RESULTS.json')
check('30 verification-repair outcomes retained',len(ver['rows'])==30 and all(x['status']=='pass' for x in ver['rows']))
source_map=load('data/source-map.json')
archive=ROOT/'research/hackathon';local=archive.exists()
for s in source_map['sources']:
 pub=ROOT/s['public'];check('export hash: '+s['public'],pub.is_file() and sha(pub)==s['public_sha256'])
 if local:
  src=archive/s['source'];check('original hash: '+s['source'],src.is_file() and sha(src)==s['original_sha256'])
if local:check('live archive matches campaign directory census',set(x.name for x in archive.iterdir() if x.is_dir())==set(x['directory'] for x in c['campaigns']))
zip_path=ROOT/'releases/eval-author-meta-eval-scored-v2.zip'
expected='fb4fca7b22311573f65337f83fb17ad63fa0cce4225505f2727ffc6506cf1c45'
check('immutable release SHA256',sha(zip_path)==expected)
check('immutable release size',zip_path.stat().st_size==25923702)
zip_count=0
with zipfile.ZipFile(zip_path) as z:
 for info in z.infolist():
  if info.is_dir():continue
  zip_count+=1;dest=ROOT/'meta-eval'/info.filename
  check('extracted bytes: '+info.filename,dest.is_file() and hashlib.sha256(z.read(info)).hexdigest()==sha(dest))
docs=[ROOT/'README.md',ROOT/'AGENTS.md',ROOT/'AI-ASSISTANCE.md',ROOT/'RIGHTS.md',*sorted((ROOT/'docs').rglob('*.md'))]
link_count=0
for doc in docs:
 for match in re.finditer(r'\[[^\]]*\]\(([^)]+)\)',doc.read_text(encoding='utf-8-sig')):
  target=match[1].strip('<>')
  if re.match(r'(https?://|mailto:|#)',target):continue
  target=unquote(target.split('#')[0]);link_count+=1
  check('link: '+str(doc.relative_to(ROOT))+' -> '+target,(doc.parent/target).exists())
# A clone must also retain the source records of every linked current campaign.
for x in c['campaigns']:check('campaign page: '+x['directory'],(ROOT/x['portfolio_page']).exists())
report={'schema':'portfolio-validation/v1','all_passed':not failures,'checks_passed':len(checks),'failures':failures,'campaigns':55,'r1_r10_protocols':67,'r1_r10_counted_episodes':295,'authored_protocols':len(p['protocols']),'meta_author_attempts':31,'scored_packages':19,'release_files_checked':zip_count,'curated_document_links_checked':link_count,'source_exports_checked':len(source_map['sources']),'local_archive_present':local,'human_review_complete':False,'model_calls':0}
# A run in a clone can inspect the historical receipt without rewriting it.
print(json.dumps(report,indent=2))
sys.exit(0 if not failures else 1)

