function getParam(name){
  const u=new URL(window.location.href);
  return u.searchParams.get(name)||"";
}

const EMAIL_RX=/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i;
const rxLower=/[a-z]/, rxUpper=/[A-Z]/, rxDigit=/\d/, rxSym=/[^\w\s]/;

function toggle(id, tid){
  const el=document.getElementById(id);
  const t=document.getElementById(tid);
  if(el.type==="password"){el.type="text"; t.textContent="ocultar";}
  else{el.type="password"; t.textContent="ver";}
}

function check(){
  const p1=document.getElementById("pwd1").value;
  const p2=document.getElementById("pwd2").value;

  const goodLen=p1.length>=8;
  const goodLow=rxLower.test(p1);
  const goodUp =rxUpper.test(p1);
  const goodNum=rxDigit.test(p1);
  const goodSym=rxSym.test(p1);
  const equal  =p1!=="" && p1===p2;

  set("r-len",goodLen); set("r-low",goodLow); set("r-up",goodUp);
  set("r-num",goodNum); set("r-sym",goodSym); set("r-eq",equal);

  const all=goodLen && goodLow && goodUp && goodNum && goodSym && equal;
  document.getElementById("btn").disabled=!all;
}
function set(id, ok){
  const el=document.getElementById(id);
  el.className= ok ? "okreq" : "badreq";
}

document.getElementById("pwd1").addEventListener("input",check);
document.getElementById("pwd2").addEventListener("input",check);

async function cambiar(){
  const token=getParam("token");
  const p1=document.getElementById("pwd1").value;
  const p2=document.getElementById("pwd2").value;
  const error=document.getElementById("error");
  const ok=document.getElementById("ok");
  error.textContent=""; ok.textContent="";
  if(!token){error.textContent="Token inválido.";return;}
  if(p1!==p2){error.textContent="Las contraseñas no coinciden.";return;}

  try{
    const r=await fetch(`${window.API_BASE}/api/users/password/reset`,{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({token:token,new_password:p1})
    });
    const d=await r.json();
    if(r.ok){
      ok.textContent=d.mensaje||"Contraseña actualizada.";
      setTimeout(()=>{window.location.href="/frontend/login.html"},1400);
    }else{
      error.textContent=d.mensaje||"No se pudo actualizar la contraseña.";
    }
  }catch(e){
    error.textContent="Error de conexión.";
  }
}
