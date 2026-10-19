from flask import Blueprint

bp = Blueprint("spk", __name__)

from app.spk import routes  # noqa: E402,F401
