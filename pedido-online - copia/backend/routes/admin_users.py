from flask import Blueprint, request, jsonify, session
import re
from backend.services.user_service import list_users, create_user, update_user, delete_user

admin_users_bp = Blueprint("admin_users", __name__)

EMAIL_RX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def _is_admin() -> bool:
    rol = session.get("rol") or session.get("role")
    if isinstance(rol, str) and rol:
        return rol.lower() in {"admin", "administrador"}
    id_rol = session.get("id_rol")
    try:
        return int(id_rol) == 1
    except Exception:
        return False

def _valid_email(s: str) -> bool:
    return bool(EMAIL_RX.match((s or "").strip()))

def _strong_pass(p: str) -> bool:
    if not p or len(p) < 8:
        return False
    has_u = re.search(r"[A-Z]", p) is not None
    has_l = re.search(r"[a-z]", p) is not None
    has_d = re.search(r"[0-9]", p) is not None
    has_s = re.search(r"[^A-Za-z0-9]", p) is not None
    return has_u and has_l and has_d and has_s

@admin_users_bp.route("/api/admin/users", methods=["GET", "POST", "OPTIONS"])
def users_collection():
    if request.method == "OPTIONS":
        return ("", 204)
    if not _is_admin():
        return jsonify({"mensaje": "No autorizado"}), 403

    if request.method == "GET":
        q = request.args.get("q", "").strip()
        role = request.args.get("role")
        try:
            role_id = int(role) if role else None
        except Exception:
            role_id = None
        return jsonify(list_users(q or None, role_id))

    data = request.get_json(silent=True) or {}
    nombre = (data.get("nombre") or "").strip()
    email  = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()
    try:
        id_rol = int(data.get("id_rol") or 2)
    except Exception:
        id_rol = 2

    if not nombre or not email:
        return jsonify({"mensaje": "Nombre y correo son obligatorios"}), 400
    if not _valid_email(email):
        return jsonify({"mensaje": "Correo inválido"}), 400
    if not password:
        return jsonify({"mensaje": "La contraseña es obligatoria"}), 400
    if not _strong_pass(password):
        return jsonify({"mensaje": "Contraseña insegura. Usa 8+ caracteres con mayúsculas, minúsculas, números y símbolo."}), 400

    err = create_user(nombre, email, password, id_rol)
    if err:
        return jsonify({"mensaje": err}), 400
    return jsonify({"mensaje": "Usuario creado"}), 201

@admin_users_bp.route("/api/admin/users/<int:user_id>", methods=["PUT", "PATCH", "DELETE", "OPTIONS"])
def users_item(user_id: int):
    if request.method == "OPTIONS":
        return ("", 204)
    if not _is_admin():
        return jsonify({"mensaje": "No autorizado"}), 403

    if request.method in ("PUT", "PATCH"):
        data = request.get_json(silent=True) or {}
        nombre = (data.get("nombre") or "").strip()
        email  = (data.get("email") or "").strip().lower()
        password = (data.get("password") or "").strip()
        try:
            id_rol = int(data.get("id_rol") or 2)
        except Exception:
            id_rol = 2

        if not nombre or not email:
            return jsonify({"mensaje": "Nombre y correo son obligatorios"}), 400
        if not _valid_email(email):
            return jsonify({"mensaje": "Correo inválido"}), 400
        if password and not _strong_pass(password):
            return jsonify({"mensaje": "Contraseña insegura. Usa 8+ caracteres con mayúsculas, minúsculas, números y símbolo."}), 400

        err = update_user(user_id, nombre, email, password if password else None, id_rol)
        if err:
            return jsonify({"mensaje": err}), 400
        return jsonify({"mensaje": "Usuario actualizado"})

    err = delete_user(user_id)
    if err:
        return jsonify({"mensaje": err}), 404
    return jsonify({"mensaje": "Usuario eliminado"})
