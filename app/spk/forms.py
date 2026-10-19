from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.widgets import CheckboxInput, ListWidget


class ProfileForm(FlaskForm):
    nama = StringField(
        "Nama lengkap",
        validators=[
            DataRequired(message="Nama lengkap wajib diisi."),
            Length(max=120, message="Nama maksimal 120 karakter."),
        ],
    )
    skills = SelectMultipleField(
        "Skill yang dikuasai",
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
        validators=[DataRequired(message="Pilih minimal satu skill.")],
    )
    minat = SelectMultipleField(
        "Karier yang diminati",
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
        validators=[Optional()],
        coerce=int,
    )
    submit = SubmitField("Simpan Profil")
