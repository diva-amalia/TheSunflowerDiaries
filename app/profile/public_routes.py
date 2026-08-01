from flask import (
    abort,
    render_template,
)

from flask_login import login_required

from app.models import (
    User,
    Poem,
    Note,
)

from . import profile


# ==========================
# PUBLIC PROFILE
# ==========================

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

    stats = {

        "poems": len(public_poems),

        "notes": len(public_notes),

    }

    return render_template(

        "profile/public_profile.html",

        user=profile_user,

        poems=public_poems,

        notes=public_notes,

        stats=stats,

    )