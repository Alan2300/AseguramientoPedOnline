import os
from datetime import datetime

def reset_password_email(nombre: str, link: str, ttl_min: int) -> str:
    brand = os.getenv("APP_NAME", "Pedido Online")
    support = os.getenv("SUPPORT_EMAIL", "")
    year = datetime.utcnow().year
    saludo = f"Hola {nombre}" if nombre else "Hola"

    return f"""\
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <title>Restablecer contraseña</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body{{background:#f5f6f8;margin:0;padding:24px;font-family:Arial,Helvetica,sans-serif;color:#1f2937}}
      .card{{max-width:560px;margin:0 auto;background:#fff;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.06);overflow:hidden}}
      .header{{padding:20px 24px;border-bottom:1px solid #e5e7eb}}
      .brand{{font-weight:700;font-size:18px;color:#111827}}
      .content{{padding:24px}}
      .title{{font-size:20px;font-weight:700;margin:0 0 8px}}
      p{{margin:0 0 12px;line-height:1.55}}
      .btn{{display:inline-block;background:#2563eb;color:#fff;text-decoration:none;padding:12px 18px;border-radius:10px;font-weight:600}}
      .note{{font-size:12px;color:#6b7280;margin-top:8px}}
      .footer{{padding:16px 24px;border-top:1px solid #e5e7eb;font-size:12px;color:#6b7280;text-align:center}}
      a{{color:#2563eb}}
    </style>
  </head>
  <body>
    <div class="card">
      <div class="header"><div class="brand">{brand}</div></div>
      <div class="content">
        <h1 class="title">Restablecer tu contraseña</h1>
        <p>{saludo},</p>
        <p>Recibimos una solicitud para restablecer tu contraseña. Haz clic en el botón para continuar.</p>
        <p style="margin:18px 0">
          <a href="{link}" class="btn">Restablecer contraseña</a>
        </p>
        <p class="note">Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
        <p class="note" style="word-break:break-all">{link}</p>
        <p class="note">Este enlace vence en <strong>{ttl_min} minutos</strong> y solo puede usarse una vez.</p>
        <p class="note">Si no solicitaste este cambio, puedes ignorar este mensaje.</p>
      </div>
      <div class="footer">
        © {year} {brand}. {('Soporte: ' + support) if support else ''}
      </div>
    </div>
  </body>
</html>"""
