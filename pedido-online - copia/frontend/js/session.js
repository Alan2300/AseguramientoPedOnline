const ROLE_HOME = {
  1: "/frontend/admin_panel.html",
  2: "/frontend/user_panel.html"
};

function getUser() {
  try { return JSON.parse(localStorage.getItem("usuario")) || null; }
  catch { return null; }
}

function getToken() {
  return localStorage.getItem("token") || null;
}

function goHome() {
  const u = getUser();
  if (!u) { location.href = "/frontend/login.html"; return; }
  const dest = ROLE_HOME[u.id_rol] || "/frontend/login.html";
  location.href = dest;
}

function requireAuth() {
  const u = getUser();
  if (!u) location.href = "/frontend/login.html";
}
