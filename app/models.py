from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    """
    User model for authentication.
    """

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    display_name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ==========================
    # PASSWORD METHODS
    # ==========================

    def set_password(self, password):
        """
        Hash and store the user's password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verify the user's password.
        """
        return check_password_hash(
            self.password_hash,
            password
        )

    # ==========================
    # REPRESENTATION
    # ==========================

    def __repr__(self):
        return (
            f"<User "
            f"id={self.id} "
            f"username='{self.username}'>"
        )