from __future__ import annotations

from flask import Flask

from routes.admin import admin_bp
from routes.api import api_bp
from routes.auth import auth_bp
from routes.cart import cart_bp
from routes.catalog import catalog_bp
from routes.main import main_bp
from routes.orders import orders_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(main_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")
