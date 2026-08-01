from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from types import SimpleNamespace

from app.extensions import db
from app.models import Poem


poem = Blueprint(
    "poem",
    __name__,
    url_prefix="/poem",
)


def _get_user_poem(poem_id):

    poem = Poem.query.filter_by(
        id=poem_id,
        user_id=current_user.id,
    ).first()

    if poem is None:
        abort(404)

    return poem


def _get_poem(poem_id):

    poem = Poem.query.get_or_404(poem_id)

    if not poem.is_public and poem.user_id != current_user.id:
        abort(404)

    return poem


# ==========================
# CREATE POEM
# ==========================


@poem.route("/new", methods=["GET", "POST"])
@login_required
def create_poem():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        content = request.form.get(
            "content",
            ""
        ).strip()

        visibility = request.form.get(
            "visibility",
            "private"
        )

        is_public = visibility == "public"

        if not title or not content:

            flash(
                "Please write both a title and a poem.",
                "warning",
            )

            return render_template(
                "poem/create.html",
                page_title="Plant a Poem",
                submit_label="🌻 Plant",
                poem=SimpleNamespace(
                    title=title,
                    content=content,
                    is_public=is_public,
                ),
                action_url=url_for("poem.create_poem"),
                back_url=url_for("garden.home"),
            )

        poem = Poem(
            title=title,
            content=content,
            is_public=is_public,
            author=current_user,
        )

        db.session.add(poem)
        db.session.commit()

        flash(
            "🌻 Your flower has been planted.",
            "success",
        )

        return redirect(
            url_for("garden.home")
        )

    return render_template(
        "poem/create.html",
        page_title="Plant a Poem",
        submit_label="🌻 Plant",
        poem=None,
        action_url=url_for("poem.create_poem"),
        back_url=url_for("garden.home"),
    )


# ==========================
# MY POEMS
# ==========================


@poem.route("/")
@login_required
def my_poems():

    poems = Poem.query.filter_by(
        user_id=current_user.id,
    ).order_by(
        Poem.created_at.desc(),
    ).all()

    return render_template(
        "poem/my_poems.html",
        poems=poems,
    )


# ==========================
# READ POEM
# ==========================


@poem.route("/<int:poem_id>")
@login_required
def view_poem(poem_id):

    poem = _get_poem(poem_id)

    back_url = (
        url_for("poem.my_poems")
        if poem.user_id == current_user.id
        else url_for("explore.home")
    )

    return render_template(
        "poem/view.html",
        poem=poem,
        back_url=back_url,
    )


# ==========================
# EDIT POEM
# ==========================


@poem.route("/<int:poem_id>/edit", methods=["GET", "POST"])
@login_required
def edit_poem(poem_id):

    poem_obj = _get_user_poem(poem_id)

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        content = request.form.get(
            "content",
            ""
        ).strip()

        visibility = request.form.get(
            "visibility",
            "private"
        )

        if not title or not content:

            flash(
                "Please write both a title and a poem.",
                "warning",
            )

            return render_template(
                "poem/create.html",
                page_title="Edit Poem",
                submit_label="Save",
                poem=SimpleNamespace(
                    title=title,
                    content=content,
                    is_public=(visibility == "public"),
                ),
                action_url=url_for("poem.edit_poem", poem_id=poem_obj.id),
                back_url=url_for("poem.view_poem", poem_id=poem_obj.id),
            )

        poem_obj.title = title
        poem_obj.content = content
        poem_obj.is_public = visibility == "public"
        db.session.commit()

        flash(
            "🌿 Your poem has been updated.",
            "success",
        )

        return redirect(
            url_for("poem.my_poems")
        )

    return render_template(
        "poem/create.html",
        page_title="Edit Poem",
        submit_label="Save",
        poem=poem_obj,
        action_url=url_for("poem.edit_poem", poem_id=poem_obj.id),
        back_url=url_for("poem.view_poem", poem_id=poem_obj.id),
    )



# ==========================
# REMOVE POEM
# ==========================


@poem.route("/<int:poem_id>/remove", methods=["GET", "POST"])
@login_required
def remove_poem(poem_id):

    poem_obj = _get_user_poem(poem_id)

    if request.method == "POST":

        db.session.delete(poem_obj)
        db.session.commit()

        flash(
            "🍂 Your poem has been removed from the garden.",
            "success",
        )

        return redirect(
            url_for("poem.my_poems")
        )

    return render_template(
        "poem/confirm_remove.html",
        poem=poem_obj,
    )