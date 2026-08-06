from flask import (
    abort,
    render_template,
)

from flask_login import (
    current_user,
    login_required,
)

from app.models import (
    Follow,
    User,
    Poem,
    Note,
)

from . import profile


# ==========================================
# PUBLIC PROFILE
# ==========================================

@profile.route("/u/<string:username>")
@login_required
def public_profile(username):

    profile_user = User.query.filter_by(
        username=username,
    ).first()

    if profile_user is None:
        abort(404)

    public_poems = (
        Poem.query.filter_by(
            user_id=profile_user.id,
            is_public=True,
        )
        .order_by(
            Poem.created_at.desc()
        )
        .all()
    )

    public_notes = (
        Note.query.filter_by(
            user_id=profile_user.id,
            is_public=True,
        )
        .order_by(
            Note.created_at.desc()
        )
        .all()
    )

    blooms = sorted(
        public_poems + public_notes,
        key=lambda bloom: bloom.created_at,
        reverse=True,
    )

    for bloom in blooms:
        bloom.is_cherished = any(
            cherish.user_id == current_user.id
            for cherish in bloom.cherishes
        )

    followers_count = Follow.query.filter_by(
        following_id=profile_user.id,
    ).count()
    following_count = Follow.query.filter_by(
        follower_id=profile_user.id,
    ).count()
    is_following = False

    if current_user.id != profile_user.id:
        is_following = Follow.query.filter_by(
            follower_id=current_user.id,
            following_id=profile_user.id,
        ).first() is not None

    cherish_count = 0
    for bloom in public_poems + public_notes:
        cherish_count += len(bloom.cherishes)

    stats = {
        "public_poems": len(public_poems),
        "public_notes": len(public_notes),
    }

    return render_template(
        "profile/public_profile.html",
        user=profile_user,
        blooms=blooms,
        stats=stats,
        followers_count=followers_count,
        following_count=following_count,
        cherish_count=cherish_count,
        is_following=is_following,
    )


# ==========================================
# FOLLOWERS PAGE
# ==========================================

@profile.route("/u/<string:username>/followers")
@login_required
def followers(username):

    user = User.query.filter_by(
        username=username,
    ).first_or_404()

    followers = (
        User.query
        .join(Follow, Follow.follower_id == User.id)
        .filter(Follow.following_id == user.id)
        .all()
    )

    return render_template(
        "profile/followers.html",
        user=user,
        followers=followers,
    )


# ==========================================
# FOLLOWING PAGE
# ==========================================

@profile.route("/u/<string:username>/following")
@login_required
def following(username):

    user = User.query.filter_by(
        username=username,
    ).first_or_404()

    following = (
        User.query
        .join(Follow, Follow.following_id == User.id)
        .filter(Follow.follower_id == user.id)
        .all()
    )

    return render_template(
        "profile/following.html",
        user=user,
        following=following,
    )