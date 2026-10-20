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
    # Format: "Skill:skor" dipisah koma, mis. "Python:4.6, SQL:3.8".
    # Skor = tingkat kepentingan skill untuk karier ini (skala 1-5,
    # dari Dataset Lowongan IT Indonesia). Entri tanpa ":skor"
    # (mis. input manual via panel admin) dianggap berbobot 3.0.
    skills = db.Column(db.Text, nullable=False, default="")
    gaji_min = db.Column(db.Integer, default=0)  # juta rupiah per bulan
    gaji_max = db.Column(db.Integer, default=0)
    demand = db.Column(db.Integer, default=5)  # skala 1-10

    def skill_list(self):
        """Nama skill saja (tanpa skor), untuk tampilan & kosakata."""
        return [s.split(":")[0].strip() for s in self.skills.split(",") if s.strip()]

    def skill_scores(self):
        """Dict {nama_skill_lower: skor float} untuk vektor CBF berbobot."""
        hasil = {}
        for bagian in self.skills.split(","):
            bagian = bagian.strip()
            if not bagian:
                continue
            if ":" in bagian:
                nama, _, skor = bagian.rpartition(":")
                try:
                    nilai = float(skor.strip())
                except ValueError:
                    nilai = 3.0
            else:
                nama, nilai = bagian, 3.0
            nama = nama.strip()
            if nama:
                hasil[nama.lower()] = nilai
        return hasil


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
    # Format: "Skill:nilai" dipisah koma, mis. "Python:4, SQL:3".
    # Nilai = tingkat penguasaan yang dinilai sendiri oleh mahasiswa
    # (skala 0-5; hanya skill bernilai > 0 yang disimpan). Entri lama
    # tanpa ":nilai" (format checkbox biner) dianggap bernilai 3.0,
    # konvensi yang sama seperti Career.skill_scores().
    skills = db.Column(db.Text, default="")
    minat = db.Column(db.Text, default="")  # id karier diminati, dipisah koma
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def skill_list(self):
        """Nama skill saja (tanpa nilai), untuk tampilan."""
        return [s.split(":")[0].strip() for s in self.skills.split(",") if s.strip()]

    def skill_scores(self):
        """Dict {nama_skill_lower: nilai float} untuk vektor CBF berbobot.

        Entri tanpa ":nilai" (profil lama format biner) dianggap 3.0
        agar data lama tetap dapat dihitung dan tidak crash.
        """
        hasil = {}
        for bagian in self.skills.split(","):
            bagian = bagian.strip()
            if not bagian:
                continue
            if ":" in bagian:
                nama, _, nilai_teks = bagian.rpartition(":")
                try:
                    nilai = float(nilai_teks.strip())
                except ValueError:
                    nilai = 3.0
            else:
                nama, nilai = bagian, 3.0
            nama = nama.strip()
            if nama:
                hasil[nama.lower()] = nilai
        return hasil

    def minat_ids(self):
        return [int(x) for x in self.minat.split(",") if x.strip().isdigit()]


class RecommendationResult(db.Model):
    """Hasil perhitungan per profil.

    Kolom batch_id menandai satu kali perhitungan: semua baris dari
    perhitungan yang sama memakai batch_id yang sama. Batch lama tidak
    dihapus agar halaman Riwayat bisa menampilkan hasil-hasil terdahulu;
    tampilan Hasil dan Dasbor selalu memakai batch terbaru.

    Kolom bobot menyimpan bobot SAW yang benar-benar dipakai pada
    batch ini, sebagai JSON list 4 angka yang SUDAH dinormalisasi
    (mis. "[0.35, 0.25, 0.2, 0.2]"). Sama di semua baris satu batch.
    NULL untuk batch lama sebelum fitur bobot kustom ada.
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
    bobot = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    career = db.relationship("Career")
