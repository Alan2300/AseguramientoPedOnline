const EMAIL_RX=/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i;

async function enviar(){
  const email=document.getElementById("email").value.trim();
  const error=document.getElementById("error");
  const ok=document.getElementById("ok");
  error.textContent=""; ok.textContent="";
  if(!EMAIL_RX.test(email)){error.textContent="Ingresa un correo válido.";return;}
  try{
    const r=await fetch(`${window.API_BASE}/api/users/password/forgot`,{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({email})
    });
    const d=await r.json();
    ok.textContent=d.mensaje||"Si el correo existe, se ha enviado un enlace.";
  }catch(e){
    error.textContent="Error de conexión.";
  }
}
