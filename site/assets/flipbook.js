/* Flipbook album engine (page curl by dragging a bottom corner). Usage: window.ALBUM={el,imgs,pages,chapters,chapBar} then load this file. */
(function(){
const A=window.ALBUM, IMG=A.imgs, P=A.pages;
const N=P.length, root=document.getElementById(A.el), book=root.querySelector('.book'), stage=root.querySelector('.stage');
if(typeof A.chapBar==='string')A.chapBar=root.querySelector(A.chapBar);
let W=0,H=0,mode='',pos=0,busy=false,turn=null;
const ph=(n,w,h)=>{const s=(w&&h)?` style="width:${w}px;height:${h}px"`:'';return `<span class="ph"${s}><img src="${IMG[n].src}" alt="" draggable="false"></span>`};
function fit(n,bw,bh){const r=IMG[n].w/IMG[n].h;let w=bw,h=w/r;if(h>bh){h=bh;w=h*r}return [Math.round(w),Math.round(h)]}
function pageHTML(i,side){
  if(i<0||i>=N)return '';
  const p=P[i],cls=side||((i%2===0)?'R':'L'),fol=(i>0&&i<N-1)?`<span class="folio">${String(i).padStart(2,'0')}</span>`:'';let inner='';
  if(p.t==='cover'){const [w,h]=fit(p.img,W*0.76,H*0.5);inner=`<div class="gframe"></div>${ph(p.img,w,h)}<div class="our">${p.our||''}</div><div class="title">${p.title||''}</div><div class="mark">${p.mark||''}</div><div class="meta">${p.meta||''}</div>`}
  else if(p.t==='backc')inner=`<div class="gframe"></div><div class="title">${p.title||'Thank you'}</div><div class="meta">${p.meta||''}</div>`;
  else if(p.t==='full')inner=`${ph(p.img)}${p.cap?`<div class="cap">${p.cap}</div>`:''}`;
  else if(p.t==='mat'){const [w,h]=fit(p.img,W*0.84,H*0.72);inner=`${ph(p.img,w,h)}${p.cap?`<div class="cap">${p.cap}</div>`:''}${p.sub?`<div class="sub">${p.sub}</div>`:''}${fol}`}
  else if(p.t==='duo'){const a=fit(p.imgs[0],W*0.8,H*0.37),b=fit(p.imgs[1],W*0.8,H*0.37);inner=`${ph(p.imgs[0],a[0],a[1])}${ph(p.imgs[1],b[0],b[1])}${p.cap?`<div class="cap">${p.cap}</div>`:''}${fol}`}
  else if(p.t==='chap')inner=`<div class="gframe"></div><p class="eb">${p.eb}</p><div class="names">${p.names}</div><p class="kind">${p.kind}</p><div class="rule"></div><p class="d">${p.d}</p>${fol}`;
  else inner=p.html+fol;
  return `<div class="pg ${p.t} ${cls}">${inner}</div>`;
}
const maxPos=()=>mode==='spread'?N/2:N-1;
function build(){
  const vw=stage.clientWidth,vh=window.innerHeight,m=vw>=760?'spread':'single';
  if(m!==mode){pos=mode===''?0:(m==='spread'?Math.ceil(pos/2):Math.max(0,pos*2-1));}
  mode=m;const maxH=Math.max(360,vh-215);
  W=Math.floor(m==='spread'?Math.min(460,(vw-20)/2,maxH*0.8):Math.min(480,vw,maxH*0.8));H=Math.round(W*1.25);
  pos=Math.min(pos,maxPos());
  stage.className='stage '+m;book.className='book '+m;book.style.cssText=`width:${m==='spread'?2*W:W}px;height:${H}px;--u:${W/100}px`;
  book.innerHTML=`<div class="bookshadow"></div><div class="slot l"></div><div class="slot r"></div>${m==='spread'?'<div class="spine"></div>':''}<div class="corner l"></div><div class="corner r"></div>`;
  book.querySelectorAll('.slot').forEach(s=>{s.style.width=W+'px';s.style.height=H+'px'});
  const r=book.querySelector('.slot.r');r.style.left=(m==='spread'?W:0)+'px';if(m==='single')book.querySelector('.slot.l').remove();
  if(m==='spread')book.querySelector('.spine').style.left=W+'px';
  rest();
}
function rest(){
  const L=book.querySelector('.slot.l'),R=book.querySelector('.slot.r'),sh=book.querySelector('.bookshadow');
  if(mode==='spread'){L.innerHTML=pageHTML(2*pos-1);R.innerHTML=pageHTML(2*pos);
    const x=pos===0?-W/2:pos===N/2?W/2:0;book.style.transform=`translateX(${x}px)`;sh.style.left=pos===0?W+'px':'0';sh.style.right=pos===N/2?W+'px':'0';
    book.querySelector('.spine').style.opacity=(pos===0||pos===N/2)?0:1;}
  else{R.innerHTML=pageHTML(pos,'R');book.style.transform='';}
  root.querySelector('.prev').disabled=pos===0;root.querySelector('.next').disabled=pos===maxPos();
  const c=root.querySelector('.count');
  if(mode==='spread')c.textContent=pos===0?'Cover':pos===N/2?'Back cover':`Pages ${2*pos-1}–${2*pos}`;
  else c.textContent=pos===0?'Cover':pos===N-1?'Back cover':`Page ${pos} of ${N-2}`;
  if(typeof markChap==='function')markChap();
}
/* ---- page curl geometry ---- */
function clipPoly(poly,M,n,keepPos){const out=[];for(let i=0;i<poly.length;i++){const a=poly[i],b=poly[(i+1)%poly.length];const da=(a[0]-M[0])*n[0]+(a[1]-M[1])*n[1],db=(b[0]-M[0])*n[0]+(b[1]-M[1])*n[1];const ia=keepPos?da>=0:da<=0,ib=keepPos?db>=0:db<=0;if(ia)out.push(a);if(ia!==ib){const t=da/(da-db);out.push([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]);}}return out}
const polyCSS=p=>p.length?`polygon(${p.map(v=>v[0].toFixed(1)+'px '+v[1].toFixed(1)+'px').join(',')})`:'polygon(0 0,0 0,0 0)';
function startTurn(dir){ // dir: 1 forward, -1 backward
  if(busy||turn)return null;
  if(dir>0&&pos>=maxPos())return null;if(dir<0&&pos<=0)return null;
  const t={dir,side:'R',slotX:mode==='spread'?W:0,rev:false};
  const L=book.querySelector('.slot.l'),R=book.querySelector('.slot.r');
  let front,back;
  if(mode==='spread'){
    if(dir>0){front=pageHTML(2*pos);back=pageHTML(2*pos+1);R.innerHTML=pageHTML(2*pos+2);}
    else{t.side='L';t.slotX=0;front=pageHTML(2*pos-1);back=pageHTML(2*pos-2);L.innerHTML=pageHTML(2*pos-3);}
    book.querySelector('.bookshadow').style.left='0';book.querySelector('.bookshadow').style.right='0';
  }else{
    if(dir>0){front=pageHTML(pos,'R');back='<div class="blank"></div>';R.innerHTML=pageHTML(pos+1,'R');}
    else{t.rev=true;front=pageHTML(pos-1,'R');back='<div class="blank"></div>';}
  }
  const el=document.createElement('div');el.className='turn';el.style.cssText=`left:${t.slotX}px;width:${W}px;height:${H}px`;
  el.innerHTML=`<div class="under"><i></i></div><div class="front">${front}</div><div class="flapw"><div class="flap" style="width:${W}px;height:${H}px">${back}<i></i></div></div>`;
  book.appendChild(el);t.el=el;t.C=t.side==='R'?[W,H]:[0,H];t.S=t.side==='R'?[0,H]:[W,H];t.end=t.side==='R'?[-W,H]:[2*W,H];
  t.P=t.rev?t.end.slice():t.C.slice();turn=t;draw(t.P);return t;
}
function clampP(t,p){let x=p[0],y=p[1];const S=t.S,T=[S[0],0];let dx=x-S[0],dy=y-S[1],d=Math.hypot(dx,dy);if(d>W){x=S[0]+dx/d*W;y=S[1]+dy/d*W}
  const D=Math.hypot(W,H);dx=x-T[0];dy=y-T[1];d=Math.hypot(dx,dy);if(d>D){x=T[0]+dx/d*D;y=T[1]+dy/d*D}return [x,y]}
function draw(p){
  const t=turn;if(!t)return;p=clampP(t,p);t.P=p;const C=t.C,el=t.el,front=el.querySelector('.front'),fw=el.querySelector('.flapw'),flap=el.querySelector('.flap'),under=el.querySelector('.under');
  const dx=C[0]-p[0],dy=C[1]-p[1],dist=Math.hypot(dx,dy);
  if(dist<1.5){front.style.clipPath='';fw.style.display='none';under.style.display='none';return}
  fw.style.display='';under.style.display='';
  const n=[dx/dist,dy/dist],M=[(C[0]+p[0])/2,(C[1]+p[1])/2],rect=[[0,0],[W,0],[W,H],[0,H]];
  const fp=clipPoly(rect,M,n,false),cp=clipPoly(rect,M,n,true);
  front.style.clipPath=polyCSS(fp);under.style.clipPath=polyCSS(cp);
  flap.style.clipPath=polyCSS(cp.map(v=>[W-v[0],v[1]]));
  const a=-(1-2*n[0]*n[0]),c=-2*n[0]*n[1],b=2*n[0]*n[1],d=1-2*n[1]*n[1],mn=M[0]*n[0]+M[1]*n[1];
  const e=(1-2*n[0]*n[0])*W+2*mn*n[0],f=-2*n[0]*n[1]*W+2*mn*n[1];
  fw.style.transform=`matrix(${a},${b},${c},${d},${e},${f})`;
  const us=under.firstElementChild,th=Math.atan2(-n[0],n[1]);us.style.height=Math.min(150,dist*0.55)+'px';
  us.style.transform=`translate(${M[0]}px,${M[1]}px) rotate(${th}rad) translate(-1500px,0)`;
  const fs=flap.lastElementChild,n2=[-n[0],n[1]],th2=Math.atan2(-n2[0],n2[1]);fs.style.height=(dist/2+2)+'px';
  fs.style.transform=`translate(${W-M[0]}px,${M[1]}px) rotate(${th2}rad) translate(-1500px,0)`;
}
function finish(t,complete){
  busy=true;const from=t.P.slice(),to=complete?(t.rev?t.C:t.end):(t.rev?t.end:t.C),t0=performance.now(),dur=Math.max(220,520*Math.hypot(to[0]-from[0],to[1]-from[1])/(2*W));
  (function step(now){let k=Math.min(1,(now-t0)/dur);const e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2;
    draw([from[0]+(to[0]-from[0])*e,from[1]+(to[1]-from[1])*e-Math.sin(Math.PI*e)*H*0.10*(Math.abs(to[0]-from[0])/(2*W))]);
    if(k<1)requestAnimationFrame(step);else{if(complete)pos+=t.dir;t.el.remove();turn=null;busy=false;rest();}
  })(t0);
}
function go(dir){const t=startTurn(dir);if(t)finish(t,true)}
/* ---- pointer: drag a corner ---- */
let drag=null;
function local(e){const r=book.getBoundingClientRect();return [e.clientX-r.left,e.clientY-r.top]}
function toP(t,q){let x=q[0]-t.slotX,y=q[1];if(t.rev)x=2*x-W;return [x,Math.min(y,H+40)]}
book.addEventListener('pointerdown',e=>{
  if(busy||turn||e.target.closest('a'))return;const q=local(e),bw=mode==='spread'?2*W:W;let dir=0;
  if(q[0]>bw-W*0.42)dir=1;else if(q[0]<W*0.42)dir=-1;if(!dir)return;
  if(mode==='spread'){if(dir>0&&pos===0&&q[0]<W)return;if(dir<0&&pos===N/2&&q[0]>W)return;}
  const t=startTurn(dir);if(!t)return;drag={t,x0:e.clientX,y0:e.clientY,moved:false};try{book.setPointerCapture(e.pointerId)}catch(_){}
  draw(toP(t,q));e.preventDefault();
});
book.addEventListener('pointermove',e=>{
  if(drag){if(Math.hypot(e.clientX-drag.x0,e.clientY-drag.y0)>6)drag.moved=true;draw(toP(drag.t,local(e)));return}
  if(busy||turn||e.pointerType!=='mouse')return;
});
function endDrag(e,cancel){if(!drag)return;const t=drag.t,moved=drag.moved;drag=null;
  const pr=Math.hypot(t.P[0]-t.C[0],t.P[1]-t.C[1])/(2*W);let complete;
  if(cancel)complete=false;else if(!moved)complete=true;else complete=t.rev?pr<0.7:pr>0.3;finish(t,complete);}
book.addEventListener('pointerup',e=>endDrag(e,false));book.addEventListener('pointercancel',e=>endDrag(e,true));
root.querySelector('.prev').onclick=()=>go(-1);root.querySelector('.next').onclick=()=>go(1);
root.tabIndex=-1;root.addEventListener('keydown',e=>{if(e.key==='ArrowRight')go(1);if(e.key==='ArrowLeft')go(-1);});
/* jump to a page index (chapter buttons) */
A.jump=function(i){jump(i)};
root.addEventListener('click',e=>{const a=e.target.closest('[data-page]');if(a){e.preventDefault();jump(+a.dataset.page);}});
function jump(i){if(busy||turn)return;pos=mode==='spread'?Math.ceil(i/2):i;pos=Math.min(pos,maxPos());rest();markChap();}
function curPage(){return mode==='spread'?Math.min(2*pos,N-1):pos}
function markChap(){if(!A.chapBar)return;const cp=curPage();let on=-1;A.chapters.forEach((c,k)=>{if(cp>=c.at)on=k});A.chapBar.querySelectorAll('button').forEach((b,k)=>b.classList.toggle('on',k===on));}
if(A.chapBar){A.chapters.forEach(c=>{const b=document.createElement('button');b.type='button';b.textContent=c.label;b.onclick=()=>{jump(c.at);root.scrollIntoView({behavior:'smooth',block:'nearest'})};A.chapBar.appendChild(b)});}
let rt;addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(()=>{if(!turn&&!busy)build()},160);});
build();
/* intro: peel the corner once so people see it can be turned */
setTimeout(()=>{if(busy||turn||pos!==0||matchMedia('(prefers-reduced-motion:reduce)').matches)return;const t=startTurn(1);if(!t)return;busy=true;const t0=performance.now();
  (function s(now){const k=Math.min(1,(now-t0)/1300),a=Math.sin(Math.PI*k);draw([t.C[0]-a*W*0.32,t.C[1]-a*H*0.16]);if(k<1)requestAnimationFrame(s);else{t.el.remove();turn=null;busy=false;rest();}})(t0);},900);


/* auto-open the cover once (owner, Nov 25): if nobody has touched the magazine after ~4s and it is on screen, open to the first spread, then never move on its own again */
let touched=false;['pointerdown','keydown','wheel','touchstart'].forEach(ev=>root.addEventListener(ev,()=>{touched=true},{passive:true}));
let onScreen=true;if('IntersectionObserver' in window){new IntersectionObserver(es=>{onScreen=es[0].isIntersecting&&es[0].intersectionRatio>0.5},{threshold:[0,0.5,1]}).observe(stage)}
setTimeout(()=>{if(touched||pos!==0||busy||turn||!onScreen||matchMedia('(prefers-reduced-motion:reduce)').matches)return;go(1)},4200);
})();
