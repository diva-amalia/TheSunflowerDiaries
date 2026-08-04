import config
from app import create_app
from app.extensions import db
from app.models import Follow, User


def _create_app_with_users():
    config.Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    app = create_app()
    app.config.update(TESTING=True)

    with app.app_context():
        db.drop_all()
        db.create_all()

        follower = User(
            username="follower",
            display_name="Follower One",
            email="follower@example.com",
        )
        follower.set_password("secret123")

        following = User(
            username="following",
            display_name="Following One",
            email="following@example.com",
        )
        following.set_password("secret123")

        db.session.add_all([follower, following])
        db.session.commit()

    return app, follower, following


def test_follow_and_unfollow_update_counters():
    app, _, _ = _create_app_with_users()

    with app.app_context():
        follower = User.query.filter_by(username="follower").first()
        following = User.query.filter_by(username="following").first()

    with app.test_client() as client:
        login_response = client.post(
            "/auth/login",
            data={
                "username_or_email": "follower",
                "password": "secret123",
            },
            follow_redirects=True,
        )
        assert login_response.status_code == 200

        follow_response = client.post(
            f"/follow/{following.id}",
            follow_redirects=True,
        )
        assert follow_response.status_code == 200
        assert Follow.query.filter_by(
            follower_id=follower.id,
            following_id=following.id,
        ).count() == 1

        profile_response = client.get(f"/u/{following.username}")
        assert profile_response.status_code == 200
        assert b"Followers" in profile_response.data
        assert b"Following" in profile_response.data

        unfollow_response = client.post(
            f"/unfollow/{following.id}",
            follow_redirects=True,
        )
        assert unfollow_response.status_code == 200
        assert Follow.query.filter_by(
            follower_id=follower.id,
            following_id=following.id,
        ).count() == 0


def test_cannot_follow_self_or_duplicate_follow():
    app, _, _ = _create_app_with_users()

    with app.app_context():
        follower = User.query.filter_by(username="follower").first()
        following = User.query.filter_by(username="following").first()

    with app.test_client() as client:
        client.post(
            "/auth/login",
            data={
                "username_or_email": "follower",
                "password": "secret123",
            },
            follow_redirects=True,
        )

        self_follow_response = client.post(
            f"/follow/{follower.id}",
            follow_redirects=True,
        )
        assert self_follow_response.status_code == 200
        assert Follow.query.filter_by(follower_id=follower.id).count() == 0

        first_follow_response = client.post(
            f"/follow/{following.id}",
            follow_redirects=True,
        )
        assert first_follow_response.status_code == 200

        second_follow_response = client.post(
            f"/follow/{following.id}",
            follow_redirects=True,
        )
        assert second_follow_response.status_code == 200
        assert Follow.query.filter_by(
            follower_id=follower.id,
            following_id=following.id,
        ).count() == 1
