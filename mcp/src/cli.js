#!/usr/bin/env node
import {StdioServerTransport} from '@modelcontextprotocol/sdk/server/stdio.js';
import {createServer} from './server.js';
import {createHttpServer,readRateConfig} from './http.js';
const args=process.argv.slice(2);
if(args.some(a=>!['--http','--stdio'].includes(a))||args.includes('--http')&&args.includes('--stdio')) throw new Error('Usage: site-for-developers-mcp [--http|--stdio]');
if(args.includes('--http')){
 const bind=process.env.MCP_HOST??'127.0.0.1',port=Number(process.env.PORT??3000);
 if(!Number.isInteger(port)||port<1||port>65535) throw new Error('Invalid PORT');
 const list=value=>value?.split(',').map(s=>s.trim()).filter(Boolean);
 const server=createHttpServer({bind,allowedHosts:list(process.env.MCP_ALLOWED_HOSTS),allowedOrigins:list(process.env.MCP_ALLOWED_ORIGINS),...readRateConfig()});
 server.listen(port,bind,()=>console.error(`MCP HTTP listening on ${bind}:${port}`));
 server.on('error',error=>{console.error(error.message);process.exitCode=1;});
 for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>{server.close();server.closeIdleConnections();});
}else await createServer().connect(new StdioServerTransport());
