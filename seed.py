"""Isi database awal: admin, 10 karier IT, 4 kriteria SAW.

ADAPTASI DATASET O*NET (bahan Bab Metodologi):
Sumber: O*NET Database 31.0 milik U.S. Department of Labor (lisensi Creative
Commons, unduh gratis dari onetcenter.org). Data asli berbahasa Inggris dan
berkonteks pasar kerja Amerika Serikat, sehingga dilakukan adaptasi:
  1. Penerjemahan: seluruh nama karier, deskripsi, dan nama skill
     diterjemahkan ke Bahasa Indonesia yang natural. Istilah teknologi yang
     merupakan nama proper (Python, SQL, Git, Docker, dsb.) dipertahankan
     sebagaimana aslinya karena bersifat universal.
  2. Penyesuaian gaji: estimasi gaji diubah ke rentang Rupiah yang wajar
     untuk pasar kerja Indonesia (dinyatakan dalam juta rupiah per bulan).
  3. Penyesuaian demand: tingkat kebutuhan pasar (skala 1-10) disesuaikan
     dengan kondisi industri teknologi Indonesia.
  4. Subset: diambil 10 profesi bidang Informatika yang paling relevan
     bagi mahasiswa.
"""
from app import create_app, db
from app.models import Career, Criterion, User

KARIER = [
    (
        "Pengembang Perangkat Lunak",
        "Membangun dan memelihara aplikasi perangkat lunak.",
        "Python, Java, Git, SQL",
        5, 12, 9,
    ),
    (
        "Ilmuwan Data",
        "Menganalisis data untuk menghasilkan wawasan bisnis.",
        "Python, SQL, Pembelajaran Mesin, Statistika",
        6, 14, 9,
    ),
    (
        "Insinyur DevOps",
        "Mengelola alur peluncuran aplikasi dan infrastruktur komputasi awan.",
        "Docker, Kubernetes, Linux, CI/CD",
        6, 13, 8,
    ),
    (
        "Analis Keamanan Siber",
        "Melindungi sistem dari serangan siber.",
        "Keamanan Jaringan, Python, SIEM, Linux",
        6, 14, 9,
    ),
    (
        "Pengembang Web Frontend",
        "Membangun antarmuka web yang interaktif.",
        "HTML, CSS, JavaScript, React",
        4, 10, 8,
    ),
    (
        "Pengembang Aplikasi Mobile",
        "Membangun aplikasi Android dan iOS.",
        "Kotlin, Swift, Flutter, Java",
        5, 11, 7,
    ),
    (
        "Administrator Basis Data",
        "Mengelola dan mengamankan basis data.",
        "SQL, PostgreSQL, Pencadangan, Linux",
        5, 10, 6,
    ),
    (
        "Insinyur Pembelajaran Mesin",
        "Membangun model pembelajaran mesin untuk produksi.",
        "Python, TensorFlow, Pembelajaran Mendalam, SQL",
        7, 15, 8,
    ),
    (
        "Analis Sistem",
        "Menganalisis kebutuhan dan merancang solusi sistem.",
        "UML, SQL, Analisis Bisnis, Python",
        4, 9, 6,
    ),
    (
        "Pengembang Game",
        "Membangun permainan video 2D dan 3D.",
        "C#, Unity, C++, Git",
        5, 12, 6,
    ),
]

KRITERIA = [
    ("C1", "Kecocokan skill (CBF)", 0.35),
    ("C2", "Prospek gaji", 0.25),
    ("C3", "Demand pasar", 0.20),
    ("C4", "Kesesuaian minat", 0.20),
]


def main():
    app = create_app()
    with app.app_context():
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", nama="Administrator", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            print("Akun admin dibuat (admin / admin123).")

        for nama, deskripsi, skills, gmin, gmax, demand in KARIER:
            if not Career.query.filter_by(nama=nama).first():
                db.session.add(
                    Career(
                        nama=nama,
                        deskripsi=deskripsi,
                        skills=skills,
                        gaji_min=gmin,
                        gaji_max=gmax,
                        demand=demand,
                    )
                )
        print(f"{len(KARIER)} data karier disiapkan.")

        for kode, nama, bobot in KRITERIA:
            if not Criterion.query.filter_by(kode=kode).first():
                db.session.add(Criterion(kode=kode, nama=nama, bobot=bobot))
        print(f"{len(KRITERIA)} kriteria disiapkan.")

        db.session.commit()
        print("Seed selesai.")


if __name__ == "__main__":
    main()
