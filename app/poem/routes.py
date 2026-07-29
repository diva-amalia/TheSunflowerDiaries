from flask import Blueprint

poem = Blueprint("poem", __name__)


@poem.route("/poem")
def poem_home():
    return "Poem blueprint"
