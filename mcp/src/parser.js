import {createHash} from 'node:crypto';
const clean = text => text.replace(/<[^>]*>/g,'').trim();
export function parseCatalog(markdown) {
 const section=markdown.match(/^## 링크\s*\n([\s\S]*?)(?=^## |$(?![\s\S]))/m);
 if(!section) throw new Error('Missing authoritative 링크 section');
 const categories=[], stack=[], byUrl=new Map(), refs=[], anchors=new Map(), seenSpanIds=new Set(); let entries=0;
 for(const [index,line] of section[1].split('\n').entries()) {
  for(const span of line.matchAll(/<span\b[^>]*\bid=["']([^"']*)["'][^>]*>/g)) {
   if(seenSpanIds.has(span[1])) throw new Error(`Duplicate span ID ${span[1]} at ${index}`);
   seenSpanIds.add(span[1]);
  }
  const bullet=line.match(/^( *)- (.*)$/);
  if(!bullet) {
   if(/^\s*(?:[-*+]\s|\d+[.)]\s)/.test(line)||/https?:\/\/|<span\b|\]\(/.test(line)) throw new Error(`Unsupported list/site syntax at ${index}`);
   continue;
  }
  const depth=bullet[1].length, body=bullet[2];
  while(stack.length && stack.at(-1).depth>=depth) stack.pop();
  const spans=[...body.matchAll(/<span id="([a-z0-9-]+)">([^<]*)<\/span>/g)];
  if(spans.length){
   if(/https?:\/\//.test(body)) throw new Error(`Unsupported category/site syntax at ${index}`);
   const primary=spans.find(s=>s[2].trim()); if(!primary) throw new Error(`Empty category at ${index}`);
   if(anchors.has(primary[1])) throw new Error('Duplicate category');
   const category={id:primary[1],name:clean(primary[2]),parent:stack.at(-1)?.id??null};categories.push(category);
   for(const s of spans) anchors.set(s[1],primary[1]);stack.push({id:primary[1],depth});continue;
  }
  if(/<span\b/.test(body)) throw new Error(`Unsupported span syntax at ${index}`);
  const links=[...body.matchAll(/(?<!!)\[([^\]]+)\]\(([^\s)]+)\)/g)];
  for(const l of links.filter(l=>l[2].startsWith('#'))) refs.push({target:l[2].slice(1),name:body.startsWith('[')?clean(l[1]):null,categories:stack.map(s=>s.id)});
  if(!body.startsWith('[')) {
   if(/https?:\/\//.test(body)) throw new Error(`Unsupported site syntax at ${index}`);
   continue;
  }
  const link=links[0]; if(!link) throw new Error(`Malformed link at ${index}`);
  if(link[2].startsWith('#')) continue;
  if(!stack.length) throw new Error('Site outside category');
  let url;try {url=new URL(link[2]);}catch {throw new Error('Invalid site URL');}
  if(!['https:','http:'].includes(url.protocol)||url.username||url.password) throw new Error('Unsafe site URL');
  const canonical=url.href;
  const labels=[...link[1].matchAll(/<sub>(.*?)<\/sub>/g)].flatMap(m=>m[1].split(',').map(s=>s.trim()));
  if(labels.some(l=>!['EN','KR','F','$','O'].includes(l))) throw new Error('Unknown metadata');
  const name=clean(link[1].replace(/<sub>.*?<\/sub>/g,'')); if(!name) throw new Error('Empty site name');
  const description=body.slice(link.index+link[0].length).replace(/^\s*-\s*/,'').trim();
  entries++;
  let site=byUrl.get(canonical);
  if(!site){site={id:'site_'+createHash('sha256').update(canonical).digest('hex').slice(0,24),name,url:canonical,description,categories:[],languages:[],rawLabels:[],cost:'unknown',openSource:false};byUrl.set(canonical,site);}
  site.categories=[...new Set([...site.categories,...stack.map(s=>s.id)])];
  site.languages=[...new Set([...site.languages,...labels.filter(l=>['EN','KR'].includes(l))])].sort();
  site.rawLabels=[...new Set([...site.rawLabels,...labels])];
  const free=site.rawLabels.includes('F'),paid=site.rawLabels.includes('$');
  site.cost=free?(paid?'free-and-paid':'free'):(paid?'paid-or-freemium':'unknown');site.openSource ||= labels.includes('O');
 }
 for(const ref of refs){
  const target=anchors.get(ref.target); if(!target) throw new Error(`Unresolved category #${ref.target}`);
  // A named site reference merges only that site, not every site under its target.
  if(ref.name){const matches=[...byUrl.values()].filter(s=>s.name.toLowerCase()===ref.name.toLowerCase()&&s.categories.includes(target));if(matches.length!==1) throw new Error(`Unresolved named reference ${ref.name}`);matches[0].categories=[...new Set([...matches[0].categories,...ref.categories])];}
 }
 if(!byUrl.size) throw new Error('Empty extraction');
 for(const s of byUrl.values()) s.categories.sort((a,b)=>categories.findIndex(c=>c.id===a)-categories.findIndex(c=>c.id===b));
 return {categories,sites:[...byUrl.values()].sort((a,b)=>a.id.localeCompare(b.id)),stats:{entries,uniqueSites:byUrl.size,categoryCount:categories.length}};
}
