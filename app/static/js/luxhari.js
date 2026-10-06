(function(){
  const drawer=document.getElementById('drawer'),scrim=document.getElementById('scrim');
  function open(){drawer?.classList.add('open');scrim?.classList.add('open')}
  function close(){drawer?.classList.remove('open');scrim?.classList.remove('open')}
  document.getElementById('mobileMenu')?.addEventListener('click',open);
  document.querySelector('.menu-toggle')?.addEventListener('click',open);
  document.getElementById('drawerClose')?.addEventListener('click',close);
  scrim?.addEventListener('click',close);

  document.querySelectorAll('[data-love]').forEach(btn=>btn.addEventListener('click',async(e)=>{
    e.preventDefault(); e.stopPropagation();
    const id=btn.dataset.love;
    let saved=JSON.parse(localStorage.getItem('luxhari_interests')||'[]');
    if(!saved.includes(id)) saved.push(id); else saved=saved.filter(x=>x!==id);
    localStorage.setItem('luxhari_interests',JSON.stringify(saved));
    try{const r=await fetch('/api/love/'+id,{method:'POST'});const data=await r.json();const span=btn.querySelector('span');if(span)span.textContent=data.loves}catch(err){}
    btn.firstChild.textContent=saved.includes(id)?'♥ ':'♡ ';
  }));

  const grid=document.getElementById('interestGrid');
  const empty=document.getElementById('interestEmpty');
  if(grid){
    const ids=JSON.parse(localStorage.getItem('luxhari_interests')||'[]');
    Promise.all(ids.map(id=>fetch('/product/'+id).then(r=>r.ok?r.text():null).catch(()=>null))).then(htmls=>{
      const pages=htmls.filter(Boolean);
      if(!pages.length){empty.style.display='block';return}
      empty.style.display='none';
      pages.forEach(html=>{const doc=new DOMParser().parseFromString(html,'text/html');const card=doc.querySelector('.product-page');if(!card)return;const a=document.createElement('a');a.className='mini-card';a.href=card.querySelector('form')?.action?.replace('/cart/add/','/product/')||'#';const img=card.querySelector('.product-visual img');if(img){a.innerHTML='<img src="'+img.src+'" alt=""><h3>'+doc.querySelector('.product-info h1')?.textContent+'</h3><p>'+doc.querySelector('.price')?.textContent+'</p>';grid.appendChild(a)}})
    })
  }
  setTimeout(()=>document.querySelectorAll('.toast').forEach(t=>{t.style.opacity='0';t.style.transform='translateY(-8px)';setTimeout(()=>t.remove(),4500)}),3000);
})();
