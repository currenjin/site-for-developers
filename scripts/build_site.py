"""Build the public SFD site from the repository's canonical README.

No runtime network calls, package dependencies or second editable catalogue.
Only the explicit file allowlist is emitted into the Pages artifact.
"""
import argparse
import copy
import xml.etree.ElementTree as ET
import json
import os
import shutil
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape
from readme_catalog import parse_readme

ROOT=Path(__file__).resolve().parents[1]
SITE_URL='https://currenjin.github.io/site-for-developers/'
ASSETS=['index.html','styles.css','app.js','art/scene.html','art/poster.png','art/three.min.js','art/THREE-LICENSE.txt']
GENERATED=['resources.json','logo.svg','favicon.svg','LICENSE','.nojekyll','404.html','sitemap.xml']

def build(output, revision=None):
    output=Path(output).resolve()
    protected=[ROOT,ROOT/'web',ROOT/'scripts',ROOT/'tests',ROOT/'.git']
    if any(output==p or (p!=ROOT and output.is_relative_to(p)) for p in protected):
        raise ValueError('Refusing to build over source files')
    expected=set(ASSETS+GENERATED)
    if output.exists():
        if output.is_symlink():raise ValueError('Output must not be a symlink')
        unknown=[str(p.relative_to(output)) for p in output.rglob('*') if p.is_symlink() or (p.is_file() and str(p.relative_to(output)) not in expected)]
        if unknown:raise ValueError('Refusing to overwrite a directory with unknown files: '+', '.join(unknown))
    revision=revision or os.environ.get('GITHUB_SHA') or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    data=parse_readme((ROOT/'README.md').read_text(encoding='utf-8'))
    if not data['resources'] or not data['categories']:raise ValueError('README catalogue unexpectedly empty')
    data['source']={'repository':'https://github.com/currenjin/site-for-developers','commit':revision,'readme':'https://github.com/currenjin/site-for-developers/blob/'+revision+'/README.md'}
    for name in ASSETS:
        source=ROOT/'web'/name
        if not source.is_file() or source.is_symlink():raise ValueError('Missing or unsafe website asset: '+name)
    output.mkdir(parents=True,exist_ok=True)
    for name in ASSETS:
        dest=output/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'web'/name,dest)
    shutil.copyfile(ROOT/'resources/icons/header_base/576x157/header_base.svg',output/'logo.svg')
    # Reuse the original gem path and gradients, never the wordmark, at tab-icon scale.
    ns='{http://www.w3.org/2000/svg}'
    original=ET.parse(ROOT/'resources/icons/header_base/576x157/header_base.svg').getroot()
    paths=original.findall(ns+'path')
    if len(paths)!=2:raise ValueError('Logo structure changed; verify the favicon gem selection')
    ET.register_namespace('',ns[1:-1])
    icon=ET.Element(ns+'svg',{'width':'64','height':'64','viewBox':'22 12 128 128','fill':'none'})
    icon.append(copy.deepcopy(paths[1]))
    defs=original.find(ns+'defs')
    if defs is not None:icon.append(copy.deepcopy(defs))
    (output/'favicon.svg').write_text(ET.tostring(icon,encoding='unicode')+'\n',encoding='utf-8')
    shutil.copyfile(ROOT/'LICENSE',output/'LICENSE')
    (output/'resources.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (output/'.nojekyll').write_text('',encoding='utf-8')
    (output/'404.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>페이지를 찾을 수 없습니다 · SFD</title><style>body{margin:12vh auto;padding:24px;max-width:600px;font:16px/1.7 system-ui;color:#242332}a{color:#4f39f6}</style><h1>페이지를 찾을 수 없습니다.</h1><p>주소를 확인하거나 리소스 목록으로 돌아가세요.</p><a href="'+SITE_URL+'">Site for Developers로 돌아가기 ↗</a></html>',encoding='utf-8')
    (output/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+escape(SITE_URL)+'</loc></url></urlset>\n',encoding='utf-8')
    return {'resources':len(data['resources']),'categories':len(data['categories']),'revision':revision,'output':str(output)}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'_site');parser.add_argument('--revision');args=parser.parse_args()
    print(json.dumps(build(args.output,args.revision),ensure_ascii=False))
