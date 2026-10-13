import {json,error,rpc,digest,escapeHtml} from '../lib/core.js';
const validId=s=>/^[0-9a-f]{8}-[0-9a-f-]{27,}$/i.test(s||'');
const validToken=s=>/^[A-Za-z0-9_-]{30,80}$/.test(s||'');
function html(title,content,status=200){
 return new Response('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow,noarchive">'+
 '<meta name="referrer" content="no-referrer"><meta name="viewport" content="width=device-width, initial-scale=1">'+
 '<title>'+escapeHtml(title)+' · Compound Solar</title><style>body{font:16px system-ui;background:#f5f9f7;color:#18343a;padding:10vh 20px}main{margin:auto;max-width:520px;background:white;padding:36px;border:1px solid #dce9e5;border-radius:16px}button{background:#0f716e;color:white;border:0;border-radius:8px;padding:14px 20px;font-weight:700;cursor:pointer}</style></head><body><main><h1>'+escapeHtml(title)+'</h1>'+content+'<p><a href="https://compound.ie/solar/">Return to Compound Solar</a></p></main></body></html>',
 {status,headers:{'Cache-Control':'no-store','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'"}});
}
export function GET(request){
 const url=new URL(request.url),project=url.searchParams.get('project'),token=url.searchParams.get('token');
 if(!validId(project)||!validToken(token))return html('Invalid verification link','<p>This link is invalid.</p>',400);
 return html('Confirm your quote request','<p>Use this confirmation button to verify that you requested solar quotations.</p>'+
  '<form method="post" action="/api/verify"><input type="hidden" name="project" value="'+escapeHtml(project)+'">'+
  '<input type="hidden" name="token" value="'+escapeHtml(token)+'"><button type="submit">Confirm my solar quote request</button></form>');
}
export async function POST(request){
 try{
   const body=await request.text();
   if(body.length>500)return html('Unable to verify','<p>The confirmation link was invalid.</p>',400);
   const form=new URLSearchParams(body),project=form.get('project'),token=form.get('token');
   if(!validId(project)||!validToken(token))return html('Unable to verify','<p>The confirmation link was invalid.</p>',400);
   const r=await rpc('solar_confirm_email',{p_project_id:project,p_token_digest:digest(token)});
   return r?.status==='verified'
     ?html('Email confirmed','<p>Your solar quote request is now verified. Approved installers can review its anonymous summary, but your contact information stays private until a qualified introduction is purchased.</p>')
     :html('Unable to verify','<p>Please request another confirmation email.</p>',400);
 }catch{return html('Unable to verify','<p>The link may have expired. Please contact Compound Solar.</p>',400);}
}
