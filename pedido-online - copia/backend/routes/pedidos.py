from flask import Blueprint, request, jsonify, session
from backend.services.order_service import create_order

pedidos_bp = Blueprint("pedidos", __name__)

@pedidos_bp.route("", methods=["POST"])
def crear_pedido():
    user_id = session.get("user_id") or session.get("id_usuario")
    if not user_id:
        return jsonify({"mensaje": "No autenticado"}), 401
    data = request.get_json(silent=True) or {}
    items = data.get("items") or data.get("productos") or []
    result, err = create_order(int(user_id), items)
    if err:
        return jsonify({"mensaje": err}), 400
    return jsonify({"mensaje": "Pedido creado", "pedido": result}), 201
