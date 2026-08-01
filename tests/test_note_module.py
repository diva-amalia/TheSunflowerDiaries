import config
from app import create_app
from app.extensions import db
from app.models import Note, User


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
