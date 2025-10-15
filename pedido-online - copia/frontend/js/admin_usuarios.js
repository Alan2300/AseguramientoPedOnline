const API_BASE = (window.API_BASE_URL || "http://127.0.0.1:5000").replace(/\/$/,"")
const ADMIN_HOME  = "/frontend/admin_panel.html"
const CLIENT_HOME = "/frontend/productos_cliente.html"

const ROLES = { 1:"Administrador", 2:"Cliente" }
const EMAIL_RX = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/

function q(s){return document.querySelector(s)}
async function j(url,opt={}){const r=await fetch(url,{credentials:"include",headers:{"Content-Type":"application/json"},...opt});let d={};try{d=await r.json()}catch{}if(!r.ok)throw new Error(d.mensaje||"Error");return d}

function goTo(u){ location.href=u }
async function goHome(){
  try{
    const me = await j(`${API_BASE}/api/users/me`)
    const rol = String(me.rol||me.role||"").toLowerCase()
    if(rol==="admin"||rol==="administrador"){ goTo(ADMIN_HOME); return }
    if(rol==="cliente"){ goTo(CLIENT_HOME); return }
  }catch(_){
    try{
      const u=JSON.parse(localStorage.getItem("usuario")||"null")
      const idRol=Number(u&&u.id_rol)
      if(idRol===1){ goTo(ADMIN_HOME); return }
      if(idRol===2){ goTo(CLIENT_HOME); return }
    }catch{}
  }
  goTo("/frontend/login.html")
}

function strongPass(p){
  if(!p || p.length<8) return false
  return /[A-Z]/.test(p)&&/[a-z]/.test(p)&&/[0-9]/.test(p)&&/[^A-Za-z0-9]/.test(p)
}

function row(u){
  const tr=document.createElement("tr")
  tr.innerHTML=`
    <td>${u.nombre||""}</td>
    <td>${u.email||""}</td>
    <td>${ROLES[u.id_rol]||u.rol||u.id_rol}</td>
    <td>
      <button class="btn warn" data-act="edit">Editar</button>
      <button class="btn danger" data-act="del">Eliminar</button>
    </td>
  `
  tr.querySelector('[data-act="edit"]').onclick=()=>openEdit(u)
  tr.querySelector('[data-act="del"]').onclick=()=>delUser(u)
  return tr
}

async function loadUsers(){
  const tb=q("#tbodyUsers"); tb.innerHTML=`<tr><td colspan="4" class="muted">Cargando…</td></tr>`
  const qv = (q("#q").value||"").trim()
  const role = q("#role").value
  const params = new URLSearchParams()
  if(qv) params.set("q", qv)
  if(role) params.set("role", role)
  const url = `${API_BASE}/api/admin/users${params.toString() ? ("?"+params.toString()) : ""}`
  try{
    const users = await j(url)
    tb.innerHTML=""
    users.forEach(u=>tb.appendChild(row(u)))
    if(!users.length) tb.innerHTML=`<tr><td colspan="4" class="muted">No hay usuarios.</td></tr>`
  }catch(e){
    tb.innerHTML=`<tr><td colspan="4" class="muted">No se pudo cargar. ${e.message||""}</td></tr>`
  }
}

function openNew(){
  q("#dlgTitle").textContent="Registrar usuario"
  q("#userId").value=""
  q("#nombre").value=""
  q("#email").value=""
  q("#password").value=""
  q("#rol").value="2"
  q("#err").textContent=""
  q("#dlgUser").showModal()
}

function openEdit(u){
  q("#dlgTitle").textContent=`Editar usuario`
  q("#userId").value=u.id_usuario
  q("#nombre").value=u.nombre||""
  q("#email").value=u.email||""
  q("#password").value=""
  q("#rol").value=String(u.id_rol||2)
  q("#err").textContent=""
  q("#dlgUser").showModal()
}

async function save(){
  const id=q("#userId").value.trim()
  const nombre=q("#nombre").value.trim()
  const email=(q("#email").value||"").trim().toLowerCase()
  const password=q("#password").value
  const id_rol=Number(q("#rol").value)
  const err=q("#err")

  err.textContent=""
  if(!nombre){ err.textContent="El nombre es obligatorio"; return }
  if(!EMAIL_RX.test(email)){ err.textContent="Correo inválido"; return }
  if(!id){
    if(!password){ err.textContent="La contraseña es obligatoria"; return }
    if(!strongPass(password)){ err.textContent="Contraseña insegura. Usa 8+ caracteres con mayúsculas, minúsculas, números y símbolo."; return }
  }else{
    if(password && !strongPass(password)){ err.textContent="Contraseña insegura. Usa 8+ caracteres con mayúsculas, minúsculas, números y símbolo."; return }
  }

  const payload={ nombre, email, password, id_rol }
  try{
    if(id){
      await j(`${API_BASE}/api/admin/users/${id}`,{method:"PUT",body:JSON.stringify(payload)})
    }else{
      await j(`${API_BASE}/api/admin/users`,{method:"POST",body:JSON.stringify(payload)})
    }
    q("#dlgUser").close()
    await loadUsers()
  }catch(e){
    err.textContent=e.message||"Error"
  }
}

async function delUser(u){
  if(!confirm(`¿Eliminar a "${u.nombre}"?`)) return
  try{
    await j(`${API_BASE}/api/admin/users/${u.id_usuario}`,{method:"DELETE"})
    await loadUsers()
  }catch(e){ alert(e.message||"No se pudo eliminar") }
}

document.addEventListener("DOMContentLoaded", ()=>{
  q("#btnHome").onclick=goHome
  q("#btnLogout").onclick=async()=>{ try{await fetch(`${API_BASE}/api/users/logout`,{method:"POST",credentials:"include"})}catch{} goTo("/frontend/login.html") }
  q("#btnAdd").onclick=openNew
  q("#btnSave").onclick=save
  q("#btnCancel").onclick=()=>q("#dlgUser").close()

  q("#btnSearch").onclick=loadUsers
  q("#q").addEventListener("keydown",e=>{ if(e.key==="Enter"){ e.preventDefault(); loadUsers() }})
  q("#role").addEventListener("change", loadUsers)

  loadUsers()
})
