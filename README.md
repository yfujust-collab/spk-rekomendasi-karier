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

[Fitur](#fitur) · [Cara Jalan](#cara-jalan) · [Deploy](#deploy) · [Struktur](#struktur) · [Dataset](#dataset)

</div>

## Fitur

- **Autentikasi berbasis peran**: admin mengelola data, mahasiswa menerima rekomendasi.
- **Form profil mahasiswa**: nama, skill yang dikuasai, dan karier yang diminati.
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

## Diagram Perancangan

Diagram use case, flowchart, activity, sequence, class, DFD, dan ERD tersedia sebagai gambar. Khusus ERD: digenerate dari skema database aktual (SQLite hasil seed, via refleksi SQLAlchemy) memakai script `gen_erd_real.py`, bukan digambar manual, sehingga dijamin 1:1 dengan tabel yang dipakai aplikasi (setara fitur Designer di phpMyAdmin).

## Dataset

Data karier (19 profesi IT beserta skill, estimasi gaji, dan demand) diadaptasi dari **O*NET Database 31.0** milik U.S. Department of Labor, Employment and Training Administration (USDOL/ETA), lisensi **CC BY 4.0**. Ganti atau tambah data lewat panel admin sesuai kebutuhan penelitian, atau lewat `seed.py` (membaca langsung file CSV dataset).

### Atribusi (wajib dicantumkan, mis. di skripsi)

> Data karier diadaptasi dari O*NET 31.0 Database oleh U.S. Department of Labor, Employment and Training Administration (USDOL/ETA), digunakan di bawah lisensi CC BY 4.0. USDOL/ETA tidak menyetujui, mendukung, atau menguji modifikasi ini.

### Ringkasan adaptasi (bahan Bab Metodologi)

Data mentah O*NET berbahasa Inggris dan berkonteks pasar kerja Amerika Serikat, sehingga dilakukan adaptasi:

1. **Subset**: 19 okupasi bidang Informatika yang relevan bagi mahasiswa (dari 1.016 okupasi O*NET): 14 awal + 5 tambahan yang populer di loker Indonesia (IT Support, Data Analyst, AI Engineer, DevOps Engineer, Network Support).
2. **Nama tampil**: kolom `judul_id` memakai nama Inggris gaya job loker (mis. "Software Developer", "Data Analyst") karena itu sebutan yang dikenal mahasiswa; kolom `judul_en` menyimpan nama resmi O*NET sebagai referensi. Deskripsi dan nama skill diterjemahkan ke Bahasa Indonesia yang natural. Istilah teknologi yang merupakan nama proper (Python, SQL, Git, Docker, dsb.) dipertahankan karena bersifat universal.
3. **Kurasi skill Informatika untuk CBF**: dari 35 skill O*NET, dipilih 12 skill yang relevan dengan Jurusan Informatika (Pemrograman, Analisis Sistem, Evaluasi Sistem, Perancangan Teknologi, Pemecahan Masalah Kompleks, Berpikir Kritis, Matematika, Pemecahan Masalah Teknis, Analisis Operasional, Analisis Kendali Mutu, Pembelajaran Aktif, Penilaian & Pengambilan Keputusan). Skill teknisi/non-IT (mis. Pemilihan Peralatan, Instalasi, Perawatan Peralatan, Perbaikan) sengaja dikecualikan agar vektor CBF mencerminkan kompetensi Informatika. Memakai 35 skill sekaligus memberi cosine similarity 0.97-0.99 antar-karier IT (hampir identik, tidak bisa membedakan), sehingga kurasi ini juga berfungsi sebagai seleksi fitur.
4. **Threshold biner**: kolom `skills` di aplikasi ini berupa teks dipisah koma (vektor biner), sehingga bobot importance O*NET (skala 1-5) tidak bisa disimpan langsung. Skill dengan importance >= 3.0 (kategori "penting" ke atas) dicantumkan sebagai ciri khas karier; yang di bawahnya tidak. Ambang ini dipilih empiris: ambang 2.0 membuat 11 dari 14 karier bervektor identik, sedangkan 3.0 menghasilkan 18 vektor unik dari 19 karier (sebaran cosine 0.62-1.00). Satu-satunya pasangan identik adalah Programmer vs DevOps Engineer: nilai importance aslinya berbeda (mis. Pemrograman 4.75 vs 3.50) tetapi ambang biner menyamakan keduanya — keterbatasan model biner yang dicatat jujur di sini.
5. **Demand (C3)**: jumlah hot technology per karier dinormalisasi min-max ke skala 1-10.

### Catatan jujur tentang gaji (bahan Bab Metodologi)

O*NET tidak menyediakan data gaji; kolom estimasi gaji di `karier.csv` memang dikosongkan oleh pembangun dataset. Angka gaji pada tabel di bawah adalah estimasi pasar kerja Indonesia dalam juta rupiah per bulan (pola entry 4-7, mid 7-12, senior/spesialis 10-18, disesuaikan per peran), di-hardcode di `seed.py` dan diberi komentar eksplisit. Ganti dengan data survei gaji bila tersedia (mis. dataset Kaggle *AI-Powered Job Recommendations*). Bobot importance skill O*NET juga mencerminkan pasar Amerika Serikat, bukan Indonesia.

| # | Karier | Demand (1-10) | Estimasi gaji (jt Rp/bln) |
|---|--------|---------------|---------------------------|
| 1 | Software Developer | 10 | 5-12 |
| 2 | Programmer | 6 | 4-10 |
| 3 | Web Developer | 8 | 4-10 |
| 4 | UI/UX Designer | 7 | 4-10 |
| 5 | QA Engineer | 8 | 4-10 |
| 6 | Data Scientist | 3 | 6-14 |
| 7 | Data Engineer | 3 | 5-12 |
| 8 | Database Administrator | 7 | 5-10 |
| 9 | Cybersecurity Analyst | 6 | 5-13 |
| 10 | Security Engineer | 3 | 6-15 |
| 11 | Network Architect | 6 | 5-13 |
| 12 | System Administrator | 6 | 4-10 |
| 13 | System Analyst | 7 | 4-10 |
| 14 | IT Project Manager | 8 | 6-16 |
| 15 | IT Support | 7 | 4-8 |
| 16 | Data Analyst | 6 | 5-12 |
| 17 | AI Engineer | 4 | 7-18 |
| 18 | DevOps Engineer | 8 | 6-16 |
| 19 | Network Support | 1 | 4-10 |

Jalankan seed ulang kapan saja: `python seed.py` (idempoten: data master lama dihapus lalu diisi ulang dari CSV). Lihat docstring `seed.py` untuk dokumentasi adaptasi lengkap.
