<div align="center">

# **Rancang Bangun Sistem Pendukung Keputusan Rekomendasi Karier Mahasiswa Informatika Berbasis Web Menggunakan Metode Content-Based Filtering dan Simple Additive Weighting (SAW)**

*SPK Karier: sistem pendukung keputusan berbasis web untuk merekomendasikan karier mahasiswa Informatika.*

*Content-Based Filtering bertemu Simple Additive Weighting dalam satu alur yang transparan.*

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![License](https://img.shields.io/badge/License-MIT-green)

| Metode | Peran |
|---|---|
| Content-Based Filtering | Mengukur kecocokan skill (cosine similarity) |
| Simple Additive Weighting | Memberi peringkat akhir dari 4 kriteria berbobot |

[Fitur](#fitur) · [Cara Jalan](#cara-jalan) · [Deploy](#deploy) · [Struktur](#struktur) · [Dataset](#dataset) · [Analisis Sensitivitas](#analisis-sensitivitas)

</div>

## Fitur

- **Autentikasi berbasis peran**: admin mengelola data, mahasiswa menerima rekomendasi.
- **Form profil mahasiswa**: nama, tingkat penguasaan tiap skill (skala 0 sampai 5), dan karier yang diminati.
- **Perhitungan dua tahap**: CBF untuk skor kecocokan skill, SAW untuk peringkat akhir.
- **Transparansi penuh**: halaman hasil menampilkan matriks keputusan, matriks ternormalisasi, dan skor preferensi tiap karier, plus grafik Chart.js.
- **Riwayat perhitungan**: setiap perhitungan disimpan sebagai batch tersendiri; hasil lama bisa dibuka ulang tanpa tertimpa.
- **Bobot SAW kustom per pengguna**: mahasiswa dapat mengatur bobot C1 sampai C4 sendiri di halaman hasil; bobot kustom tersimpan di sesi (tidak mengubah bobot master admin) dan bobot yang dipakai tercatat pada tiap batch, halaman riwayat, dan ekspor CSV.
- **Export CSV**: unduh hasil rekomendasi batch terbaru sebagai berkas CSV.
- **Panel admin**: kelola data karier (skill, gaji, demand) serta kriteria dan bobot SAW.

## Cara Jalan

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
python run.py
```

Buka `http://127.0.0.1:5000`, masuk sebagai admin (`admin` / `admin123`, segera ganti) atau daftar sebagai mahasiswa.

## Deploy

Panduan lengkap di [DEPLOY.md](DEPLOY.md): deploy ke VPS dengan Docker
(`docker build` + `docker run`, volume untuk SQLite atau `DATABASE_URL`
untuk Postgres) dan opsi PythonAnywhere (virtualenv, konfigurasi WSGI,
seed). Wajib ganti kredensial admin default dan set `SECRET_KEY` lewat
environment sebelum aplikasi dibuka ke publik.

## Struktur

```
app/
├── auth/        login, daftar, keluar
├── admin/       dasbor, CRUD karier, CRUD kriteria
├── spk/         form profil, hitung rekomendasi, hasil
├── services/    cbf.py (cosine similarity), saw.py (normalisasi + skor)
├── models.py    User, Career, Criterion, StudentProfile, RecommendationResult
└── templates/   Jinja2 + Tailwind + Chart.js
analysis/        analisis sensitivitas bobot (Bab 4)
```

## Diagram Perancangan

Diagram use case, flowchart, activity, sequence, class, DFD, dan ERD tersedia sebagai gambar. Khusus ERD: digenerate dari skema database aktual (SQLite hasil seed, via refleksi SQLAlchemy) memakai script `gen_erd_real.py`, bukan digambar manual, sehingga dijamin 1:1 dengan tabel yang dipakai aplikasi (setara fitur Designer di phpMyAdmin).

## Dataset

Sistem ini memakai satu dataset primer, yaitu Dataset Lowongan IT Indonesia: matriks kebutuhan skill 19 jabatan IT × 30 hard skill yang dibangun sendiri melalui *text mining* 479 lowongan IT unik dari id.indeed.com (19–20 Oktober 2026, 18–31 lowongan per jabatan). File dataset ada di folder `data-loker-id/` (`skill_matrix.csv`, `demand_gaji.csv`, `README.md` berisi metodologi lengkap).

### Cara dataset dibangun (bahan Bab Metodologi)

1. **Pengumpulan**: scraping halaman lowongan IT Indonesia (judul, deskripsi/requirements, info gaji). Sumber lain yang diuji namun gagal diakses dicatat di `data-loker-id/README.md`.
2. **Ekstraksi skill**: *keyword matching* 30 hard skill teknis (SQL, Python, JavaScript, Git, AWS, Agile, Linux, dst.) terhadap teks Requirements tiap lowongan; normalisasi varian penulisan.
3. **Skor 1–5**: untuk tiap jabatan *o* dan skill *s*, `skor(o,s) = 1 + 4 × (pct(o,s) / max_pct(o))` dengan `pct` = % lowongan jabatan *o* yang menyebut skill *s* (satu desimal, relatif per jabatan).
4. **Demand (C3)**: jumlah lowongan per jabatan, dinormalisasi min-max ke skala 1–10.
5. **Gaji (C2)**: dari info gaji yang tercantum di lowongan (median/min/max per jabatan, dalam juta Rp/bulan).
6. **Vektor CBF berbobot di kedua sisi**: skor 1–5 dipakai langsung sebagai entri vektor karier (tanpa threshold biner), sehingga nuansa tingkat kepentingan lestari. Vektor mahasiswa juga berbobot: tiap skill dinilai sendiri oleh mahasiswa dengan skala penguasaan 0 sampai 5 (0 = tidak menguasai, 5 = ahli) pada form profil, sehingga kedua vektor simetris. Simetri ini perbaikan bertahap atas model awal yang biner di kedua sisi (skill berskor 4.75 dan 3.50 disamakan 1.0, dan kedalaman penguasaan mahasiswa tidak tertangkap sama sekali).

### Tabel demand & gaji per jabatan (dari dataset)

| Karier | Demand (1-10) | Gaji (jt Rp/bln) | n lowongan | n gaji |
|--------|---------------|------------------|------------|--------|
| AI Engineer | 2 | 7-15 | 20 | 1 |
| Cybersecurity Analyst | 10 | 5-10 | 31 | 3 |
| Data Analyst | 1 | 6-6 | 18 | 1 |
| Database Administrator | 8 | 3-23 | 28 | 3 |
| Data Engineer | 9 | 5-6 | 29 | 1 |
| DevOps Engineer | 2 | 6-15 | 20 | 3 |
| Data Scientist | 6 | 11-15 | 25 | 1 |
| IT Project Manager | 2 | 5-12 | 20 | 2 |
| IT Support | 2 | 5-15* | 20 | 0 |
| Network Architect | 9 | 6-17 | 30 | 4 |
| Network Support | 2 | 5-10 | 20 | 8 |
| Programmer | 9 | 2-13 | 29 | 6 |
| QA Engineer | 9 | 15-25 | 30 | 1 |
| Security Engineer | 7 | 6-15 | 26 | 5 |
| Software Developer | 7 | 6-7 | 27 | 1 |
| System Administrator | 10 | 4-16 | 31 | 4 |
| System Analyst | 4 | 6-15 | 23 | 2 |
| UI/UX Designer | 8 | 5-12 | 28 | 7 |
| Web Developer | 5 | 4-40 | 24 | 4 |

\* **Imputasi, bukan observasi**: tidak satu pun lowongan IT Support mencantumkan gaji (n_gaji=0), sehingga rentang 5–15 jt diisi dari median 18 jabatan lain. Ditandai eksplisit di `seed.py` dan di sini.

### Keterbatasan dataset (bahan Bab Metodologi, ditulis jujur)

- Satu sumber (Indeed); sampel 18–31 lowongan per jabatan (kecil).
- Ekstraksi skill = *keyword matching*, bukan NLP.
- Mayoritas iklan berbahasa Inggris; hanya ±12% lowongan yang mencantumkan gaji.
- *Snapshot* Oktober 2026. Pasar kerja berubah seiring waktu, jadi *re-scraping* berkala disarankan.
- Validasi silang dengan Indotask (World Bank 2020) hanya kualitatif karena taksonomi skill berbeda; detailnya di `data-loker-id/README.md`.

Jalankan seed ulang kapan saja: `python seed.py` (idempoten: data master lama dihapus lalu diisi ulang dari CSV). Lihat docstring `seed.py` untuk dokumentasi lengkap.

## Analisis Sensitivitas

Halaman hasil menyediakan panel **Atur Bobot Kriteria**: mahasiswa mengisi bobot C1 sampai C4 (masing-masing 0 sampai 1) lalu menekan Hitung Ulang. Bobot kustom disimpan di sesi pengguna, bukan di data master, jadi bobot admin tetap menjadi nilai default untuk semua pengguna. Bila total bobot kustom bukan 1, sistem menormalisasikannya otomatis dan mencatatnya. Bobot yang benar-benar dipakai pada suatu perhitungan (setelah normalisasi) disimpan pada batch hasil, ditampilkan di halaman riwayat, dan disertakan sebagai baris metadata pada ekspor CSV, sehingga setiap hasil dapat ditelusuri bobotnya.

Untuk menguji seberapa stabil ranking terhadap perubahan bobot, jalankan:

```bash
python analysis/sensitivitas.py
```

Skrip ini mengevaluasi tiga profil contoh (Backend/Data, Jaringan, Frontend; tiap skill diberi rating penguasaan realistis 0 sampai 5) pada 6 skenario deterministik (dominasi tunggal tiap kriteria dan perturbasi C1 sebesar ±0,10) serta 200 sampel acak Dirichlet di sekitar bobot default (seed 42), memakai fungsi CBF dan SAW yang sama persis dengan aplikasi. Hasil ditulis ke `analysis/hasil_sensitivitas.md` (tabel dan kesimpulan, siap dikutip untuk Bab 4) dan `analysis/hasil_sensitivitas.csv`. Ringkasan hasil: peringkat pertama bertahan pada 91,6% skenario dan himpunan 3 besar utuh pada 74,6% skenario; perubahan terbesar terjadi pada skenario dominasi tunggal.
