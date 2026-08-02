from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, url_for, current_app

from extensions import db
from forms.contact import ContactForm
from models import ContactMessage
from utils.logging import log_event

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        contact_message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data,
        )
        db.session.add(contact_message)
        db.session.commit()
        log_event(current_app.logger, "contact_message")
        flash("Votre message a été envoyé.", "success")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", form=form)
