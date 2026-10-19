"""Model database SPK Rekomendasi Karier."""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(UserMixin, db.Model):
    """Pengguna: admin atau mahasiswa."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="mahasiswa")
    nama = db.Column(db.String(120))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Career(db.Model):
    """Data karier (alternatif keputusan)."""

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(120), nullable=False)
    deskripsi = db.Column(db.Text)
    skills = db.Column(db.Text, nullable=False, default="")  # dipisah koma
    gaji_min = db.Column(db.Integer, default=0)  # juta rupiah per bulan
    gaji_max = db.Column(db.Integer, default=0)
    demand = db.Column(db.Integer, default=5)  # skala 1-10

    def skill_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]


class Criterion(db.Model):
    """Kriteria SAW beserta bobot."""

    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(10), unique=True, nullable=False)  # C1..Cn
    nama = db.Column(db.String(120), nullable=False)
    bobot = db.Column(db.Float, nullable=False, default=0.25)
    tipe = db.Column(db.String(10), nullable=False, default="benefit")


class StudentProfile(db.Model):
    """Profil mahasiswa yang diisi lewat form."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    nama = db.Column(db.String(120), nullable=False)
    nim = db.Column(db.String(30))
    skills = db.Column(db.Text, default="")  # skill dikuasai, dipisah koma
    minat = db.Column(db.Text, default="")  # id karier diminati, dipisah koma
    ipk = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def skill_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    def minat_ids(self):
        return [int(x) for x in self.minat.split(",") if x.strip().isdigit()]


class RecommendationResult(db.Model):
    """Hasil perhitungan per profil.

    Kolom batch_id menandai satu kali perhitungan: semua baris dari
    perhitungan yang sama memakai batch_id yang sama. Batch lama tidak
    dihapus agar halaman Riwayat bisa menampilkan hasil-hasil terdahulu;
    tampilan Hasil dan Dasbor selalu memakai batch terbaru.
    """

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(
        db.Integer, db.ForeignKey("student_profile.id"), nullable=False
    )
    career_id = db.Column(db.Integer, db.ForeignKey("career.id"), nullable=False)
    skor_cbf = db.Column(db.Float, default=0.0)
    skor_saw = db.Column(db.Float, default=0.0)
    peringkat = db.Column(db.Integer, default=0)
    batch_id = db.Column(db.String(32), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    career = db.relationship("Career")
