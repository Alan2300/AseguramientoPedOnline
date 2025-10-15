const API_BASE = (window.API_BASE_URL || "http://127.0.0.1:5000").replace(/\/$/,"")

const ADMIN_HOME  = "/frontend/admin_panel.html"
const CLIENT_HOME = "/frontend/user_panel.html"

let ALL = []
let VIEW = []

function q(s){return document.querySelector(s)}
function fmtQ(n){n=Number(n||0);return "Q "+n.toFixed(2)}
async function fetchJSON(url,opt={}){const r=await fetch(url,{credentials:"include",headers:{"Content-Type":"application/json"},...opt});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.mensaje||"Error");return d}

function selectedStatuses(){return [...document.querySelectorAll("#statusBox input[type=checkbox]:checked")].map(x=>x.value)}
function setStatuses(vals){const set=new Set(vals);document.querySelectorAll("#statusBox input[type=checkbox]").forEach(ch=>ch.checked=set.has(ch.value))}

function matchesSearch(o, q){
  if(!q) return true
  q=q.toLowerCase()
  const bag=[
    String(o.id||""), o.fecha||"", o.estado||"",
    String(o.productos||""), String(o.total||""),
    (o.product_names||"")
  ].join(" ").toLowerCase()
  return bag.includes(q)
}

function render(){
  const tbody=q("#tbodyMine")
  const statuses=new Set(selectedStatuses())
  const qtxt=(q("#txtSearch").value||"").trim().toLowerCase()

  VIEW=ALL
    .filter(o=>statuses.size===0 ? true : statuses.has(o.estado))
    .filter(o=>matchesSearch(o,qtxt))

  if(!VIEW.length){ tbody.innerHTML=`<tr><td colspan="5" class="muted">No hay resultados.</td></tr>`; return }

  tbody.innerHTML=""
  VIEW.forEach(p=>{
    const tr=document.createElement("tr")
    tr.innerHTML=`
      <td>#${p.id}</td>
      <td>${p.fecha}</td>
      <td>${p.productos}</td>
      <td class="right">${fmtQ(p.total)}</td>
      <td>${p.estado}</td>
    `
    tbody.appendChild(tr)
  })
}

async function loadMine(){
  q("#tbodyMine").innerHTML=`<tr><td colspan="5" class="muted">Cargando…</td></tr>`
  try{
    const me = await fetchJSON(`${API_BASE}/api/users/me`)
    const fromLS = JSON.parse(localStorage.getItem("usuario") || "null")
    q("#who").textContent = (fromLS && fromLS.nombre) || me.nombre || me.name || ""
  }catch(_){
    const fromLS = JSON.parse(localStorage.getItem("usuario") || "null")
    q("#who").textContent = (fromLS && fromLS.nombre) || ""
  }

  try{
    const data = await fetchJSON(`${API_BASE}/api/orders/mine`)
    ALL = Array.isArray(data) ? data : []
    render()
  }catch(e){
    q("#tbodyMine").innerHTML=`<tr><td colspan="5" class="muted">No se pudo cargar el seguimiento. ${e.message||""}</td></tr>`
  }
}

function goTo(u){ window.location.href=u }
async function goHome(){
  try{
    const me=await fetchJSON(`${API_BASE}/api/users/me`)
    const rol=String(me.rol||me.role||"").toLowerCase()
    if(rol==="admin"||rol==="administrador"){ goTo(ADMIN_HOME); return }
    if(rol==="cliente"){ goTo(CLIENT_HOME); return }
  }catch(_){
    try{
      const u=JSON.parse(localStorage.getItem("usuario")||"null")
      const idRol=Number(u && u.id_rol)
      if(idRol===1){ goTo(ADMIN_HOME); return }
      if(idRol===2){ goTo(CLIENT_HOME); return }
    }catch(_){}
  }
  goTo("/frontend/login.html")
}

document.addEventListener("DOMContentLoaded", ()=>{
  setStatuses([]) 

  q("#btnAll").onclick  = ()=>{ setStatuses(["Pendiente","En proceso","Completado","Cancelado"]); render() }
  q("#btnNone").onclick = ()=>{ setStatuses([]); render() }
  q("#txtSearch").addEventListener("input", render)
  document.querySelectorAll("#statusBox input[type=checkbox]").forEach(ch=>ch.addEventListener("change", render))
  q("#btnHome").addEventListener("click", goHome)

  document.getElementById("btnLogout").addEventListener("click", async ()=>{
    try{ await fetch(`${API_BASE}/api/users/logout`,{method:"POST",credentials:"include"}) }catch(e){}
    location.href="/frontend/login.html"
  })

  loadMine()
})
