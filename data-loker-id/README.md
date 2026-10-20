# Dataset Lowongan IT Indonesia

Dataset primer untuk Sistem Pendukung Keputusan Rekomendasi Karier Mahasiswa Informatika.
Dibangun melalui **text mining lowongan kerja IT Indonesia** — menggantikan dataset O*NET (AS)
agar konteksnya sesuai pasar kerja Indonesia.

## Ringkasan

| Aspek | Nilai |
|---|---|
| Jumlah lowongan (N) | 1.066 (unik, setelah dedup lintas sumber) |
| Untuk text mining | 1.045 (deskripsi > 200 karakter) |
| Jabatan | 22 (IT, istilah job loker) |
| Skill final | 30 (hard skill teknis) |
| Sumber | id.indeed.com (554) + glints.com (550) — jumlah mentah sebelum dedup |
| Periode pengambilan | 19 jabatan awal: Indeed 19–20 Okt 2026, Glints 20 Okt 2026 (03:00–05:00 UTC) · perluasan 3 jabatan: 20 Okt 2026 |
| Cakupan wilayah | Indonesia |

### Sebaran per jabatan

| Jabatan | N lowongan | Indeed | Glints | N untuk mining |
|---|---|---|---|---|
| Software Developer | 49 | 26 | 23 | 49 |
| Programmer | 52 | 27 | 25 | 51 |
| Web Developer | 47 | 22 | 25 | 46 |
| UI/UX Designer | 51 | 27 | 25 | 50 |
| QA Engineer | 53 | 29 | 24 | 52 |
| Data Scientist | 48 | 23 | 25 | 48 |
| Data Engineer | 52 | 29 | 23 | 52 |
| Database Administrator | 52 | 27 | 25 | 51 |
| Cybersecurity Analyst | 54 | 30 | 24 | 53 |
| Security Engineer | 51 | 26 | 25 | 50 |
| Network Architect | 54 | 30 | 24 | 54 |
| System Administrator | 55 | 31 | 24 | 54 |
| System Analyst | 46 | 23 | 23 | 36 |
| IT Project Manager | 45 | 20 | 25 | 45 |
| IT Support | 45 | 20 | 25 | 45 |
| Data Analyst | 39 | 18 | 21 | 39 |
| AI Engineer | 45 | 20 | 25 | 45 |
| DevOps Engineer | 43 | 19 | 25 | 43 |
| Network Support | 45 | 20 | 25 | 45 |
| Frontend Developer | 45 | 23 | 22 | 45 |
| Backend Developer | 46 | 23 | 24 | 45 |
| Mobile Developer | 49 | 25 | 24 | 47 |

## File

- `skill_matrix.csv` — matriks 22 jabatan × 30 skill. Kolom: `kode_jabatan`, `nama_jabatan`,
  `skill`, `skor` (1–5, 1 desimal). 660 baris.
- `demand_gaji.csv` — per jabatan: `n_lowongan` (demand), `n_indeed`, `n_glints` (komposisi
  sumber), `n_gaji` (setelah cleaning), `n_gaji_indeed`, `n_gaji_glints`,
  `gaji_min_rp`, `gaji_max_rp`, `gaji_median_rp` (IDR/bulan).
- `raw/`, `raw_glints/` — data mentah hasil scraping (tidak untuk publikasi, lihat Keterbatasan).
- `scrape.py`, `retry_scrape.py`, `build_dataset.py`, `scrape_glints.py`, `build_merged.py`,
  `scrape_indeed_new.py`, `scrape_glints_new.py`, `build_expand.py` — skrip reproduksibel
  (urutan: scraping per sumber → merge dengan `build_merged.py`; perluasan jabatan baru
  dengan `scrape_*_new.py` → `build_expand.py`).

## Metodologi

### 1. Pengumpulan data

**Sumber 1 — id.indeed.com.** Lowongan dikumpulkan dari situs agregator lowongan (halaman
HTML publik) dengan pencarian kata kunci per jabatan (contoh: `"software developer"`,
`"data analyst"`; lihat `scrape.py` untuk daftar lengkap query primer + cadangan). Setiap
lowongan diambil halaman detailnya untuk teks deskripsi/requirements lengkap.

Pengambilan dilakukan sopan: delay 2–4 detik antar request (6–10 detik pada retry),
user-agent browser wajar. Ketika Indeed mulai memutus koneksi (HTTP IncompleteRead) setelah
±350 request, pengambilan dihentikan dan 6 jabatan yang belum terisi dilengkapi keesokan
harinya dengan delay lebih panjang (`retry_scrape.py`).

**Sumber 2 — glints.com.** Lowongan dikumpulkan melalui API GraphQL internal Glints
(`searchJobsV3`: judul, perusahaan, kota, gaji, tipe pekerjaan) memakai **akun pengguna
sendiri dengan persetujuan eksplisit** (bukan dataset lama JobWorthPredictor — data itu
sengaja tidak dipakai sama sekali atas permintaan pemilik data). Query yang sama dengan
Indeed, target 25 lowongan per jabatan.

Deskripsi tiap lowongan diambil dari halaman detail (`/id/opportunities/jobs/{id}`),
teksnya diekstrak dari field `description` JSON-LD `JobPosting` (Schema.org). Delay 3–6
detik antar halaman detail, 4–8 detik antar pencarian; UA browser wajar; proses berhenti
sopan jika kena block berulang. Jaringan ke Glints sempat tidak stabil (TLS handshake
timeout berulang) — skrip dibuat dapat di-*resume* (baris disimpan per jabatan, baris
yang sudah lengkap dilewati), sehingga total waktu pengambilan ±2 jam.

Sumber lain yang **diuji tetapi tidak dipakai** (dicatat agar transparan):
- JobStreet Indonesia — proteksi anti-bot (Cloudflare).
- KarierHub (Kemnaker) — tidak dapat dijangkau dari jaringan penelitian.
- Tech in Asia Jobs, LinkedIn — butuh JavaScript/login.

### 1b. Dedup lintas sumber

28 lowongan muncul di kedua portal (dihitung sekali): kunci dedup = judul + nama
perusahaan yang dinormalisasi (lowercase, non-alfanumerik dibuang). Dari kelompok
duplikat, disimpan record dengan deskripsi terpanjang; field gaji digabung dari semua
duplikat (ambil yang non-kosong). Setelah dedup: **926 lowongan unik** (479 Indeed +
475 Glints) — angka korpus sebelum perluasan Fase 4 (lihat sub-bab 1c).
Keterbatasan: variasi penulisan nama perusahaan yang jauh berbeda
(mis. "PT X" vs "X Corp") bisa lolos dari dedup — jumlah duplikat aktual mungkin sedikit
lebih besar.

### 1c. Perluasan cakupan (Fase 4 dataset)

20 Oktober 2026: cakupan diperluas dari 19 menjadi **22 jabatan** dengan menambah tiga
jabatan yang selama ini tertelan kategori umum ("Software Developer" / "Programmer"):
**Frontend Developer** (FEDEV), **Backend Developer** (BEDEV), dan **Mobile Developer**
(MOBDEV).

- Scraping fresh dari kedua sumber dengan metode dan query yang sama persis dengan fase
  sebelumnya: Indeed 75 lowongan (25 per jabatan), Glints 75 lowongan (25 per jabatan);
  setelah dedup lintas sumber: **140 lowongan unik** (10 duplikat dibuang), 137 di antaranya
  berdeskripsi substansial dan dipakai untuk mining.
- **Kamus 30 skill dibakukan, tidak dipilih ulang**: ketiga jabatan baru diskor terhadap
  kamus yang sama, sehingga skor 19 jabatan lama **tidak berubah sama sekali** (terverifikasi
  dengan diff sebelum/sesudah — 570 baris identik).
- Total korpus kini **1.066 lowongan unik** (1.045 untuk mining). Per jabatan baru:
  Frontend 45 (I:23, G:22, n_gaji 16, median Rp8,5 jt), Backend 46 (I:23, G:24, n_gaji 20,
  median Rp8,5 jt), Mobile 49 (I:25, G:24, n_gaji 12, median Rp6,0 jt).
- **Normalisasi demand dihitung ulang**: demand skala 1–10 (min-max di `seed.py`) kini atas
  22 jabatan. Rentang n tetap 39–55 sehingga pergeseran nilai ternormalisasi kecil, tetapi
  nilai demand beberapa jabatan lama dapat bergeser 1 poin karena himpunan pembandingnya
  berubah. Ini diperlakukan eksplisit sebagai perubahan metodologi, bukan koreksi data.

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

- **Demand** = jumlah lowongan unik per jabatan (setelah dedup lintas sumber).
- **Gaji**: diambil dari field gaji terstruktur tiap portal (Indeed: `salaryMin`/`salaryMax`
  + teks gaji; Glints: `salaries.minAmount`/`maxAmount`). Cleaning: (a) gaji "per tahun"
  dikonversi ke bulanan (÷12); (b) nilai < Rp2 juta/bulan dibuang sebagai noise salah input;
  (c) lowongan magang/intern dikecualikan dari statistik gaji (segmen pasar berbeda).
  Glints mencantumkan gaji jauh lebih sering dari Indeed, sehingga n_gaji per jabatan naik
  dari 0–8 (Indeed saja) menjadi **16–26** per jabatan (gabungan). Median tetap harus dibaca
  bersama kolom `n_gaji`/`n_gaji_indeed`/`n_gaji_glints` sebagai indikator keandalan.
  Contoh efeknya: median QA Engineer berubah dari Rp25,0 jt (n=1, tidak stabil) menjadi
  Rp5,1 jt (n=18); IT Support yang sebelumnya tanpa data gaji kini memiliki n_gaji=17
  (semua dari Glints, median Rp5,0 jt).

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

## 30 skill final (frekuensi dokumen, data gabungan 1.045 lowongan)

SQL 250, Python 190, Git 190, JavaScript 189, REST API 137, Agile 129, MySQL 122,
PostgreSQL 120, Linux 118, AWS 117, CI/CD 117, React 111, Java 110,
Artificial Intelligence 104, Docker 102, HTML 102, PHP 100, Go 100, CSS 97,
Excel 94, GCP 92, Azure 84, Firewall 83, SQL Server 73, Kubernetes 73,
Machine Learning 62, TCP/IP 55, Laravel 55, DNS 54, Routing & Switching 50.

(Catatan: dibanding versi Indeed saja, VPN dan TypeScript terdesak keluar oleh
TCP/IP dan Laravel pada fase multi-sumber. Pada perluasan Fase 4, kamus 30 skill ini
dibakukan — bukan dipilih ulang dari korpus yang lebih besar — sehingga skor 19 jabatan
lama tidak berubah.

## Keterbatasan (jujur, untuk bab 3–5 skripsi)

1. **Dua sumber** (Indeed + Glints). Glints mencantumkan gaji lebih sering dan profil
   lowongannya lebih lokal, sementara Indeed adalah agregator lintas industri — bias
   platform tetap ada di masing-masing.
2. **Ukuran sampel per jabatan sedang** (39–55; tiga jabatan hasil perluasan 45–49).
   Cukup untuk peringkat relatif, belum untuk inferensi populasi.
3. **Bias query**: hasil pencarian portal memengaruhi komposisi sampel (mis. sampel
   "Software Developer" condong ke peran JavaScript/Node.js).
4. **Ekstraksi = pencocokan kata kunci**, bukan NLP. Sinonim di luar kamus tidak
   tertangkap; konteks negasi ("tidak wajib menguasai X") tidak dibedakan.
5. **Iklan berbahasa Inggris dominan**; lowongan berbahasa Indonesia penuh mungkin
   kurang terwakili karena kata kunci pencarian berbahasa Inggris.
6. **Dedup lintas sumber tidak sempurna** — varian nama perusahaan yang sangat berbeda
   bisa lolos, sehingga N sedikit over-estimated.
7. **Snapshot waktu**: pasar kerja IT bergerak cepat; dataset ini potret 19–20 Okt 2026
   (termasuk perluasan 3 jabatan pada 20 Okt 2026).

## Sitasi yang disarankan

> Dataset Lowongan IT Indonesia v3 (2026). Dibangun melalui text mining 1.066 lowongan
> kerja IT unik dari id.indeed.com (554) dan glints.com (550, jumlah mentah sebelum dedup),
> periode 19–20 Okt 2026: 22 jabatan × 30 skill, skor 1–5 ternormalisasi per jabatan. Skrip:
> `scrape.py`, `retry_scrape.py`, `scrape_glints.py`, `build_merged.py`,
> `scrape_indeed_new.py`, `scrape_glints_new.py`, `build_expand.py`.

## Lisensi data

Data mentah (`raw/` + `raw_glints/`) adalah cuplikan halaman publik untuk keperluan penelitian —
**tidak dipublikasikan** dan tidak diunggah ke GitHub. Dataset bersih (agregat
statistik) bebas dipakai untuk skripsi ini dengan mencantumkan metodologi di atas.
