import random

from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
)

main = Blueprint(
    "main",
    __name__,
    template_folder="../templates",
)
from flask import (
    abort,
    render_template,
)

# ==========================
# LANDING PAGE
# ==========================

@main.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================
# BEGIN JOURNEY
# ==========================

@main.route("/begin")
def begin_journey():

    if current_user.is_authenticated:

        return redirect(
            url_for("main.welcome")
        )

    return redirect(
        url_for("auth.login")
    )


# ==========================
# WELCOME PAGE
# ==========================

@main.route("/welcome")
@login_required
def welcome():

    verses = [

        [
            "Some words never ask",
            "to be remembered.",
            "They only hope",
            "to be written.",
        ],

        [
            "Every poem begins",
            "as a seed.",
            "Write gently.",
            "",
        ],

        [
            "The quietest gardens",
            "often bloom",
            "with the deepest stories.",
            "",
        ],

        [
            "Welcome home.",
            "Your words have been",
            "waiting for you.",
            "",
        ],

        [
            "Some flowers bloom",
            "without asking",
            "to be seen.",
            "",
        ],

    ]

    verse = random.choice(verses)

    return render_template(
        "welcome/welcome.html",
        verse=verse,
    )
# ==========================
# PUBLIC PROFILE
# ==========================

from flask import abort

from app.models import User


