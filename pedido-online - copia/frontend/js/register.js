const EMAIL_RX = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i;

function passChecks(p){
  return {
    len: typeof p==="string" && p.length>=8,
    low: /[a-z]/.test(p||""),
    up:  /[A-Z]/.test(p||""),
    num: /\d/.test(p||""),
    sym: /[^\w\s]/.test(p||"")
  };
}

function setErr(id,msg){ const el=document.getElementById(id); if(el) el.textContent=msg||""; }
function mark(el,ok){ el.classList.toggle("ok",!!ok); }

function liveEmailHint(){
  const email=document.getElementById("correo").value.trim();
  if(!email) { setErr("errEmail",""); return; }
  setErr("errEmail", EMAIL_RX.test(email) ? "" : "Debe ser un correo válido con formato usuario@dominio.com");
}

function livePassHint(){
  const p=document.getElementById("contrasena").value;
  const c=passChecks(p);
  mark(document.getElementById("rLen"), c.len);
  mark(document.getElementById("rLow"), c.low);
  mark(document.getElementById("rUp"),  c.up);
  mark(document.getElementById("rNum"), c.num);
  mark(document.getElementById("rSym"), c.sym);
  const ok = c.len && c.low && c.up && c.num && c.sym;
  setErr("errPass", ok ? "" : "La contraseña no cumple todos los requisitos.");
}

document.addEventListener("input", (e)=>{
  if(e.target && e.target.id==="correo") liveEmailHint();
  if(e.target && e.target.id==="contrasena") livePassHint();
});

async function registrar(){
  const nombre = document.getElementById("nombre_usuario").value.trim();
  const email  = document.getElementById("correo").value.trim();
  const pass   = document.getElementById("contrasena").value;
  const banner = document.getElementById("errorBanner");

  setErr("errNombre",""); setErr("errEmail",""); setErr("errPass",""); banner.textContent="";

  let ok = true;
  if(!nombre || nombre.length<2){ setErr("errNombre","El nombre debe tener al menos 2 caracteres."); ok=false; }
  if(!EMAIL_RX.test(email)){ setErr("errEmail","Debe ser un correo válido con formato usuario@dominio.com."); ok=false; }
  const pc = passChecks(pass);
  if(!(pc.len && pc.low && pc.up && pc.num && pc.sym)){
    setErr("errPass","La contraseña debe tener mínimo 8 caracteres, e incluir minúscula, mayúscula, número y símbolo.");
    ok=false;
  }
  if(!ok) return;

  const btn=document.getElementById("btnRegister"); if(btn) btn.disabled=true;

  try{
    const resp = await fetch("http://127.0.0.1:5000/api/users/register",{
      method:"POST",
      headers:{ "Content-Type":"application/json" },
      body:JSON.stringify({ nombre, email, password: pass })
    });
    const data = await resp.json();

    if(!resp.ok){
      if(data && data.errores){
        if(data.errores.nombre) setErr("errNombre", data.errores.nombre);
        if(data.errores.email)  setErr("errEmail",  data.errores.email);
        if(data.errores.password) setErr("errPass", data.errores.password);
      } else if(data && data.mensaje){
        banner.textContent = data.mensaje;
      } else {
        banner.textContent = "No se pudo registrar.";
      }
      return;
    }

    alert("Registro exitoso. Ahora puedes iniciar sesión.");
    window.location.href="login.html";
  } catch(e){
    banner.textContent="Error de conexión.";
  } finally {
    if(btn) btn.disabled=false;
  }
}
