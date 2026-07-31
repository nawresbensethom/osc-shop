from __future__ import annotations

from extensions import db
from models.mixins import TimestampMixin


class Review(TimestampMixin, db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False, default=5)
    title = db.Column(db.String(120), nullable=False, default="")
    body = db.Column(db.Text, nullable=False, default="")
    is_approved = db.Column(db.Boolean, nullable=False, default=True)

    product = db.relationship("Product", back_populates="reviews")
    user = db.relationship("User", back_populates="reviews")

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "title": self.title,
            "body": self.body,
            "is_approved": self.is_approved,
        }
