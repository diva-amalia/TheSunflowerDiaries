

from flask import Flask
from sqlalchemy import inspect, text

from config import Config

from app.extensions import db, login_manager
from app.models import Note, User

from app.main.routes import main
from app.auth.routes import auth
from app.garden.routes import garden
from app.note.routes import note
from app.poem.routes import poem
from app.profile.routes import profile
from app.explore import explore
from app.cherish import cherish


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
    app.register_blueprint(garden)
    app.register_blueprint(note)
    app.register_blueprint(poem)
    app.register_blueprint(profile)
    app.register_blueprint(explore)
    app.register_blueprint(cherish)
    

    # ==========================
    # CREATE DATABASE
    # ==========================

    with app.app_context():
        db.create_all()

        inspector = inspect(db.engine)

        if "notes" in inspector.get_table_names():
            columns = {
                column["name"]
                for column in inspector.get_columns("notes")
            }

            if "is_public" not in columns:
                with db.engine.begin() as connection:
                    connection.execute(
                        text(
                            "ALTER TABLE notes ADD COLUMN is_public BOOLEAN NOT NULL DEFAULT 0"
                        )
                    )

        if "users" in inspector.get_table_names():
            columns = {
                column["name"]
                for column in inspector.get_columns("users")
            }

            if "bio" not in columns:
                with db.engine.begin() as connection:
                    connection.execute(
                        text(
                            "ALTER TABLE users ADD COLUMN bio VARCHAR(250)"
                        )
                    )

    return app