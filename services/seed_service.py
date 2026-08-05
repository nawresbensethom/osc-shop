from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from secrets import token_hex

from flask import Flask

from extensions import db
from models import CartItem, Order, OrderItem, Product, Review, User


def _create_user(username: str, email: str, password: str, role: str = "user", full_name: str = "") -> User:
    user = User(username=username, email=email, role=role, full_name=full_name or username.title())
    user.set_password(password)
    return user


def seed_demo_data(app: Flask) -> None:
    if User.query.first() or Product.query.first():
        return

    admin = _create_user("admin", "admin@osc-shop.local", "Admin123!", "admin", "OSC Administrator")
    users = [
        _create_user(f"user{i}", f"user{i}@osc-shop.local", "User123!", "user", f"User {i}")
        for i in range(1, 6)
    ]

    products = []
    for index in range(1, 21):
        product = Product(
            name=f"Produit Démo {index}",
            short_description=f"Produit de démonstration numéro {index}",
            description=f"Description longue du produit démo {index}.",
            category="Demo",
            price=Decimal(f"{19 + index}.90"),
            stock=10 + index,
            image_url=f"https://via.placeholder.com/640x420?text=Produit+{index}",
        )
        products.append(product)

    db.session.add(admin)
    db.session.add_all(users + products)
    db.session.flush()

    reviews = []
    for index, product in enumerate(products[:10], start=1):
        reviews.append(
            Review(
                product_id=product.id,
                user_id=users[(index - 1) % len(users)].id,
                rating=((index - 1) % 5) + 1,
                title=f"Avis {index}",
                body=f"Avis démo pour {product.name}.",
            )
        )

    orders = []
    for index in range(1, 11):
        user = users[(index - 1) % len(users)]
        order = Order(
            order_number=token_hex(8),
            user_id=user.id,
            status="completed" if index % 2 == 0 else "pending",
            customer_name=user.full_name,
            customer_email=user.email,
            shipping_address="123 Demo Street, Demo City",
            total_amount=Decimal("0.00"),
            created_at=datetime.now(timezone.utc) - timedelta(days=index),
        )
        item_product = products[(index - 1) % len(products)]
        item = OrderItem(
            product_id=item_product.id,
            product_name=item_product.name,
            unit_price=item_product.price,
            quantity=1 + (index % 3),
            line_total=Decimal(item_product.price) * (1 + (index % 3)),
        )
        order.items.append(item)
        order.recalculate_total()
        orders.append(order)

    cart_item = CartItem(user_id=users[0].id, product_id=products[0].id, quantity=2)

    db.session.add_all(reviews + orders + [cart_item])
    db.session.commit()
