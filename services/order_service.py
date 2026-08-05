from __future__ import annotations

from models import Order


def user_orders(user_id: int):
    return Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
