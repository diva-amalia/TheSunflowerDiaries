from flask import Blueprint

note = Blueprint("note", __name__)


@note.route("/note")
def note_home():
    return "Note blueprint"
