from __future__ import annotations

from flask import Blueprint, abort, render_template, request, current_app
from flask_login import current_user, login_required

from extensions import db
from forms.cart import CartAddForm
from forms.review import ReviewForm
from models import Product, Review
from services.demo_service import demo_flag
from utils.logging import log_event

catalog_bp = Blueprint("catalog", __name__, url_prefix="/products")


@catalog_bp.route("/")
def list_products():
    query = request.args.get("q", "").strip()
    if query:
        log_event(current_app.logger, f"search:{query}")
    products = Product.query.filter_by(is_active=True)
    if query:
        products = products.filter(Product.name.ilike(f"%{query}%"))
    products = products.order_by(Product.created_at.desc()).all()
    return render_template("catalog/list.html", products=products, query=query)


@catalog_bp.route("/<int:product_id>")
def product_detail(product_id: int):
    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        abort(404)
    form = ReviewForm()
    reviews = Review.query.filter_by(product_id=product.id, is_approved=True).order_by(Review.created_at.desc()).all()
    return render_template(
        "catalog/detail.html",
        product=product,
        reviews=reviews,
        form=form,
        cart_form=CartAddForm(),
        demo_xss=demo_flag("ENABLE_XSS"),
        can_review=current_user.is_authenticated,
    )


@catalog_bp.route("/<int:product_id>/review", methods=["POST"])
@login_required
def add_review(product_id: int):
    product = db.session.get(Product, product_id)
    if not product:
        abort(404)
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            product_id=product.id,
            user_id=current_user.id,
            rating=form.rating.data,
            title=form.title.data,
            body=form.body.data,
        )
        db.session.add(review)
        db.session.commit()
    return render_template("catalog/review_success.html", product=product)
