from flask import Blueprint

profile = Blueprint("profile", __name__)


@profile.route("/profile")
def profile_home():
    return "Profile blueprint"
