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
from app.models import Note


note = Blueprint(
    "note",
    __name__,
    url_prefix="/note",
)


def _get_user_note(note_id):

    note_obj = Note.query.filter_by(
        id=note_id,
        user_id=current_user.id,
    ).first()

    if note_obj is None:
        abort(404)

    return note_obj


def _get_note(note_id):

    note_obj = Note.query.get_or_404(note_id)

    if not note_obj.is_public and note_obj.user_id != current_user.id:
        abort(404)

    return note_obj


# ==========================
# CREATE NOTE
# ==========================

@note.route("/new", methods=["GET", "POST"])
@login_required
def create_note():

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
                "Please write both a title and a note.",
                "warning",
            )

            return render_template(
                "note/create.html",
                page_title="Plant a Note",
                submit_label="📝 Save Note",
                note=SimpleNamespace(
                    title=title,
                    content=content,
                    is_public=is_public,
                ),
                action_url=url_for("note.create_note"),
                back_url=url_for("garden.home"),
            )

        note_obj = Note(
            title=title,
            content=content,
            is_public=is_public,
            author=current_user,
        )

        db.session.add(note_obj)
        db.session.commit()

        flash(
            "🌻 Your note has been safely kept.",
            "success",
        )

        return redirect(
            url_for("garden.home")
        )

    return render_template(
        "note/create.html",
        page_title="Plant a Note",
        submit_label="📝 Save Note",
        note=None,
        action_url=url_for("note.create_note"),
        back_url=url_for("garden.home"),
    )


# ==========================
# MY NOTES
# ==========================

@note.route("", methods=["GET"])
@note.route("/", methods=["GET"])
@login_required
def my_notes():

    notes = Note.query.filter_by(
        user_id=current_user.id,
    ).order_by(
        Note.created_at.desc(),
    ).all()

    return render_template(
        "note/my_notes.html",
        notes=notes,
    )


# ==========================
# VIEW NOTE
# ==========================

@note.route("/<int:note_id>")
@login_required
def view_note(note_id):

    note_obj = _get_note(note_id)

    back_url = (
        url_for("note.my_notes")
        if note_obj.user_id == current_user.id
        else url_for("garden.home")
    )

    return render_template(
        "note/view.html",
        note=note_obj,
        back_url=back_url,
    )


# ==========================
# EDIT NOTE
# ==========================

@note.route("/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit_note(note_id):

    note_obj = _get_user_note(note_id)

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
                "Please write both a title and a note.",
                "warning",
            )

            return render_template(
                "note/create.html",
                page_title="Edit Note",
                submit_label="Save",
                note=SimpleNamespace(
                    title=title,
                    content=content,
                    is_public=(visibility == "public"),
                ),
                action_url=url_for("note.edit_note", note_id=note_obj.id),
                back_url=url_for("note.view_note", note_id=note_obj.id),
            )

        note_obj.title = title
        note_obj.content = content
        note_obj.is_public = visibility == "public"
        db.session.commit()

        flash(
            "🌻 Your note has been updated.",
            "success",
        )

        return redirect(
            url_for("note.my_notes")
        )

    return render_template(
        "note/create.html",
        page_title="Edit Note",
        submit_label="Save",
        note=note_obj,
        action_url=url_for("note.edit_note", note_id=note_obj.id),
        back_url=url_for("note.view_note", note_id=note_obj.id),
    )


# ==========================
# DELETE NOTE
# ==========================

@note.route("/<int:note_id>/remove", methods=["GET", "POST"])
@login_required
def delete_note(note_id):

    note_obj = _get_user_note(note_id)

    if request.method == "POST":

        db.session.delete(note_obj)
        db.session.commit()

        flash(
            "🌻 Your note has been removed.",
            "success",
        )

        return redirect(
            url_for("note.my_notes")
        )

    return render_template(
        "note/confirm_remove.html",
        note=note_obj,
    )
