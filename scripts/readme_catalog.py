"""Deterministic, dependency-free parser for SFD's README list dialect.
Fails on unsupported resource rows instead of silently dropping external links.
"""
import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any

ROOT=Path(__file__).resolve().parents[1]

def plain(text):
    # Only known formatting tags: angle-bracket book titles are source prose.
    text=re.sub(r'</?(?:sub|b|strong|em|i|code|span)(?:\s[^>]*)?>','',text,flags=re.I)
    return html.unescape(text.replace('**','').replace('`','')).strip()

def safe_url(value):
    if any(ord(c)<33 for c in value) or '\\' in value: return False
    try:
        u=urlsplit(value)
        return u.scheme in ('http','https') and bool(u.hostname) and u.username is None and u.password is None
    except ValueError: return False

def link_at_start(text):
    if not text.startswith('['): return None
    depth=0; end=None
    for i,c in enumerate(text):
        if i and text[i-1]=='\\': continue
        if c=='[': depth+=1
        elif c==']':
            depth-=1
            if depth==0: end=i; break
    if end is None or text[end+1:end+2]!='(': return None
    depth=1
    for j in range(end+2,len(text)):
        c=text[j]
        if text[j-1]=='\\': continue
        if c=='(': depth+=1
        elif c==')':
            depth-=1
            if depth==0: return text[1:end],text[end+2:j],text[j+1:].strip()
    return None

def parse_readme(text: str) -> dict[str, Any]:
    resources=[]; categories=[]; stack=[]; seen=Counter(); refs=[]; active=False
    for number,line in enumerate(text.splitlines(),1):
        if line.startswith('## '):
            if line.strip()=='## 링크': active=True; continue
            if active: break
        if not active: continue
        m=re.match(r'^(\s*)-\s+(.*)$',line)
        if not m: continue
        indent=len(m[1].expandtabs(4)); body=m[2]
        spans=re.findall(r'<span\s+id=[\"\']([^\"\']+)[\"\']\s*>(.*?)</span>',body)
        if spans:
            while stack and stack[-1][0]>=indent: stack.pop()
            nonempty=[(i,plain(t)) for i,t in spans if plain(t)]
            if len(nonempty)!=1: raise ValueError(f'Ambiguous category line {number}')
            cid,title=nonempty[0]
            if any(c['id']==cid for c in categories): raise ValueError(f'Duplicate category {cid}')
            path=[item[1] for item in stack]+[cid]
            categories.append({'id':cid,'name':title,'parent':stack[-1][1] if stack else None,'path':path,'aliases':[i for i,t in spans if i!=cid]})
            stack.append((indent,cid)); continue
        link=link_at_start(body)
        if not link:
            if re.search(r'\]\(https?://',body): raise ValueError(f'Unsupported external resource line {number}')
            continue
        label,url,tail=link
        if url.startswith('#'):
            refs.append({'name':plain(label),'target':url[1:],'categoryPath':[i[1] for i in stack]}); continue
        if not safe_url(url): raise ValueError(f'Unsafe resource URL on line {number}: {url}')
        while stack and stack[-1][0]>=indent: stack.pop()
        if not stack: raise ValueError(f'Uncategorized resource line {number}')
        subs=re.findall(r'<sub>(.*?)</sub>',label,flags=re.I)
        name=plain(re.sub(r'<sub>.*?</sub>','',label,flags=re.I))
        description=plain(re.sub(r'^-\s*','',tail))
        path=[i[1] for i in stack]
        identity=json.dumps([path,name,url],ensure_ascii=False)
        seen[identity]+=1
        rid=hashlib.sha256(identity.encode()).hexdigest()[:16]+'-'+str(seen[identity])
        resources.append({'id':rid,'name':name,'url':url,'description':description,'labels':[plain(v).strip() for s in subs for v in s.split(',') if plain(v).strip()],'labelSource':subs,'categoryPath':path,'sourceLine':number})
    for c in categories: c['count']=sum(c['id'] in r['categoryPath'] for r in resources)
    return {'resources':resources,'categories':categories,'categoryReferences':refs}
