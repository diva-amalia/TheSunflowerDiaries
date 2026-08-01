from flask import Blueprint


explore = Blueprint(
    "explore",
    __name__,
    url_prefix="/explore",
)

from . import routes