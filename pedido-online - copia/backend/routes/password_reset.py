from flask import Blueprint, request, jsonify
import os
import re
import bcrypt

from backend.services.password_reset_service import (
    create_reset_token,
    consume_reset_token,
    mark_token_used
)
from backend.services.email_service import send_email
from backend.services.email_templates import reset_password_email
from backend.database import SessionLocal
from backend.models.user import Usuario


password_reset_bp = Blueprint("password_reset", __name__)

_rx_lower = re.compile(r"[a-z]")
_rx_upper = re.compile(r"[A-Z]")
_rx_digit = re.compile(r"\d")
_rx_sym   = re.compile(r"[^\w\s]")  

def _password_is_strong(p: str) -> bool:
    return (
        isinstance(p, str) and len(p) >= 8 and
        _rx_lower.search(p) and
        _rx_upper.search(p) and
        _rx_digit.search(p) and
        _rx_sym.search(p)
    )


@password_reset_bp.route("/api/users/password/forgot", methods=["POST"])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"mensaje": "Correo requerido."}), 400

    user_info, raw_token = create_reset_token(email)

    if user_info and raw_token:
        base_url = os.getenv("FRONTEND_BASE_URL", "http://127.0.0.1:5500")
        ttl = int(os.getenv("RESET_TOKEN_TTL_MINUTES", "30"))
        link = f"{base_url}/frontend/reset_password.html?token={raw_token}"

        html = reset_password_email(user_info.get("nombre", ""), link, ttl)
        try:
            send_email(email, "Restablecer contraseña", html)
        except Exception as e:
            print("[EMAIL_ERROR]", repr(e))

    return jsonify({"mensaje": "Si el correo existe, se ha enviado un enlace para restablecer la contraseña."}), 200


@password_reset_bp.route("/api/users/password/reset", methods=["POST"])
def reset_password():
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()
    new_password = (data.get("new_password") or "").strip()

    if not token or not new_password:
        return jsonify({"mensaje": "Token y nueva contraseña son requeridos."}), 400

    if not _password_is_strong(new_password):
        return jsonify({
            "mensaje": "La contraseña debe tener al menos 8 caracteres e incluir minúscula, mayúscula, número y símbolo."
        }), 400

    token_info = consume_reset_token(token)
    if not token_info:
        return jsonify({"mensaje": "Token inválido o expirado."}), 400

    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.id_usuario == token_info["user_id"]).first()
        if not user:
            return jsonify({"mensaje": "Usuario no encontrado."}), 404

        hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user.password = hashed
        db.commit()

        mark_token_used(token_info["pr_id"])
        return jsonify({"mensaje": "Contraseña actualizada correctamente."}), 200
    except Exception:
        db.rollback()
        return jsonify({"mensaje": "No se pudo actualizar la contraseña."}), 500
    finally:
        db.close()
