"""Titik masuk aplikasi. Jalankan: python run.py

Variabel environment (opsional):
  HOST         antarmuka yang di-bind, default 127.0.0.1 (0.0.0.0 di Docker)
  PORT         port HTTP, default 5000
  FLASK_DEBUG  set "1" untuk mode debug lokal, default "0"
"""
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "1") == "1",
    )
