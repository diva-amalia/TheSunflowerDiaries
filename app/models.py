from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from app.extensions import db


class User(UserMixin, db.Model):
    """
    User model for authentication.
    """

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
    )

    display_name = db.Column(
        db.String(100),
        nullable=False,
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    bio = db.Column(
        db.String(250),
        nullable=True,
    )

    avatar = db.Column(
    db.String(255),
    nullable=True,
    )

    poems = db.relationship(
        "Poem",
        back_populates="author",
        cascade="all, delete-orphan",
        lazy=True,
    )

    notes = db.relationship(
        "Note",
        back_populates="author",
        cascade="all, delete-orphan",
        lazy=True,
    )
    cherishes = db.relationship(
    "Cherish",
    back_populates="user",
    cascade="all, delete-orphan",
)

    following = db.relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
        lazy=True,
    )

    followers = db.relationship(
        "Follow",
        foreign_keys="Follow.following_id",
        back_populates="following",
        cascade="all, delete-orphan",
        lazy=True,
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
            password,
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


class Poem(db.Model):
    """
    Poem model.
    """

    __tablename__ = "poems"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    title = db.Column(
        db.String(150),
        nullable=False,
    )

    content = db.Column(
        db.Text,
        nullable=False,
    )

    is_public = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    author = db.relationship(
        "User",
        back_populates="poems",
    )

    cherishes = db.relationship(
    "Cherish",
    back_populates="poem",
    cascade="all, delete-orphan",
)

    # ==========================
    # REPRESENTATION
    # ==========================

    def __repr__(self):
        return (
            f"<Poem "
            f"id={self.id} "
            f"title='{self.title}'>"
        )


class Note(db.Model):
    """
    Note model.
    """

    __tablename__ = "notes"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    title = db.Column(
        db.String(150),
        nullable=False,
    )

    content = db.Column(
        db.Text,
        nullable=False,
    )

    is_public = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    author = db.relationship(
        "User",
        back_populates="notes",
    )
    cherishes = db.relationship(
    "Cherish",
    back_populates="note",
    cascade="all, delete-orphan",
)


    # ==========================
    # REPRESENTATION
    # ==========================

    def __repr__(self):
        return (
            f"<Note "
            f"id={self.id} "
            f"title='{self.title}'>"
        )

class Follow(db.Model):
    """
    Follow relationship between users.
    """

    __tablename__ = "follows"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    follower_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    following_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    follower = db.relationship(
        "User",
        foreign_keys=[follower_id],
        back_populates="following",
    )

    following = db.relationship(
        "User",
        foreign_keys=[following_id],
        back_populates="followers",
    )

    def __repr__(self):
        return f"<Follow follower_id={self.follower_id} following_id={self.following_id}>"


class Cherish(db.Model):
    """
    Appreciation for poems or notes.
    """

    __tablename__ = "cherishes"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    poem_id = db.Column(
        db.Integer,
        db.ForeignKey("poems.id"),
        nullable=True,
    )

    note_id = db.Column(
        db.Integer,
        db.ForeignKey("notes.id"),
        nullable=True,
    )

    user = db.relationship(
        "User",
        back_populates="cherishes",
    )

    poem = db.relationship(
        "Poem",
        back_populates="cherishes",
    )

    note = db.relationship(
        "Note",
        back_populates="cherishes",
    )

    def __repr__(self):
        return f"<Cherish id={self.id}>"