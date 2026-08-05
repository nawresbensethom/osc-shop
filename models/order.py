from __future__ import annotations

from decimal import Decimal
from secrets import token_hex

from extensions import db
from models.mixins import TimestampMixin


class Order(TimestampMixin, db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(32), unique=True, nullable=False, default=lambda: token_hex(8))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="pending")
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    customer_name = db.Column(db.String(120), nullable=False, default="")
    customer_email = db.Column(db.String(120), nullable=False, default="")
    shipping_address = db.Column(db.Text, nullable=False, default="")
    notes = db.Column(db.Text, nullable=False, default="")

    user = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def recalculate_total(self) -> None:
        self.total_amount = sum((item.line_total for item in self.items), Decimal("0.00"))

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "order_number": self.order_number,
            "status": self.status,
            "total_amount": float(self.total_amount),
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "items": [item.to_dict() for item in self.items],
        }


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    product_name = db.Column(db.String(140), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    line_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "unit_price": float(self.unit_price),
            "quantity": self.quantity,
            "line_total": float(self.line_total),
        }
