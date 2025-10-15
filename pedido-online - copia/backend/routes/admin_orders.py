from flask import Blueprint, request, jsonify, session
import os
from backend.services.order_service import list_orders, update_order_status, ALLOWED_STATUSES
from backend.services.email_service import send_email

admin_orders_bp = Blueprint("admin_orders", __name__)

def is_admin():
    rol = session.get("rol") or session.get("role") or session.get("user_role")
    return str(rol).lower() in {"admin", "administrador", "1"}

@admin_orders_bp.route("/orders", methods=["GET"])
def admin_orders_list():
    if not is_admin():
        return jsonify({"mensaje": "No autorizado"}), 403
    return jsonify(list_orders())

@admin_orders_bp.route("/orders/<int:order_id>/status", methods=["PATCH"])
def admin_orders_update_status(order_id):
    if not is_admin():
        return jsonify({"mensaje": "No autorizado"}), 403
    data = request.get_json(silent=True) or {}
    status = (data.get("status") or "").strip()
    if status not in ALLOWED_STATUSES:
        return jsonify({"mensaje": "Estado inválido"}), 400

    updated, err = update_order_status(order_id, status)
    if err:
        return jsonify({"mensaje": err}), 404

    to_email = updated.get("cliente_email")
    if to_email:
        front = os.getenv("FRONTEND_BASE_URL", "http://127.0.0.1:5500")
        track_url = f"{front}/frontend/seguimiento_pedidos.html?pedido={order_id}"
        subject = f"Actualización de tu pedido #{order_id}: {status}"
        html = render_status_email(
            nombre=updated.get("cliente_nombre", ""),
            order_id=order_id,
            nuevo_estado=status,
            track_url=track_url,
        )
        try:
            send_email(to_email, subject, html)
        except Exception:
            pass

    return jsonify({"mensaje": "Estado actualizado", "pedido": updated})

def render_status_email(nombre: str, order_id: int, nuevo_estado: str, track_url: str) -> str:
    return f"""
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Actualización de Pedido</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="margin:0;background:#f5f7fb;font-family:Arial,Helvetica,sans-serif;color:#1f2937;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f5f7fb;padding:24px 0;">
    <tr>
      <td align="center">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:14px;overflow:hidden;box-shadow:0 6px 24px rgba(0,0,0,.06);">
          <tr>
            <td style="background:#0d6efd;padding:24px 28px;color:#fff;font-size:22px;font-weight:700;">
              Actualización de Pedido
            </td>
          </tr>
          <tr>
            <td style="padding:28px;">
              <p style="margin:0 0 12px 0;font-size:16px;">Hola {nombre or "cliente"},</p>
              <p style="margin:0 0 16px 0;font-size:16px;line-height:1.5;">
                El estado de tu <strong>pedido #{order_id}</strong> fue actualizado a
                <span style="display:inline-block;background:#eef6ff;color:#0d6efd;padding:4px 10px;border-radius:999px;font-weight:700;">{nuevo_estado}</span>.
              </p>
              <p style="margin:0 0 22px 0;font-size:16px;line-height:1.5;">
                Ingresa para ver el detalle y el progreso. Por tu seguridad, debes iniciar sesión antes de acceder.
              </p>
              <p>
                <a href="{track_url}" style="background:#0d6efd;color:#fff;text-decoration:none;padding:12px 20px;border-radius:10px;font-weight:700;display:inline-block">Ver seguimiento</a>
              </p>
              <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">
              <p style="margin:0;color:#6b7280;font-size:13px;">Si no solicitaste este pedido, ignora este correo.</p>
            </td>
          </tr>
          <tr>
            <td style="background:#f9fafb;color:#6b7280;padding:16px 28px;font-size:12px;">
              © {os.getenv('APP_NAME','Pedidos App')}
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
