from __future__ import annotations

from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, url_for, current_app
from flask_login import current_user, login_required

from extensions import db
from forms.cart import CartAddForm, CheckoutForm
from models import CartItem, Order, OrderItem, Product
from utils.logging import log_event

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


def _cart_items():
    return CartItem.query.filter_by(user_id=current_user.id).all()


@cart_bp.route("/")
@login_required
def view_cart():
    items = _cart_items()
    total = sum((Decimal(str(item.product.price)) * item.quantity for item in items), Decimal("0.00"))
    return render_template("cart/view.html", items=items, total=total, form=CheckoutForm())


@cart_bp.route("/add/<int:product_id>", methods=["POST"])
@login_required
def add(product_id: int):
    form = CartAddForm()
    if not form.validate_on_submit():
        return redirect(url_for("catalog.product_detail", product_id=product_id))
    product = db.session.get(Product, product_id)
    if not product or not product.is_active:
        flash("Produit indisponible.", "warning")
        return redirect(url_for("catalog.list_products"))
    quantity = max(1, int(form.quantity.data or 1))
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=current_user.id, product_id=product.id, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    log_event(current_app.logger, "cart_add")
    flash("Produit ajouté au panier.", "success")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/remove/<int:item_id>", methods=["POST"])
@login_required
def remove(item_id: int):
    item = db.session.get(CartItem, item_id)
    if item and item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        log_event(current_app.logger, "cart_remove")
        flash("Article supprimé du panier.", "info")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    form = CheckoutForm()
    if form.validate_on_submit():
        items = _cart_items()
        if not items:
            flash("Le panier est vide.", "warning")
            return redirect(url_for("cart.view_cart"))
        order = Order(
            user_id=current_user.id,
            customer_name=form.customer_name.data,
            customer_email=form.customer_email.data,
            shipping_address=form.shipping_address.data,
            notes=form.notes.data,
            status="completed",
        )
        db.session.add(order)
        db.session.flush()
        total = Decimal("0.00")
        for item in items:
            line_total = Decimal(str(item.product.price)) * item.quantity
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product.id,
                product_name=item.product.name,
                unit_price=item.product.price,
                quantity=item.quantity,
                line_total=line_total,
            )
            db.session.add(order_item)
            total += line_total
            db.session.delete(item)
        order.total_amount = total
        db.session.commit()
        log_event(current_app.logger, f"order_created:{order.order_number}")
        flash("Commande fictive enregistrée.", "success")
        return redirect(url_for("orders.history"))
    return redirect(url_for("cart.view_cart"))
