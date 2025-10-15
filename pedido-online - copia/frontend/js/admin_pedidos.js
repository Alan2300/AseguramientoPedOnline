const API_BASE = (window.API_BASE_URL || "http://127.0.0.1:5000").replace(/\/$/,"")
const ESTADOS = ["Pendiente", "En proceso", "Completado", "Cancelado"]

const ADMIN_HOME  = "/frontend/admin_panel.html"
const CLIENT_HOME = "/frontend/productos_cliente.html"

let ALL_ORDERS = []
let VIEW = []

function q(s){return document.querySelector(s)}
function fmtQ(n){n=Number(n||0);return "Q "+n.toFixed(2)}
async function fetchJSON(url,opt={}){const r=await fetch(url,{credentials:"include",headers:{"Content-Type":"application/json"},...opt});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.mensaje||"Error");return d}

function estadoSelect(actual){
  const sel=document.createElement("select"); sel.className="input"
  ESTADOS.forEach(x=>{const o=document.createElement("option");o.value=x;o.textContent=x;if(x===actual)o.selected=true;sel.appendChild(o)})
  return sel
}

function selectedStatuses(){return [...document.querySelectorAll("#statusBox input[type=checkbox]:checked")].map(x=>x.value)}
function setStatuses(vals){const set=new Set(vals);document.querySelectorAll("#statusBox input[type=checkbox]").forEach(ch=>ch.checked=set.has(ch.value))}

function matchesSearch(o, q){
  if(!q) return true
  q=q.toLowerCase()
  const bag=[
    String(o.id||""),
    o.fecha||"",
    o.estado||"",
    o.cliente_nombre||"",
    o.cliente_email||"",
    String(o.productos||""),
    String(o.total||""),
    (o.product_names||"")
  ].join(" ").toLowerCase()
  return bag.includes(q)
}

function render(){
  const tbody=q("#tbodyPedidos")
  const statuses=new Set(selectedStatuses())
  const qtxt=(q("#txtSearch").value||"").trim().toLowerCase()

  VIEW=ALL_ORDERS
    .filter(o=>statuses.size===0 ? true : statuses.has(o.estado))
    .filter(o=>matchesSearch(o,qtxt))

  if(!VIEW.length){ tbody.innerHTML=`<tr><td colspan="7" class="muted">No hay resultados.</td></tr>`; return }

  tbody.innerHTML=""
  VIEW.forEach(p=>{
    const tr=document.createElement("tr")
    const tdId=document.createElement("td"); tdId.textContent="#"+p.id
    const tdF=document.createElement("td"); tdF.textContent=p.fecha
    const tdCli=document.createElement("td"); tdCli.innerHTML=`<div>${p.cliente_nombre||""}</div><div class="muted">${p.cliente_email||""}</div>`
    const tdPro=document.createElement("td"); tdPro.textContent=p.productos
    const tdTot=document.createElement("td"); tdTot.className="right"; tdTot.textContent=fmtQ(p.total)
    const tdEst=document.createElement("td"); const sel=estadoSelect(p.estado); tdEst.appendChild(sel)
    const tdAcc=document.createElement("td"); const b=document.createElement("button"); b.className="btn primary"; b.textContent="Actualizar"

    b.onclick=async()=>{
      b.disabled=true
      try{
        await fetchJSON(`${API_BASE}/api/admin/orders/${p.id}/status`,{method:"PATCH",body:JSON.stringify({status:sel.value})})
        alert(`Pedido #${p.id} actualizado a "${sel.value}". Se notificó al cliente por correo.`)
        await loadOrders(true)
      }catch(e){ alert(e.message||"Error al actualizar") } finally{ b.disabled=false }
    }

    tdAcc.appendChild(b)
    tr.append(tdId,tdF,tdCli,tdPro,tdTot,tdEst,tdAcc)
    tbody.appendChild(tr)
  })
}

async function loadOrders(silent=false){
  if(!silent){ q("#tbodyPedidos").innerHTML=`<tr><td colspan="7" class="muted">Cargando…</td></tr>` }
  try{
    const data=await fetchJSON(`${API_BASE}/api/admin/orders`)
    ALL_ORDERS=Array.isArray(data)?data:[]
    render()
  }catch(e){
    q("#tbodyPedidos").innerHTML=`<tr><td colspan="7" class="muted">No se pudo cargar. ${e.message||""}</td></tr>`
  }
}

function goTo(url){ window.location.href = url }

async function goHome(){
  try{
    const me = await fetchJSON(`${API_BASE}/api/users/me`)
    const rol = String(me.rol || me.role || "").toLowerCase()
    if(rol==="admin" || rol==="administrador"){ goTo(ADMIN_HOME); return }
    if(rol==="cliente"){ goTo(CLIENT_HOME); return }
  }catch(_){/* fallback abajo */}
  try{
    const u = JSON.parse(localStorage.getItem("usuario")||"null")
    const idRol = Number(u && u.id_rol)
    if(idRol===1){ goTo(ADMIN_HOME); return }
    if(idRol===2){ goTo(CLIENT_HOME); return }
  }catch(_){}
  goTo("/frontend/login.html")
}

document.addEventListener("DOMContentLoaded", ()=>{
  setStatuses(["Pendiente","En proceso"])
  q("#btnAll").onclick = ()=>{ setStatuses(ESTADOS); render() }
  q("#btnNone").onclick = ()=>{ setStatuses([]); render() }
  q("#txtSearch").addEventListener("input", render)
  document.querySelectorAll("#statusBox input[type=checkbox]").forEach(ch=>ch.addEventListener("change", render))
  q("#btnHome").addEventListener("click", goHome)

  document.getElementById("btnLogout").addEventListener("click", async ()=>{
    try{ await fetch(`${API_BASE}/api/users/logout`,{method:"POST",credentials:"include"}) }catch(e){}
    location.href="/frontend/login.html"
  })

  loadOrders()
})
