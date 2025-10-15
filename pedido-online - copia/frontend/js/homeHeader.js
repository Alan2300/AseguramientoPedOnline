(function () {
  const header = document.createElement("header");
  header.className = "app-header";
  header.innerHTML = `
    <div class="app-header__wrap">
      <button class="home-btn" type="button" onclick="goHome()">← Inicio</button>
      <div class="app-header__spacer"></div>
    </div>
  `;
  document.addEventListener("DOMContentLoaded", () => {
    const mount = document.getElementById("app-header");
    if (mount) mount.replaceWith(header);
    else document.body.prepend(header);
  });
})();
