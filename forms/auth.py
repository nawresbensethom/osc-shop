from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from models import User


class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisateur ou email", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=8, max=128)])
    remember_me = BooleanField("Se souvenir de moi")


class RegisterForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    full_name = StringField("Nom complet", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField("Confirmer le mot de passe", validators=[DataRequired(), EqualTo("password")])

    def validate_username(self, field):  # noqa: D401
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Ce nom d'utilisateur est déjà utilisé.")

    def validate_email(self, field):  # noqa: D401
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Cet email est déjà utilisé.")


class ProfileForm(FlaskForm):
    full_name = StringField("Nom complet", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    bio = TextAreaField("Bio", validators=[Length(max=1000)])
