from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, url_for, current_app
from flask_login import current_user, login_required

from extensions import db
from forms.product import ProductForm
from models import ContactMessage, Order, Product, Review, User
from utils.decorators import admin_required
from utils.logging import log_event

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "users": User.query.count(),
        "products": Product.query.count(),
        "orders": Order.query.count(),
        "reviews": Review.query.count(),
        "messages": ContactMessage.query.count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/products")
@login_required
@admin_required
def products():
    return render_template("admin/products.html", products=Product.query.order_by(Product.created_at.desc()).all())


@admin_bp.route("/products/new", methods=["GET", "POST"])
@login_required
@admin_required
def product_create():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            short_description=form.short_description.data,
            description=form.description.data,
            category=form.category.data,
            price=form.price.data,
            stock=form.stock.data,
            image_url=form.image_url.data,
        )
        db.session.add(product)
        db.session.commit()
        flash("Produit ajouté.", "success")
        return redirect(url_for("admin.products"))
    return render_template("admin/product_form.html", form=form, mode="create")


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def product_edit(product_id: int):
    product = db.session.get(Product, product_id)
    if not product:
        abort(404)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        form.populate_obj(product)
        db.session.commit()
        flash("Produit modifié.", "success")
        return redirect(url_for("admin.products"))
    return render_template("admin/product_form.html", form=form, mode="edit")


@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
@admin_required
def product_delete(product_id: int):
    product = db.session.get(Product, product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        log_event(current_app.logger, f"product_delete:{product_id}")
        flash("Produit supprimé.", "warning")
    return redirect(url_for("admin.products"))


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    return render_template("admin/users.html", users=User.query.order_by(User.created_at.desc()).all())


@admin_bp.route("/orders")
@login_required
@admin_required
def orders():
    return render_template("admin/orders.html", orders=Order.query.order_by(Order.created_at.desc()).all())


@admin_bp.route("/reviews")
@login_required
@admin_required
def reviews():
    return render_template("admin/reviews.html", reviews=Review.query.order_by(Review.created_at.desc()).all())


@admin_bp.route("/messages")
@login_required
@admin_required
def messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin/messages.html", messages=messages)


@admin_bp.route("/messages/<int:message_id>")
@login_required
@admin_required
def message_detail(message_id: int):
    message = db.session.get(ContactMessage, message_id)
    if not message:
        abort(404)
    return render_template("admin/message_detail.html", message=message)


@admin_bp.route("/messages/<int:message_id>/read", methods=["POST"])
@login_required
@admin_required
def message_mark_read(message_id: int):
    message = db.session.get(ContactMessage, message_id)
    if not message:
        abort(404)
    message.is_read = True
    message.status = "read"
    db.session.commit()
    flash("Message marqué comme lu.", "success")
    return redirect(url_for("admin.messages"))
