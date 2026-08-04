import io
import os

import config
from app import create_app
from app.extensions import db
from app.models import Cherish, Note, Poem, User


def test_note_crud_flow():
    config.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    app = create_app()
    app.config.update(TESTING=True)

    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(
            username="noter",
            display_name="Note Reader",
            email="note@example.com",
        )
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()

    with app.test_client() as client:
        login_response = client.post(
            "/auth/login",
            data={
                "username_or_email": "noter",
                "password": "secret123",
            },
            follow_redirects=True,
        )
        assert login_response.status_code == 200

        create_response = client.post(
            "/note/new",
            data={
                "title": "A calm note",
                "content": "A quiet thought for the garden.",
                "visibility": "private",
            },
            follow_redirects=True,
        )
        assert create_response.status_code == 200
        assert b"Your note has been safely kept." in create_response.data

        notes_response = client.get("/note/")
        assert notes_response.status_code == 200
        assert b"A calm note" in notes_response.data

        note = Note.query.filter_by(title="A calm note").first()
        assert note is not None

        view_response = client.get(f"/note/{note.id}")
        assert view_response.status_code == 200
        assert b"A calm note" in view_response.data

        update_response = client.post(
            f"/note/{note.id}/edit",
            data={
                "title": "Updated note",
                "content": "A softer thought now.",
                "visibility": "public",
            },
            follow_redirects=True,
        )
        assert update_response.status_code == 200
        assert b"Your note has been updated." in update_response.data

        delete_response = client.post(
            f"/note/{note.id}/remove",
            follow_redirects=True,
        )
        assert delete_response.status_code == 200
        assert b"Your note has been removed." in delete_response.data
        assert Note.query.count() == 0


def test_public_profile_shows_cherish_state_for_blooms():
    config.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    username = "bloomuser"

    app = create_app()
    app.config.update(TESTING=True)

    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(
            username=username,
            display_name="Bloom User",
            email="bloom@example.com",
        )
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()

        poem = Poem(
            title="A blooming poem",
            content="A lovely bloom for the public profile.",
            is_public=True,
            user_id=user.id,
        )
        db.session.add(poem)
        db.session.commit()

        db.session.add(
            Cherish(
                user_id=user.id,
                poem_id=poem.id,
            )
        )
        db.session.commit()

    with app.test_client() as client:
        login_response = client.post(
            "/auth/login",
            data={
                "username_or_email": username,
                "password": "secret123",
            },
            follow_redirects=True,
        )
        assert login_response.status_code == 200

        response = client.get(f"/u/{username}")
        assert response.status_code == 200
        assert b"cherish-form" in response.data
        assert b"Read" in response.data
        assert "💛" in response.get_data(as_text=True)


def test_profile_edit_uploads_avatar_and_updates_profile_fields():
    config.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    app = create_app()
    app.config.update(TESTING=True)

    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(
            username="sunflower",
            display_name="Sunflower Girl",
            email="sunflower@example.com",
        )
        user.set_password("secret123")
        db.session.add(user)
        db.session.commit()

    with app.test_client() as client:
        login_response = client.post(
            "/auth/login",
            data={
                "username_or_email": "sunflower",
                "password": "secret123",
            },
            follow_redirects=True,
        )
        assert login_response.status_code == 200

        image_data = b"fake-image-data"
        avatar_file = (
            io.BytesIO(image_data),
            "avatar.png",
        )

        edit_response = client.post(
            "/profile/edit",
            data={
                "display_name": "Sunflower Muse",
                "username": "musegarden",
                "bio": "A gentle gardener.",
                "avatar": avatar_file,
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        assert edit_response.status_code == 200
        assert b"Your profile has been updated." in edit_response.data

        updated_user = User.query.filter_by(username="musegarden").first()
        assert updated_user is not None
        assert updated_user.display_name == "Sunflower Muse"
        assert updated_user.bio == "A gentle gardener."
        assert updated_user.avatar is not None
        assert updated_user.avatar.endswith(".png")

        avatar_path = os.path.join(
            app.static_folder,
            updated_user.avatar,
        )
        assert os.path.exists(avatar_path)
