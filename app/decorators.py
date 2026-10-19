"""Decorator hak akses."""
from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def admin_required(view):
    @wraps(view)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != "admin":
            abort(403)
        return view(*args, **kwargs)

    return decorated
