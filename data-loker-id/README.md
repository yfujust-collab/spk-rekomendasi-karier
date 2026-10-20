# Dataset Lowongan IT Indonesia

Dataset primer untuk Sistem Pendukung Keputusan Rekomendasi Karier Mahasiswa Informatika.
Dibangun melalui **text mining lowongan kerja IT Indonesia** — menggantikan dataset O*NET (AS)
agar konteksnya sesuai pasar kerja Indonesia.

## Ringkasan

| Aspek | Nilai |
|---|---|
| Jumlah lowongan (N) | 479 (unik, setelah dedup URL) |
| Untuk text mining | 456 (deskripsi > 200 karakter) |
| Jabatan | 19 (IT, istilah job loker) |
| Skill final | 30 (hard skill teknis) |
| Sumber | id.indeed.com |
| Periode pengambilan | 19–20 Oktober 2026 (23:00 UTC – 01:30 UTC; 06:00–08:30 WIB 20 Okt 2026) |
| Cakupan wilayah | Indonesia (filter lokasi "Indonesia") |

### Sebaran per jabatan

| Jabatan | N lowongan | N untuk mining |
|---|---|---|
| Software Developer | 27 | 26 |
| Programmer | 29 | 26 |
| Web Developer | 24 | 21 |
| UI/UX Designer | 28 | 27 |
| QA Engineer | 30 | 29 |
| Data Scientist | 25 | 24 |
| Data Engineer | 29 | 29 |
| Database Administrator | 28 | 27 |
| Cybersecurity Analyst | 31 | 29 |
| Security Engineer | 26 | 25 |
| Network Architect | 30 | 30 |
| System Administrator | 31 | 31 |
| System Analyst | 23 | 14 |
| IT Project Manager | 20 | 20 |
| IT Support | 20 | 20 |
| Data Analyst | 18 | 18 |
| AI Engineer | 20 | 20 |
| DevOps Engineer | 20 | 20 |
| Network Support | 20 | 20 |

## File

- `skill_matrix.csv` — matriks 19 jabatan × 30 skill. Kolom: `kode_jabatan`, `nama_jabatan`,
  `skill`, `skor` (1–5, 1 desimal). 570 baris.
- `demand_gaji.csv` — per jabatan: `n_lowongan` (demand), `n_gaji_mentah`, `n_gaji` (setelah
  cleaning), `gaji_min_rp`, `gaji_max_rp`, `gaji_median_rp` (IDR/bulan).
- `raw/` — data mentah hasil scraping (tidak untuk publikasi, lihat Keterbatasan).
- `scrape.py`, `retry_scrape.py`, `build_dataset.py` — skrip reproduksibel.

## Metodologi

### 1. Pengumpulan data

Lowongan dikumpulkan dari **id.indeed.com** (situs agregator lowongan, halaman HTML publik)
dengan pencarian kata kunci per jabatan (contoh: `"software developer"`, `"data analyst"`;
lihat `scrape.py` untuk daftar lengkap query primer + cadangan). Setiap lowongan diambil
halaman detailnya untuk teks deskripsi/requirements lengkap.

Pengambilan dilakukan sopan: delay 2–4 detik antar request (6–10 detik pada retry),
user-agent browser wajar. Ketika Indeed mulai memutus koneksi (HTTP IncompleteRead) setelah
±350 request, pengambilan dihentikan dan 6 jabatan yang belum terisi dilengkapi keesokan
harinya dengan delay lebih panjang (`retry_scrape.py`).

Sumber lain yang **diuji tetapi tidak dipakai** (dicatat agar transparan):
- Glints — data lowongan di-render via GraphQL API privat (butuh header sesi internal);
  tidak di-reverse-engineer lebih jauh.
- JobStreet Indonesia — proteksi anti-bot (Cloudflare).
- KarierHub (Kemnaker) — tidak dapat dijangkau dari jaringan penelitian.
- Tech in Asia Jobs, LinkedIn — butuh JavaScript/login.
- Data Glints milik peneliti (repo JobWorthPredictor) **sengaja tidak dipakai** atas
  permintaan pemilik data (menghindari bias dataset ganda).

### 2. Ekstraksi skill (text mining)

Pendekatan: **pencocokan kamus (dictionary-based keyword matching)** terhadap gabungan
teks judul + deskripsi lowongan (case-insensitive, word boundary).

- Kamus awal: ±80 pola regex mencakup bahasa pemrograman, framework, database, tools
  DevOps/cloud, keamanan, jaringan, dan metode kerja. Normalisasi varian ejaan
  ("JS"→JavaScript, "React.js"→React, "Golang"→Go, "K8s"→Kubernetes, dsb.).
- Hanya **hard skill teknis**; soft skill generik ("komunikasi", "kerja sama") dikecualikan.
- Kasus khusus: kata "AI" saja terbukti 65% kemunculannya adalah jargon deskripsi
  perusahaan ("we are an AI company"), bukan syarat skill — sehingga pola "AI" mentah
  dibuang dan diganti pola konteks-spesifik ("AI models", "AI algorithms", "generative AI",
  "artificial intelligence", dsb.).
- **Kriteria skill final**: 30 skill dengan frekuensi dokumen tertinggi di seluruh korpus
  (rentang 22–104 lowongan per skill). Daftar lengkap + frekuensi: lihat tabel di bawah.

### 3. Rumus skor (1–5)

Analog dengan skala importance O*NET (1 = tidak penting, 5 = sangat penting), tetapi
dihitung dari data Indonesia. Untuk tiap jabatan *o* dan skill *s*:

```
pct(o,s)  = 100 × (jumlah lowongan jabatan o yang menyebut skill s)
                  / (jumlah lowongan jabatan o yang memiliki deskripsi)

skor(o,s) = 1 + 4 × ( pct(o,s) / max_pct(o) )
```

dengan `max_pct(o)` = pct tertinggi di jabatan *o*. Skor dibulatkan 1 desimal.
Skor bersifat **relatif dalam satu jabatan** (skill paling sering disebut = 5,0);
perbandingan antar-jabatan memakai peringkat, bukan angka mentah.

### 4. Demand dan gaji

- **Demand** = jumlah lowongan per jabatan apa adanya (N per jabatan pada tabel di atas).
- **Gaji**: diambil dari field gaji terstruktur Indeed (`salaryMin`/`salaryMax`) dan teks
  gaji ("RpX – RpY"). Cleaning: (a) gaji "per tahun" dikonversi ke bulanan (÷12);
  (b) nilai < Rp2 juta/bulan dibuang sebagai noise salah input; (c) lowongan magang/intern
  dikecualikan dari statistik gaji (segmen pasar berbeda). `n_gaji_mentah` = sebelum
  cleaning, `n_gaji` = sesudah. Hanya ±12% lowongan mencantumkan gaji — median dengan
  n kecil dilaporkan apa adanya (kolom `n_gaji` menunjukkan keandalannya).

### 5. Validasi silang: Indotask (World Bank, 2020)

"Indonesia's Occupational Tasks and Skills 2020" (Indotask) adalah survei pilot World Bank
yang mereplikasi modul O*NET untuk 51 okupasi Indonesia, termasuk *Software developers*
(hal. 42, skor importance 1–5). Perbandingan kualitatif:

- Selaras: *Programming* (Indotask 3,9/5) ↔ Python/JavaScript/Java dominan di hasil mining;
  *Systems Analysis* (4,0), *Technology Design* (4,0) ↔ tumpukan teknologi web/data yang
  tinggi.
- Berbeda: skill teratas Indotask adalah *Troubleshooting* (4,5), *Installation* (4,3),
  *Repairing* (4,1) — karena sampel "Software developers" mereka mencakup jabatan
  *Software Technician*. Hasil mining (dari iklan lowongan) mencerminkan **syarat rekrutmen
  eksplisit**, bukan penilaian pekerja.
- Keterbatasan validasi: taksonomi skill berbeda (Indotask memakai 35 skill umum O*NET,
  dataset ini memakai 30 hard skill teknis), sehingga perbandingan hanya kualitatif.

## 30 skill final (frekuensi dokumen)

SQL 104, Python 98, JavaScript 76, Git 59, AWS 55, Agile 55, Linux 54,
Artificial Intelligence 53, PHP 50, HTML 50, Excel 44, Azure 44, Java 43, MySQL 43,
Firewall 43, CSS 42, CI/CD 42, GCP 42, Go 35, REST API 34, React 33, Docker 33,
Machine Learning 32, PostgreSQL 30, Kubernetes 29, VPN 25, SQL Server 24,
Routing & Switching 24, TypeScript 22, DNS 22.

## Keterbatasan (jujur, untuk bab 3–5 skripsi)

1. **Satu sumber** (id.indeed.com). Agregator ini menampung lintas industri, tetapi
   bias platform tetap ada (mis. startup teknologi over-represented).
2. **Ukuran sampel per jabatan kecil** (18–31). Cukup untuk peringkat relatif, belum
   untuk inferensi populasi.
3. **Bias query**: hasil pencarian Indeed memengaruhi komposisi sampel (mis. sampel
   "Software Developer" condong ke peran JavaScript/Node.js).
4. **Ekstraksi = pencocokan kata kunci**, bukan NLP. Sinonim di luar kamus tidak
   tertangkap; konteks negasi ("tidak wajib menguasai X") tidak dibedakan.
5. **Iklan berbahasa Inggris dominan**; lowongan berbahasa Indonesia penuh mungkin
   kurang terwakili karena kata kunci pencarian berbahasa Inggris.
6. **Gaji jarang dicantumkan** (±12%); median gaji dengan n kecil tidak stabil —
   gunakan kolom `n_gaji` sebagai indikator keandalan.
7. **Snapshot waktu**: pasar kerja IT bergerak cepat; dataset ini potret Oktober 2026.

## Sitasi yang disarankan

> Dataset Lowongan IT Indonesia (2026). Dibangun melalui text mining 479 lowongan kerja
> IT dari id.indeed.com (19 jabatan × 30 skill, skor 1–5 ternormalisasi per jabatan).
> Skrip: `scrape.py`, `build_dataset.py`.

## Lisensi data

Data mentah (`raw/`) adalah cuplikan halaman publik untuk keperluan penelitian —
**tidak dipublikasikan** dan tidak diunggah ke GitHub. Dataset bersih (agregat
statistik) bebas dipakai untuk skripsi ini dengan mencantumkan metodologi di atas.
