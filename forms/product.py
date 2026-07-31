from __future__ import annotations

from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProductForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(max=140)])
    short_description = StringField("Courte description", validators=[DataRequired(), Length(max=255)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=5000)])
    category = StringField("Catégorie", validators=[DataRequired(), Length(max=80)])
    price = DecimalField("Prix", validators=[DataRequired(), NumberRange(min=0)], places=2, default=Decimal("0.00"))
    stock = IntegerField("Stock", validators=[DataRequired(), NumberRange(min=0)])
    image_url = StringField("Image", validators=[Optional(), Length(max=255)])
