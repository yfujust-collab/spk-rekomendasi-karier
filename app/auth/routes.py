from flask import flash, redirect, render_template, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm
from app.models import User


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("spk.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("spk.index"))
        flash("Nama pengguna atau kata sandi salah.", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("spk.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data.strip()).first():
            flash("Nama pengguna sudah dipakai.", "danger")
        else:
            user = User(
                username=form.username.data.strip(),
                nama=form.nama.data.strip(),
                role="mahasiswa",
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Pendaftaran berhasil. Silakan masuk.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    # bobot kustom bersifat per sesi per pengguna: bersihkan saat keluar
    session.pop("bobot_custom", None)
    logout_user()
    flash("Anda sudah keluar.", "info")
    return redirect(url_for("auth.login"))
