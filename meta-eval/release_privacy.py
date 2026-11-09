"""Targeted transcript redaction for release copies; originals are never edited."""
import hashlib
import json
import re

MEMORY=re.compile(r'memories|MEMORY\.md|memory_search|read_memory',re.I)
CITATION=re.compile(r'<oai-mem-citation>.*?</oai-mem-citation>',re.S)

def sanitize(path, data):
    if path.endswith(('.txt','.md')):
        try:plain=data.decode('utf-8')
        except UnicodeDecodeError:plain=''
        if CITATION.search(plain):
            clean=CITATION.sub('[Memory citation omitted from public copy]',plain)
            return clean.encode('utf-8'),[{'reason':'memory_citation_removed_from_text'}]
    if path.endswith('.json'):
        try:value=json.loads(data.decode('utf-8'))
        except (ValueError,UnicodeDecodeError):return data,[]
        records=[]
        def walk(node,location=''):
            if isinstance(node,dict):
                command=node.get('command','')
                if isinstance(command,str)and MEMORY.search(command):
                    removed={k:node[k]for k in ['command','aggregated_output','output_excerpt','arguments','result']if k in node}
                    records.append({'json_pointer':location,'reason':'copied_memory_command_and_result',
                                    'removed_fields_sha256':hashlib.sha256(json.dumps(removed,sort_keys=True).encode()).hexdigest()})
                    for k in removed:node[k]='[REDACTED external memory command/content; original retained locally]'
                for key,item in node.items():walk(item,location+'/'+str(key))
            elif isinstance(node,list):
                for index,item in enumerate(node):walk(item,location+'/'+str(index))
        walk(value)
        return ((json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode(),records)if records else(data,[])
    if not (path.endswith(('.jsonl','.log')) or path.endswith('/log.txt') or path.endswith('/transcript.txt')):
        return data,[]
    try:text=data.decode('utf-8')
    except UnicodeDecodeError:return data,[]
    records=[];out=[]
    for index,line in enumerate(text.splitlines(keepends=True),1):
        try:event=json.loads(line)
        except ValueError:
            if MEMORY.search(line):
                records.append({'line':index,'reason':'unstructured_memory_reference','original_line_sha256':hashlib.sha256(line.encode()).hexdigest()})
                out.append('[REDACTED unrelated memory reference; original retained locally]\n')
            else:out.append(line)
            continue
        item=event.get('item',{})if isinstance(event,dict)else{}
        command=item.get('command','')
        is_memory=bool(MEMORY.search(command))or ('memory'in str(item.get('server','')).lower() and item.get('type')=='mcp_tool_call')
        changed=False
        if is_memory:
            removed={k:item[k]for k in ['command','aggregated_output','arguments','result','error']if k in item}
            records.append({'line':index,'event_id':item.get('id'),'reason':'memory_search_command_and_result',
                            'removed_fields_sha256':hashlib.sha256(json.dumps(removed,sort_keys=True).encode()).hexdigest()})
            if 'command'in item:item['command']='[REDACTED external memory search command]'
            for key in ['aggregated_output','arguments','result','error']:
                if key in item:item[key]='[REDACTED unrelated private memory content; original retained locally]'
            changed=True
        for key in ['text']:
            if isinstance(item.get(key),str)and CITATION.search(item[key]):
                item[key]=CITATION.sub('[Memory citation omitted from public copy]',item[key]);changed=True
                records.append({'line':index,'event_id':item.get('id'),'reason':'memory_citation_removed'})
        out.append(json.dumps(event,ensure_ascii=False)+'\n'if changed else line)
    clean=''.join(out).encode('utf-8')
    return clean,records
