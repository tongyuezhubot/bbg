/* 渲染收银台正面，确认台面上的字 */
const fs=require("fs");
let lab=fs.readFileSync(__dirname+"/spritelab.js","utf8");
let head=lab.slice(0, lab.indexOf("/* ── 从 HTML 里取出真正在用的绘制代码 ── */"));
head=head.replace('const fs = require("fs");','').replace('const zlib = require("zlib");','');
globalThis.fs=fs; globalThis.zlib=require("zlib");
head+="\nglobalThis.MiniCtx=MiniCtx; globalThis.writePNG=writePNG;";
(0,eval)(head);

let js=fs.readFileSync(__dirname+"/../index.html","utf8").match(/<script>([\s\S]*)<\/script>/)[1];
js=js.replace("let saveT = 0;","let saveT = 0; globalThis.__api={drawCounter,drawPerson,makePerson,counter,TW,STAFF_POST};");
const RAF=[]; globalThis.requestAnimationFrame=f=>RAF.push(f);
globalThis.performance={now:()=>0}; globalThis.matchMedia=()=>({matches:false});
globalThis.addEventListener=()=>{};
const store={}; globalThis.localStorage={getItem:k=>k in store?store[k]:null,setItem:(k,v)=>{store[k]=String(v)}};
const dummy=()=>new Proxy({},{get:(t,k)=>{
  if(k==="createLinearGradient"||k==="createRadialGradient")return()=>({addColorStop(){}});
  if(k==="canvas")return{width:0,height:0}; return()=>{};},set:()=>true});
globalThis.document={getElementById:()=>({getContext:dummy}),createElement:()=>({width:0,height:0,getContext:dummy}),visibilityState:"visible"};
eval(js);
const A=globalThis.__api, TW=A.TW, c=A.counter;

const X0=(c.x-1)*TW, Y0=(c.y-3)*TW, W=(c.w+2)*TW, H=6*TW;
const ctx=new MiniCtx(W,H);
ctx.fillStyle="#6b563c"; ctx.fillRect(0,0,W,H);          // 地板底色，别用透明棋盘干扰读字
ctx.translate=null;
// 手动平移：画完再整体搬进画布不方便，直接偏移坐标系
const shifted=new Proxy(ctx,{get:(t,k)=>{
  if(k==="fillRect") return (x,y,w,h)=>t.fillRect(x-X0,y-Y0,w,h);
  return typeof t[k]==="function"?t[k].bind(t):t[k];
}, set:(t,k,v)=>{t[k]=v;return true;}});

A.drawCounter(shifted,0);
// 站两个店员在柜台后，看看字会不会被挡
[[A.STAFF_POST.x,"bear"],[A.STAFF_POST.x-1,"rabbit"]].forEach(([tx,key])=>{
  const n=A.makePerson(key); n.dir="n"; n.seed=0; n.path=[];
  n.px=tx*TW+TW/2; n.py=A.STAFF_POST.y*TW+TW-2;
  A.drawPerson(shifted,n,0);
});
writePNG(__dirname+"/counter.png", ctx.buf, W, H, 10);
console.log("counter.png", W+"x"+H, "(10x)");
