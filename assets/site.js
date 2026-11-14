// Joenell Studio — shared page script: menu, reveal-on-scroll, search box, form prefill + submit.
(function(){
  const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];

  // mobile menu
  const btn=$('.menu-btn'), nav=$('nav.main');
  if(btn&&nav){btn.addEventListener('click',()=>{const o=nav.classList.toggle('open');btn.setAttribute('aria-expanded',o);btn.textContent=o?'✕':'☰';});}

  // reveal on scroll
  const io='IntersectionObserver' in window?new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}}),{rootMargin:'0px 0px -8% 0px'}):null;
  $$('.reveal').forEach(el=>io?io.observe(el):el.classList.add('in'));

  // dates: no past dates
  const today=new Date();today.setMinutes(today.getMinutes()-today.getTimezoneOffset());
  $$('input[type=date]').forEach(i=>{if(!i.min)i.min=today.toISOString().slice(0,10);});

  // prefill a form from ?date=&package=&photographer=
  const q=new URLSearchParams(location.search);
  $$('form[data-prefill]').forEach(f=>{
    q.forEach((v,k)=>{
      const els=f.elements[k]; if(!els) return;
      if(els instanceof RadioNodeList||els.type==='radio'){$$(`input[name="${k}"]`,f).forEach(r=>{if(r.value===v)r.checked=true;});}
      else if(els.tagName==='SELECT'){if([...els.options].some(o=>o.value===v))els.value=v;}
      else els.value=v;
    });
  });

  // submit forms with data-endpoint as JSON
  $$('form[data-endpoint]').forEach(f=>{
    f.addEventListener('submit',async e=>{
      e.preventDefault();
      const msg=$('.msg',f), sub=$('button[type=submit]',f);
      msg.className='msg'; msg.textContent='';
      if(!f.checkValidity()){f.reportValidity();return;}
      const data={};
      new FormData(f).forEach((v,k)=>{data[k]=data[k]?[].concat(data[k],v):v;});
      data.page=location.pathname;
      sub.disabled=true; const label=sub.textContent; sub.textContent='Sending…';
      try{
        const r=await fetch(f.dataset.endpoint,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(data)});
        const j=await r.json().catch(()=>({}));
        if(!r.ok||!j.ok) throw new Error(j.error||'Something went wrong.');
        f.hidden=true; const done=document.getElementById(f.dataset.done);
        if(done){done.style.display='block';done.scrollIntoView({behavior:'smooth',block:'center'});}
      }catch(err){
        msg.className='msg err';
        msg.innerHTML=(err.message||'Something went wrong.')+' If it keeps happening, email <a href="mailto:hello@joenellstudio.com">hello@joenellstudio.com</a>.';
        sub.disabled=false; sub.textContent=label;
      }
    });
  });

  // footer year
  $$('[data-year]').forEach(el=>el.textContent=new Date().getFullYear());
})();
