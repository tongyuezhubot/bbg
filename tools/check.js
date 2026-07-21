const GW=40,GH=28;
const grid=Array.from({length:GH},()=>new Uint8Array(GW));
const box=(x,y,w,h,v=1)=>{for(let j=y;j<y+h;j++)for(let i=x;i<x+w;i++)if(i>=0&&j>=0&&i<GW&&j<GH)grid[j][i]=v;};
const walk=(x,y)=>x>=0&&y>=0&&x<GW&&y<GH&&grid[y][x]===0;
box(0,0,GW,2);box(0,2,1,GH-2);box(GW-1,2,1,GH-2);box(0,GH-1,GW,1);
grid[25][GW-1]=0;grid[26][GW-1]=0;
const IWV=[],IWH=[];
const aV=(x,y,h)=>{IWV.push({x,y,h});box(x,y,1,h);};
const aH=(x,y,w)=>{IWH.push({x,y,w});box(x,y,w,1);};
aV(12,2,12);aH(12,16,8);aV(19,2,3);aV(19,7,9);aV(28,2,2);aV(28,6,1);aH(23,7,GW-23);aH(22,24,GW-22);
const shelves=[];const aS=(x,y,w)=>{shelves.push({x,y,w});box(x,y,w,1);};
aS(2,2,10);aS(14,2,5);aS(20,2,8);aS(29,2,3);aS(35,2,4);aS(9,26,5);aS(24,26,13);
const wsh=[];const aWS=(x,y,h,dir)=>{wsh.push({x,y,h,dir});box(x,y,1,h);};
aWS(1,2,7,'w');aWS(1,14,5,'w');aWS(13,2,11,'w');aWS(38,11,6,'e');
const PILL=[{x:32,y:2,w:3,h:3},{x:31,y:8,w:3,h:3}];PILL.forEach(p=>box(p.x,p.y,p.w,p.h));
const TABLES=[];
function addTable(x,y,w,h,label){const t={x,y,w,h,label,chairs:[]};box(x,y,w,h);
 const a=Math.floor(w*.25),b=Math.floor(w*.75),c=Math.floor(h*.25),d=Math.floor(h*.75);
 if(w>=h){for(const i of new Set([a,b])){t.chairs.push({x:x+i,y:y-1,dir:'s'});t.chairs.push({x:x+i,y:y+h,dir:'n'});}}
 else{for(const j of new Set([c,d])){t.chairs.push({x:x-1,y:y+j,dir:'e'});t.chairs.push({x:x+w,y:y+j,dir:'w'});}}
 TABLES.push(t);}
addTable(2,4,7,2,'左上长桌');addTable(3,9,3,5,'左墙桌');addTable(8,9,3,5,'左中桌');
addTable(15,4,3,5,'包间大桌');addTable(22,4,5,2,'北窗桌');addTable(22,10,4,4,'中庭方桌');
addTable(28,13,4,3,'东厅一桌');addTable(34,13,4,3,'东厅二桌');addTable(13,18,5,3,'厅心长桌');
addTable(21,20,5,3,'南厅大桌');addTable(28,19,4,3,'东南桌');addTable(35,19,3,3,'角落桌');
const SOFAS=[];function aSofa(x,y,w,dir){const s={x,y,w,dir,seats:[]};box(x,y,w,1);
 for(let i=0;i<w;i++)s.seats.push({x:x+i,y,dir});SOFAS.push(s);}
aSofa(3,20,4,'s');aSofa(8,22,4,'s');aSofa(35,9,4,'w');
box(4,26,4,1); // TV
box(14,24,6,1); // counter
[{x:10,y:3},{x:20,y:22},{x:26,y:23},{x:11,y:17}].forEach(p=>grid[p.y][p.x]=1);

// flood from spawn
const SP={x:38,y:25};
const seen=Array.from({length:GH},()=>new Uint8Array(GW));
const q=[SP];seen[SP.y][SP.x]=1;
while(q.length){const c=q.pop();
 for(const[dx,dy]of[[1,0],[-1,0],[0,1],[0,-1]]){const nx=c.x+dx,ny=c.y+dy;
  if(walk(nx,ny)&&!seen[ny][nx]){seen[ny][nx]=1;q.push({x:nx,y:ny});}}}
const FRONT={n:[0,-1],s:[0,1],e:[1,0],w:[-1,0]};
let bad=0;
// 椅子：直接走上椅格
TABLES.forEach(t=>t.chairs.forEach((c,i)=>{
 if(!(walk(c.x,c.y)&&seen[c.y][c.x])){bad++;console.log('UNREACHABLE',t.label+'#'+i,'chair',c.x,c.y,'walkable='+walk(c.x,c.y));}}));
// 沙发：正面一排里找可达落脚点
SOFAS.forEach((sf,si)=>{const f=FRONT[sf.dir];
 const front=sf.seats.map(s=>({x:s.x+f[0],y:s.y+f[1]})).filter(a=>walk(a.x,a.y)&&seen[a.y][a.x]);
 if(!front.length){bad+=sf.seats.length;console.log('UNREACHABLE sofa'+si,'no front access');}
 else console.log('sofa'+si,'front access tiles:',front.length);});
[{x:15,y:23},{x:17,y:23},{x:19,y:23}].forEach((c,i)=>{if(!seen[c.y][c.x]){bad++;console.log('UNREACHABLE queue',i,c);}});
[{x:16,y:25}].forEach(c=>{if(!seen[c.y][c.x]){bad++;console.log('UNREACHABLE staffpost',c);}});
// unreachable floor pockets
let pockets=0;
for(let y=0;y<GH;y++)for(let x=0;x<GW;x++)if(walk(x,y)&&!seen[y][x]){pockets++;if(pockets<12)console.log('pocket',x,y);}
console.log('bad seats/targets:',bad,' unreachable floor tiles:',pockets);
// render ascii
let out='';
for(let y=0;y<GH;y++){let r='';for(let x=0;x<GW;x++){r+= grid[y][x]? (seen[y][x]?'?':'#') : (seen[y][x]?'.':'!');}out+=String(y).padStart(2)+' '+r+'\n';}
console.log(out);
