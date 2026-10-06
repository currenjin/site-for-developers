import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {parseCatalog} from '../src/parser.js';
const args=process.argv.slice(2), at=args.indexOf('--readme');
const text=await readFile(at<0?new URL('../../README.md',import.meta.url):args[at+1],'utf8');
const parsed=parseCatalog(text);
const result={source:{url:'https://github.com/currenjin/site-for-developers/blob/main/README.md',version:'sha256:'+createHash('sha256').update(text).digest('hex'),verified:false,note:'README snapshot provenance only; not live URL, language, price or license verification.'},...parsed};
const serialized=JSON.stringify(result,null,2)+'\n', path=new URL('../catalog.json',import.meta.url);
if(args.includes('--check')){if(await readFile(path,'utf8')!==serialized) throw new Error('Catalog stale: run npm run catalog:generate');}
else await writeFile(path,serialized);
console.log(JSON.stringify(result.stats));
