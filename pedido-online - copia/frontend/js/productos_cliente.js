window.API_BASE = window.API_BASE || (window.API_BASE_URL || "http://127.0.0.1:5000").replace(/\/$/,"");

function getUsuario() {
  try { return JSON.parse(localStorage.getItem("usuario")) || null; } catch { return null; }
}

function carritoKey() {
  const u = getUsuario();
  return u && u.id_usuario ? `carrito_${u.id_usuario}` : "carrito";
}

function leerCarrito() {
  try { return JSON.parse(localStorage.getItem(carritoKey())) || []; } catch { return []; }
}

function guardarCarrito(arr) {
  localStorage.setItem(carritoKey(), JSON.stringify(arr));
}

function agregarAlCarrito(prod, cantidad) {
  const nCant = Math.max(1, parseInt(cantidad, 10) || 1);
  const cart = leerCarrito();
  const idx = cart.findIndex(x => Number(x.id_producto) === Number(prod.id_producto));
  if (idx >= 0) {
    cart[idx].cantidad = Number(cart[idx].cantidad || 0) + nCant;
  } else {
    cart.push({
      id_producto: Number(prod.id_producto),
      nombre: prod.nombre || "",
      descripcion: prod.descripcion || "",
      precio_unitario: Number(prod.precio_unitario || 0),
      cantidad: nCant
    });
  }
  guardarCarrito(cart);
  alert("Producto agregado al carrito");
}

async function cargarProductos() {
  const cont = document.getElementById("listaProductos");
  cont.innerHTML = "";
  const res = await fetch(`${window.API_BASE}/api/products/list`);
  const data = await res.json();
  if (!Array.isArray(data) || data.length === 0) {
    cont.innerHTML = "<div class='muted'>No hay productos disponibles.</div>";
    return;
  }
  data.forEach(p => {
    const card = document.createElement("div");
    card.className = "card";
    const stock = Number(p.stock ?? 0);
    card.innerHTML = `
      <div class="title">${p.nombre || ""}</div>
      <div class="muted">${p.descripcion || ""}</div>
      <div class="price">Precio: Q${Number(p.precio_unitario || 0).toFixed(2)}</div>
      <div class="muted">Disponibles: ${stock}</div>
      <div class="row">
        <input type="number" min="1" value="1" class="qty">
        <button class="btn">Agregar al Carrito</button>
      </div>
    `;
    const qty = card.querySelector(".qty");
    card.querySelector(".btn").addEventListener("click", () => agregarAlCarrito(p, qty.value));
    cont.appendChild(card);
  });
}

document.addEventListener("DOMContentLoaded", cargarProductos);
