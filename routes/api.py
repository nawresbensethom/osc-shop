from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_user

from extensions import csrf, db
from models import ContactMessage, Order, Product, User
from services.auth_backend import get_auth_backend
from services.demo_service import demo_flag
from utils.rate_limit import check_rate_limit

api_bp = Blueprint("api", __name__)


def _paginate(query, page: int, limit: int) -> tuple[list[object], int]:
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return items, total


@api_bp.route("/products")
def products():
    query = Product.query.filter_by(is_active=True)
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(max(1, request.args.get("limit", 20, type=int)), 100)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))

    query = query.order_by(Product.created_at.desc())
    items, total = _paginate(query, page, limit)
    return jsonify(
        {
            "items": [item.to_dict() for item in items],
            "meta": {"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit if total else 0},
        }
    )


@api_bp.route("/product/<int:product_id>")
def product_detail(product_id: int):
    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        return jsonify({"error": "not_found"}), 404
    return jsonify(product.to_dict())


@api_bp.route("/login", methods=["POST"])
@csrf.exempt
def login():
    payload = request.get_json(force=True, silent=True) or {}
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
    if not demo_flag("ENABLE_BRUTE_FORCE"):
        limit_result = check_rate_limit(
            f"api-login:{client_ip}",
            limit=5 if not demo_flag("ENABLE_RATE_LIMITING") else 3,
            window_seconds=60,
        )
        if not limit_result.allowed:
            return jsonify({"error": "rate_limited", "retry_after": limit_result.retry_after}), 429
    backend = get_auth_backend()
    user = backend.authenticate(payload.get("username", ""), payload.get("password", ""))
    if not user:
        if demo_flag("ENABLE_ENUMERATION"):
            known_user = User.query.filter((User.username == payload.get("username", "")) | (User.email == payload.get("username", ""))).first()
            if known_user:
                return jsonify({"error": "wrong_password"}), 401
            return jsonify({"error": "unknown_account"}), 401
        return jsonify({"error": "invalid_credentials"}), 401
    login_user(user)
    return jsonify({"message": "authenticated", "user": user.to_dict()})


@api_bp.route("/orders")
def orders():
    if not current_user.is_authenticated:
        return jsonify({"error": "unauthorized"}), 401
    page = max(1, request.args.get("page", 1, type=int))
    limit = min(max(1, request.args.get("limit", 20, type=int)), 100)
    query = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc())
    orders_list, total = _paginate(query, page, limit)
    return jsonify(
        {
            "items": [order.to_dict() for order in orders_list],
            "meta": {"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit if total else 0},
        }
    )


@api_bp.route("/profile")
def profile():
    if not current_user.is_authenticated:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(current_user.to_dict())


@api_bp.route("/profile", methods=["PUT"])
@csrf.exempt
def update_profile():
    if not current_user.is_authenticated:
        return jsonify({"error": "unauthorized"}), 401
    payload = request.get_json(force=True, silent=True) or {}
    current_user.full_name = payload.get("full_name", current_user.full_name)
    current_user.email = payload.get("email", current_user.email)
    current_user.bio = payload.get("bio", current_user.bio)
    db.session.commit()
    return jsonify({"message": "profile_updated", "user": current_user.to_dict()})


@api_bp.route("/contact", methods=["POST"])
@csrf.exempt
def contact():
    payload = request.get_json(force=True, silent=True) or {}
    message = ContactMessage(
        name=payload.get("name", ""),
        email=payload.get("email", ""),
        subject=payload.get("subject", ""),
        message=payload.get("message", ""),
    )
    if not all([message.name, message.email, message.subject, message.message]):
        return jsonify({"error": "invalid_payload"}), 400
    db.session.add(message)
    db.session.commit()
    return jsonify({"message": "contact_saved", "id": message.id}), 201


@api_bp.route("/health")
def health():
    return jsonify({"status": "ok"})
