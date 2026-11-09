
import argparse, json, sys
from oracle import loads, evaluate
from optimizer import optimize
p=argparse.ArgumentParser()
p.add_argument('command', choices=['run'])
p.add_argument('--request', required=True)
p.add_argument('--optimize', action='store_true')
args=p.parse_args()
try:
    with open(args.request, encoding='utf-8') as f: r=loads(f.read())
    evaluate(r)  # The original request must be valid before rewriting.
    plan=optimize(r['plan']) if args.optimize else r['plan']
    rows,n=evaluate({'tables': r['tables'], 'plan': plan})
    print(json.dumps({'rows': rows, 'join_comparisons': False, 'optimized_plan': plan}))
except Exception as exc:
    print(str(exc),file=sys.stderr)
    sys.exit(2)
