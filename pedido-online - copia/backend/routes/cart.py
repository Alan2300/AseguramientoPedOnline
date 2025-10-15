from flask import Blueprint

cart_bp = Blueprint('cart_bp', __name__)

@cart_bp.route('/example')
def example():
    return "Módulo de carrito funcionando"
