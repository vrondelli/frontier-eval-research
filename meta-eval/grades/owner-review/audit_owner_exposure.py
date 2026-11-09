"""Scoped source-path exposure census over completed captured native tool records."""
from pathlib import Path
import collections,hashlib,json,re
B=Path(__file__).resolve().parents[2];rows=[]
for path in sorted((B/'runs').rglob('transcript.jsonl')):
 if 'clean_screen' in path.parts:continue
 commands=[];mcp=[];hits=[];types=collections.Counter()
 for line in path.read_text(encoding='utf-8',errors='replace').splitlines():
  try:x=json.loads(line)
  except ValueError:continue
  item=x.get('item',{})
  if x.get('type')=='item.completed':types[item.get('type','missing_type')]+=1
  if item.get('type')=='command_execution'and x.get('type')=='item.completed':
   command=item.get('command','');commands.append(command)
   # CLI commands retain escaped backslashes; normalize repeated separators too.
   lower=re.sub('/+','/',command.lower().replace('\\','/'))
   matched=[needle for needle in ['owner/cases','owner/check_cases','complete-recap-audit','saved_luna_decimal','owner/adjudication','memory.md','provenance.json']if needle in lower]
   if matched:hits.append({'matches':matched,'command':command,'command_sha256':hashlib.sha256(command.encode()).hexdigest()})
  if item.get('type')=='mcp_tool_call'and x.get('type')=='item.completed':mcp.append({'server':item.get('server'),'tool':item.get('tool')})
 rows.append({'transcript':str(path.relative_to(B)),'completed_item_types':dict(types),'completed_shell_commands':len(commands),'completed_mcp_calls':len(mcp),'mcp_names':mcp,'source_or_memory_path_hits':hits})
audit=B/'grades/audit-review/METADATA-EXPOSURE.json';review=json.loads(audit.read_text())if audit.exists()else None
provenance_reads=[{'model':c['model'],'case_id':c['case_id'],'events':len(c.get('confirmed_provenance_content_events',[]))}for c in review['case_reviews']if c.get('confirmed_provenance_content_events')]if review else []
out={'kind':'scoped_owner_source_path_exposure_search','scope':'Native completed command receipts and MCP tool names in captured transcripts; exact path/string search, not cryptographic read confinement or semantic proof. Memory references and provenance exposure are real context additions, not proof of owner-bank access.','correction':'Initial narrow pattern missed Windows escaped separators and memory references. Its zero was not evidence of no memory access. Metadata exposure review takes precedence for observed reads.','metadata_review_reference':'grades/audit-review/METADATA-EXPOSURE.json','confirmed_provenance_read_subjects':provenance_reads,'root_independently_confirmed_external_memory_reads':[{'model':'gpt-6.1-sol','case_id':'H1'},{'model':'gpt-6-astra','case_id':'H1'},{'model':'gpt-6-astra','case_id':'H3'}],'rows':rows}
(B/'grades/owner-review/EXPOSURE-PATH-CENSUS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'transcripts':len(rows),'shell_commands':sum(r['completed_shell_commands']for r in rows),'mcp_calls':sum(r['completed_mcp_calls']for r in rows),'path_hit_transcripts':sum(bool(r['source_or_memory_path_hits'])for r in rows)}))
