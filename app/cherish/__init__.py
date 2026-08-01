from flask import Blueprint

cherish = Blueprint(
    "cherish",
    __name__,
    url_prefix="/cherish",
)

from . import routes