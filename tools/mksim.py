import re, sys, os
h=open(os.path.join(os.path.dirname(__file__),'..','index.html')).read()
js=re.search(r'<script>(.*)</script>', h, re.S).group(1)
js=js.replace('let saveT = 0;','let saveT = 0; globalThis.__api={saveState,loadState,get people(){return people},CAST,personGeom,SAVE_KEY};')
stub='''
let RAF=[]; globalThis.requestAnimationFrame=f=>RAF.push(f);
globalThis.performance={now:()=>0}; globalThis.matchMedia=()=>({matches:false});
globalThis.addEventListener=()=>{};
const store={}; globalThis.__store=store;
globalThis.localStorage={getItem:k=>k in store?store[k]:null,setItem:(k,v)=>{store[k]=String(v)}};
const c2d=()=>new Proxy({},{get:(t,k)=>{
  if(k==='createLinearGradient'||k==='createRadialGradient')return()=>({addColorStop(){}});
  if(k==='canvas')return{width:0,height:0}; return ()=>{};}, set:()=>true});
globalThis.document={getElementById:()=>({getContext:c2d}),createElement:()=>({width:0,height:0,getContext:c2d}),visibilityState:'visible'};
'''
tail='''
const A=globalThis.__api; let t=0; const step=1/30;
let sideWalk=0, walkFrames=0;          // 走路时侧身的帧数 —— 改成平移后应当恒为 0
let sideAny=0, allFrames=0;            // 任何状态下侧身的帧数（躺着除外，躺姿本来就是侧的）
const sideWhere={};
const run=(min)=>{const s={};for(let i=0;i<30*60*min;i++){t+=step*1000;const f=RAF.shift();if(!f)break;f(t);
  for(const p of A.people){
    if(!p.lying){ allFrames++;
      if(p.dir==='e'||p.dir==='w'){ sideAny++;
        const k=(p.role==='regular'||!p.castKey?p.state:p.task)||'?'; sideWhere[k]=(sideWhere[k]||0)+1; } }
    if(p.path&&p.path.length){ walkFrames++; if(p.dir==='e'||p.dir==='w') sideWalk++; }
    if(!p.castKey) continue; const o=s[p.castKey]=s[p.castKey]||{n:0,lie:0,st:new Set(),x:[]};
    o.n++; if(p.lying)o.lie++; o.st.add(p.role==='regular'?p.state:p.task); o.x.push(Math.round(p.px)); }}
  return s;};

console.log('── 跑 25 分钟 ──');
let s=run(25);
for(const k of Object.keys(A.CAST)){const p=A.people.find(x=>x.castKey===k);const o=s[k];
  const span=Math.max(...o.x)-Math.min(...o.x);
  console.log(`${p.name.padEnd(4)} 躺着${String((o.lie/o.n*100).toFixed(0)).padStart(3)}%  横向活动范围${String(span).padStart(4)}px  [${[...o.st].sort()}]`);}

console.log('\\n── 躺姿腿长（按体型） ──');
for(const k of Object.keys(A.CAST)){const p=A.people.find(x=>x.castKey===k);
  console.log(`${p.name.padEnd(4)} build=${(p.build||'normal').padEnd(9)} 站姿腿长=${A.personGeom(p).legLen}  躺姿腿长=${Math.round(A.personGeom(p).legLen*2.5)}px`);}

console.log('\\n── 走路一律平移（含随机顾客，不只是常驻） ──');
console.log(`走路帧 ${walkFrames}，其中侧身 ${sideWalk} 帧  ${sideWalk===0?'← 通过':'← 失败'}`);
console.log(`站着/坐着共 ${allFrames} 帧，其中侧身 ${sideAny} 帧  ${sideAny===0?'← 通过':'← 失败: '+JSON.stringify(sideWhere)}`);

console.log('\\n── 体型对照（站姿总高 = 腿 + 躯干） ──');
for(const k of Object.keys(A.CAST)){const p=A.people.find(x=>x.castKey===k);const g=A.personGeom(p);
  console.log(`${p.name.padEnd(7)} ${(p.build||'normal').padEnd(9)} 腿${g.legLen} 躯干${g.torsoH} 总高${String(g.legLen+g.torsoH).padStart(2)} 半宽${g.torsoHW} 眼镜=${p.glasses?'有':'无'} 战衣=${p.spider?'有':'无'}`);}

console.log('\\n── 海莉不再戴帽（含老存档里 hat=true 的情况） ──');
A.saveState();
const hd=JSON.parse(globalThis.__store[A.SAVE_KEY]);
hd.people.find(p=>p.castKey==='haley').hat=true;   // 伪造一份"戴着帽子"的旧存档
globalThis.__store[A.SAVE_KEY]=JSON.stringify(hd);
A.loadState();
let h2=A.people.find(p=>p.castKey==='haley');
console.log('读档后 hat =', h2.hat, ' cap =', h2.cap);
run(10);
h2=A.people.find(p=>p.castKey==='haley');
console.log('进出 10 分钟后 hat =', h2.hat, h2.hat?'← 失败':'← 通过');

console.log('\\n── 老存档兼容：v3 存档里没有小熊/雪兔/lanwen ──');
A.saveState();
const old=JSON.parse(globalThis.__store[A.SAVE_KEY]);
old.people=old.people.filter(p=>!['bear','rabbit','lanwen'].includes(p.castKey));
globalThis.__store[A.SAVE_KEY]=JSON.stringify(old);
A.loadState();
console.log('读档后三位新角色是否补齐:', ['bear','rabbit','lanwen'].every(k=>A.people.some(p=>p.castKey===k)));
run(5);
console.log('补齐后跑 5 分钟无异常');

console.log('\\n── 旧存档注入测试：把海莉塞回 state="resident" ──');
A.saveState();
const d=JSON.parse(globalThis.__store[A.SAVE_KEY]);
const hy0=d.people.find(p=>p.castKey==='haley');
hy0.state='resident'; hy0.task='wake'; hy0.sitting=true; hy0.chair=null; hy0.seat=null;
globalThis.__store[A.SAVE_KEY]=JSON.stringify(d);
A.loadState();
let hy=A.people.find(p=>p.castKey==='haley');
console.log('读档瞬间 海莉 state =', hy.state);
s=run(3);
hy=A.people.find(p=>p.castKey==='haley');
const o=s.haley, span=Math.max(...o.x)-Math.min(...o.x);
console.log('之后 3 分钟 走过的状态 =', [...o.st].sort().join(','));
console.log('横向活动范围 =', span, 'px   当前 state =', hy.state, ' sitting =', hy.sitting);
console.log(span>16 ? '通过：海莉动起来了' : '失败：海莉还是卡住');
'''
open(os.path.join(os.path.dirname(__file__),'sim.js'),'w').write(stub+js+tail)
