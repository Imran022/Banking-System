import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../site');
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8'};
http.createServer(async(req,res)=>{
  try {
    const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const rel=pathname==='/'?'index.html':pathname.slice(1);
    const target=path.resolve(root,rel);
    if(!target.startsWith(root+path.sep))throw new Error('Invalid path');
    let body=await fs.readFile(target);
    if(rel==='index.html')body=body.toString().replace(/<script type="text\/htmlpreview" src="[^"]+app\.js"><\/script>/,'<script defer src="/app.js"></script>').replace(/https:\/\/raw\.githubusercontent\.com\/Imran022\/Banking-System\/codex\/capitol-ledger-live\/site\/styles\.css/,'/styles.css');
    if(rel==='app.js')body=body.toString().replace('https://raw.githubusercontent.com/Imran022/Banking-System/codex/capitol-ledger-live/site/','http://127.0.0.1:4173/');
    res.writeHead(200,{'content-type':types[path.extname(target)]||'application/octet-stream','cache-control':'no-store'});res.end(body);
  } catch {res.writeHead(404);res.end('Not found');}
}).listen(4173,'127.0.0.1');
