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

[Fitur](#fitur) · [Cara Jalan](#cara-jalan) · [Struktur](#struktur) · [Dataset](#dataset)

</div>

## Fitur

- **Autentikasi berbasis peran**: admin mengelola data, mahasiswa menerima rekomendasi.
- **Form profil mahasiswa**: skill yang dikuasai, karier yang diminati, IPK.
- **Perhitungan dua tahap**: CBF untuk skor kecocokan skill, SAW untuk peringkat akhir.
- **Transparansi penuh**: halaman hasil menampilkan matriks keputusan, matriks ternormalisasi, dan skor preferensi tiap karier, plus grafik Chart.js.
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

Data karier awal (10 profesi IT beserta skill, estimasi gaji, dan demand) diadaptasi dari **O*NET Database** milik U.S. Department of Labor (lisensi Creative Commons). Ganti atau tambah data lewat panel admin sesuai kebutuhan penelitian.

### Adaptasi Dataset O*NET (bahan Bab Metodologi)

Data asli O*NET berbahasa Inggris dan berkonteks pasar kerja Amerika Serikat, sehingga dilakukan empat langkah adaptasi sebelum dipakai:

1. **Penerjemahan**: nama karier, deskripsi, dan nama skill diterjemahkan ke Bahasa Indonesia yang natural. Istilah teknologi yang merupakan nama proper (Python, SQL, Git, Docker, dsb.) dipertahankan karena bersifat universal.
2. **Penyesuaian gaji**: estimasi gaji diubah ke rentang Rupiah yang wajar untuk pasar Indonesia (juta rupiah per bulan).
3. **Penyesuaian demand**: tingkat kebutuhan pasar (skala 1-10) disesuaikan dengan kondisi industri teknologi Indonesia.
4. **Subset**: diambil 10 profesi bidang Informatika yang paling relevan bagi mahasiswa.

Lihat dokumentasi lengkap adaptasi di docstring `seed.py`.
