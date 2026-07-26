import re, sys, os
h=open(os.path.join(os.path.dirname(__file__),'..','index.html')).read()
# 非贪婪：只要店本身那块 <script>，别把落地页的脚本和中间的 HTML 也抠进来
js=re.search(r'<script>(.*?)</script>', h, re.S).group(1)
js=js.replace('let saveT = 0;','let saveT = 0; globalThis.__api={saveState,loadState,get people(){return people},CAST,personGeom,SAVE_KEY,TABLES,TW,get gang(){return gang},get GANG(){return GANG}};')
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
let inTable=0; const inTableWhere={};   // 站进桌子里的帧数（腿会被桌面盖没）
let dupSeat=0; const dupWhere={};       // 一个座位同时被两个人认领的帧数
let badBy=0; const badByWhere={};       // p.chair.by 指向别人
let overlap=0; const overlapWhere={};   // 两个坐着的人画在同一位置
let stand=0; const standWhere={};       // 站着的人踩在别人坐着的椅子上
const run=(min)=>{const s={};for(let i=0;i<30*60*min;i++){t+=step*1000;const f=RAF.shift();if(!f)break;f(t);
  for(const p of A.people){
    if(!p.lying){ allFrames++;
      if(p.dir==='e'||p.dir==='w'){ sideAny++;
        const k=(p.role==='regular'||!p.castKey?p.state:p.task)||'?'; sideWhere[k]=(sideWhere[k]||0)+1; } }
    if(p.path&&p.path.length){ walkFrames++; if(p.dir==='e'||p.dir==='w') sideWalk++; }
    // 站着的人落在桌子格子里 ⇒ 桌面会从上沿再往上盖 6px，腿会被整段吃掉
    if(!p.sitting&&!p.lying) for(const tb of A.TABLES)
      if(p.px>tb.x*A.TW&&p.px<(tb.x+tb.w)*A.TW&&p.py>tb.y*A.TW&&p.py<(tb.y+tb.h)*A.TW){
        inTable++; inTableWhere[tb.label]=(inTableWhere[tb.label]||0)+1; }
    if(!p.castKey) continue; const o=s[p.castKey]=s[p.castKey]||{n:0,lie:0,st:new Set(),x:[]};
    o.n++; if(p.lying)o.lie++; o.st.add(p.role==='regular'?p.state:p.task); o.x.push(Math.round(p.px)); }
  // 同一把椅子 / 沙发位不能同时被两个人认领
  const claim=new Map();
  for(const p of A.people){
    // gang 成员的 chair 和 gangSeat 指同一把椅子，先按人去重，只比不同人之间
    for(const c of new Set([p.chair,p.seat,p.gangSeat].filter(Boolean))){
      const who=q=>(q.name||q.castKey||'客')+':'+((q.role==='regular'||!q.castKey?q.state:q.task)||'?');
      if(claim.has(c)){ dupSeat++;
        const k=[who(claim.get(c)),who(p)].sort().join(' + '); dupWhere[k]=(dupWhere[k]||0)+1; }
      else claim.set(c,p); }
    if(p.chair&&p.chair.by&&p.chair.by!==p){ badBy++;
      badByWhere[(p.name||'客')+'→'+(p.chair.by.name||'客')]=1; } }
  // 站着的人踩到别人正坐着的椅子格上 —— 画面上就是两个人叠在一张椅子上
  const seatedAt=new Map();
  for(const p of A.people) if(p.sitting&&p.chair&&p.state!=='away') seatedAt.set(p.chair,p);
  // 走路途中路过别人椅子是正常的，只揪站定不动还压在人身上的
  for(const p of A.people){ if(p.sitting||p.lying||p.state==='away') continue;
    if(p.path&&p.path.length) continue;
    const tx=Math.floor(p.px/A.TW), ty=Math.floor(p.py/A.TW);
    for(const [c,q] of seatedAt) if(c.x===tx&&c.y===ty){ stand++;
      standWhere[(p.name||'客')+':'+((p.role==='regular'||!p.castKey?p.state:p.task)||'?')+' 踩 '+(q.name||'客')]=
        (standWhere[(p.name||'客')+':'+((p.role==='regular'||!p.castKey?p.state:p.task)||'?')+' 踩 '+(q.name||'客')]||0)+1; } }
  const sit=A.people.filter(p=>p.sitting&&p.state!=='away');
  for(let a=0;a<sit.length;a++)for(let b=a+1;b<sit.length;b++)
    if(Math.abs(sit[a].px-sit[b].px)<3&&Math.abs(sit[a].py-sit[b].py)<3){ overlap++;
      overlapWhere[[sit[a].name||'客',sit[b].name||'客'].sort().join(' + ')]=1; }
  }
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

console.log('\\n── 一个座位只能有一个人 ──');
console.log(`同座帧数 ${dupSeat}  ${dupSeat===0?'← 通过':'← 失败: '+JSON.stringify(dupWhere)}`);
console.log(`chair.by 指向别人 ${badBy} 帧  ${badBy===0?'← 通过':'← 失败: '+JSON.stringify(badByWhere)}`);
console.log(`站着的人踩别人椅子 ${stand} 帧  ${stand===0?'← 通过':'← 失败: '+JSON.stringify(Object.fromEntries(Object.entries(standWhere).sort((a,b)=>b[1]-a[1]).slice(0,6)))}`);
console.log(`两个坐着的人重叠 ${overlap} 帧  ${overlap===0?'← 通过':'← 失败: '+JSON.stringify(overlapWhere)}`);

console.log('\\n── 起身不留落座偏移：没人站在桌子格子里 ──');
console.log(`站着的帧里，落在桌子格子内 ${inTable} 帧  ${inTable===0?'← 通过':'← 失败: '+JSON.stringify(inTableWhere)}`);

console.log('\\n── 体型对照（站姿总高 = 腿 + 躯干） ──');
for(const k of Object.keys(A.CAST)){const p=A.people.find(x=>x.castKey===k);const g=A.personGeom(p);
  console.log(`${p.name.padEnd(7)} ${(p.build||'normal').padEnd(9)} 腿${g.legLen} 躯干${g.torsoH} 总高${String(g.legLen+g.torsoH).padStart(2)} 半宽${g.torsoHW} 眼镜=${p.glasses?'有':'无'} 战衣=${p.spider?'有':'无'}`);}

console.log('\\n── 组队进行中存盘再读档 ──');
let tries=0; while(!A.gang&&tries++<40) run(1);
if(!A.gang) console.log('40 分钟没等到组队，跳过');
else {
  const before=[dupSeat,overlap,badBy];
  const seats=A.gang.members.map(m=>m.gangSeat&&m.gangSeat.by===m);
  console.log('组队中，成员', A.gang.members.map(m=>m.name).join('/'), ' 座位归属正常 =', seats.every(Boolean));
  A.saveState(); A.loadState();
  const back=A.people.filter(p=>A.GANG.includes(p.castKey));
  console.log('读档后 gangSeat =', back.map(p=>p.gangSeat?'有':'无').join(','),
              ' chair =', back.map(p=>p.chair?'有':'无').join(','),
              ' task =', back.map(p=>p.task).join(','));
  run(6);
  console.log(`读档后 6 分钟：同座 ${dupSeat-before[0]} 帧、重叠 ${overlap-before[1]} 帧、by 错位 ${badBy-before[2]} 帧`);
  console.log(JSON.stringify(dupWhere), JSON.stringify(overlapWhere));
}

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
