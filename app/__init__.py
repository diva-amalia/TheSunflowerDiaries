from flask import Flask

from app.auth.routes import auth
from app.main.routes import main
from app.note.routes import note
from app.poem.routes import poem
from app.profile.routes import profile


def create_app():
    app = Flask(__name__)

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(note)
    app.register_blueprint(poem)
    app.register_blueprint(profile)

    return app