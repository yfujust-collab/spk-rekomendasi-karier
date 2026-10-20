"""Seed database dari Dataset Lowongan IT Indonesia (bukan data hardcode).

Skrip ini membaca dua file CSV dari folder dataset:
  - skill_matrix.csv : 22 jabatan IT x 30 hard skill, skor 1-5
                       (kolom: kode_jabatan, nama_jabatan, skill, skor)
  - demand_gaji.csv  : demand & gaji per jabatan
                       (kolom: kode_jabatan, nama_jabatan, n_lowongan,
                       n_gaji, gaji_min_rp, gaji_max_rp, gaji_median_rp)

DATASET LOWONGAN IT INDONESIA (bahan Bab Metodologi)
---------------------------------------------------
Dataset primer yang dibangun khusus untuk penelitian ini melalui text
mining 1.066 lowongan IT unik dari id.indeed.com dan glints.com
(19-20 Oktober 2026, 39-55 lowongan per jabatan; 1.045 berdeskripsi
substansial dipakai untuk mining skill). Metode: ekstraksi skill
berbasis NLP (spaCy) — segmentasi seksi deskripsi, pencocokan frasa
sadar lemma atas kamus 30 hard skill, dan deteksi negasi — lalu
frekuensi kemunculan per jabatan dinormalisasi ke skor 1-5 dengan rumus:

    skor(o, s) = 1 + 4 * (pct(o, s) / max_pct(o))

pct(o, s) = % lowongan jabatan o yang menyebut skill s (satu desimal).
Demand (C3) = jumlah lowongan per jabatan (dinormalisasi min-max ke
1-10 di bawah). Gaji (C2) = dari info gaji yang tercantum di lowongan
(median per jabatan; n_gaji 12-26 per jabatan, mayoritas dari Glints).

Dataset ini MENGGANTIKAN PENUH dataset adaptasi O*NET yang dipakai
sebelumnya. O*NET tidak lagi menjadi sumber data sistem ini.

Keterbatasan yang dicatat jujur:
  - Dua sumber (Indeed + Glints); sampel 39-55 per jabatan.
  - Ekstraksi NLP tetap berbasis kamus 30 skill (sinonim di luar
    kamus tidak tertangkap; aturan negasi bersifat lokal).
  - Mayoritas iklan berbahasa Inggris; snapshot Oktober 2026.

Deskripsi tiap jabatan (Bahasa Indonesia) ada di
data-loker-id/deskripsi.csv (dipetakan via nama jabatan yang sama
persis); bila tidak ditemukan, seed GAGAL dengan pesan jelas
(fail loudly, bukan karangan diam-diam).

Format kolom Career.skills: "Skill:skor" dipisah koma, mis.
"Python:4.6, SQL:3.8". Skor 1-5 dipakai langsung sebagai vektor
BERBOBOT di layanan CBF (lihat app/services/cbf.py) — tidak ada
lagi threshold biner.

IDEMPOTEN: skrip ini menghapus seluruh data master lama (karier,
kriteria, dan hasil rekomendasi yang merujuk karier) lalu mengisi
ulang dari CSV. Akun pengguna dan profil mahasiswa dipertahankan,
tetapi daftar minat pada profil perlu diisi ulang karena id karier
berubah.

Contoh:
    python seed.py
    python seed.py --matrix-csv /path/ke/skill_matrix.csv
    DATABASE_URL=sqlite:////tmp/uji.db python seed.py
"""
import argparse
import csv
import os
import statistics
import sys

DEFAULT_DATASET_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data-loker-id"
)
# Deskripsi tiap jabatan (Bahasa Indonesia), satu file dengan dataset.
ARSIP_DESKRIPSI = os.path.join(DEFAULT_DATASET_DIR, "deskripsi.csv")

# IMPUTASI (bukan observasi): IT Support tidak punya data gaji sama
# sekali di dataset (n_gaji=0). Nilai min/med/max di bawah dihitung
# sebagai median dari 18 jabatan lain yang punya data — lihat kode.
# Ditandai eksplisit di README sebagai keterbatasan.
KODE_IMPUTASI_GAJI = {"ITSUP"}

KRITERIA = [
    ("C1", "Kecocokan skill (CBF)", 0.35),
    ("C2", "Prospek gaji", 0.25),
    ("C3", "Demand pasar", 0.20),
    ("C4", "Kesesuaian minat", 0.20),
]

KOLOM_WAJIB_MATRIX = {"kode_jabatan", "nama_jabatan", "skill", "skor"}
KOLOM_WAJIB_DEMAND = {
    "kode_jabatan",
    "nama_jabatan",
    "n_lowongan",
    "n_gaji",
    "gaji_min_rp",
    "gaji_max_rp",
    "gaji_median_rp",
}


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


def rp_ke_juta(nilai_rp):
    """Konversi rupiah -> juta rupiah, dibulatkan (untuk kolom model)."""
    return int(round(nilai_rp / 1_000_000))


def main():
    parser = argparse.ArgumentParser(
        description="Seed database SPK dari Dataset Lowongan IT Indonesia."
    )
    parser.add_argument(
        "--matrix-csv",
        default=os.path.join(DEFAULT_DATASET_DIR, "skill_matrix.csv"),
        help="Path ke skill_matrix.csv (default: folder data-loker-id/).",
    )
    parser.add_argument(
        "--demand-csv",
        default=os.path.join(DEFAULT_DATASET_DIR, "demand_gaji.csv"),
        help="Path ke demand_gaji.csv (default: folder data-loker-id/).",
    )
    args = parser.parse_args()

    matrix_csv = os.path.expanduser(args.matrix_csv)
    demand_csv = os.path.expanduser(args.demand_csv)
    daftar_matrix = baca_csv(matrix_csv, KOLOM_WAJIB_MATRIX)
    daftar_demand = baca_csv(demand_csv, KOLOM_WAJIB_DEMAND)

    # Deskripsi dari file dataset; gagal keras bila ada jabatan
    # tanpa deskripsi.
    deskripsi = {}
    with open(ARSIP_DESKRIPSI, newline="", encoding="utf-8") as f:
        for baris in csv.DictReader(f):
            deskripsi[baris["nama_jabatan"].strip()] = baris[
                "deskripsi_id"
            ].strip()

    skill_per_kode = {}
    for baris in daftar_matrix:
        try:
            skor = float(baris["skor"])
        except (TypeError, ValueError):
            continue
        if not 1.0 <= skor <= 5.0:
            raise SystemExit(
                f"Skor di luar 1-5 pada {matrix_csv}: {baris}"
            )
        skill_per_kode.setdefault(baris["kode_jabatan"], []).append(
            (baris["skill"].strip(), skor)
        )
    # Urutkan skill tiap jabatan dari skor tertinggi (untuk tampilan).
    for kode in skill_per_kode:
        skill_per_kode[kode].sort(key=lambda x: -x[1])

    # Gaji: pakai min/max observasi; imputasi untuk n_gaji=0.
    # (Median tiap jabatan tersedia di demand_gaji.csv bila diperlukan
    # analisis lanjutan; model hanya menyimpan min & max.)
    def ambil_gaji(baris):
        if int(baris["n_gaji"] or 0) > 0:
            return (float(baris["gaji_min_rp"]), float(baris["gaji_max_rp"]))
        return None

    gaji_obs = {
        b["kode_jabatan"]: ambil_gaji(b)
        for b in daftar_demand
        if ambil_gaji(b) is not None
    }
    imput_min = statistics.median(g[0] for g in gaji_obs.values())
    imput_max = statistics.median(g[1] for g in gaji_obs.values())
    for kode in KODE_IMPUTASI_GAJI:
        if kode not in gaji_obs:
            gaji_obs[kode] = (imput_min, imput_max)
            print(
                f"IMPUTASI (bukan observasi): gaji {kode} = "
                f"median 18 jabatan lain "
                f"({rp_ke_juta(imput_min)}-{rp_ke_juta(imput_max)} jt)."
            )

    n_lowongan = [int(b["n_lowongan"]) for b in daftar_demand]
    nmin, nmax = min(n_lowongan), max(n_lowongan)

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

        for baris in daftar_demand:
            kode = baris["kode_jabatan"]
            nama = baris["nama_jabatan"].strip()
            if nama not in deskripsi:
                raise SystemExit(
                    f"Jabatan '{nama}' tidak punya deskripsi di "
                    f"{ARSIP_DESKRIPSI}; tambahkan manual, jangan dikarang."
                )
            pasangan = skill_per_kode.get(kode, [])
            skills = ", ".join(f"{s}:{g}" for s, g in pasangan)
            demand = normalisasi_demand(int(baris["n_lowongan"]), nmin, nmax)
            gmin, gmax = gaji_obs[kode]
            db.session.add(
                Career(
                    nama=nama,
                    deskripsi=deskripsi[nama],
                    skills=skills,
                    gaji_min=rp_ke_juta(gmin),
                    gaji_max=rp_ke_juta(gmax),
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
    print(f"{len(daftar_demand)} karier dari {demand_csv} berhasil di-seed.")
    n_skill = len({s for v in skill_per_kode.values() for s, _ in v})
    print(f"Total {n_skill} skill unik dengan skor berbobot 1-5.")
    print("Seed selesai.")


if __name__ == "__main__":
    main()
