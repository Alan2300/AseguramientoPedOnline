window.API_BASE = window.API_BASE || (window.API_BASE_URL || "http://127.0.0.1:5000").replace(/\/$/,"");

function getUsuario() {
  try { return JSON.parse(localStorage.getItem("usuario")) || null; } catch { return null; }
}

function carritoKey() {
  const u = getUsuario();
  return u && u.id_usuario ? `carrito_${u.id_usuario}` : "carrito";
}

function sanitizeArray(arr) {
  return (Array.isArray(arr) ? arr : []).filter(x =>
    Number.isInteger(Number(x.id_producto)) &&
    Number(x.id_producto) > 0 &&
    typeof x.nombre === "string" &&
    !isNaN(Number(x.precio_unitario)) &&
    Number.isInteger(Number(x.cantidad)) &&
    Number(x.cantidad) > 0
  ).map(x => ({
    id_producto: Number(x.id_producto),
    nombre: x.nombre,
    descripcion: x.descripcion || "",
    precio_unitario: Number(x.precio_unitario || 0),
    cantidad: Number(x.cantidad || 1)
  }));
}

function leerCarrito() {
  try {
    const raw = JSON.parse(localStorage.getItem(carritoKey())) || [];
    const clean = sanitizeArray(raw);
    if (clean.length !== raw.length) localStorage.setItem(carritoKey(), JSON.stringify(clean));
    return clean;
  } catch {
    return [];
  }
}

function guardarCarrito(arr) {
  localStorage.setItem(carritoKey(), JSON.stringify(sanitizeArray(arr)));
}

function formatearQ(num) {
  const n = Number(num || 0);
  return n.toFixed(2);
}

function renderCarrito() {
  const usuario = getUsuario();
  if (!usuario || !usuario.id_usuario) {
    alert("Debes iniciar sesión primero.");
    window.location.href = "login.html";
    return;
  }

  const carrito = leerCarrito();
  const container = document.getElementById("carritoContainer");
  const totalEl = document.getElementById("total");
  if (!container || !totalEl) return;

  container.innerHTML = "";
  let total = 0;

  carrito.forEach((item, index) => {
    const precio = Number(item.precio_unitario || 0);
    const cant = Number(item.cantidad || 0);
    total += precio * cant;

    const div = document.createElement("div");
    div.className = "card";
    div.innerHTML = `
      <div class="card-info">
        <h3>${item.nombre || ""}</h3>
        <p>${item.descripcion || ""}</p>
        <p>Precio unitario: Q${formatearQ(precio)}</p>
      </div>
      <div>
        Cantidad:
        <input type="number" min="1" value="${cant}" data-idx="${index}">
        <button data-del="${index}">Eliminar</button>
      </div>
    `;
    container.appendChild(div);
  });

  totalEl.textContent = formatearQ(total);

  container.querySelectorAll('input[type="number"]').forEach(inp => {
    inp.addEventListener("change", e => {
      const idx = parseInt(e.target.getAttribute("data-idx"), 10);
      const arr = leerCarrito();
      arr[idx].cantidad = Math.max(1, parseInt(e.target.value, 10));
      guardarCarrito(arr);
      renderCarrito();
    });
  });

  container.querySelectorAll('button[data-del]').forEach(btn => {
    btn.addEventListener("click", e => {
      const idx = parseInt(e.target.getAttribute("data-del"), 10);
      const arr = leerCarrito();
      arr.splice(idx, 1);
      guardarCarrito(arr);
      renderCarrito();
    });
  });
}

function mapCarritoToItems() {
  return leerCarrito().map(it => ({
    id_producto: Number(it.id_producto),
    cantidad: Number(it.cantidad)
  }));
}

async function enviarPedido() {
  const estado = await fetch(`${window.API_BASE}/api/users/me`, { credentials: "include" }).then(r => r.json());
  if (!estado.autenticado) {
    alert("No autenticado. Inicia sesión.");
    window.location.href = "login.html";
    return;
  }

  const items = mapCarritoToItems();
  if (items.length === 0) {
    alert("Tu carrito está vacío o inválido.");
    return;
  }

  const btn = document.getElementById("btnConfirmar");
  if (btn) btn.disabled = true;

  try {
    const res = await fetch(`${window.API_BASE}/api/pedidos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ items })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      alert(data.mensaje || "Error al crear pedido");
      return;
    }
    alert(`Pedido #${data.pedido.id_pedido} creado correctamente.`);
    localStorage.removeItem(carritoKey());
    window.location.href = "user_panel.html";
  } catch (e) {
    alert("Error en la conexión.");
  } finally {
    if (btn) btn.disabled = false;
  }
}

async function cerrarSesion() {
  await fetch(`${window.API_BASE}/api/users/logout`, { method: "POST", credentials: "include" });
  localStorage.removeItem("usuario");
  localStorage.removeItem(carritoKey());
  window.location.href = "login.html";
}

document.addEventListener("DOMContentLoaded", () => {
  renderCarrito();
  const btnC = document.getElementById("btnConfirmar");
  if (btnC) btnC.addEventListener("click", enviarPedido);
  const btnL = document.getElementById("btnLogout");
  if (btnL) btnL.addEventListener("click", cerrarSesion);
});
