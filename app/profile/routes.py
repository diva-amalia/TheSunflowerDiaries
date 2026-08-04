import os
from pathlib import Path
from uuid import uuid4

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Follow, Note, Poem, User


profile = Blueprint(
    "profile",
    __name__,
)

ALLOWED_AVATAR_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def _get_profile_user(user_id):

    user = User.query.get_or_404(user_id)

    if user.id != current_user.id:
        return None

    return user


def _get_avatar_upload_dir():
    upload_dir = Path(current_app.static_folder) / "uploads" / "avatars"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def _save_avatar(upload_file):
    if upload_file is None or upload_file.filename == "":
        return None

    filename = secure_filename(upload_file.filename)

    if not filename:
        return None

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_AVATAR_EXTENSIONS:
        return False

    upload_dir = _get_avatar_upload_dir()
    unique_filename = f"{uuid4().hex}{extension}"
    destination = upload_dir / unique_filename
    upload_file.save(destination)

    return os.path.join("uploads", "avatars", unique_filename).replace("\\", "/")


def _delete_avatar_file(relative_path):
    if not relative_path:
        return

    absolute_path = Path(current_app.static_folder) / relative_path

    if absolute_path.exists():
        absolute_path.unlink()


def _get_follow_status(current_user_obj, profile_user):
    if current_user_obj.id == profile_user.id:
        return False, False

    existing_follow = Follow.query.filter_by(
        follower_id=current_user_obj.id,
        following_id=profile_user.id,
    ).first()

    return existing_follow is not None, existing_follow is not None


def _get_follow_counts(user_id):
    followers_count = Follow.query.filter_by(following_id=user_id).count()
    following_count = Follow.query.filter_by(follower_id=user_id).count()
    return followers_count, following_count


def _get_cherishes_received_count(user_id):
    poem_count = db.session.query(Poem.id).filter_by(user_id=user_id).count()
    note_count = db.session.query(Note.id).filter_by(user_id=user_id).count()

    if poem_count == 0 and note_count == 0:
        return 0

    total_cherishes = 0

    poems = Poem.query.filter_by(user_id=user_id).all()
    notes = Note.query.filter_by(user_id=user_id).all()

    for poem in poems:
        total_cherishes += len(poem.cherishes)

    for note in notes:
        total_cherishes += len(note.cherishes)

    return total_cherishes


# ==========================
# PROFILE HOME
# ==========================

@profile.route("/profile")
@login_required
def index():

    user = _get_profile_user(current_user.id)

    if user is None:
        return redirect(url_for("garden.home"))

    poems = Poem.query.filter_by(
        user_id=user.id,
    ).order_by(
        Poem.created_at.desc(),
    ).all()

    notes = Note.query.filter_by(
        user_id=user.id,
    ).order_by(
        Note.created_at.desc(),
    ).all()

    followers_count, following_count = _get_follow_counts(user.id)
    cherishes_received = _get_cherishes_received_count(user.id)

    stats = {
        "total_poems": Poem.query.filter_by(user_id=user.id).count(),
        "total_notes": Note.query.filter_by(user_id=user.id).count(),
        "public_poems": Poem.query.filter_by(user_id=user.id, is_public=True).count(),
        "private_poems": Poem.query.filter_by(user_id=user.id, is_public=False).count(),
        "public_notes": Note.query.filter_by(user_id=user.id, is_public=True).count(),
        "private_notes": Note.query.filter_by(user_id=user.id, is_public=False).count(),
        "followers": followers_count,
        "following": following_count,
        "cherishes_received": cherishes_received,
    }

    return render_template(
        "profile/profile.html",
        user=user,
        poems=poems,
        notes=notes,
        stats=stats,
    )


# ==========================
# EDIT PROFILE
# ==========================

@profile.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():

    user = _get_profile_user(current_user.id)

    if user is None:
        return redirect(url_for("garden.home"))

    if request.method == "POST":

        display_name = request.form.get(
            "display_name",
            "",
        ).strip()

        username = request.form.get(
            "username",
            "",
        ).strip()

        bio = request.form.get(
            "bio",
            "",
        ).strip()

        if not display_name:
            flash(
                "Display name is required.",
                "warning",
            )
            return render_template(
                "profile/edit.html",
                user=user,
                display_name=display_name,
                username=username,
                bio=bio,
            )

        if not username:
            flash(
                "Username is required.",
                "warning",
            )
            return render_template(
                "profile/edit.html",
                user=user,
                display_name=display_name,
                username=username,
                bio=bio,
            )

        if len(username) > 50:
            flash(
                "Username must be 50 characters or fewer.",
                "warning",
            )
            return render_template(
                "profile/edit.html",
                user=user,
                display_name=display_name,
                username=username,
                bio=bio,
            )

        if len(bio) > 250:
            flash(
                "Bio must be 250 characters or fewer.",
                "warning",
            )
            return render_template(
                "profile/edit.html",
                user=user,
                display_name=display_name,
                username=username,
                bio=bio,
            )

        existing_user = User.query.filter(
            User.username == username,
            User.id != user.id,
        ).first()

        if existing_user is not None:
            flash(
                "That username is already taken.",
                "warning",
            )
            return render_template(
                "profile/edit.html",
                user=user,
                display_name=display_name,
                username=username,
                bio=bio,
            )

        avatar_file = request.files.get("avatar")
        avatar_upload = _save_avatar(avatar_file)

        if avatar_upload is False:
            flash(
                "Please choose a valid image file: PNG, JPG, JPEG, GIF, or WEBP.",
                "warning",
            )
            return render_template(
                "profile/edit.html",
                user=user,
                display_name=display_name,
                username=username,
                bio=bio,
            )

        if avatar_upload is not None:
            if user.avatar:
                _delete_avatar_file(user.avatar)
            user.avatar = avatar_upload

        user.display_name = display_name
        user.username = username
        user.bio = bio
        db.session.commit()

        flash(
            "🌻 Your profile has been updated.",
            "success",
        )

        return redirect(url_for("profile.index"))

    return render_template(
        "profile/edit.html",
        user=user,
        display_name=user.display_name,
        username=user.username,
        bio=user.bio or "",
    )



# ==========================
# PUBLIC PROFILE
# ==========================

@profile.route("/u/<string:username>")
@login_required
def public_profile(username):

    user = User.query.filter_by(
        username=username,
    ).first_or_404()

    poems = (
        Poem.query.filter_by(
            user_id=user.id,
            is_public=True,
        ).all()
    )

    notes = (
        Note.query.filter_by(
            user_id=user.id,
            is_public=True,
        ).all()
    )

    blooms = sorted(
        poems + notes,
        key=lambda bloom: bloom.created_at,
        reverse=True,
    )

    for bloom in blooms:
        bloom.is_cherished = any(
            cherish.user_id == current_user.id
            for cherish in bloom.cherishes
        )

    followers_count, following_count = _get_follow_counts(user.id)
    cherish_count = _get_cherishes_received_count(user.id)
    is_following = Follow.query.filter_by(
        follower_id=current_user.id,
        following_id=user.id,
    ).first() is not None

    stats = {
        "public_poems": len(poems),
        "public_notes": len(notes),
        "followers": followers_count,
        "following": following_count,
        "cherishes_received": cherish_count,
    }

    return render_template(
        "profile/public_profile.html",
        user=user,
        blooms=blooms,
        stats=stats,
        followers_count=followers_count,
        following_count=following_count,
        cherish_count=cherish_count,
        is_following=is_following,
    )


@profile.route("/follow/<int:user_id>", methods=["POST"])
@login_required
def follow_user(user_id):

    target_user = User.query.get(user_id)

    if target_user is None:
        flash("That user could not be found.", "warning")
        return redirect(url_for("explore.home"))

    if target_user.id == current_user.id:
        flash("You cannot follow yourself.", "warning")
        return redirect(url_for("profile.public_profile", username=target_user.username))

    existing_follow = Follow.query.filter_by(
        follower_id=current_user.id,
        following_id=target_user.id,
    ).first()

    if existing_follow is not None:
        flash("You are already following this person.", "warning")
        return redirect(url_for("profile.public_profile", username=target_user.username))

    follow = Follow(
        follower_id=current_user.id,
        following_id=target_user.id,
    )
    db.session.add(follow)
    db.session.commit()

    flash("🌻 You are now following this user.", "success")
    return redirect(url_for("profile.public_profile", username=target_user.username))


@profile.route("/unfollow/<int:user_id>", methods=["POST"])
@login_required
def unfollow_user(user_id):

    target_user = User.query.get(user_id)

    if target_user is None:
        flash("That user could not be found.", "warning")
        return redirect(url_for("explore.home"))

    follow = Follow.query.filter_by(
        follower_id=current_user.id,
        following_id=target_user.id,
    ).first()

    if follow is None:
        flash("You are not following this user.", "warning")
        return redirect(url_for("profile.public_profile", username=target_user.username))

    db.session.delete(follow)
    db.session.commit()

    flash("🌻 You have unfollowed this user.", "success")
    return redirect(url_for("profile.public_profile", username=target_user.username))