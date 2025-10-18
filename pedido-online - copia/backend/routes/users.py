from flask import Blueprint, request, jsonify, session
import re
import uuid
import bcrypt
from backend.services.user_service import find_user_by_email, create_user

users_bp = Blueprint("users", __name__)

email_rx = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)

def validar_email(v):
    return isinstance(v, str) and email_rx.match(v.strip()) is not None

def validar_password(p):
    if not isinstance(p, str): return False
    if len(p) < 8: return False
    if not re.search(r"[a-z]", p): return False
    if not re.search(r"[A-Z]", p): return False
    if not re.search(r"\d", p): return False
    if not re.search(r"[^\w\s]", p): return False
    return True

@users_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json(silent=True) or {}
    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    id_rol = 2

    errores = {}
    if not nombre or len(nombre) < 2:
        errores["nombre"] = "Nombre requerido (mínimo 2 caracteres)."
    if not validar_email(email):
        errores["email"] = "Correo inválido."
    if not validar_password(password):
        errores["password"] = "La contraseña debe tener al menos 8 caracteres e incluir minúscula, mayúscula, número y símbolo."
    if errores:
        return jsonify({"errores": errores}), 400

    if find_user_by_email(email):
        return jsonify({"mensaje": "El correo ya está registrado."}), 409

    ok = create_user(nombre, email, password, id_rol)
    if not ok:
        return jsonify({"mensaje": "Error al registrar usuario."}), 500

    return jsonify({"mensaje": "Registro exitoso"}), 201

@users_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not validar_email(email) or not password:
        return jsonify({"mensaje": "Correo y contraseña son obligatorios y válidos."}), 400

    user = find_user_by_email(email)
    if user and bcrypt.checkpw(password.encode("utf-8"), (user["password"] or "").encode("utf-8")):
        session["user_id"] = user["id_usuario"]
        rol = "admin" if str(user.get("id_rol", "")) in {"1", "admin", "Administrador"} else "cliente"
        session["rol"] = rol
        session.permanent = True 

        token = f"fake-token-{uuid.uuid4()}"
        user_data = {
            "id_usuario": user["id_usuario"],
            "nombre": user["nombre"],
            "email": user["email"],
            "id_rol": user["id_rol"]
        }
        return jsonify({"mensaje": "Login correcto", "token": token, "usuario": user_data, "rol": rol}), 200

    return jsonify({"mensaje": "Credenciales incorrectas."}), 401

@users_bp.route("/me", methods=["GET"])
def me():
    uid = session.get("user_id")
    rol = session.get("rol")
    if not uid:
        return jsonify({"autenticado": False}), 200
    return jsonify({"autenticado": True, "user_id": uid, "rol": rol}), 200

@users_bp.route("/logout", methods=["POST"])
def logout_user():
    session.clear()
    return jsonify({"mensaje": "logout ok"}), 200
