#!/usr/bin/env python3
"""Inspect published summaries without running any model-authored code."""
from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
load=lambda p:json.loads((r/p).read_text(encoding='utf-8-sig'))
c=load('data/campaigns.json');p=load('data/frontier-protocols.json');a=load('data/meta-eval-attempts.json')
print('FRONTIER EVAL RESEARCH')
print(f'{c["directories_covered"]} study directories; {len(p["protocols"])} authored frontier designs; 31 final author attempts.')
print('Counts have different units and are not pooled. Human semantic review: incomplete.\n')
print(f'{"Attempt":76} {"Score /100":15} Failed checks')
for row in a['attempts']:
 s=row['scoring'];bounds=s.get('score_interval')
 if bounds:
  print(f'{row["id"]:76} {bounds[0]:6.2f}-{bounds[1]:6.2f}  {", ".join(s.get("critical_failures",[])) or "None established"}')
print('\nSee docs/META-EVAL-SCORES.md for every outcome, including unscored attempts.')
print('Stable semantic counterexamples: 5 H1 outputs + 3 H6 outputs; no pooled reliability rate.')
print('Original-task payroll: one failure / one pass in completed selected fresh pair; two interrupted slots remain unknown.')
