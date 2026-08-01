from flask import redirect, request
from flask_login import current_user, login_required

from app.extensions import db
from app.models import (
    Cherish,
    Note,
    Poem,
)

from . import cherish


# ==========================
# CHERISH POEM
# ==========================

@cherish.route("/poem/<int:poem_id>", methods=["POST"])
@login_required
def cherish_poem(poem_id):

    poem = Poem.query.get_or_404(poem_id)

    existing = Cherish.query.filter_by(
        user_id=current_user.id,
        poem_id=poem.id,
    ).first()

    if existing:

        db.session.delete(existing)

    else:

        db.session.add(
            Cherish(
                user_id=current_user.id,
                poem_id=poem.id,
            )
        )

    db.session.commit()

    return redirect(
        request.referrer or "/"
    )


# ==========================
# CHERISH NOTE
# ==========================

@cherish.route("/note/<int:note_id>", methods=["POST"])
@login_required
def cherish_note(note_id):

    note = Note.query.get_or_404(note_id)

    existing = Cherish.query.filter_by(
        user_id=current_user.id,
        note_id=note.id,
    ).first()

    if existing:

        db.session.delete(existing)

    else:

        db.session.add(
            Cherish(
                user_id=current_user.id,
                note_id=note.id,
            )
        )

    db.session.commit()

    return redirect(
        request.referrer or "/"
    )