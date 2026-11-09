# Fresh source fixture inventory-reservations-fresh-01 436a0cfc0639
"""Finite bag query executor. Complete the documented language in this module."""
import copy

def scalar(expr,row):
 if not isinstance(expr,dict) or len(expr)!=1:raise ValueError('expression shape')
 op,arg=next(iter(expr.items()))
 if op=='col':return row[arg]
 if op=='lit':
  if arg is not None and type(arg) not in (str,int):raise ValueError('literal type')
  return arg
 if op in ('add','sub'):
  if not isinstance(arg,list) or len(arg)!=2:raise ValueError('arithmetic arity')
  a,b=(scalar(x,row) for x in arg)
  if any(v is not None and type(v)is not int for v in [a,b]):raise ValueError('integer arithmetic')
  if a is None or b is None:return None
  return a+b if op=='add' else a-b
 raise ValueError('unknown expression')

def truth(pred,row):
 if not isinstance(pred,dict) or len(pred)!=1:raise ValueError('predicate shape')
 op,arg=next(iter(pred.items()))
 if op=='is_null':return scalar(arg,row) is None
 if op=='not':
  v=truth(arg,row);return None if v is None else not v
 if op in ('and','or'):
  if not isinstance(arg,list) or len(arg)<2:raise ValueError('boolean arity')
  vs=[truth(p,row) for p in arg]
  if op=='and':return False if False in vs else (None if None in vs else True)
  return True if True in vs else (None if None in vs else False)
 if op not in ('eq','ne','lt','le','gt','ge') or not isinstance(arg,list) or len(arg)!=2:raise ValueError('comparison')
 a,b=[scalar(v,row) for v in arg]
 if a is None or b is None:return None
 if type(a)!=type(b) or type(a) not in (int,str):raise ValueError('comparison types')
 return {'eq':lambda:a==b,'ne':lambda:a!=b,'lt':lambda:a<b,'le':lambda:a<=b,'gt':lambda:a>b,'ge':lambda:a>=b}[op]()

def execute(tables,plan):
 def walk(p):
  if not isinstance(p,dict) or not isinstance(p.get('op'),str):raise ValueError('plan shape')
  op=p['op']
  if op=='scan':
   if set(p)!={'op','table','as'} or not isinstance(p['as'],str) or not p['as'] or '.' in p['as']:raise ValueError('scan shape')
   t=tables[p['table']];cols={p['as']+'.'+k:v for k,v in t['columns'].items()};return [{p['as']+'.'+k:v for k,v in r.items()} for r in t['rows']],cols,0
  if op in ('filter','project','group'):
   rs,cols,n=walk(p['input'])
   # Infer expressions/predicates even on empty input with schema-typed dummy values.
   dummy={k:(0 if v=='int' else ('' if v=='str' else None)) for k,v in cols.items()}
   if op=='filter':
    if set(p)!={'op','input','predicate'}:raise ValueError('filter shape')
    truth(p['predicate'],dummy);return [r for r in rs if truth(p['predicate'],r) is True],cols,n
   if op=='project':
    if set(p)!={'op','input','fields'} or not isinstance(p['fields'],dict):raise ValueError('project shape')
    inferred={k:scalar(e,dummy) for k,e in p['fields'].items()};return [{k:scalar(e,r) for k,e in p['fields'].items()} for r in rs],{k:('int' if type(v)is int else ('str' if type(v)is str else 'null')) for k,v in inferred.items()},n
   raise NotImplementedError('TODO implement GROUP semantics')
   if set(p)!={'op','input','keys','aggregates'} or not isinstance(p['keys'],list) or len(set(p['keys']))!=len(p['keys']) or any(k not in cols for k in p['keys']) or not isinstance(p['aggregates'],dict) or set(p['keys'])&set(p['aggregates']):raise ValueError('group shape')
   for a in p['aggregates'].values():
    if a.get('fn')=='count_all':
     if set(a)!={'fn'}:raise ValueError('count_all shape')
    elif a.get('fn') in ('sum','count'):
     if set(a)!={'fn','expr'}:raise ValueError('aggregate shape')
     v=scalar(a['expr'],dummy)
     if a['fn']=='sum' and v is not None and type(v)is not int:raise ValueError('sum integer')
    else:raise ValueError('aggregate function')
   groups={}
   for r in rs:groups.setdefault(tuple(r[k] for k in p['keys']),[]).append(r)
   if not rs and not p['keys']:groups[()]=[]
   out=[]
   for key,group in groups.items():
    row=dict(zip(p['keys'],key))
    for name,a in p['aggregates'].items():
     if a['fn']=='count_all':row[name]=len(group)
     else:
      vs=[scalar(a['expr'],r) for r in group];vs=[v for v in vs if v is not None]
      row[name]=len(vs) if a['fn']=='count' else (sum(vs) if vs else None)
    out.append(row)
   return out,{**{k:cols[k] for k in p['keys']},**{k:'int' for k in p['aggregates']}},n
  if op=='join':
   if set(p)!={'op','kind','left','right','left_on','right_on'} or p['kind'] not in ('inner','left'):raise ValueError('join shape')
   if p['kind']=='left':raise NotImplementedError('TODO implement LEFT JOIN')
   left,lc,ln=walk(p['left']);right,rc,rn=walk(p['right']);assert not set(lc)&set(rc),'overlapping qualified fields';assert p['left_on'] in lc and p['right_on'] in rc and (lc[p['left_on']]==rc[p['right_on']] or 'null' in (lc[p['left_on']],rc[p['right_on']])),'join keys';out=[];n=ln+rn
   for a in left:
    matched=False
    for b in right:
     n+=1;x=a[p['left_on']];y=b[p['right_on']]
     if x is not None and y is not None and x==y:out.append({**a,**b});matched=True
    if not matched and p['kind']=='left':out.append({**a,**{k:None for k in rc}})
   return out,{**lc,**rc},n
  raise ValueError('unknown plan operator')
 rows,_,comparisons=walk(plan);return rows,comparisons

def validate_request(request):
 if not isinstance(request,dict) or set(request)!={'tables','plan'} or not isinstance(request['tables'],dict):raise ValueError('request shape')
 for name,t in request['tables'].items():
  if not isinstance(name,str) or not name or set(t)!={'columns','rows'} or not isinstance(t['columns'],dict) or not isinstance(t['rows'],list):raise ValueError('table shape')
  if any(not isinstance(k,str) or not k or '.' in k or v not in ('int','str') for k,v in t['columns'].items()):raise ValueError('column schema')
  for r in t['rows']:
   if not isinstance(r,dict) or set(r)!=set(t['columns']):raise ValueError('row fields')
   for k,v in r.items():
    if v is not None and type(v)!=(int if t['columns'][k]=='int' else str):raise ValueError('row type')
 return request
