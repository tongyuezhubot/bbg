/* 只画头，放到很大，检查脸型和镜架 */
const fs=require("fs");
let lab=fs.readFileSync(__dirname+"/spritelab.js","utf8");
let head=lab.slice(0, lab.indexOf("/* ── 从 HTML 里取出真正在用的绘制代码 ── */"));
head=head.replace('const fs = require("fs");','').replace('const zlib = require("zlib");','');
globalThis.fs=fs; globalThis.zlib=require("zlib");
head+="\nglobalThis.MiniCtx=MiniCtx; globalThis.writePNG=writePNG;";
(0,eval)(head);

let js=fs.readFileSync(__dirname+"/../index.html","utf8").match(/<script>([\s\S]*)<\/script>/)[1];
js=js.replace("let saveT = 0;","let saveT = 0; globalThis.__api={drawPerson,makePerson,CAST,personGeom};");
const RAF=[]; globalThis.requestAnimationFrame=f=>RAF.push(f);
globalThis.performance={now:()=>0}; globalThis.matchMedia=()=>({matches:false});
globalThis.addEventListener=()=>{};
const store={}; globalThis.localStorage={getItem:k=>k in store?store[k]:null,setItem:(k,v)=>{store[k]=String(v)}};
const dummy=()=>new Proxy({},{get:(t,k)=>{
  if(k==="createLinearGradient"||k==="createRadialGradient")return()=>({addColorStop(){}});
  if(k==="canvas")return{width:0,height:0}; return()=>{};},set:()=>true});
globalThis.document={getElementById:()=>({getContext:dummy}),createElement:()=>({width:0,height:0,getContext:dummy}),visibilityState:"visible"};
eval(js);
const A=globalThis.__api;

const WHO=["lanwen","bear","haley"], DIRS=["s","e","w"];
const CW=17, CH=19;
const W=CW*DIRS.length, H=CH*WHO.length;
const ctx=new MiniCtx(W,H);
for(let y=0;y<H;y++)for(let x=0;x<W;x++){ctx.fillStyle=((x>>2)+(y>>2))%2?"#d8d2c4":"#c9c2b2";ctx.fillRect(x,y,1,1);}
ctx.fillStyle="rgba(0,0,0,.25)";
for(let i=1;i<WHO.length;i++)ctx.fillRect(0,i*CH,W,1);
for(let i=1;i<DIRS.length;i++)ctx.fillRect(i*CW,0,1,H);

WHO.forEach((key,row)=>{
  DIRS.forEach((d,col)=>{
    const n=A.makePerson(key); n.dir=d; n.seed=0; n.path=[]; n.hat=false;
    const g=A.personGeom(n);
    // 把脚底放在格子下方，让头正好落在格子里
    const cx=col*CW+Math.floor(CW/2);
    const headTop=row*CH+3;
    const py=headTop+7+g.torsoH+g.legLen;
    const shifted=new Proxy(ctx,{get:(t,k)=>{
      if(k==="fillRect")return(x,y,w,h)=>{ if(y>=row*CH&&y<row*CH+CH) t.fillRect(x,y,w,h); };
      return typeof t[k]==="function"?t[k].bind(t):t[k];},set:(t,k,v)=>{t[k]=v;return true;}});
    n.px=cx; n.py=py;
    A.drawPerson(shifted,n,0);
  });
});
writePNG(__dirname+"/faces.png", ctx.buf, W, H, 34);
console.log("faces.png", W+"x"+H, "(34x)  行:", WHO.join(" / "), " 列: 正面/朝东/朝西");
