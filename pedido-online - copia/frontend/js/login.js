window.API_BASE = window.API_BASE || (window.API_BASE_URL || "http://127.0.0.1:5000").replace(/\/$/,"");
const EMAIL_RX = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i;

async function login() {
  const correo = document.getElementById("correo").value.trim();
  const contrasena = document.getElementById("contrasena").value;
  const error = document.getElementById("error");
  const btn = document.querySelector("button[onclick='login()']");
  error.textContent = "";

  if (!EMAIL_RX.test(correo)) { error.textContent = "Ingresa un correo válido."; return; }
  if (!contrasena) { error.textContent = "Ingresa tu contraseña."; return; }
  if (btn) btn.disabled = true;

  try {
    const resp = await fetch(`${window.API_BASE}/api/users/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email: correo, password: contrasena })
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) { error.textContent = data.mensaje || "Credenciales incorrectas."; return; }

    localStorage.setItem("usuario", JSON.stringify(data.usuario || {}));
    localStorage.setItem("token", data.token || "");

    if (typeof goHome === "function") {
      goHome();
    } else {
      const ROLE_HOME = { 1: "/frontend/admin_panel.html", 2: "/frontend/user_panel.html", "admin": "/frontend/admin_panel.html", "cliente": "/frontend/user_panel.html" };
      const rol = data.rol || (data.usuario || {}).id_rol;
      const destino = ROLE_HOME[rol] || "/frontend/login.html";
      window.location.href = destino;
    }
  } catch (e) {
    error.textContent = "Error de conexión.";
  } finally {
    if (btn) btn.disabled = false;
  }
}

async function me() {
  const r = await fetch(`${window.API_BASE}/api/users/me`, { credentials: "include" });
  return r.json();
}

async function logout() {
  await fetch(`${window.API_BASE}/api/users/logout`, { method: "POST", credentials: "include" });
  localStorage.removeItem("usuario");
  localStorage.removeItem("token");
}
