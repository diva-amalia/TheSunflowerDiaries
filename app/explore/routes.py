from flask import (
    render_template,
    request,
)

from flask_login import (
    login_required,
    current_user,
)

from app.models import (
    Note,
    Poem,
)

from . import explore


# ==========================
# EXPLORE HOME
# ==========================

@explore.route("/")
@login_required
def home():

    active_tab = request.args.get(
        "tab",
        "bloomed",
    )

    poems = (
        Poem.query.filter_by(
            is_public=True,
        )
        .order_by(
            Poem.created_at.desc(),
        )
        .all()
    )

    notes = (
        Note.query.filter_by(
            is_public=True,
        )
        .order_by(
            Note.created_at.desc(),
        )
        .all()
    )

    if active_tab == "poems":

        feed = poems

    elif active_tab == "notes":

        feed = notes

    else:

        feed = sorted(
            poems + notes,
            key=lambda item: item.created_at,
            reverse=True,
        )

    for item in feed:

        item.is_cherished = any(
        cherish.user_id == current_user.id
        for cherish in item.cherishes
    )

    return render_template(
        "explore/home.html",
        active_tab=active_tab,
        feed=feed,
    )
