from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.widgets import CheckboxInput, ListWidget

# Catatan: tingkat penguasaan skill TIDAK memakai field WTForms.
# Alasannya, 30 baris input nilai (satu per skill) lebih aman diisi
# lewat input HTML biasa dan divalidasi seluruhnya di server (lihat
# fungsi profil di app/spk/routes.py) — pola yang sama seperti panel
# bobot kustom. WTForms me-render atribut "required" pada tiap input
# turunannya sehingga browser pernah menuntut semua checkbox
# dicentang; pola manual menghindari jebakan itu.


class ProfileForm(FlaskForm):
    nama = StringField(
        "Nama lengkap",
        validators=[
            DataRequired(message="Nama lengkap wajib diisi."),
            Length(max=120, message="Nama maksimal 120 karakter."),
        ],
    )
    minat = SelectMultipleField(
        "Karier yang diminati",
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
        validators=[Optional()],
        coerce=int,
    )
    submit = SubmitField("Simpan Profil")
