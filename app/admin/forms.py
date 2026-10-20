from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange


class CareerForm(FlaskForm):
    nama = StringField(
        "Nama karier",
        validators=[
            DataRequired(message="Nama karier wajib diisi."),
            Length(max=120, message="Nama karier maksimal 120 karakter."),
        ],
    )
    deskripsi = TextAreaField("Deskripsi")
    skills = TextAreaField(
        "Skill dan bobot (format: Skill:skor, pisahkan dengan koma)",
        validators=[DataRequired(message="Skill karier wajib diisi.")],
        description="Contoh: Python:4.6, SQL:3.8, Git:2.6. Skor 1-5; "
        "entri tanpa skor dianggap berbobot 3.0.",
    )
    gaji_min = IntegerField(
        "Gaji minimum (juta rupiah/bulan)",
        validators=[
            NumberRange(
                min=0, message="Gaji minimum tidak boleh kurang dari 0."
            )
        ],
        default=0,
    )
    gaji_max = IntegerField(
        "Gaji maksimum (juta rupiah/bulan)",
        validators=[
            NumberRange(
                min=0, message="Gaji maksimum tidak boleh kurang dari 0."
            )
        ],
        default=0,
    )
    demand = IntegerField(
        "Tingkat demand pasar (1-10)",
        validators=[
            NumberRange(
                min=1, max=10, message="Demand harus antara 1 sampai 10."
            )
        ],
        default=5,
    )
    submit = SubmitField("Simpan")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False
        if (
            self.gaji_min.data is not None
            and self.gaji_max.data is not None
            and self.gaji_min.data > self.gaji_max.data
        ):
            self.gaji_min.errors.append(
                "Gaji minimum tidak boleh lebih besar dari gaji maksimum."
            )
            return False
        return True


class CriterionForm(FlaskForm):
    nama = StringField(
        "Nama kriteria",
        validators=[
            DataRequired(message="Nama kriteria wajib diisi."),
            Length(max=120, message="Nama kriteria maksimal 120 karakter."),
        ],
    )
    bobot = FloatField(
        "Bobot (0-1)",
        validators=[
            DataRequired(message="Bobot wajib diisi."),
            NumberRange(
                min=0, max=1, message="Bobot harus antara 0 sampai 1."
            ),
        ],
    )
    submit = SubmitField("Simpan")
