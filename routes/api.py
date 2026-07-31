from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_login import current_user
from flask_login import login_user

from extensions import csrf, db
from models import Order, Product
from services.auth_backend import get_auth_backend

api_bp = Blueprint("api", __name__)


@api_bp.route("/products")
def products():
    items = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).all()
    return jsonify([item.to_dict() for item in items])


@api_bp.route("/product/<int:product_id>")
def product_detail(product_id: int):
    product = db.session.get(Product, product_id)
    return (jsonify(product.to_dict()), 200) if product else (jsonify({"error": "not_found"}), 404)


@api_bp.route("/login", methods=["POST"])
@csrf.exempt
def login():
    payload = request.get_json(force=True, silent=True) or {}
    backend = get_auth_backend()
    user = backend.authenticate(payload.get("username", ""), payload.get("password", ""))
    if not user:
        return jsonify({"error": "invalid_credentials"}), 401
    login_user(user)
    return jsonify({"message": "authenticated", "user": user.to_dict()})


@api_bp.route("/orders")
def orders():
    if not current_user.is_authenticated:
        return jsonify({"error": "unauthorized"}), 401
    orders_list = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders_list])


@api_bp.route("/profile")
def profile():
    if not current_user.is_authenticated:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(current_user.to_dict())
