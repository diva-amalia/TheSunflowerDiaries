from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from app.extensions import db
from app.models import User


auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


# ==========================
# LOGIN
# ==========================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("main.welcome"))

    if request.method == "GET":
        return render_template("auth/login.html")

    username_or_email = request.form.get(
        "username_or_email",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    user = User.query.filter(
        (User.username == username_or_email)
        |
        (User.email == username_or_email.lower())
    ).first()

    if user is None or not user.check_password(password):

        flash(
            "Invalid username/email or password.",
            "danger",
        )

        return redirect(
            url_for("auth.login")
        )

    login_user(user)

    flash(
        f"Welcome back, {user.display_name} 🌻",
        "success",
    )

    return redirect(
    url_for("main.welcome")
    )

# ==========================
# REGISTER
# ==========================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("auth/register.html")

    username = request.form.get("username", "").strip()
    display_name = request.form.get("display_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # ==========================
    # VALIDATION
    # ==========================

    if not username:
        flash("Username is required.", "danger")
        return redirect(url_for("auth.register"))

    if not display_name:
        flash("Display name is required.", "danger")
        return redirect(url_for("auth.register"))

    if not email:
        flash("Email is required.", "danger")
        return redirect(url_for("auth.register"))

    if len(password) < 8:
        flash("Password must be at least 8 characters.", "danger")
        return redirect(url_for("auth.register"))

    if password != confirm_password:
        flash("Passwords do not match.", "danger")
        return redirect(url_for("auth.register"))

    # ==========================
    # UNIQUE CHECK
    # ==========================

    existing_username = User.query.filter_by(
        username=username
    ).first()

    if existing_username:
        flash("Username already exists.", "danger")
        return redirect(url_for("auth.register"))

    existing_email = User.query.filter_by(
        email=email
    ).first()

    if existing_email:
        flash("Email is already registered.", "danger")
        return redirect(url_for("auth.register"))

    # ==========================
    # CREATE USER
    # ==========================

    user = User(
        username=username,
        display_name=display_name,
        email=email,
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    flash(
        "Account created successfully. Please sign in.",
        "success",
    )

    return redirect(url_for("auth.login"))

# ==========================
# LOGOUT
# ==========================

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("main.home")
    )