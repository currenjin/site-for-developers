import {McpServer} from '@modelcontextprotocol/sdk/server/mcp.js';
import {z} from 'zod';
import {catalog,searchSites} from './catalog.js';
const annotations={readOnlyHint:true,destructiveHint:false,idempotentHint:true,openWorldHint:false};
const response=data=>({content:[{type:'text',text:JSON.stringify(data)}],structuredContent:data});
export function createServer(){
 const server=new McpServer({name:'site-for-developers',version:'0.1.0'});
 server.registerTool('search_sites',{description:'Search the bundled README snapshot using bilingual keywords. Metadata is not verification.',annotations,inputSchema:z.object({query:z.string().max(200).optional(),category:z.string().max(100).optional(),language:z.enum(['EN','KR']).optional(),limit:z.number().int().min(1).max(20).default(10)}).strict()},async args=>response(searchSites(args)));
 server.registerTool('get_site',{description:'Get a site by stable catalog ID; never fetches its URL.',annotations,inputSchema:z.object({id:z.string().min(1).max(100)}).strict()},async ({id})=>{const site=catalog.sites.find(s=>s.id===id);return site?response({site,source:catalog.source}):{isError:true,content:[{type:'text',text:'Unknown site ID'}]};});
 server.registerTool('list_categories',{description:'List README category hierarchy and site counts.',annotations,inputSchema:z.object({}).strict()},async()=>response({categories:catalog.categories.map(c=>({...c,count:catalog.sites.filter(s=>s.categories.includes(c.id)).length})),source:catalog.source}));
 return server;
}
