'use strict';
const $ = id => document.getElementById(id);
const element = (tag, className, text) => { const n=document.createElement(tag); if(className)n.className=className; if(text!==undefined)n.textContent=text; return n; };
const safeURL = value => { try { const u=new URL(value); return ['http:','https:'].includes(u.protocol)&&!u.username&&!u.password&&!/[\s\\]/u.test(value); } catch { return false; } };
let data, categories, selected='', query='';
function readState(){
  const p=new URLSearchParams(location.search); query=p.get('q')||'';
  const raw=p.get('category')||'';
  selected=categories.has(raw)?raw:(data.categories.find(c=>c.aliases.includes(raw))?.id||'');
  $('search').value=query;
}
function updateURL(){
  const u=new URL(location.href);
  query?u.searchParams.set('q',query):u.searchParams.delete('q');
  selected?u.searchParams.set('category',selected):u.searchParams.delete('category');
  if(u.href!==location.href)history.pushState(null,'',u);
}
function categoryLink(c){
  const row=element('div','cat-row'); const a=element('a');
  const u=new URL(location.href);c.id?u.searchParams.set('category',c.id):u.searchParams.delete('category');
  a.href=u.pathname+u.search+u.hash; a.dataset.category=c.id;
  a.append(element('span','',c.name),element('span','cat-count',String(c.count)));
  a.addEventListener('click',e=>{if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;e.preventDefault();selected=c.id;updateURL();render();});
  row.append(a);return row;
}
function buildCategories(){
  const nav=$('categories');nav.append(categoryLink({id:'',name:'전체 리소스',count:data.resources.length}));
  function group(c){
    const wrapper=element('div','cat-group');const row=categoryLink(c);wrapper.append(row);
    const children=data.categories.filter(x=>x.parent===c.id);
    if(children.length){
      const inner=element('div','cat-children');inner.id='children-'+c.id;inner.hidden=true;
      const toggle=element('button','cat-toggle','⌄');toggle.type='button';toggle.setAttribute('aria-label',c.name+' 하위 카테고리');toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-controls',inner.id);
      toggle.addEventListener('click',()=>{inner.hidden=!inner.hidden;toggle.setAttribute('aria-expanded',String(!inner.hidden));});
      row.append(toggle);children.forEach(child=>inner.append(group(child)));wrapper.append(inner);
    }return wrapper;
  }
  data.categories.filter(c=>!c.parent).forEach(c=>nav.append(group(c)));
  $('category-total').textContent=String(data.categories.length);
}
function render(){
  const normalized=query.normalize('NFKC').toLocaleLowerCase().trim();const terms=normalized.split(/\s+/).filter(Boolean);
  const matches=data.resources.filter(r=>(!selected||r.categoryPath.includes(selected))&&terms.every(term=>[r.name,r.description,...r.categoryPath.map(id=>categories.get(id).name)].join(' ').normalize('NFKC').toLocaleLowerCase().includes(term)));
  $('category-heading').textContent=selected?categories.get(selected).name:'전체 리소스';
  $('result-count').textContent=matches.length+'개 / 전체 '+data.resources.length+'개';
  $('filter-summary').textContent=query?'“'+query+'” 검색 결과':'README 수록 순서';
  $('reset').hidden=!query&&!selected;
  const fragment=document.createDocumentFragment();
  for(const r of matches){
    if(!safeURL(r.url))continue;
    const card=element('article','resource');card.dataset.id=r.id;
    const link=element('a');link.href=r.url;link.target='_blank';link.rel='noopener noreferrer';
    const top=element('div','resource-top');top.append(element('h3','',r.name),element('span','outbound','↗'));top.lastChild.setAttribute('aria-hidden','true');link.append(top);
    if(r.description)link.append(element('p','',r.description));
    const meta=element('div','resource-meta');meta.append(element('span','resource-path',r.categoryPath.map(id=>categories.get(id).name).join(' / ')));
    if(r.labels.length){const labels=element('span','labels');for(const label of r.labels)labels.append(element('span','label',label));meta.append(labels);}
    link.append(meta);card.append(link);fragment.append(card);
  }
  $('results').replaceChildren(fragment);$('empty').hidden=matches.length!==0;
  document.querySelectorAll('[data-category]').forEach(a=>{
    a.setAttribute('aria-current',String(a.dataset.category===selected));
    const u=new URL(a.href);query?u.searchParams.set('q',query):u.searchParams.delete('q');a.href=u.pathname+u.search+u.hash;
  });
  if(selected)for(const id of categories.get(selected).path){const inner=$('children-'+id);if(inner){inner.hidden=false;document.querySelector('[aria-controls="'+inner.id+'"]').setAttribute('aria-expanded','true');}}
}
async function initArt(){
  const frame=$('gem-frame'), poster=$('gem-poster'), slot=document.querySelector('.gem-slot');
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  let motionObserver;
  try{
    await poster.decode();poster.hidden=false;$('art-placeholder').hidden=true;
    if(reduced.matches)return;
    frame.src='art/scene.html';
    for(let attempt=0;attempt<100;attempt++){
      await new Promise(resolve=>setTimeout(resolve,50));
      const child=frame.contentWindow;
      if(child?.__GEM_ERROR__)return;
      if(child?.__GEM_READY__){
        frame.hidden=false;$('art-placeholder').hidden=true;
        motionObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{
          child.setMotionEnabled(entry.isIntersecting&&!document.hidden&&!reduced.matches);
        }),{threshold:.05});motionObserver.observe(slot);
        document.addEventListener('visibilitychange',()=>child.setMotionEnabled(!document.hidden&&!reduced.matches&&slot.getBoundingClientRect().bottom>0&&slot.getBoundingClientRect().top<innerHeight));
        reduced.addEventListener('change',()=>{
          frame.hidden=reduced.matches;child.setMotionEnabled(!reduced.matches&&!document.hidden);
        });
        return;
      }
    }
  }catch{/* Keep the original rendered poster if WebGL or the local scene is unavailable. */}
}
async function init(){
  initArt();
  try{
    const response=await fetch('resources.json');if(!response.ok)throw new Error('Catalogue unavailable');data=await response.json();categories=new Map(data.categories.map(c=>[c.id,c]));
    readState();buildCategories();render();
    $('readme-link').href=data.source.readme;$('source-revision').textContent='원본 '+data.source.commit.slice(0,7);
    $('search').addEventListener('input',()=>{query=$('search').value;updateURL();render();});
    $('search-form').addEventListener('submit',e=>{e.preventDefault();$('directory').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});});
    $('reset').addEventListener('click',()=>{query='';selected='';$('search').value='';updateURL();render();});
    addEventListener('popstate',()=>{readState();render();});
    addEventListener('keydown',e=>{if(e.key==='/'&&!/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)&&!e.metaKey&&!e.ctrlKey){e.preventDefault();$('search').focus();}});
  }catch(error){$('load-error').hidden=false;$('result-count').textContent='목록을 불러오지 못했습니다.';console.error(error);}
}
init();
