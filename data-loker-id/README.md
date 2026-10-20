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
  22 jabatan. Pada perluasan ini rentang n tidak berubah (tetap 39–55), sehingga nilai
  ternormalisasi 19 jabatan lama faktanya tidak bergeser. Dicatat sebagai kaidah metodologi:
  normalisasi selalu dihitung atas seluruh jabatan yang aktif, jadi pada perluasan berikutnya
  nilai lama dapat bergeser bila rentang n berubah.

### 2. Ekstraksi skill (text mining berbasis NLP)

Sejak 20 Oktober 2026 ekstraksi skill memakai **pipeline NLP berbasis spaCy**
(`en_core_web_sm`, skrip `nlp_extract.py`), menggantikan pencocokan kata kunci
(keyword matching) fase awal. Kamus **30 skill dibakukan** (daftar di bawah) —
yang berubah hanya cara mendeteksi penyebutan skill pada tiap lowongan.
Demand dan gaji **tidak berubah**.

Pipeline per lowongan (judul + deskripsi):

1. **Normalisasi teks**: mojibake UTF-8 hasil scraping diperbaiki (apostrof
   yang tersimpan sebagai karakter kontrol dikembalikan ke `'`), token lengket
   dipisah ("HTML+CSS" → "HTML + CSS", "Rest&SOAP" → "Rest & SOAP",
   "Git(version" → "Git (version").
2. **Segmentasi seksi**: deskripsi dipecah berdasarkan penanda header
   (Requirements, Qualifications, Responsibilities, Job Description,
   What We're Looking For, Kualifikasi, Persyaratan, Tanggung Jawab, dst.).
   Skill hanya dihitung bila muncul di seksi **relevan** (persyaratan,
   kualifikasi, tanggung jawab, deskripsi pekerjaan); penyebutan yang hanya
   ada di seksi profil perusahaan (About Us, Tentang Kami, Who We Are) atau
   benefit **tidak dihitung**. Teks sebelum header pertama dianggap relevan
   (umumnya ringkasan peran); deskripsi tanpa header memakai seluruh teks
   (fallback). Judul lowongan selalu relevan.
3. **Pencocokan frasa sadar lemma**: 30 skill dicocokkan sebagai urutan token
   hasil tokenisasi spaCy dalam dua aliran kunci — lemma (menangkap variasi
   morfologis: "firewalls" → firewall, "APIs" → api) dan bentuk permukaan
   (jaring pengaman istilah teknis dan proper noun). Frasa multi-kata
   (REST API, SQL Server, Machine Learning, Artificial Intelligence, CI/CD,
   TCP/IP, Routing & Switching) dicocokkan sebagai satu frasa utuh. Aturan
   sadar POS untuk kata ambigu: "Go" hanya dihitung sebagai PROPN/NOUN (bukan
   kata kerja "go"), "Excel" gugur bila kata kerja ("excels at problem
   solving"), "REST" tunggal hanya bila tertulis ALL-CAPS ("the rest of the
   team" tidak dihitung). Untuk AI dipertahankan daftar frasa konteks
   ("artificial intelligence", "generative AI", "AI models", dsb.) karena
   kata "AI" mentah terbukti 65% kemunculannya adalah jargon profil
   perusahaan, bukan syarat skill.
4. **Deteksi negasi**: penyebutan dalam konteks negasi tidak dihitung —
   dependency `neg` spaCy yang sub-tree-nya mencakup frasa ("Docker is not
   required"; konstruksi "not limited to" dikecualikan), pola
   "no experience/knowledge (in|with|of) X", "without X"/"tanpa X", penanda
   yang menempel tepat sesudah frasa ("X is a plus", "X menjadi nilai
   tambah", "X (not required)", "X tidak wajib"), serta "tidak wajib/
   bukan syarat" tepat sebelum frasa. Skill dihitung bila ada ≥ 1 penyebutan
   sah (seksi relevan dan tidak ternegasi).

Hanya **hard skill teknis**; soft skill generik ("komunikasi", "kerja sama")
dikecualikan dari kamus.

**Validasi metode (keyword matching vs NLP).** Kedua metode dijalankan pada
korpus yang sama (1.045 lowongan × 30 skill = 31.350 sel lowongan-skill):

| Ukuran | Nilai |
|---|---:|
| Agreement rate | 99,68% (31.251 dari 31.350 sel sama) |
| Terdeteksi kedua metode | 3.182 sel |
| Hanya keyword matching | 98 sel (gugur oleh filter NLP) |
| Hanya NLP | 1 sel ("Postgre" → PostgreSQL; varian yang lolos dari regex) |

Rincian 98 sel yang gugur oleh NLP: **61 sel** bentuk ambigu regex yang bukan
penyebutan skill (kata kerja "go" pada "go beyond"/"go all in", akhiran
".js" pada "React.js"/"Next.js" yang tertangkap sebagai JavaScript,
"the rest of the team" sebagai REST, ".html" pada URL sebagai HTML, header
"WHERE YOU'LL GO"); **28 sel** konteks negasi/nilai tambah ("CI/CD is a
plus", "familiarity with Golang is a plus"); **5 sel** hanya muncul di seksi
tidak relevan; **4 sel** kata kerja "excel(s)". Profil top-3 skill per
jabatan praktis stabil: 20 dari 22 jabatan identik, 2 jabatan (Mobile
Developer, Programmer) hanya bertukar urutan internal dengan himpunan top-3
yang sama. Skor berubah pada 106 dari 660 sel (maksimum |Δ| = 1,0). Matriks
versi keyword matching diarsipkan lokal sebagai
`skill_matrix_keyword_matching.csv` (tidak dipublikasikan); rincian per sel
ada di `nlp_changes.csv` dan `nlp_vs_keyword.md`.

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

## 30 skill final (frekuensi dokumen hasil ekstraksi NLP, 1.045 lowongan)

SQL 249, Python 187, Git 186, JavaScript 163, REST API 128, Agile 126, MySQL 122,
PostgreSQL 121, Linux 118, AWS 117, CI/CD 114, React 111, Java 109, Docker 102,
Artificial Intelligence 101, HTML 100, PHP 99, CSS 97, Excel 90, GCP 87,
Azure 83, Firewall 82, Go 74, Kubernetes 73, SQL Server 69, Machine Learning 62,
TCP/IP 55, DNS 54, Laravel 54, Routing & Switching 50.

(Catatan: 30 skill ini awalnya dipilih sebagai frekuensi dokumen tertinggi pada
fase keyword matching — dibanding versi Indeed saja, VPN dan TypeScript terdesak
keluar oleh TCP/IP dan Laravel pada fase multi-sumber. Pada perluasan Fase 4
kamus dibakukan, bukan dipilih ulang, sehingga skor 19 jabatan lama tidak
berubah; pada peralihan ke ekstraksi NLP kamus yang sama dipertahankan.)

## Keterbatasan (jujur, untuk bab 3–5 skripsi)

1. **Dua sumber** (Indeed + Glints). Glints mencantumkan gaji lebih sering dan profil
   lowongannya lebih lokal, sementara Indeed adalah agregator lintas industri — bias
   platform tetap ada di masing-masing.
2. **Ukuran sampel per jabatan sedang** (39–55; tiga jabatan hasil perluasan 45–49).
   Cukup untuk peringkat relatif, belum untuk inferensi populasi.
3. **Bias query**: hasil pencarian portal memengaruhi komposisi sampel (mis. sampel
   "Software Developer" condong ke peran JavaScript/Node.js).
4. **Ekstraksi NLP tetap berbasis kamus** (spaCy + kamus 30 skill): sinonim dan
   teknologi di luar kamus tidak tertangkap; aturan negasi bersifat lokal —
   penanda "nilai tambah" pada daftar panjang (mis. "(AWS/GCP) is a plus")
   hanya menggugurkan skill yang tepat mendahuluinya; model bahasa Inggris
   dipakai juga untuk lowongan berbahasa Indonesia campuran.
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
> `scrape_indeed_new.py`, `scrape_glints_new.py`, `build_expand.py`, `nlp_extract.py`.

## Lisensi data

Data mentah (`raw/` + `raw_glints/`) adalah cuplikan halaman publik untuk keperluan penelitian —
**tidak dipublikasikan** dan tidak diunggah ke GitHub. Dataset bersih (agregat
statistik) bebas dipakai untuk skripsi ini dengan mencantumkan metodologi di atas.
