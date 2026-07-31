from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange


class ReviewForm(FlaskForm):
    rating = IntegerField("Note", validators=[DataRequired(), NumberRange(min=1, max=5)])
    title = StringField("Titre", validators=[DataRequired(), Length(max=120)])
    body = TextAreaField("Avis", validators=[DataRequired(), Length(max=5000)])
