/* 把地板贴图整张画出来，看看地毯到底铺了多大 */
const fs=require("fs");
let lab=fs.readFileSync(__dirname+"/spritelab.js","utf8");
let head=lab.slice(0, lab.indexOf("/* ── 从 HTML 里取出真正在用的绘制代码 ── */"));
head=head.replace('const fs = require("fs");','').replace('const zlib = require("zlib");','');
globalThis.fs=fs; globalThis.zlib=require("zlib");
head+="\nglobalThis.MiniCtx=MiniCtx; globalThis.writePNG=writePNG;";
(0,eval)(head);

let js=fs.readFileSync(__dirname+"/../index.html","utf8").match(/<script>([\s\S]*)<\/script>/)[1];
js=js.replace("let saveT = 0;","let saveT = 0; globalThis.__api={RUG,TW,GW,GH,NW,NH};");

const RAF=[]; globalThis.requestAnimationFrame=f=>RAF.push(f);
globalThis.performance={now:()=>0}; globalThis.matchMedia=()=>({matches:false});
globalThis.addEventListener=()=>{};
const store={}; globalThis.localStorage={getItem:k=>k in store?store[k]:null,setItem:(k,v)=>{store[k]=String(v)}};

// 真正记录 floorTex 的那块画布，其它画布照旧用哑对象
let floorCtx=null, made=0;
const dummy=()=>new Proxy({},{get:(t,k)=>{
  if(k==="createLinearGradient"||k==="createRadialGradient")return()=>({addColorStop(){}});
  if(k==="canvas")return{width:0,height:0}; return()=>{};},set:()=>true});
globalThis.document={
  getElementById:()=>({getContext:dummy}),
  createElement:()=>{
    made++;
    if(made===3){                       // 第 3 张 mk() 出来的就是 floorTex
      const c=new MiniCtx(640,448); floorCtx=c;
      return {width:0,height:0,getContext:()=>c};
    }
    return {width:0,height:0,getContext:dummy};
  },
  visibilityState:"visible",
};
eval(js);
const A=globalThis.__api;
console.log("RUG =", JSON.stringify(A.RUG), "→ 像素", A.RUG.x*A.TW+","+A.RUG.y*A.TW,
            A.RUG.w*A.TW+"x"+A.RUG.h*A.TW, " 画布", A.NW+"x"+A.NH);
writePNG(__dirname+"/floor.png", floorCtx.buf, 640, 448, 2);
console.log("floor.png (2x)");
