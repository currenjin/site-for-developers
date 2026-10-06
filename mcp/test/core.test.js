import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {parseCatalog} from '../src/parser.js';
import {catalog, searchSites} from '../src/catalog.js';
test('original Korean keywords survive practice synonyms with honest fields',()=>{
 const regex=searchSites({query:'학습',category:'regex',limit:20}).items.find(s=>s.name==='Regex101');
 assert.ok(regex); assert.ok(regex.matchedFields.includes('description'));
 const git=searchSites({query:'깃 실습',limit:20}).items.find(s=>s.name==='Learn Git Branching');
 assert.ok(git); assert.ok(git.matchedFields.includes('description'));
 for(const word of ['튜토리얼','게임']) {
  const site=catalog.sites.find(s=>s.description.includes(word)); assert.ok(site);
  assert.ok(searchSites({query:word,limit:1000}).items.some(s=>s.id===site.id));
 }
});
test('dollar label means paid or freemium and preserves raw labels',()=>{
 const parse=labels=>parseCatalog(`## 링크\n- <span id="a">A</span>\n  - [Site <sub>${labels}</sub>](https://site.test)`).sites[0];
 assert.equal(parse('$').cost,'paid-or-freemium'); assert.deepEqual(parse('$').rawLabels,['$']);
 assert.equal(parse('F, $').cost,'free-and-paid'); assert.deepEqual(parse('EN, F, $, O').rawLabels,['EN','F','$','O']);
});
for(const prefix of ['\t- ','  1. ','  1) ','  * ','  + ','  ']) test(`unsupported external syntax ${JSON.stringify(prefix)} fails instead of dropping a site`,()=>{
 assert.throws(()=>parseCatalog(`## 링크\n- <span id="a">A</span>\n  - [Valid](https://valid.test)\n${prefix}[Site](https://site.test)`),/Unsupported/);
});
for(const spans of ['<span id="alias"></span><span id="alias">B</span>','<span id="a"></span><span id="b">B</span>']) test(`duplicate alias anchors ${spans} fail closed`,()=>{
 assert.throws(()=>parseCatalog(`## 링크\n- <span id="a">A</span><span id="alias"></span>\n- ${spans}\n  - [Site](https://site.test)`),/Duplicate/);
});
const fixture = `![image](https://image.test)
## 링크
- <span id="group">Group</span>
  - <span id="a">A</span>
    - [Git <sub>KR, EN, F</sub>](https://git.test) - 깃 실습
    - [Cursor](#b) - 참고
  - <span id="b">B</span>
    - [Git](https://git.test/) - duplicate
    - [Cursor](https://cursor.test) - editor
## License
- [contributor](https://github.com/person)
`;
test('parser handles hierarchy, labels, canonical duplicates and named cross-reference without importing whole category',()=>{
 const c=parseCatalog(fixture); assert.equal(c.sites.length,2);
 const git=c.sites.find(s=>s.name==='Git'); assert.deepEqual(git.categories,['group','a','b']); assert.deepEqual(git.languages,['EN','KR']); assert.equal(git.cost,'free');
 const cursor=c.sites.find(s=>s.name==='Cursor'); assert.deepEqual(cursor.categories,['group','a','b']); assert.equal(cursor.cost,'unknown');
 assert.equal(parseCatalog(fixture).sites[0].id,c.sites[0].id);
});
test('parser fails closed on missing section, malformed site or unresolved reference',()=>{
 for(const text of ['',fixture.replace('https://cursor.test','javascript:bad'),fixture.replace('#b','#missing')]) assert.throws(()=>parseCatalog(text));
});
test('authoritative snapshot extraction and provenance',async()=>{
 const text=await readFile(new URL('../../README.md',import.meta.url),'utf8'); const c=parseCatalog(text);
 assert.deepEqual(c.stats,{entries:376,uniqueSites:370,categoryCount:57});
 assert.deepEqual(c.sites,catalog.sites); assert.ok(c.sites.length>250); assert.ok(c.categories.length>50);
 assert.ok(!c.sites.some(s=>/stargazers|contrib.rocks|shields.io/.test(s.url)));
 assert.ok(c.sites.find(s=>s.name==='IntelliJ IDEA').categories.includes('ide'));
 assert.ok(c.sites.find(s=>s.name==='Cursor').categories.includes('other-ide-tool'));
 assert.equal(catalog.source.verified,false); assert.match(catalog.source.version,/^sha256:/);
});
test('bilingual keyword matches explain fields, filter and bound results',()=>{
 for(const [q,name] of [['깃 실습','Learn Git Branching'],['레디스','Redis Docs'],['정규표현식','Regex101'],['regular expression','Regex101']]) {
 const r=searchSites({query:q,limit:20}); assert.ok(r.items.some(s=>s.name===name),q); assert.ok(r.items.every(s=>s.matchedFields.length&&!('score'in s)));
 }
 assert.equal(searchSites({query:'zzzznonexistent'}).items.length,0);
 assert.ok(searchSites({category:'study',language:'KR'}).items.every(s=>s.categories.includes('study')&&s.languages.includes('KR')));
 assert.ok(searchSites({}).items.length<=20);
});
