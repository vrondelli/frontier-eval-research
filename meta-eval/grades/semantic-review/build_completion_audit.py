"""Evidence-based21-node completion audit; zero actor calls, no human signoff."""
from pathlib import Path
from datetime import datetime, timezone
import ast, hashlib, json, re, zipfile
B=Path(__file__).resolve().parents[2]
def read(rel, default=None):
 p=B/rel
 return json.loads(p.read_text(encoding="utf-8-sig"))if p.exists()else default
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def evidence(paths):return [{"path":p,"exists":(B/p).exists(),"sha256":sha(B/p)if(B/p).is_file()else None}for p in paths]
results=read("RESULTS.json",{})
cohorts={c["id"]:c for c in results.get("cohorts",[])}
rows=results.get("attempts",[])
all_terminal=len(rows)==31 and all(c["all_terminal_capture"]for c in cohorts.values())
all_reviewed=len(rows)==31 and all(c["all_semantically_adjudicated"]for c in cohorts.values())
human=read("grades/semantic-review/HUMAN-REVIEW-STATUS.json",{"human_review_completed":False})
freeze=read("FREEZE.json",{})
frozen_checks=[{"path":p,"exists":(B/p).is_file(),"hash_matches":(B/p).is_file()and sha(B/p)==h}for p,h in freeze.get("files",{}).items()]
syntax=[]
for rel in ["run_screen.py","run_confirmation_v2.py","run_confirmation_h6_v2.py","run_clean_screen_v2.py","run_eval_current.py","refresh_results.py","build_release.py","verify_release.py"]:
 p=B/rel
 try:ast.parse(p.read_text(encoding="utf8"));syntax.append({"path":rel,"parse_ok":True,"sha256":sha(p)})
 except Exception as e:syntax.append({"path":rel,"parse_ok":False,"error":str(e)})
archive=B/"release/eval-author-meta-eval.zip"
release={"exists":archive.exists(),"archive":"release/eval-author-meta-eval.zip"}
if archive.exists():
 release.update(sha256=sha(archive),bytes=archive.stat().st_size)
 with zipfile.ZipFile(archive)as z:
  names=set(z.namelist());m=json.loads(z.read("RELEASE-MANIFEST.json"));bad=[]
  for r in m["files"]:
   if r["path"]not in names or hashlib.sha256(z.read(r["path"])).hexdigest()!=r["sha256"]:bad.append(r["path"])
  archived= json.loads(z.read("RESULTS.json"))if"RESULTS.json"in names else{}
  release.update(manifest_files=len(m["files"]),internal_hash_mismatches=bad,archived_attempts=len(archived.get("attempts",[])),archived_pending_semantic=len(archived.get("pending",[])),archived_results_equal_current="RESULTS.json"in names and z.read("RESULTS.json")== (B/"RESULTS.json").read_bytes(),contains_adjudication="ADJUDICATION.md"in names)
 receipts=[]
 for p in (B/"grades/release-verification").glob("*.json"):
  j=read(p.relative_to(B).as_posix(),{})
  receipts.append({"path":p.relative_to(B).as_posix(),"archive_hash_matches":j.get("archive_sha256")==release["sha256"],"all_passed":j.get("all_passed"),"model_calls":j.get("model_calls"),"checks":[{"script":c.get("script"),"exit_code":c.get("exit_code")}for c in j.get("checks",[])]})
 release["clean_replay_receipts"]=receipts
 release["matching_clean_replay_verified"]=any(r["archive_hash_matches"]and r["all_passed"]is True and r["model_calls"]==0 for r in receipts)
release_final=all_terminal and all_reviewed and release.get("matching_clean_replay_verified",False)and release.get("archived_results_equal_current",False)and not release.get("internal_hash_mismatches",[1])
# Every original DAG node is adjudicated against its actual implementation path.
specs={
"D00":("qualified", "Claim contract distinguishes construction dimensions, historical workflow and fresh author attempts.",["protocol/CLAIMS.md","protocol/RUN-POLICY.json","DESIGN.md"],[]),
"D01":("qualified_deviation","One exact author instruction text recovered(H2); eight explicitly reconstructed. No full original-context replication.",["sources/INSTRUCTION-PROVENANCE.json","sources/successor-recovery/H6-ORIGINAL-ROOT-REQUEST.json"],["Preserve exact1/reconstructed8 and unavailable-session-context qualification."]),
"D02":("qualified_deviation","Source census/custody exists. Historical context, metadata and staged H8/H9 populations remain distinct.",["sources/SOURCE-MANIFEST.json","sources/PACKET-VALIDATION.json","grades/audit-review/METADATA-EXPOSURE.json"],[]),
"D03":("qualified_deviation","Nine frozen packets are source-bound; H2 CAL placement/context and newline normalization are disclosed.",["sources/PACKET-VALIDATION.json","packets/primary/H2/PROVENANCE.json","grades/semantic-review/CONTEXT-DEVIATIONS.json"],[]),
"D04":("qualified_deviation","All nine source-license matrices exist; matrices were consolidated after outcome inspection, not prospective gold.",["owner/contracts/CONTRACT-INDEX.json","owner/contracts/README.md"],[]),
"D05":("qualified_deviation","Independent finite positives exist. H4 original complete candidates invalidated; H6 original full-domain positive labels excluded. H2/H3 successor positives are post-outcome component controls.",["owner/ADJUDICATION.json","owner/expansion-h4/MANIFEST.json","owner/semantic-successor/QUALIFICATION-PORTABLE.json"],["Do not upgrade finite/component positives to full-system correctness."]),
"D06":("qualified_deviation","Negative/sibling banks and independent witnesses exist; H4 correction and ten H2/H3 semantic controls are post-outcome and explicitly scoped.",["owner/cases/manifest.json","owner/audit_cases/manifest.json","owner/semantic-successor/MANIFEST.json","owner/semantic-successor/QUALIFICATION-PORTABLE.json"],[]),
"D07":("qualified_deviation","Docker owner-bank boundary and native nested bubblewrap demonstrated. Generation read isolation remains unproven; native memory/context possible.",["owner/runtime/ISOLATED-SELF-CHECK.json","owner/runtime/GENERATION-BOUNDARY-PROBE.json","grades/owner-review/EXPOSURE-PATH-CENSUS.json","grades/owner-review/sol-H1-FULL-BWRAP.json"],[]),
"D08":("qualified_deviation","Current checker applies seven full-task exclusions; native interfaces and manual semantic components used. Complete universal positive qualification is unknown.",["run_eval_current.py","CURRENT-SCORING.md","owner/ADJUDICATION.json","grades/owner-review/H6-REVIEW.md"],["Retain incomplete full-domain qualification rather than inventing green full-system gold."]),
"D09":("qualified_deviation","Primary bytes frozen. Source snapshots/prompt hashes and stdin newline normalization do not imply full-session byte replication.",["FREEZE.json","sources/PACKET-VALIDATION.json"],[]),
"D10":("qualified","Coached packets built separately with explicit stronger checklist; clean primary instruction remains the same sentence.",["build_coached_packets.py","packets/coached/H1/prompt.md","packets/coached/H6/prompt.md","protocol/COACHED-HIT-DIAGNOSTIC-POLICY.json"],[]),
"D11":("human_review_pending","Independent AI source/semantic/boundary reviews exist. User explicitly has not reviewed task meanings; no human signoff.",["grades/semantic-review/HUMAN-REVIEW-STATUS.json","grades/semantic-review/OWNER-REVIEW-PACK.md","grades/semantic-review/H1-INDEPENDENT.json","grades/semantic-review/H6-INDEPENDENT.json"],["Actual owner task-meaning/criterion review remains pending; continue authorized work meanwhile."]),
"D12":("qualified_deviation","Exploratory freeze explicitly records unqualified semantic cases and human review pending; cannot retrospectively become fully prospective.",["FREEZE.json","grades/audit-review/FREEZE-EXPOSURE-REVIEW.json","audit/CONFIRMATION-CONTROLLER-AMENDMENT.json"],[]),
"D13":("qualified_deviation","Actual model transport and runtime proved via fixed runs and environment/capture tests. Original named CALIBRATION.json absent; qualification uses actual receipts.",["grades/audit-review/ENVIRONMENT.json","grades/audit-review/CAPTURE-V2-SELF-CHECK.json","runs/SCREEN-TERMINAL.json"],[]),
"D14":("qualified_deviation","Fixed18 screen terminal:13 ordinary completions,2 recovered completed-turn H9 deliveries,3 timeouts. Six fixed confirmations and3 budget diagnostics terminal, with H6draw1 native terminal unknown.",["runs/SCREEN-TERMINAL.json","runs/CONFIRMATION-TERMINAL.json","runs/CONFIRMATION-H6-TERMINAL.json","runs/BUDGET-H1-TERMINAL.json","protocol/COHORT-INDEX.json"],[]),
"D15":("qualified_deviation","All initial completed/recovered artifacts reviewed in native or source-licensed component interfaces. H5 timeout probes remain diagnostics and H2/H3 manual AI review is not human approval.",["RESULTS.json","grades/owner-review/H1-REVIEW.md","grades/owner-review/H6-REVIEW.md","grades/audit-review/H9-INDEPENDENT-REPLAY.json"],[]),
"D16":("qualified"if cohorts.get("selected_hit_coached_staging",{}).get("all_terminal_capture")else"pending_terminal","Fixed coached pair admitted as separate final secondary condition; no extra model arms.",["protocol/COACHED-HIT-DIAGNOSTIC-POLICY.json","runs/COACHED-HIT-DIAGNOSTIC-TERMINAL.json","runs/COACHED-HIT-DIAGNOSTIC-STATUS.json"],[]if cohorts.get("selected_hit_coached_staging",{}).get("all_terminal_capture")else["Wait only for already admitted coached pair; no replacement."]),
"D17":("qualified_deviation"if cohorts.get("selected_hit_coached_staging",{}).get("all_semantically_adjudicated")else"pending_adjudication","Coached verdicts imported only for terminal completed artifacts with actual semantic replay receipts.",["grades/RESULTS-SUCCESSOR-ADJUDICATIONS.json","RESULTS.json"],[]if cohorts.get("selected_hit_coached_staging",{}).get("all_semantically_adjudicated")else["Finish immutable native coached scoring and import evidence sidecar."]),
"D18":("qualified_deviation"if all_reviewed else"pending_successor_adjudication","Source-licensed adjudication preserves control invalidations, timeouts/captureunknown, distinct fresh conditions, and full-system unknowns.",["ADJUDICATION.md","RESULTS.json","owner/ADJUDICATION.json"],[]if all_reviewed else["Finish pending successor native judgments without inferring from exit0."]),
"D19":("qualified_deviation"if all_reviewed else"pending_final_refresh","Results31 matrix, actual per-turn token receipts and no pooled rate implemented; report exposes any pending outcomes.",["RESULTS.md","RESULTS.json","refresh_results.py"],[]if all_reviewed else["Refresh results after last native adjudication; preserve noUSD/unknownusage limits."]),
"D20":("qualified_local_release"if release_final else"pending_final_release","Current archive hashes and actual clean-extraction replay are checked below. Final external DELIVERY record is authoritative; archived audit is a prepackaging snapshot. Prior verified candidate remains a backup.",["release/DELIVERY.json","release/CANDIDATE-DELIVERY.json","release/eval-author-meta-eval.zip","grades/release-verification/CANDIDATE-CLEAN-FINDINGS.json","build_release.py","verify_release.py","submission/OWNER-CHECKLIST.md"],[]if release_final else["Build current final archive after last results; verify extraction, privacy and saved native reproductions; bind proof to exact archive hash."])
}
dag=read("DAG-PLAN.json",{})
assert len(dag["nodes"])==len(specs)==21 and set(specs)=={n["id"]for n in dag["nodes"]}
nodes=[]
for n in dag["nodes"]:
 status,judgment,paths,remaining=specs[n["id"]]
 nodes.append({"id":n["id"],"title":n["title"],"original_planned_output":n["output"],"status":status,"judgment":judgment,"evidence":evidence(paths),"remaining":remaining})
link_checks=[]
for rel in ["RESULTS.md","ADJUDICATION.md","grades/semantic-review/OWNER-REVIEW-PACK.md"]:
 p=B/rel
 refs=re.findall(r"\]\(([^)]+)\)",p.read_text(encoding="utf8"))if p.exists()else[]
 missing=[r for r in refs if not r.startswith(("http:","https:"))and not(p.parent/r).exists()]
 link_checks.append({"path":rel,"link_count":len(refs),"missing":missing})
audit={"schema_version":"eval-author-completion-audit/v2","audit_utc":datetime.now(timezone.utc).isoformat(),"auditor":"independent_AI_agent_not_human","goal_achieved":release_final,"goal_action":"software_build_delivered_human_qualification_pending"if release_final else"finish_current_software_release","software_build_complete":release_final,"human_formal_qualification_complete":human.get("human_review_completed",False),"owner_actions_after_build":["Human task-meaning and criterion review","Record/publish video if desired","Accept submission terms and submit externally"],"planned_attempts":31,"all_terminal_capture":all_terminal,"all_semantically_adjudicated":all_reviewed,"human_review":human,"instruction_fidelity":"one_exact_instruction_text_job_eight_reconstructed_no_full_session_replication","node_count":len(nodes),"nodes":nodes,"cohorts":list(cohorts.values()),"source_parse_checks":syntax,"frozen_file_checks":frozen_checks,"frozen_hash_mismatches":[x["path"]for x in frozen_checks if not x["hash_matches"]],"markdown_link_checks":link_checks,"release_snapshot":release,"packaging_audit_policy":"The archived audit is a prepackaging snapshot. Final proof belongs to external release/DELIVERY.json; later local audit updates do not mutate or require rebuilding the exact verified archive.","local_release_qualified":release_final,"concrete_remaining":[x for n in nodes for x in n["remaining"]],"model_calls":0}
(B/"COMPLETION-AUDIT.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
lines=["# Independent completion audit","",f"Snapshot: {audit['audit_utc']}. Source and receipts inspected; zero model calls. AI audit only; human review is explicitly pending. Software delivery and later human/external owner actions are separate.","",f"Fixed31 attempts: terminal capture={all_terminal}; semantic adjudications complete={all_reviewed}. Original instruction fidelity: one exact-text job and eight reconstructions; no full-session replication. Current release qualified={release_final}. Software build complete={release_final}; human formal qualification complete={human.get('human_review_completed',False)}.","","| Node | Status | Evidence-based judgment | Remaining |","|---|---|---|---|"]
for n in nodes:
 links="; ".join("["+e["path"]+"]("+e["path"]+")"for e in n["evidence"]if e["exists"])
 lines.append("| "+n["id"]+" "+n["title"]+" | "+n["status"]+" | "+n["judgment"]+" "+links+" | "+" ".join(n["remaining"])+" |")
lines +=["","Source syntax checks: "+str(sum(x["parse_ok"]for x in syntax))+"/"+str(len(syntax))+". Frozen hash mismatches: "+str(audit["frozen_hash_mismatches"])+". Linked source files were resolved on disk. Actual native commands and stdout/stderr are retained in each cited scoring/replay receipt; parsing code alone is not test execution.","","## Remaining work",""]+["- "+x for x in audit["concrete_remaining"]]+["","[COMPLETION-AUDIT.json](COMPLETION-AUDIT.json) binds source hashes, per-node evidence, link checks, exact archive inventory/hash validation and any matching clean-extraction proof. The original DAG paths are logical plans; actual replacement paths and qualifications are explicit above. A green form, completed model turn or unqualified finite positive does not prove full eval correctness."]
(B/"COMPLETION-AUDIT.md").write_text("\n".join(lines)+"\n",encoding="utf8")
print(json.dumps({"nodes":21,"all_terminal_capture":all_terminal,"all_reviewed":all_reviewed,"frozen_hash_mismatches":audit["frozen_hash_mismatches"],"link_checks":link_checks,"local_release_qualified":release_final,"software_build_complete":release_final,"human_formal_qualification_complete":human.get("human_review_completed",False),"model_calls":0}))
