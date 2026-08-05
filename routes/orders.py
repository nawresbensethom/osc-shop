from __future__ import annotations

from flask import Blueprint, abort, render_template
from flask_login import login_required, current_user

from extensions import db
from models import Order

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


@orders_bp.route("/")
@login_required
def history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("orders/history.html", orders=orders)


@orders_bp.route("/<int:order_id>")
@login_required
def detail(order_id: int):
    order = db.session.get(Order, order_id)
    if not order or order.user_id != current_user.id:
        abort(404)
    return render_template("orders/detail.html", order=order)
