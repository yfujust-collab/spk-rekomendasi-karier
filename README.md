<div align="center">

# **SPK Rekomendasi Karier**

Sistem pendukung keputusan berbasis web untuk merekomendasikan karier mahasiswa Informatika.

*Content-Based Filtering bertemu Simple Additive Weighting dalam satu alur yang transparan.*

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![License](https://img.shields.io/badge/License-MIT-green)

| Metode | Peran |
|---|---|
| Content-Based Filtering | Mengukur kecocokan skill (cosine similarity) |
| Simple Additive Weighting | Memberi peringkat akhir dari 4 kriteria berbobot |

[Fitur](#fitur) · [Cara Jalan](#cara-jalan) · [Deploy](#deploy) · [Struktur](#struktur) · [Dataset](#dataset)

</div>

## Fitur

- **Autentikasi berbasis peran**: admin mengelola data, mahasiswa menerima rekomendasi.
- **Form profil mahasiswa**: skill yang dikuasai, karier yang diminati, IPK.
- **Perhitungan dua tahap**: CBF untuk skor kecocokan skill, SAW untuk peringkat akhir.
- **Transparansi penuh**: halaman hasil menampilkan matriks keputusan, matriks ternormalisasi, dan skor preferensi tiap karier, plus grafik Chart.js.
- **Riwayat perhitungan**: setiap perhitungan disimpan sebagai batch tersendiri; hasil lama bisa dibuka ulang tanpa tertimpa.
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
```

## Dataset

Data karier (14 profesi IT beserta skill, estimasi gaji, dan demand) diadaptasi dari **O*NET Database 31.0** milik U.S. Department of Labor, Employment and Training Administration (USDOL/ETA), lisensi **CC BY 4.0**. Ganti atau tambah data lewat panel admin sesuai kebutuhan penelitian, atau lewat `seed.py` (membaca langsung file CSV dataset).

### Atribusi (wajib dicantumkan, mis. di skripsi)

> Data karier diadaptasi dari O*NET 31.0 Database oleh U.S. Department of Labor, Employment and Training Administration (USDOL/ETA), digunakan di bawah lisensi CC BY 4.0. USDOL/ETA tidak menyetujui, mendukung, atau menguji modifikasi ini.

### Ringkasan adaptasi (bahan Bab Metodologi)

Data mentah O*NET berbahasa Inggris dan berkonteks pasar kerja Amerika Serikat, sehingga dilakukan adaptasi:

1. **Subset**: 14 okupasi bidang Informatika yang relevan bagi mahasiswa (dari 1.016 okupasi O*NET).
2. **Penerjemahan**: judul, deskripsi, dan nama skill diterjemahkan ke Bahasa Indonesia yang natural. Istilah teknologi yang merupakan nama proper (Python, SQL, Git, Docker, dsb.) dipertahankan karena bersifat universal.
3. **Seleksi fitur untuk CBF**: memakai 35 skill sekaligus memberi cosine similarity 0.97-0.99 antar-karier IT (hampir identik, tidak bisa membedakan). Dipakai 12 skill dengan variansi importance tertinggi antar-karier ("seleksi fitur berbasis variansi"): Matematika, Analisis Operasional, Pemilihan Peralatan, Instalasi, Pemrograman, Pemantauan Operasional, Operasi dan Kendali, Perawatan Peralatan, Pemecahan Masalah Teknis, Perbaikan, Analisis Kendali Mutu, Pengelolaan SDM.
4. **Threshold biner**: kolom `skills` di aplikasi ini berupa teks dipisah koma (vektor biner), sehingga bobot importance O*NET (skala 1-5) tidak bisa disimpan langsung. Skill dengan importance >= 2.0 dicantumkan sebagai ciri khas karier; yang di bawahnya tidak. Tanpa langkah ini semua karier punya vektor identik dan skor CBF tidak bervariasi antar-karier.
5. **Demand (C3)**: jumlah hot technology per karier dinormalisasi min-max ke skala 1-10.

### Catatan jujur tentang gaji (bahan Bab Metodologi)

O*NET tidak menyediakan data gaji; kolom estimasi gaji di `karier.csv` memang dikosongkan oleh pembangun dataset. Angka gaji pada tabel di bawah adalah estimasi pasar kerja Indonesia dalam juta rupiah per bulan (pola entry 4-7, mid 7-12, senior/spesialis 10-18, disesuaikan per peran), di-hardcode di `seed.py` dan diberi komentar eksplisit. Ganti dengan data survei gaji bila tersedia (mis. dataset Kaggle *AI-Powered Job Recommendations*). Bobot importance skill O*NET juga mencerminkan pasar Amerika Serikat, bukan Indonesia.

| # | Karier | Demand (1-10) | Estimasi gaji (jt Rp/bln) |
|---|--------|---------------|---------------------------|
| 1 | Pengembang Perangkat Lunak | 10 | 5-12 |
| 2 | Programmer Komputer | 5 | 4-10 |
| 3 | Pengembang Web | 7 | 4-10 |
| 4 | Desainer Antarmuka Web & Digital | 7 | 4-10 |
| 5 | Analis & Penguji QA Perangkat Lunak | 8 | 4-10 |
| 6 | Ilmuwan Data | 1 | 6-14 |
| 7 | Spesialis Data Warehouse | 2 | 5-12 |
| 8 | Administrator Database | 6 | 5-10 |
| 9 | Analis Keamanan Informasi | 5 | 5-13 |
| 10 | Insinyur Keamanan Informasi | 1 | 6-15 |
| 11 | Arsitek Jaringan Komputer | 5 | 5-13 |
| 12 | Administrator Sistem Jaringan & Komputer | 5 | 4-10 |
| 13 | Analis Sistem Komputer | 7 | 4-10 |
| 14 | Manajer Proyek TI | 7 | 6-16 |

Jalankan seed ulang kapan saja: `python seed.py` (idempoten: data master lama dihapus lalu diisi ulang dari CSV). Lihat docstring `seed.py` untuk dokumentasi adaptasi lengkap.
