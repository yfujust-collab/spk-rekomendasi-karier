from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange


class CareerForm(FlaskForm):
    nama = StringField("Nama karier", validators=[DataRequired(), Length(max=120)])
    deskripsi = TextAreaField("Deskripsi")
    skills = TextAreaField(
        "Skill yang dibutuhkan (pisahkan dengan koma)",
        validators=[DataRequired()],
    )
    gaji_min = IntegerField(
        "Estimasi gaji minimum (juta rupiah/bulan)",
        validators=[NumberRange(min=0)],
        default=0,
    )
    gaji_max = IntegerField(
        "Estimasi gaji maksimum (juta rupiah/bulan)",
        validators=[NumberRange(min=0)],
        default=0,
    )
    demand = IntegerField(
        "Tingkat demand pasar (1-10)",
        validators=[NumberRange(min=1, max=10)],
        default=5,
    )
    submit = SubmitField("Simpan")


class CriterionForm(FlaskForm):
    nama = StringField("Nama kriteria", validators=[DataRequired(), Length(max=120)])
    bobot = FloatField(
        "Bobot (0-1)", validators=[DataRequired(), NumberRange(min=0, max=1)]
    )
    submit = SubmitField("Simpan")
