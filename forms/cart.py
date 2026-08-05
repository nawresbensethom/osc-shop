from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, NumberRange


class CheckoutForm(FlaskForm):
    customer_name = StringField("Nom", validators=[DataRequired(), Length(max=120)])
    customer_email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    shipping_address = TextAreaField("Adresse", validators=[DataRequired(), Length(max=500)])
    notes = TextAreaField("Notes", validators=[Length(max=1000)])


class CartAddForm(FlaskForm):
    quantity = IntegerField("Quantité", validators=[DataRequired(), NumberRange(min=1, max=99)], default=1)
