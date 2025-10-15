from flask import Blueprint, jsonify, request, session
from backend.services.product_service import list_products, get_product, create_product, update_product, delete_product

products_bp = Blueprint("products", __name__)

def is_admin():
    rol = session.get("rol") or session.get("role") or session.get("user_role")
    return str(rol).lower() in {"admin", "administrador", "1"}

@products_bp.route("/list", methods=["GET"])
def products_list():
    return jsonify(list_products())

@products_bp.route("/<int:product_id>", methods=["GET"])
def products_get(product_id):
    p = get_product(product_id)
    if not p:
        return jsonify({"mensaje": "No encontrado"}), 404
    return jsonify(p)

@products_bp.route("", methods=["POST"])
def products_create():
    if not is_admin():
        return jsonify({"mensaje": "No autorizado"}), 403
    data = request.get_json(silent=True) or {}
    p = create_product(data)
    if not p:
        return jsonify({"mensaje": "No se pudo crear"}), 400
    return jsonify(p), 201

@products_bp.route("/<int:product_id>", methods=["PUT", "PATCH"])
def products_update(product_id):
    if not is_admin():
        return jsonify({"mensaje": "No autorizado"}), 403
    data = request.get_json(silent=True) or {}
    p = update_product(product_id, data)
    if not p:
        return jsonify({"mensaje": "No se pudo actualizar"}), 400
    return jsonify(p)

@products_bp.route("/<int:product_id>", methods=["DELETE"])
def products_delete(product_id):
    if not is_admin():
        return jsonify({"mensaje": "No autorizado"}), 403
    ok = delete_product(product_id)
    if not ok:
        return jsonify({"mensaje": "No se pudo eliminar"}), 400
    return jsonify({"ok": True})
