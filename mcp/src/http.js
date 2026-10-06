import {createServer as httpServer} from 'node:http';
import {StreamableHTTPServerTransport} from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import {createServer} from './server.js';
const validateBudget=(value,max,name)=>{if(!Number.isInteger(value)||value<1||value>max) throw new Error(`Invalid ${name}: expected integer 1..${max}`);return value;};
export function readRateConfig(env=process.env){
 const read=(key,fallback,max)=>{
  if(env[key]===undefined) return fallback;
  if(!/^[0-9]+$/.test(env[key])) throw new Error(`Invalid ${key}`);
  return validateBudget(Number(env[key]),max,key);
 };
 return {maxRequests:read('MCP_MAX_REQUESTS',120,100000),windowMs:read('MCP_RATE_WINDOW_MS',60000,3600000)};
}
export function createHttpServer({bind='127.0.0.1',allowedHosts,allowedOrigins=[],maxRequests=120,windowMs=60000}={}){
 validateBudget(maxRequests,100000,'maxRequests');validateBudget(windowMs,3600000,'windowMs');
 if(!['127.0.0.1','localhost','::1'].includes(bind)&&(!allowedHosts?.length||!allowedOrigins.length)) throw new Error('Public bind requires explicit MCP_ALLOWED_HOSTS and MCP_ALLOWED_ORIGINS');
 const hosts=allowedHosts??['127.0.0.1','localhost','[::1]'];
 if(hosts.includes('*')||allowedOrigins.includes('*')) throw new Error('Wildcard allowlists are forbidden');
 const buckets=new Map();
 const send=(res,status,code,message)=>{res.writeHead(status,{'content-type':'application/json','cache-control':'no-store'});res.end(JSON.stringify({jsonrpc:'2.0',error:{code,message},id:null}));};
 const server=httpServer(async(req,res)=>{
  // Only raw Host / Origin are trusted, never client-provided Forwarded headers.
  const host=(req.headers.host??'').toLowerCase().replace(/:\d+$/,'');
  if(!hosts.includes(host)||req.headers.origin&&!allowedOrigins.includes(req.headers.origin)) return send(res,403,-32000,'Host or Origin denied');
  // Health bypasses query admission, not Host/Origin validation.
  if(req.url==='/health'&&req.method==='GET'){res.writeHead(200,{'content-type':'application/json'});return res.end(JSON.stringify({status:'ok',mode:'stateless',verification:false}));}
  if(req.url!=='/mcp') return send(res,404,-32000,'Not found');
  const now=Date.now();for(const [key,b] of buckets) if(b.until<=now) buckets.delete(key);
  const ip=req.socket.remoteAddress;let bucket=buckets.get(ip);
  if(!bucket){if(buckets.size>=10000) return send(res,429,-32000,'Rate limit capacity');bucket={until:now+windowMs,count:0};buckets.set(ip,bucket);}
  if(++bucket.count>maxRequests){res.setHeader('retry-after',String(Math.ceil((bucket.until-now)/1000)));return send(res,429,-32000,'Rate limit exceeded');}
  if(req.method!=='POST'){res.setHeader('allow','POST');return send(res,405,-32000,'Method not allowed: stateless server has no GET stream or DELETE session');}
  if(!/^application\/json(?:\s*;|$)/i.test(req.headers['content-type']??'')) return send(res,415,-32000,'Expected application/json');
  let bytes=0,chunks=[],body;
  try {
   for await(const chunk of req){bytes+=chunk.length;if(bytes>65536){send(res,413,-32000,'Body exceeds 64 KiB');req.resume();return;}chunks.push(chunk);}
   try{body=JSON.parse(Buffer.concat(chunks).toString('utf8'));}catch{return send(res,400,-32700,'Parse error');}
   const mcp=createServer(),transport=new StreamableHTTPServerTransport({sessionIdGenerator:undefined,enableJsonResponse:true});
   res.once('close',()=>{void transport.close();void mcp.close();});
   await mcp.connect(transport);await transport.handleRequest(req,res,body);
  }catch{if(!res.headersSent) send(res,500,-32603,'Internal server error');}
 });
 server.requestTimeout=10000;server.headersTimeout=10000;server.keepAliveTimeout=5000;
 return server;
}
