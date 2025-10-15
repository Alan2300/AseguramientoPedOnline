from flask import Blueprint, jsonify, session, request
from backend.services.order_service import list_orders_by_user

orders_bp = Blueprint("orders", __name__)

@orders_bp.route("/mine", methods=["GET", "OPTIONS"])
def my_orders():
    if request.method == "OPTIONS":
        return ("", 204)

    user_id = session.get("user_id") or session.get("id_usuario")
    if not user_id:
        return jsonify({"mensaje": "No autenticado"}), 401

    try:
        uid = int(user_id)
    except Exception:
        return jsonify({"mensaje": "Usuario inválido"}), 400

    return jsonify(list_orders_by_user(uid))
