from __future__ import annotations

from extensions import db
from models.mixins import TimestampMixin
from utils.text import slugify


class Product(TimestampMixin, db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False, index=True)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    short_description = db.Column(db.String(255), nullable=False, default="")
    description = db.Column(db.Text, nullable=False, default="")
    category = db.Column(db.String(80), nullable=False, default="General")
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(255), nullable=False, default="https://via.placeholder.com/640x420?text=OSC+Shop")
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    reviews = db.relationship("Review", back_populates="product", cascade="all, delete-orphan")
    order_items = db.relationship("OrderItem", back_populates="product")
    cart_items = db.relationship("CartItem", back_populates="product", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        name = kwargs.get("name")
        if name and not kwargs.get("slug"):
            kwargs["slug"] = slugify(name)
        super().__init__(**kwargs)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "short_description": self.short_description,
            "description": self.description,
            "category": self.category,
            "price": float(self.price),
            "stock": self.stock,
            "image_url": self.image_url,
            "is_active": self.is_active,
        }
