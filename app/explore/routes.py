from flask import (
    render_template,
    request,
)

from sqlalchemy import or_

from flask_login import (
    login_required,
    current_user,
)

from app.models import (
    User,
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

    search_query = request.args.get(
        "q",
        "",
    ).strip()


    # USER QUERY

    users = []

    if search_query:

        keyword = f"%{search_query}%"

        users = (
            User.query
            .filter(
                or_(
                    User.username.ilike(keyword),
                    User.display_name.ilike(keyword),
                )
            )
        .all()
    )
    # ==========================
    # POEM QUERY
    # ==========================

    poem_query = Poem.query.filter_by(
        is_public=True,
    )


    if search_query:

        keyword = f"%{search_query}%"

        poem_query = (
            poem_query
            .join(Poem.author)
            .filter(
                or_(
                    Poem.title.ilike(keyword),
                    Poem.content.ilike(keyword),
                    User.username.ilike(keyword),
                    User.display_name.ilike(keyword),
                )
            )
        )


    poems = (
        poem_query
        .order_by(
            Poem.created_at.desc(),
        )
        .all()
    )


    # ==========================
    # NOTE QUERY
    # ==========================

    note_query = Note.query.filter_by(
        is_public=True,
    )


    if search_query:

        keyword = f"%{search_query}%"

        note_query = (
            note_query
            .join(Note.author)
            .filter(
                or_(
                    Note.title.ilike(keyword),
                    Note.content.ilike(keyword),
                    User.username.ilike(keyword),
                    User.display_name.ilike(keyword),
                )
            )
        )


    notes = (
        note_query
        .order_by(
            Note.created_at.desc(),
        )
        .all()
    )

    

    # ==========================
    # SELECT FEED
    # ==========================

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


    # ==========================
    # CHERISH STATUS
    # ==========================

    for item in feed:

        item.is_cherished = any(
            cherish.user_id == current_user.id
            for cherish in item.cherishes
        )


    return render_template(
        "explore/home.html",
        active_tab=active_tab,
        feed=feed,
        search_query=search_query,
        users=users,
    )