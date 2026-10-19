# SPK rekomendasi karier: panduan deploy

Aplikasi Flask ini siap deploy di dua target: VPS dengan Docker, atau
PythonAnywhere tanpa Docker. Keduanya memakai kode yang sama.

## Yang wajib diganti sebelum deploy

1. **Kredensial admin default** (`admin` / `admin123`): masuk sekali,
   lalu ganti kata sandi lewat kode atau langsung di database. Jangan
   biarkan kredensial default di server publik.
2. **SECRET_KEY**: set lewat environment variable (bukan nilai default
   di kode). Buat kunci acak yang panjang, mis.
   `python -c "import secrets; print(secrets.token_hex(32))"`.

## Opsi 1: VPS dengan Docker

Build citra:

```bash
docker build -t spk-karier .
```

Jalankan dengan volume agar database SQLite tidak hilang saat container
diganti:

```bash
docker run -d --name spk-karier -p 8000:5000 \
  -e SECRET_KEY="isi-kunci-acak-panjang" \
  -v spk-data:/app/instance \
  spk-karier
```

Container otomatis menjalankan `python seed.py` (idempoten, aman diulang)
lalu menyalakan server di port 5000.

### Pakai Postgres (opsional)

Bila ingin database terpisah, set `DATABASE_URL`, mis.

```bash
docker run -d --name spk-karier -p 8000:5000 \
  -e SECRET_KEY="isi-kunci-acak-panjang" \
  -e DATABASE_URL="postgresql+psycopg2://user:sandi@db/spk_karier" \
  spk-karier
```

Catatan: driver Postgres (`psycopg2`) tidak ada di `requirements.txt`;
tambahkan sendiri bila memakai opsi ini.

## Opsi 2: PythonAnywhere (tanpa Docker)

1. Upload seluruh file proyek (kecuali `venv/`, `__pycache__/`,
   `instance/`, `.env`) ke akun PythonAnywhere, mis. ke
   `/home/username/spk-rekomendasi-karier`.
2. Buka konsol Bash, buat virtualenv dan install dependensi:

   ```bash
   mkvirtualenv --python=/usr/bin/python3.12 spk-venv
   pip install -r requirements.txt
   ```
3. Seed database sekali:

   ```bash
   python seed.py
   ```
4. Di tab Web, buat aplikasi Flask baru, lalu atur WSGI file
   (`/var/www/username_pythonanywhere_com_wsgi.py`) menjadi:

   ```python
   import os, sys
   sys.path.insert(0, "/home/username/spk-rekomendasi-karier")
   os.chdir("/home/username/spk-rekomendasi-karier")
   from app import create_app
   application = create_app()
   ```
5. Di bagian Environment variables pada tab Web, set `SECRET_KEY`
   dengan kunci acak yang panjang. Ganti kredensial admin default
   segera setelah aplikasi bisa diakses.

## Periksa deploy berhasil

Buka URL aplikasi: halaman login muncul, masuk sebagai `admin`,
dasbor menampilkan 14 karier dan 4 kriteria. Daftarkan satu
akun mahasiswa, isi profil, dan pastikan halaman hasil menampilkan
peringkat 14 karier.
