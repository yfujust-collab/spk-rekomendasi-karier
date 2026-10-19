from flask_wtf import FlaskForm
from wtforms import FloatField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms.widgets import CheckboxInput, ListWidget


class ProfileForm(FlaskForm):
    nama = StringField("Nama lengkap", validators=[DataRequired(), Length(max=120)])
    nim = StringField("NIM", validators=[Optional(), Length(max=30)])
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
    ipk = FloatField(
        "IPK terakhir",
        validators=[Optional(), NumberRange(min=0, max=4)],
    )
    submit = SubmitField("Simpan Profil")
