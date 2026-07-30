from flask import Flask

from config import Config

from app.extensions import db, login_manager
from app.models import User

from app.main.routes import main
from app.auth.routes import auth
from app.note.routes import note
from app.poem.routes import poem
from app.profile.routes import profile


def create_app():
    """
    Create and configure the Flask application.
    """

    app = Flask(__name__)

    # ==========================
    # LOAD CONFIGURATION
    # ==========================

    app.config.from_object(Config)

    # ==========================
    # INITIALIZE EXTENSIONS
    # ==========================

    db.init_app(app)

    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    login_manager.login_message = (
        "Please sign in to continue."
    )

    login_manager.login_message_category = "info"

    # ==========================
    # USER LOADER
    # ==========================

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ==========================
    # REGISTER BLUEPRINTS
    # ==========================

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(note)
    app.register_blueprint(poem)
    app.register_blueprint(profile)

    # ==========================
    # CREATE DATABASE
    # ==========================

    with app.app_context():
        db.create_all()

    return app