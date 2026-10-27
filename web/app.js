'use strict';
const $ = id => document.getElementById(id);
const element = (tag, className, text) => { const n=document.createElement(tag); if(className)n.className=className; if(text!==undefined)n.textContent=text; return n; };
const safeURL = value => { try { const u=new URL(value); return ['http:','https:'].includes(u.protocol)&&!u.username&&!u.password&&!/[\s\\]/u.test(value); } catch { return false; } };
let data, categories, selected='', query='';
const english=document.documentElement.lang==='en';
const t=(key,values={})=>(data.ui[key]||'').replace(/\{(\w+)\}/g,(_,name)=>String(values[name]??''));
const switchLink=$('language-switch');
const switchTarget=switchLink?new URL(switchLink.getAttribute('href'),location.href):null;
function updateLanguageSwitch(){
  if(!switchTarget)return;
  const target=new URL(switchTarget);target.search=location.search;target.hash=location.hash;
  switchLink.href=target.pathname+target.search+target.hash;
}
updateLanguageSwitch();
addEventListener('hashchange',updateLanguageSwitch);
addEventListener('popstate',updateLanguageSwitch);
const originalCategory=c=>english&&c.untranslated;
function categoryName(c,className=''){
  const name=element('span',className,c.name);if(originalCategory(c))name.lang='ko';return name;
}
function searchText(value){
  if(value==null)return '';
  if(typeof value==='object')return Object.values(value).map(searchText).join(' ');
  return String(value);
}
function resourceSearchText(r){
  return searchText([r.name,r.description,r.originalName,r.originalDescription,r.searchAliases,
    ...r.categoryPath.map(id=>{const c=categories.get(id);return [c.name,c.originalName,c.searchAliases,c.aliases];})]);
}
function readState(){
  const p=new URLSearchParams(location.search); query=p.get('q')||'';
  const raw=p.get('category')||'';
  selected=categories.has(raw)?raw:(data.categories.find(c=>(c.aliases||[]).includes(raw))?.id||'');
  $('search').value=query;
}
function updateURL(){
  const u=new URL(location.href);
  query?u.searchParams.set('q',query):u.searchParams.delete('q');
  selected?u.searchParams.set('category',selected):u.searchParams.delete('category');
  if(u.href!==location.href)history.pushState(null,'',u);
  updateLanguageSwitch();
}
function categoryLink(c){
  const row=element('div','cat-row'); const a=element('a');
  const u=new URL(location.href);c.id?u.searchParams.set('category',c.id):u.searchParams.delete('category');
  a.href=u.pathname+u.search+u.hash; a.dataset.category=c.id;
  a.append(categoryName(c,'cat-name'),element('span','cat-count',String(c.count)));
  if(originalCategory(c)){const badge=element('span','original-badge',t('korean_original'));a.append(badge);}
  a.addEventListener('click',e=>{if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;e.preventDefault();selected=c.id;updateURL();render();});
  row.append(a);return row;
}
function buildCategories(){
  const nav=$('categories');nav.append(categoryLink({id:'',name:t('all_resources'),count:data.resources.length}));
  function group(c){
    const wrapper=element('div','cat-group');const row=categoryLink(c);wrapper.append(row);
    const children=data.categories.filter(x=>x.parent===c.id);
    if(children.length){
      const inner=element('div','cat-children');inner.id='children-'+c.id;inner.hidden=true;
      const toggle=element('button','cat-toggle','⌄');toggle.type='button';toggle.setAttribute('aria-label',t('subcategory_aria',{name:c.name}));toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-controls',inner.id);
      toggle.addEventListener('click',()=>{inner.hidden=!inner.hidden;toggle.setAttribute('aria-expanded',String(!inner.hidden));});
      row.append(toggle);children.forEach(child=>inner.append(group(child)));wrapper.append(inner);
    }return wrapper;
  }
  data.categories.filter(c=>!c.parent).forEach(c=>nav.append(group(c)));
  $('category-total').textContent=String(data.categories.length);
}
function render(){
  const normalized=query.normalize('NFKC').toLocaleLowerCase().trim();const terms=normalized.split(/\s+/).filter(Boolean);
  const matches=data.resources.filter(r=>(!selected||r.categoryPath.includes(selected))&&terms.every(term=>resourceSearchText(r).normalize('NFKC').toLocaleLowerCase().includes(term)));
  $('category-heading').textContent=selected?categories.get(selected).name:t('all_resources');
  $('category-heading').lang=selected&&originalCategory(categories.get(selected))?'ko':document.documentElement.lang;
  $('result-count').textContent=t('result_count',{count:matches.length,total:data.resources.length});
  $('filter-summary').textContent=query?t('search_summary',{query}):t('readme_order');
  $('reset').hidden=!query&&!selected;
  const fragment=document.createDocumentFragment();
  for(const r of matches){
    if(!safeURL(r.url))continue;
    const card=element('article','resource');card.dataset.id=r.id;
    const link=element('a');link.href=r.url;link.target='_blank';link.rel='noopener noreferrer';
    const pending=english?(r.untranslatedFields||[]):[];
    const title=element('h3','',r.name);if(pending.includes('name'))title.lang='ko';
    const top=element('div','resource-top');top.append(title,element('span','outbound','↗'));top.lastChild.setAttribute('aria-hidden','true');link.append(top);
    if(r.description){const description=element('p','',r.description);if(pending.includes('description'))description.lang='ko';link.append(description);}
    const meta=element('div','resource-meta'),path=element('span','resource-path');
    r.categoryPath.forEach((id,index)=>{if(index)path.append(document.createTextNode(' / '));path.append(categoryName(categories.get(id)));});
    meta.append(path);
    if(pending.length)meta.append(element('span','original-badge',t('korean_original')));
    if(r.labels.length){const labels=element('span','labels');for(const label of r.labels)labels.append(element('span','label',label));meta.append(labels);}
    link.append(meta);card.append(link);fragment.append(card);
  }
  const results=$('results');
  // Keep the static DOM when it already matches; replace, never append, on filters.
  const preview=results.cloneNode(false);preview.append(fragment.cloneNode(true));
  if(!results.isEqualNode(preview))results.replaceChildren(fragment);
  $('empty').hidden=matches.length!==0;
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
    frame.src=frame.dataset.scene;
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
    const status=data.translationStatus||{};
    const pendingResources=status.pendingResources??data.resources.filter(r=>r.untranslatedFields?.length).length;
    const pendingCategories=status.pendingCategories??data.categories.filter(c=>c.untranslated).length;
    $('translation-note').hidden=!(english&&(pendingResources||pendingCategories||status.pendingStrings?.length));
    $('translation-note').textContent=t('pending_note',{resources:pendingResources,categories:pendingCategories});
    $('readme-link').href=data.source.readme;$('source-revision').textContent=t('source_revision_prefix')+data.source.commit.slice(0,7);
    $('search').addEventListener('input',()=>{query=$('search').value;updateURL();render();});
    $('search-form').addEventListener('submit',e=>{e.preventDefault();$('directory').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});});
    $('reset').addEventListener('click',()=>{query='';selected='';$('search').value='';updateURL();render();});
    addEventListener('popstate',()=>{readState();render();});
    addEventListener('keydown',e=>{if(e.key==='/'&&!/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)&&!e.metaKey&&!e.ctrlKey){e.preventDefault();$('search').focus();}});
  }catch(error){
    $('load-error').hidden=false;
    if($('results').children.length&&document.body.dataset.staticLoadError){
      $('load-error').firstChild.textContent=document.body.dataset.staticLoadError+' ';
    }else $('result-count').textContent=document.body.dataset.loadErrorStatus;
    console.error(error);
  }
}
init();
