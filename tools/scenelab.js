/* 跑一帧完整画面，看满铺地毯配上家具人物是什么效果 */
const fs=require("fs");
let lab=fs.readFileSync(__dirname+"/spritelab.js","utf8");
let head=lab.slice(0, lab.indexOf("/* ── 从 HTML 里取出真正在用的绘制代码 ── */"));
head=head.replace('const fs = require("fs");','').replace('const zlib = require("zlib");','');
globalThis.fs=fs; globalThis.zlib=require("zlib");
head+="\nglobalThis.MiniCtx=MiniCtx; globalThis.writePNG=writePNG;";
(0,eval)(head);

let js=fs.readFileSync(__dirname+"/../index.html","utf8").match(/<script>([\s\S]*)<\/script>/)[1];
js=js.replace("let saveT = 0;","let saveT = 0; globalThis.__api={get people(){return people},clock};");

const RAF=[]; globalThis.requestAnimationFrame=f=>RAF.push(f);
let T=0; globalThis.performance={now:()=>T}; globalThis.matchMedia=()=>({matches:false});
globalThis.addEventListener=()=>{};
const store={}; globalThis.localStorage={getItem:k=>k in store?store[k]:null,setItem:(k,v)=>{store[k]=String(v)}};

const canvases=[]; let made=0;
const dummy=()=>new Proxy({},{get:(t,k)=>{
  if(k==="createLinearGradient"||k==="createRadialGradient")return()=>({addColorStop(){}});
  if(k==="canvas")return{width:0,height:0}; return()=>{};},set:()=>true});
// scene / lightC / floorTex 三张都用真的光栅器；drawImage 做成整张贴过去
function realCanvas(){
  const c=new MiniCtx(640,448);
  c.drawImage=(src)=>{
    const b=src&&src.__buf; if(!b) return;
    for(let i=0;i<b.length;i+=4){ if(b[i+3]){ c.buf[i]=b[i];c.buf[i+1]=b[i+1];c.buf[i+2]=b[i+2];c.buf[i+3]=b[i+3]; } }
  };
  const obj={width:640,height:448,getContext:()=>c,__buf:c.buf};
  c.canvas=obj; canvases.push(c); return obj;
}
globalThis.document={
  getElementById:()=>({getContext:dummy}),
  createElement:()=>{ made++; return made<=3?realCanvas():{width:0,height:0,getContext:dummy}; },
  visibilityState:"visible",
};
eval(js);

// 推进几帧，让人物散开到店里各处
for(let i=0;i<60*40;i++){ T+=33.3; const f=RAF.shift(); if(!f)break; f(T); }
writePNG(__dirname+"/scene.png", canvases[0].buf, 640, 448, 2);
console.log("scene.png (2x)  人数:", globalThis.__api.people.length);
