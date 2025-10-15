(function () {
  const PREFIXES = ["/uploads/", "http://127.0.0.1:5000/uploads/"];

  function esDeUploads(src) {
    if (!src) return false;
    return PREFIXES.some(p => src.indexOf(p) !== -1);
  }

  function envolverConThumb(img) {
    if (img.closest('.thumb')) return;
    const wrap = document.createElement('div');
    wrap.className = 'thumb';
    img.parentNode.insertBefore(wrap, img);
    wrap.appendChild(img);
    const badge = document.createElement('span');
    badge.className = 'zoom-badge';
    badge.textContent = '🔍 Ampliar';
    wrap.appendChild(badge);
  }

  function marcar(img) {
    if (!img || img.classList.contains("zoomable")) return;
    if (esDeUploads(img.getAttribute("src"))) {
      img.classList.add("zoomable");
      envolverConThumb(img);
    }
  }

  function escanear(root) {
    root.querySelectorAll("img").forEach(marcar);
  }

  document.addEventListener("DOMContentLoaded", function () {
    escanear(document);
    const obs = new MutationObserver(muts => {
      muts.forEach(m => {
        m.addedNodes.forEach(n => {
          if (n.nodeType === 1) {
            if (n.tagName === "IMG") marcar(n);
            else escanear(n);
          }
        });
      });
    });
    obs.observe(document.body, { childList: true, subtree: true });
  });
})();
