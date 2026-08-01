from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Note, Poem, User


profile = Blueprint(
    "profile",
    __name__,
)


def _get_profile_user(user_id):

    user = User.query.get_or_404(user_id)

    if user.id != current_user.id:
        return None

    return user


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

    stats = {
        "total_poems": Poem.query.filter_by(user_id=user.id).count(),
        "total_notes": Note.query.filter_by(user_id=user.id).count(),
        "public_poems": Poem.query.filter_by(user_id=user.id, is_public=True).count(),
        "private_poems": Poem.query.filter_by(user_id=user.id, is_public=False).count(),
        "public_notes": Note.query.filter_by(user_id=user.id, is_public=True).count(),
        "private_notes": Note.query.filter_by(user_id=user.id, is_public=False).count(),
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

        bio = request.form.get(
            "bio",
            ""
        ).strip()

        if len(bio) > 250:
            flash(
                "Bio must be 250 characters or fewer.",
                "warning",
            )
            return render_template(
                "profile/edit.html",
                user=user,
                bio=bio,
            )

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

    stats = {
        "public_poems": len(poems),
        "public_notes": len(notes),
    }

    return render_template(
        "profile/public_profile.html",
        user=user,
        blooms=blooms,
        stats=stats,
    )