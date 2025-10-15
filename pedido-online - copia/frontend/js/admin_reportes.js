const API_BASE = (window.API_BASE_URL || "http://127.0.0.1:5000").replace(/\/$/,"")
const ADMIN_HOME  = "/frontend/admin_panel.html"
const CLIENT_HOME = "/frontend/productos_cliente.html"

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

async function downloadFile(url, filename){
  const r = await fetch(url, { credentials:"include" })
  if(!r.ok){ const t = await r.text(); alert("Error: "+t); return }
  const blob = await r.blob()
  const a = document.createElement("a")
  a.href = URL.createObjectURL(blob)
  a.download = filename
  document.body.appendChild(a)
  a.click()
  URL.revokeObjectURL(a.href)
  a.remove()
}

document.addEventListener("DOMContentLoaded", ()=>{
  q("#btnHome").onclick = goHome
  q("#btnLogout").onclick = async()=>{ try{await fetch(`${API_BASE}/api/users/logout`,{method:"POST",credentials:"include"})}catch{} goTo("/frontend/login.html") }

  q("#btnRepOrders").onclick = async()=>{
    const from = q("#pedFrom").value
    const to   = q("#pedTo").value
    const client = (q("#clientQ").value||"").trim()
    const params = new URLSearchParams()
    if(from) params.set("from", from)
    if(to)   params.set("to", to)
    if(client) params.set("client", client)
    const url = `${API_BASE}/api/admin/reports/orders.xlsx${params.toString()?`?${params}`:""}`
    await downloadFile(url, "reporte_pedidos.xlsx")
  }

  q("#btnRepByStatus").onclick = async()=>{
    const st = q("#pedStatus").value
    const from = q("#pedFrom").value
    const to   = q("#pedTo").value
    const params = new URLSearchParams({ status: st })
    if(from) params.set("from", from)
    if(to)   params.set("to", to)
    const url = `${API_BASE}/api/admin/reports/status.xlsx?${params}`
    await downloadFile(url, `reporte_pedidos_${st.replaceAll(" ","_").toLowerCase()}.xlsx`)
  }

  q("#btnRepProducts").onclick = async()=>{
    const kind = q("#prodFilter").value // top | low
    const url = `${API_BASE}/api/admin/reports/products.xlsx?filter=${encodeURIComponent(kind)}`
    await downloadFile(url, `reporte_${kind==="top"?"mas":"menos"}_solicitados.xlsx`)
  }
})
