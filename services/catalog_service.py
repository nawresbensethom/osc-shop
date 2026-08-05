from __future__ import annotations

from models import Product, Review


def search_products(term: str):
    query = Product.query.filter_by(is_active=True)
    if term:
        query = query.filter(Product.name.ilike(f"%{term}%"))
    return query.order_by(Product.created_at.desc())


def get_product_reviews(product_id: int):
    return Review.query.filter_by(product_id=product_id, is_approved=True).order_by(Review.created_at.desc()).all()
