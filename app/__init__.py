
from app.models import User

from flask import Flask

from config import Config

from app.extensions import db, login_manager

from app.auth.routes import auth
from app.main.routes import main
from app.note.routes import note
from app.poem.routes import poem
from app.profile.routes import profile


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(note)
    app.register_blueprint(poem)
    app.register_blueprint(profile)

    return app