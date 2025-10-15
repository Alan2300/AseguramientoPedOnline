(function(){
  const back = document.createElement('div');
  back.className = 'lb-backdrop';
  back.innerHTML = `
    <button class="lb-close" aria-label="Cerrar">✕</button>
    <img class="lb-img" alt="">
  `;
  document.addEventListener('DOMContentLoaded',()=>document.body.appendChild(back));

  function open(src){
    const img = back.querySelector('.lb-img');
    img.src = src;
    back.classList.add('open');
  }
  function close(){ back.classList.remove('open'); }

  document.addEventListener('click', (e)=>{
    const t = e.target;
    if (t.matches('.zoomable')) {
      const full = t.getAttribute('data-full') || t.src;
      open(full);
    }
    if (t === back || t.matches('.lb-close')) close();
  });

  document.addEventListener('keydown', (e)=>{ if(e.key==='Escape') close(); });
})();
