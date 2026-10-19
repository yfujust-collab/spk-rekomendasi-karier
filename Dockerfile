# Citra Python ramping
FROM python:3.12-slim

# Tanpa buffering stdout agar log langsung terlihat di docker logs
ENV PYTHONUNBUFFERED=1 \
    FLASK_DEBUG=0 \
    HOST=0.0.0.0 \
    PORT=5000

WORKDIR /app

# Install dependensi dulu agar layer ini ter-cache bila kode berubah
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Data SQLite tinggal di volume agar tidak hilang saat container diganti
VOLUME ["/app/instance"]

EXPOSE 5000

# Jalankan seed sekali sebelum server nyala (idempoten, aman diulang)
CMD ["sh", "-c", "python seed.py && python run.py"]
