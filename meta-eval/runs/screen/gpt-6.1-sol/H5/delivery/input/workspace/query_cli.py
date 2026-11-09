# Fresh source fixture inventory-reservations-fresh-01 436a0cfc0639
"""Documented JSON query CLI;ordinary errors return exit2 and no result."""
import argparse,json,sys
from engine import validate_request,execute
from optimizer import optimize

def unique(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('duplicate JSON key:'+k)
  d[k]=v
 return d

def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['run']);p.add_argument('--request',required=True);p.add_argument('--optimize',action='store_true');args=p.parse_args()
 try:
  with open(args.request) as f:r=validate_request(json.load(f,object_pairs_hook=unique))
  plan=optimize(r['plan']) if args.optimize else r['plan'];rows,n=execute(r['tables'],plan);print(json.dumps({'rows':rows,'join_comparisons':n,'optimized_plan':plan},sort_keys=True))
 except Exception as e:print(type(e).__name__+':'+str(e),file=sys.stderr);raise SystemExit(2)
if __name__=='__main__':main()
