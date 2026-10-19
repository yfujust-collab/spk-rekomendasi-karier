from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Nama pengguna", validators=[DataRequired()])
    password = PasswordField("Kata sandi", validators=[DataRequired()])
    submit = SubmitField("Masuk")


class RegisterForm(FlaskForm):
    nama = StringField("Nama lengkap", validators=[DataRequired(), Length(max=120)])
    username = StringField(
        "Nama pengguna", validators=[DataRequired(), Length(min=3, max=80)]
    )
    password = PasswordField(
        "Kata sandi", validators=[DataRequired(), Length(min=6)]
    )
    submit = SubmitField("Daftar")
