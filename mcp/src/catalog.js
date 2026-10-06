import {readFileSync} from 'node:fs';
export const catalog=JSON.parse(readFileSync(new URL('../catalog.json',import.meta.url),'utf8'));
const normalize=s=>s.toLowerCase().replace(/정규\s*표현식|정규식|regular\s+expression/g,'regex').replace(/레디스/g,'redis').replace(/깃/g,'git').replace(/연습|exercise|practice/g,'실습');
export function searchSites({query='',category,language,limit=10}={}) {
 const terms=normalize(query).trim().split(/\s+/).filter(Boolean),items=[];
 for(const site of catalog.sites){
  if(category&&!site.categories.includes(category)||language&&!site.languages.includes(language)) continue;
  // Add aliases to their originating field; never overwrite searchable source words.
  const description=normalize(site.description);
  const fields={name:normalize(site.name),description:description+(/학습|튜토리얼|게임/.test(description)?' 실습':''),url:normalize(site.url),categories:normalize(site.categories.map(id=>id+' '+catalog.categories.find(c=>c.id===id).name).join(' '))};
  if(!terms.every(term=>Object.values(fields).some(value=>value.includes(term)))) continue;
  const matchedFields=terms.length?Object.entries(fields).filter(([,v])=>terms.some(t=>v.includes(t))).map(([k])=>k):['filters'];
  items.push({...site,matchedFields});
 }
 return {items:items.slice(0,limit),total:items.length,source:catalog.source,matchPolicy:'Case-insensitive AND keyword matching with documented bilingual aliases; stable ID order, no relevance score.'};
}
