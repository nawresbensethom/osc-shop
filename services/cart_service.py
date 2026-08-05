from __future__ import annotations

from decimal import Decimal

from extensions import db
from models import CartItem, Order, OrderItem, Product


def cart_total(items: list[CartItem]) -> Decimal:
    return sum((Decimal(str(item.product.price)) * item.quantity for item in items), Decimal("0.00"))


def add_to_cart(user_id: int, product_id: int, quantity: int) -> CartItem:
    item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(item)
    return item


def remove_from_cart(user_id: int, item_id: int) -> None:
    item = db.session.get(CartItem, item_id)
    if item and item.user_id == user_id:
        db.session.delete(item)


def checkout_cart(user_id: int, customer_name: str, customer_email: str, shipping_address: str, notes: str):
    items = CartItem.query.filter_by(user_id=user_id).all()
    order = Order(
        user_id=user_id,
        customer_name=customer_name,
        customer_email=customer_email,
        shipping_address=shipping_address,
        notes=notes,
        status="completed",
    )
    db.session.add(order)
    db.session.flush()
    total = Decimal("0.00")
    for cart_item in items:
        line_total = Decimal(str(cart_item.product.price)) * cart_item.quantity
        db.session.add(
            OrderItem(
                order_id=order.id,
                product_id=cart_item.product.id,
                product_name=cart_item.product.name,
                unit_price=cart_item.product.price,
                quantity=cart_item.quantity,
                line_total=line_total,
            )
        )
        total += line_total
        db.session.delete(cart_item)
    order.total_amount = total
    return order
