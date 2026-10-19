"""Seed database dari dataset karier adaptasi O*NET (bukan data hardcode).

Skrip ini membaca langsung dua file CSV dari folder dataset:
  - karier.csv       : 14 karier IT (kode O*NET-SOC, judul EN/ID,
                       deskripsi ID, jml_hot_tech)
  - skill_karier.csv : 35 skill O*NET per karier (skill_en, skill_id,
                       importance 1-5); disaring ke 12 skill Informatika

ADAPTASI DATASET O*NET (bahan Bab Metodologi)
--------------------------------------------
Sumber: O*NET Database 31.0, U.S. Department of Labor, Employment and
Training Administration (USDOL/ETA). Lisensi CC BY 4.0. Atribusi wajib:

    Data karier diadaptasi dari O*NET 31.0 Database oleh U.S. Department
    of Labor, Employment and Training Administration (USDOL/ETA),
    digunakan di bawah lisensi CC BY 4.0. USDOL/ETA tidak menyetujui,
    mendukung, atau menguji modifikasi ini.

Langkah adaptasi:
  1. Subset: 14 okupasi bidang Informatika dari 1.016 okupasi O*NET.
  2. Penerjemahan: judul, deskripsi, dan nama skill diterjemahkan ke
     Bahasa Indonesia. Istilah teknologi yang merupakan nama proper
     (Python, SQL, Git, Docker, dsb.) dipertahankan karena universal.
  3. Kurasi skill Informatika untuk CBF: dari 35 skill O*NET, dipilih
     12 skill yang relevan dengan Jurusan Informatika (lihat
     SKILL_INFORMATIKA di bawah). Skill teknisi/non-IT (Pemilihan
     Peralatan, Instalasi, Perawatan Peralatan, Perbaikan, dsb.)
     sengaja dikecualikan agar vektor CBF mencerminkan kompetensi
     Informatika. Memakai 35 skill sekaligus memberi cosine similarity
     0.97-0.99 antar-karier IT (hampir identik, tidak bisa membedakan),
     sehingga kurasi ini juga berfungsi sebagai seleksi fitur.
  4. Threshold biner: kolom Career.skills di aplikasi ini berupa teks
     dipisah koma (vektor biner di layanan CBF), sehingga bobot
     importance O*NET (skala 1-5) tidak bisa disimpan langsung. Skill
     dengan importance >= 3.0 (kategori "penting" ke atas) dicantumkan
     sebagai ciri khas karier; yang di bawahnya tidak. Ambang ini
     dipilih empiris: ambang 2.0 membuat 11 dari 14 karier bervektor
     identik, sedangkan 3.0 menghasilkan 14 vektor unik dengan sebaran
     cosine 0.62-0.95 antar-karier. Idealnya kolom bobot importance
     ditambahkan ke model (pengembangan lanjutan).
  5. Demand (C3): jumlah hot technology (jml_hot_tech) dinormalisasi
     min-max ke skala 1-10 lalu dibulatkan.
  6. Gaji (C2): ESTIMASI pasar kerja Indonesia, dalam juta rupiah/bulan.
     O*NET TIDAK menyediakan data gaji; kolom estimasi gaji di
     karier.csv memang sengaja dikosongkan. Angka pada tabel GAJI di
     bawah adalah perkiraan wajar mengikuti pola entry 4-7, mid 7-12,
     senior/spesialis 10-18, disesuaikan per peran. Ganti dengan data
     survei gaji bila tersedia (mis. dataset Kaggle AI-Powered Job
     Recommendations).

IDEMPOTEN: skrip ini menghapus seluruh data master lama (karier,
kriteria, dan hasil rekomendasi yang merujuk karier) lalu mengisi ulang
dari CSV. Akun pengguna dan profil mahasiswa dipertahankan, tetapi
daftar minat pada profil perlu diisi ulang karena id karier berubah.

Contoh:
    python seed.py
    python seed.py --karier-csv /path/ke/karier.csv
    DATABASE_URL=sqlite:////tmp/uji.db python seed.py
"""
import argparse
import csv
import os
import sys

DEFAULT_DATASET_DIR = os.path.expanduser(
    "~/workspace/spk-karier/onet-adaptasi"
)

# ESTIMASI gaji pasar Indonesia (juta Rp/bulan), key = kode O*NET-SOC.
# BUKAN data O*NET: O*NET tidak menyediakan data gaji.
GAJI = {
    "15-1252.00": (5, 12),   # Pengembang Perangkat Lunak
    "15-1251.00": (4, 10),   # Programmer Komputer
    "15-1254.00": (4, 10),   # Pengembang Web
    "15-1255.00": (4, 10),   # Desainer Antarmuka Web & Digital
    "15-1253.00": (4, 10),   # Analis & Penguji QA Perangkat Lunak
    "15-2051.00": (6, 14),   # Ilmuwan Data
    "15-1243.01": (5, 12),   # Spesialis Data Warehouse
    "15-1242.00": (5, 10),   # Administrator Database
    "15-1212.00": (5, 13),   # Analis Keamanan Informasi
    "15-1299.05": (6, 15),   # Insinyur Keamanan Informasi
    "15-1241.00": (5, 13),   # Arsitek Jaringan Komputer
    "15-1244.00": (4, 10),   # Administrator Sistem Jaringan & Komputer
    "15-1211.00": (4, 10),   # Analis Sistem Komputer
    "15-1299.09": (6, 16),   # Manajer Proyek TI
}
GAJI_DEFAULT = (5, 12)

# 12 skill Informatika hasil kurasi dari 35 skill O*NET (nama persis
# seperti kolom skill_id di skill_karier.csv).
SKILL_INFORMATIKA = [
    "Pemrograman",
    "Analisis Sistem",
    "Evaluasi Sistem",
    "Perancangan Teknologi",
    "Pemecahan Masalah Kompleks",
    "Berpikir Kritis",
    "Matematika",
    "Pemecahan Masalah Teknis",
    "Analisis Operasional",
    "Analisis Kendali Mutu",
    "Pembelajaran Aktif",
    "Penilaian & Pengambilan Keputusan",
]

# Ambang importance O*NET (skala 1-5): 3 = "penting". Hanya skill yang
# penting ke atas yang menjadi ciri khas karier. Diukur empiris:
# ambang 2.0 membuat 11 dari 14 karier bervektor identik (semua skill
# lolos), sedangkan ambang 3.0 memberi 14 vektor unik dengan sebaran
# cosine 0.62-0.95 antar-karier.
AMBANG_IMPORTANCE = 3.0

KRITERIA = [
    ("C1", "Kecocokan skill (CBF)", 0.35),
    ("C2", "Prospek gaji", 0.25),
    ("C3", "Demand pasar", 0.20),
    ("C4", "Kesesuaian minat", 0.20),
]

KOLOM_WAJIB_KARIER = {"kode_onetsoc", "judul_id", "deskripsi_id", "jml_hot_tech"}
KOLOM_WAJIB_SKILL = {"kode_onetsoc", "skill_id", "importance"}


def baca_csv(path, kolom_wajib):
    """Baca CSV (UTF-8) dan validasi kolom wajib."""
    if not os.path.isfile(path):
        raise SystemExit(f"File tidak ditemukan: {path}")
    with open(path, newline="", encoding="utf-8") as f:
        baris = list(csv.DictReader(f))
    kurang = kolom_wajib - set(baris[0].keys()) if baris else kolom_wajib
    if kurang:
        raise SystemExit(f"Kolom hilang di {path}: {sorted(kurang)}")
    if not baris:
        raise SystemExit(f"File kosong: {path}")
    return baris


def normalisasi_demand(nilai, minimum, maksimum):
    """Skala min-max nilai ke 1-10, dibulatkan."""
    if maksimum == minimum:
        return 5
    skor = 1 + 9 * (nilai - minimum) / (maksimum - minimum)
    return max(1, min(10, round(skor)))


def main():
    parser = argparse.ArgumentParser(
        description="Seed database SPK dari dataset O*NET adaptasi."
    )
    parser.add_argument(
        "--karier-csv",
        default=os.path.join(DEFAULT_DATASET_DIR, "karier.csv"),
        help="Path ke karier.csv (default: folder dataset onet-adaptasi).",
    )
    parser.add_argument(
        "--skill-csv",
        default=None,
        help="Path ke skill_karier.csv "
        "(default: satu folder dengan karier.csv).",
    )
    args = parser.parse_args()

    karier_csv = os.path.expanduser(args.karier_csv)
    skill_csv = os.path.expanduser(args.skill_csv) if args.skill_csv else os.path.join(
        os.path.dirname(karier_csv), "skill_karier.csv"
    )

    daftar_karier = baca_csv(karier_csv, KOLOM_WAJIB_KARIER)
    daftar_skill = baca_csv(skill_csv, KOLOM_WAJIB_SKILL)

    # Saring hanya 12 skill Informatika hasil kurasi; validasi bahwa
    # semuanya benar-benar ada di CSV.
    ada_di_csv = {baris["skill_id"] for baris in daftar_skill}
    hilang = [s for s in SKILL_INFORMATIKA if s not in ada_di_csv]
    if hilang:
        raise SystemExit(
            f"Skill kurasi tidak ditemukan di {skill_csv}: {hilang}"
        )
    urutan_skill = list(SKILL_INFORMATIKA)
    daftar_skill = [b for b in daftar_skill if b["skill_id"] in set(urutan_skill)]
    skill_per_kode = {}
    for baris in daftar_skill:
        try:
            importance = float(baris["importance"])
        except (TypeError, ValueError):
            continue
        if importance >= AMBANG_IMPORTANCE:
            skill_per_kode.setdefault(baris["kode_onetsoc"], []).append(
                baris["skill_id"]
            )
    # Samakan urutan skill tiap karier dengan urutan kanonis 12 skill.
    for kode, skills in skill_per_kode.items():
        skill_per_kode[kode] = [s for s in urutan_skill if s in skills]

    hot_tech = [int(b["jml_hot_tech"]) for b in daftar_karier]
    hmin, hmax = min(hot_tech), max(hot_tech)

    def buat_app_dan_model():
        # Impor di sini agar DATABASE_URL dari env terbaca create_app().
        from app import create_app, db  # noqa: E402
        from app.models import (  # noqa: E402
            Career,
            Criterion,
            RecommendationResult,
            User,
        )

        return create_app, db, Career, Criterion, RecommendationResult, User

    create_app, db, Career, Criterion, RecommendationResult, User = (
        buat_app_dan_model()
    )
    app = create_app()
    with app.app_context():
        # Reset data master agar seed idempoten. Hasil rekomendasi
        # dihapus dulu karena merujuk ke karier lama.
        n_hasil = RecommendationResult.query.delete()
        n_karier_lama = Career.query.delete()
        n_kriteria_lama = Criterion.query.delete()

        for baris in daftar_karier:
            kode = baris["kode_onetsoc"]
            nama = baris["judul_id"].strip()
            skills = ", ".join(skill_per_kode.get(kode, []))
            demand = normalisasi_demand(int(baris["jml_hot_tech"]), hmin, hmax)
            gaji_min, gaji_max = GAJI.get(kode, GAJI_DEFAULT)
            if kode not in GAJI:
                print(f"Peringatan: kode {kode} tidak ada di tabel GAJI, "
                      f"pakai default {GAJI_DEFAULT}.")
            db.session.add(
                Career(
                    nama=nama,
                    deskripsi=baris["deskripsi_id"].strip(),
                    skills=skills,
                    gaji_min=gaji_min,
                    gaji_max=gaji_max,
                    demand=demand,
                )
            )

        for kode, nama, bobot in KRITERIA:
            db.session.add(Criterion(kode=kode, nama=nama, bobot=bobot))

        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", nama="Administrator", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            print("Akun admin dibuat (admin / admin123).")

        db.session.commit()

    print(f"Data lama dihapus: {n_karier_lama} karier, {n_kriteria_lama} "
          f"kriteria, {n_hasil} hasil rekomendasi.")
    print(f"{len(daftar_karier)} karier dari {karier_csv} berhasil di-seed.")
    print(f"Urutan 12 skill Informatika: {', '.join(urutan_skill)}")
    print("Seed selesai.")


if __name__ == "__main__":
    main()
