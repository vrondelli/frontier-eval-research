"""Independent finite relational semantics. Never imports delivered engine/optimizer."""
import collections,copy,itertools,json

def bag(rows):return collections.Counter(json.dumps(r,sort_keys=True,separators=(',',':')) for r in rows)
def atom(e,row):
 assert isinstance(e,dict) and len(e)==1
 name=next(iter(e));v=e[name]
 if name=='col':return row[v]
 if name=='lit':assert v is None or type(v) in [int,str];return v
 assert name in ['add','sub'] and isinstance(v,list) and len(v)==2
 x=atom(v[0],row);y=atom(v[1],row)
 assert all(v is None or type(v)is int for v in [x,y])
 if x is None or y is None:return None
 return x+y if name=='add' else x-y

def predicate(e,row):
 assert isinstance(e,dict) and len(e)==1
 name=next(iter(e));v=e[name]
 if name=='is_null':return atom(v,row) is None
 if name=='not':
  a=predicate(v,row);return None if a is None else not a
 if name in ['and','or']:
  assert isinstance(v,list) and len(v)>=2;a=[predicate(q,row) for q in v]
  # Explicit three-valued tables,not Python truth coercion.
  table_and={(True,True):True,(True,False):False,(True,None):None,(False,True):False,(False,False):False,(False,None):False,(None,True):None,(None,False):False,(None,None):None}
  table_or={(True,True):True,(True,False):True,(True,None):True,(False,True):True,(False,False):False,(False,None):None,(None,True):True,(None,False):None,(None,None):None}
  result=a[0]
  for x in a[1:]:result=(table_and if name=='and' else table_or)[result,x]
  return result
 assert name in ['eq','ne','lt','le','gt','ge'] and isinstance(v,list) and len(v)==2
 x=atom(v[0],row);y=atom(v[1],row)
 if x is None or y is None:return None
 assert type(x)==type(y) and type(x) in [int,str]
 return (x==y if name=='eq' else x!=y if name=='ne' else x<y if name=='lt' else x<=y if name=='le' else x>y if name=='gt' else x>=y)

def evaluate(tables,p):
 def rec(n):
  assert isinstance(n,dict);op=n['op']
  if op=='scan':
   assert set(n)=={'op','table','as'} and isinstance(n['as'],str) and n['as'] and '.' not in n['as'];t=tables[n['table']];schema={n['as']+'.'+k:v for k,v in t['columns'].items()};return [{n['as']+'.'+k:v for k,v in row.items()} for row in t['rows']],schema,0
  if op=='join':
   assert set(n)=={'op','kind','left','right','left_on','right_on'} and n['kind'] in ['inner','left'];left,ls,lcost=rec(n['left']);right,rs,rcost=rec(n['right']);assert not set(ls)&set(rs);lt=ls[n['left_on']];rt=rs[n['right_on']];assert lt==rt or 'null' in [lt,rt];out=[]
   for x in left:
    found=[{**x,**y} for y in right if x[n['left_on']] is not None and y[n['right_on']] is not None and x[n['left_on']]==y[n['right_on']]]
    out.extend(found if found else ([{**x,**dict.fromkeys(rs)}] if n['kind']=='left' else []))
   return out,{**ls,**rs},lcost+rcost+len(left)*len(right)
  data,schema,cost=rec(n['input']);typed={k:(0 if t=='int' else '' if t=='str' else None) for k,t in schema.items()}
  if op=='filter':
   assert set(n)=={'op','input','predicate'};predicate(n['predicate'],typed);return [r for r in data if predicate(n['predicate'],r) is True],schema,cost
  if op=='project':
   assert set(n)=={'op','input','fields'} and isinstance(n['fields'],dict);typed_output={k:atom(v,typed) for k,v in n['fields'].items()};new_schema={k:'int' if type(v)is int else 'str' if type(v)is str else 'null' for k,v in typed_output.items()};return [{k:atom(v,r) for k,v in n['fields'].items()} for r in data],new_schema,cost
  assert op=='group' and set(n)=={'op','input','keys','aggregates'} and isinstance(n['keys'],list) and len(set(n['keys']))==len(n['keys']) and all(k in schema for k in n['keys']) and not set(n['keys'])&set(n['aggregates'])
  for ag in n['aggregates'].values():
   assert ag.get('fn') in ['sum','count','count_all']
   if ag['fn']=='count_all':assert set(ag)=={'fn'}
   else:
    assert set(ag)=={'fn','expr'};v=atom(ag['expr'],typed)
    if ag['fn']=='sum':assert v is None or type(v)is int
  unique_keys=[]
  for row in data:
   key=tuple(row[k] for k in n['keys'])
   if key not in unique_keys:unique_keys.append(key)
  if not data and not n['keys']:unique_keys=[()]
  output=[]
  for key in unique_keys:
   members=[r for r in data if tuple(r[k] for k in n['keys'])==key];r=dict(zip(n['keys'],key))
   for label,ag in n['aggregates'].items():
    if ag['fn']=='count_all':value=len(members)
    else:
     xs=[atom(ag['expr'],m) for m in members];xs=[x for x in xs if x is not None];value=len(xs) if ag['fn']=='count' else sum(xs) if xs else None
    r[label]=value
   output.append(r)
  return output,{**{k:schema[k] for k in n['keys']},**{k:'int' for k in n['aggregates']}},cost
 result,_,cost=rec(p);return result,cost

def edge_requests():
 t={'a':{'columns':{'k':'int','v':'int'},'rows':[{'k':1,'v':5},{'k':1,'v':5},{'k':None,'v':None},{'k':2,'v':0}]},'b':{'columns':{'k':'int','v':'int'},'rows':[{'k':1,'v':3},{'k':1,'v':4},{'k':None,'v':9}]},'empty':{'columns':{'k':'int','v':'int'},'rows':[]}}
 scan=lambda name,alias:{'op':'scan','table':name,'as':alias};j={'op':'join','kind':'left','left':scan('a','a'),'right':scan('b','b'),'left_on':'a.k','right_on':'b.k'}
 cases=[('bag-null-left',j),('empty-right-left',{**j,'right':scan('empty','b')}),('empty-global',{'op':'group','input':scan('empty','e'),'keys':[],'aggregates':{'n':{'fn':'count_all'},'s':{'fn':'sum','expr':{'col':'e.v'}}}}),('empty-keyed',{'op':'group','input':scan('empty','e'),'keys':['e.k'],'aggregates':{'n':{'fn':'count_all'}}}),('null-group',{'op':'group','input':scan('a','a'),'keys':['a.k'],'aggregates':{'n':{'fn':'count_all'},'nonnull':{'fn':'count','expr':{'col':'a.v'}},'total':{'fn':'sum','expr':{'col':'a.v'}}}}),('three-valued-not',{'op':'filter','input':scan('a','a'),'predicate':{'not':{'eq':[{'col':'a.v'},{'lit':5}]}}}),('null-projection-arithmetic',{'op':'project','input':{'op':'project','input':scan('a','a'),'fields':{'x':{'lit':None}}},'fields':{'y':{'add':[{'col':'x'},{'lit':1}]}}})]
 result=[{'name':name,'benchmark':False,'request':{'tables':copy.deepcopy(t),'plan':plan}} for name,plan in cases]
 result.append({'name':'zero-column-bag','benchmark':False,'request':{'tables':{'z':{'columns':{},'rows':[{},{}]}},'plan':{'op':'scan','table':'z','as':'z'}}})
 return result

def qualify():
 cases=edge_requests();results={c['name']:evaluate(c['request']['tables'],c['request']['plan']) for c in cases}
 assert len(results['bag-null-left'][0])==6 and results['bag-null-left'][1]==12
 assert len(results['empty-right-left'][0])==4 and results['empty-right-left'][1]==0
 assert results['empty-global'][0]==[{'n':0,'s':None}] and results['empty-keyed'][0]==[]
 assert bag(results['null-group'][0])==bag([{'a.k':1,'n':2,'nonnull':2,'total':10},{'a.k':None,'n':1,'nonnull':0,'total':None},{'a.k':2,'n':1,'nonnull':1,'total':0}])
 assert results['three-valued-not'][0]==[{'a.k':2,'a.v':0}]
 assert results['null-projection-arithmetic'][0]==[{'y':None}]*4
 assert results['zero-column-bag'][0]==[{},{}]
 return {'pass':True,'hand_derived_cases':8,'results':results}