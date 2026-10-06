import {test} from 'node:test';
import assert from 'node:assert/strict';
import {once} from 'node:events';
import {request} from 'node:http';
import {mkdtemp, rm,writeFile,readFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,dirname} from 'node:path';
import {execFileSync} from 'node:child_process';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StreamableHTTPClientTransport} from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import {StdioClientTransport} from '@modelcontextprotocol/sdk/client/stdio.js';
import {createHttpServer} from '../src/http.js';
const connect=async transport=>{const c=new Client({name:'test',version:'1'});await c.connect(transport);return c;};
test('bounded rate budget environment configuration',async()=>{
 const {readRateConfig}=await import('../src/http.js');
 assert.equal(typeof readRateConfig,'function');
 assert.deepEqual(readRateConfig({}),{maxRequests:120,windowMs:60000});
 assert.deepEqual(readRateConfig({MCP_MAX_REQUESTS:'100000',MCP_RATE_WINDOW_MS:'3600000'}),{maxRequests:100000,windowMs:3600000});
 for(const key of ['MCP_MAX_REQUESTS','MCP_RATE_WINDOW_MS']) for(const value of ['', '0','-1','1.5','Infinity','abc','10000000',' 2','1e2']) assert.throws(()=>readRateConfig({[key]:value}),/Invalid/);
});
test('invalid numeric rate budgets fail closed',()=>{
 for(const maxRequests of [0,-1,1.5,100001,NaN,Infinity,'2']) assert.throws(()=>createHttpServer({maxRequests}),/Invalid/);
 for(const windowMs of [0,-1,1.5,3600001,NaN,Infinity]) assert.throws(()=>createHttpServer({windowMs}),/Invalid/);
});
async function exercise(c){
 const {tools}=await c.listTools(); assert.deepEqual(tools.map(t=>t.name).sort(),['get_site','list_categories','search_sites']);
 assert.ok(tools.every(t=>t.annotations.readOnlyHint&&t.annotations.openWorldHint===false));
 assert.equal(tools.find(t=>t.name==='search_sites').inputSchema.properties.query.maxLength,200);
 const r=await c.callTool({name:'search_sites',arguments:{query:'깃 실습',limit:20}}); const data=JSON.parse(r.content[0].text);
 assert.ok(data.items.some(s=>s.name==='Learn Git Branching'));
 const item=await c.callTool({name:'get_site',arguments:{id:data.items[0].id}}); assert.equal(JSON.parse(item.content[0].text).site.id,data.items[0].id);
 assert.ok(JSON.parse((await c.callTool({name:'list_categories',arguments:{}})).content[0].text).categories.length>50);
 assert.ok((await c.callTool({name:'get_site',arguments:{id:'missing'}})).isError);
 assert.equal(JSON.parse((await c.callTool({name:'search_sites',arguments:{query:'zzzznonexistent'}})).content[0].text).items.length,0);
 for(const args of [{query:'x'.repeat(201)},{limit:21},{limit:0},{limit:1.5},{query:42},{language:'JP'},{extra:'bad'}]) assert.ok((await c.callTool({name:'search_sites',arguments:args})).isError,JSON.stringify(args));
}
test('real stateless HTTP SDK client and hostile HTTP requests',async t=>{
 const server=createHttpServer();server.listen(0,'127.0.0.1'); await once(server,'listening');t.after(()=>new Promise(r=>server.close(r)));
 const url=`http://127.0.0.1:${server.address().port}/mcp`;
 const c=await connect(new StreamableHTTPClientTransport(new URL(url)));t.after(()=>c.close());await exercise(c);
 for(const method of ['GET','DELETE','PUT','OPTIONS']){const r=await fetch(url,{method});assert.equal(r.status,405);assert.equal((await r.json()).jsonrpc,'2.0');assert.equal(r.headers.get('access-control-allow-origin'),null);}
 assert.equal((await fetch(url,{method:'POST',headers:{origin:'https://evil.test'}})).status,403);
 assert.equal(await new Promise((resolve,reject)=>{const req=request(url,{headers:{host:'evil.test'}},res=>{res.resume();resolve(res.statusCode);});req.on('error',reject);req.end();}),403);
 assert.equal((await fetch(url,{method:'POST',headers:{'content-type':'application/json'},body:'{broken'})).status,400);
 assert.equal((await fetch(url,{method:'POST',headers:{'content-type':'application/json'},body:' '.repeat(65537)})).status,413);
 const bad=await fetch(url,{method:'POST',headers:{'content-type':'application/json',accept:'application/json, text/event-stream'},body:JSON.stringify({oops:true})});assert.equal(bad.status,400);
 assert.equal((await fetch(url.replace('/mcp','/health'))).status,200);
});
test('rate limit and explicit public bind configuration',async t=>{
 assert.throws(()=>createHttpServer({bind:'0.0.0.0'}));
 const s=createHttpServer({maxRequests:2});s.listen(0,'127.0.0.1');await once(s,'listening');t.after(()=>new Promise(r=>s.close(r)));
 const url=`http://127.0.0.1:${s.address().port}/mcp`;assert.equal((await fetch(url)).status,405);assert.equal((await fetch(url)).status,405);assert.equal((await fetch(url,{headers:{'x-forwarded-for':'1.2.3.4'}})).status,429);
 for(let i=0;i<4;i++) assert.equal((await fetch(url.replace('/mcp','/health'))).status,200);
 for(const maxRequests of [0,-1,1.5,100001,NaN,Infinity,'2']) assert.throws(()=>createHttpServer({maxRequests}),/Invalid/);
 for(const windowMs of [0,-1,1.5,3600001,NaN,Infinity]) assert.throws(()=>createHttpServer({windowMs}),/Invalid/);
});
test('real installed tarball bin and self-contained runtime README outside repository; stale/invalid catalog check fails',async t=>{
 const dir=await mkdtemp(join(tmpdir(),'catalog-pack-'));t.after(()=>rm(dir,{recursive:true,force:true}));
 const archive=JSON.parse(execFileSync('npm',['pack','--json','--pack-destination',dir],{encoding:'utf8'}))[0].filename;
 execFileSync('tar',['-xzf',join(dir,archive),'-C',dir]);
 const documentation=await readFile(join(dir,'package/README.md'),'utf8');
 for(const text of ['Installed users','Repository developers','--stdio','--http','MCP_ALLOWED_HOSTS','MCP_ALLOWED_ORIGINS','MCP_MAX_REQUESTS','MCP_RATE_WINDOW_MS','snapshot','shared']) assert.ok(documentation.includes(text),text);
 execFileSync('npm',['install',join(dir,archive),'--ignore-scripts','--no-audit','--no-fund'],{cwd:dir,stdio:'pipe'});
 // The installed shebang must use this test runner's Node, including the Node 22 matrix.
 const c=await connect(new StdioClientTransport({command:join(dir,'node_modules/.bin/site-for-developers-mcp'),args:['--stdio'],cwd:dir,env:{PATH:dirname(process.execPath)+':'+process.env.PATH}}));t.after(()=>c.close());await exercise(c);
 execFileSync(process.execPath,['scripts/catalog.js','--check']);
 const fixture=join(dir,'invalid.md');await writeFile(fixture,'## 링크\n- <span id="a">A</span>\n  - [bad](javascript:bad)\n');
 assert.throws(()=>execFileSync(process.execPath,['scripts/catalog.js','--check','--readme',fixture],{stdio:'pipe'}));
 await writeFile(fixture,(await readFile('../README.md','utf8'))+'\nchanged snapshot\n');
 assert.throws(()=>execFileSync(process.execPath,['scripts/catalog.js','--check','--readme',fixture],{stdio:'pipe'}));
});
