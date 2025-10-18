import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from backend.routes.users import users_bp
from backend.routes.products import products_bp
from backend.routes.cart import cart_bp
from backend.routes.orders import orders_bp
from backend.routes.pedidos import pedidos_bp
from backend.routes.password_reset import password_reset_bp
from backend.routes.admin_orders import admin_orders_bp
from backend.routes.admin_users import admin_users_bp
from backend.routes.admin_reports import admin_reports_bp
un cam

#PruebaDeCambio


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "change-me-in-.env")

    default_origins = "http://127.0.0.1:5500,http://localhost:5500"
    allowed_origins = os.getenv("ALLOWED_ORIGINS", default_origins)
    origins_list = [o.strip() for o in allowed_origins.split(",")]
    CORS(
    app,
    resources={r"/api/*": {"origins": [o.strip() for o in allowed_origins.split(",")]}},
    supports_credentials=True
)

    app.config.update(SESSION_COOKIE_SAMESITE="Lax", SESSION_COOKIE_SECURE=False)

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    app.logger.setLevel(log_level)

    log_dir = os.getenv("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"), maxBytes=2000000, backupCount=3
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )
    app.logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    app.logger.addHandler(console_handler)

    @app.after_request
    def add_security_headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        return resp

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
        return send_from_directory(uploads_dir, filename)

    # Blueprints
    app.register_blueprint(users_bp,    url_prefix="/api/users")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(cart_bp,     url_prefix="/api/cart")
    app.register_blueprint(orders_bp,   url_prefix="/api/orders")
    app.register_blueprint(pedidos_bp,  url_prefix="/api/pedidos")
    app.register_blueprint(password_reset_bp)
    app.register_blueprint(admin_orders_bp, url_prefix="/api/admin")
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_reports_bp)




    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"message": "Solicitud inválida"}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"message": "No encontrado"}), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception("Error interno del servidor")
        return jsonify({"message": "Error interno del servidor"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=debug, host=host, port=port)
