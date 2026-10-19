from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField(
        "Nama pengguna",
        validators=[DataRequired(message="Nama pengguna wajib diisi.")],
    )
    password = PasswordField(
        "Kata sandi", validators=[DataRequired(message="Kata sandi wajib diisi.")]
    )
    submit = SubmitField("Masuk")


class RegisterForm(FlaskForm):
    nama = StringField(
        "Nama lengkap",
        validators=[
            DataRequired(message="Nama lengkap wajib diisi."),
            Length(max=120, message="Nama maksimal 120 karakter."),
        ],
    )
    username = StringField(
        "Nama pengguna",
        validators=[
            DataRequired(message="Nama pengguna wajib diisi."),
            Length(
                min=3,
                max=80,
                message="Nama pengguna minimal 3 dan maksimal 80 karakter.",
            ),
        ],
    )
    password = PasswordField(
        "Kata sandi",
        validators=[
            DataRequired(message="Kata sandi wajib diisi."),
            Length(min=6, message="Kata sandi minimal 6 karakter."),
        ],
    )
    submit = SubmitField("Daftar")
