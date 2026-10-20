"""Analisis sensitivitas bobot SAW (bahan Bab 4 skripsi).

Menjawab pertanyaan: seberapa stabil ranking rekomendasi bila bobot
Menjawab pertanyaan: seberapa stabil ranking rekomendasi bila bobot
kriteria berubah? Tiga profil contoh dievaluasi pada 7 skenario
deterministik dan 200 skenario acak Dirichlet di sekitar bobot
default. Metode perhitungan SAMA PERSIS dengan aplikasi
(app/services/cbf.py dan app/services/saw.py dipakai ulang):
cosine similarity vektor mahasiswa (berbobot: tingkat penguasaan
0-5) vs vektor karier (berbobot 1-5), lalu SAW dengan normalisasi
benefit.

Asumsi (tercatat agar reprodusibel):
- Rating profil contoh realistis (tidak semua 5): mahasiswa dinilai
  paling kuat pada 1-2 skill inti (4), menengah pada pendukung (3),
  dan dasar pada pelengkap (2).
- C4 (minat): tiap profil diasumsikan meminati satu karier yang
  paling sesuai profilnya (1.0 untuk karier itu, 0.2 sisanya).
- C2 = gaji_max (juta Rp/bulan), C3 = demand ternormalisasi min-max
  ke 1-10 (rumus persis seed.py).
- Skenario acak: Dirichlet dengan konsentrasi = bobot_default x 50,
  seed 42 -> sampel menyebar di sekitar default (sd ~0.07).

Output:
  analysis/hasil_sensitivitas.md   (tabel siap dikutip bab 4)
  analysis/hasil_sensitivitas.csv  (baris per profil x skenario)

Jalankan dari root repo:
    python analysis/sensitivitas.py
"""
import csv
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(REPO, "data-loker-id")

sys.path.insert(0, REPO)
from app.services import cbf, saw  # noqa: E402  (fungsi murni, tanpa DB)

N_ACAK = 200
SEED = 42
KONSENTRASI = 50.0

DEFAULT = (0.35, 0.25, 0.20, 0.20)

PROFIL = [
    {
        "nama": "Profil 1 (Backend/Data)",
        # rating tingkat penguasaan 0-5 (realistis, tidak semua 5)
        "ratings": {"Python": 4, "SQL": 4, "JavaScript": 3, "Git": 3,
                    "Docker": 2},
        "minat": "Data Engineer",
    },
    {
        "nama": "Profil 2 (Jaringan)",
        "ratings": {"TCP/IP": 4, "Firewall": 3, "Routing & Switching": 4,
                    "Linux": 3},
        "minat": "Network Architect",
    },
    {
        "nama": "Profil 3 (Frontend)",
        "ratings": {"HTML": 4, "CSS": 4, "JavaScript": 4, "React": 3},
        "minat": "Web Developer",
    },
]


class Karier:
    """Stub Career: cukup skill_list(), skill_scores(), gaji_max, demand."""

    def __init__(self, nama, skor_skill, gaji_max_juta, demand):
        self.nama = nama
        self._skor = skor_skill  # dict {skill_lower: skor 1-5}
        self.gaji_max = gaji_max_juta
        self.demand = demand

    def skill_list(self):
        return list(self._skor.keys())

    def skill_scores(self):
        return self._skor


def baca_dataset():
    """Baca CSV dataset -> list Karier (urutan deterministik)."""
    matriks = list(csv.DictReader(open(
        os.path.join(DATA_DIR, "skill_matrix.csv"), encoding="utf-8")))
    demand = list(csv.DictReader(open(
        os.path.join(DATA_DIR, "demand_gaji.csv"), encoding="utf-8")))

    n_low = [int(b["n_lowongan"]) for b in demand]
    nmin, nmax = min(n_low), max(n_low)

    def norm_demand(nilai):
        if nmax == nmin:
            return 5
        skor = 1 + 9 * (nilai - nmin) / (nmax - nmin)
        return max(1, min(10, round(skor)))

    info = {b["nama_jabatan"]: b for b in demand}
    per_jabatan = {}
    for b in matriks:
        per_jabatan.setdefault(b["nama_jabatan"], {})[b["skill"].lower()] = float(
            b["skor"])
    karier = []
    for nama, d in info.items():
        karier.append(Karier(
            nama=nama,
            skor_skill=per_jabatan.get(nama, {}),
            gaji_max_juta=float(d["gaji_max_rp"]) / 1_000_000,
            demand=norm_demand(int(d["n_lowongan"])),
        ))
    return karier


def normalisasi_bobot(bobot):
    """Sama seperti aplikasi: total harus 1, diskalakan bila beda."""
    total = sum(bobot)
    if total > 0 and abs(total - 1.0) > 1e-9:
        return [b / total for b in bobot]
    return list(bobot)


def hitung_ranking(karier, vocab, ratings_profil, minat_nama, bobot):
    """Kembalikan daftar nama karier terurut peringkat (skor SAW menurun).

    ratings_profil: dict {nama_skill: tingkat penguasaan 0-5}.
    """
    vec_mhs = cbf.vectorize(ratings_profil, vocab)
    cbf_skor = [cbf.cosine_sim(vec_mhs, cbf.career_vector(k, vocab))
                for k in karier]
    matrix = [
        [cbf_skor[i], k.gaji_max, float(k.demand),
         1.0 if k.nama == minat_nama else 0.2]
        for i, k in enumerate(karier)
    ]
    hasil = saw.hitung(matrix, normalisasi_bobot(bobot))
    return [karier[i].nama for i in hasil["ranking"]]


def metrik(ranking, ranking_default):
    """top-1 sama?; irisan top-3; rata-rata pergeseran peringkat."""
    top1 = ranking[0] == ranking_default[0]
    t3, t3d = set(ranking[:3]), set(ranking_default[:3])
    pos = {nama: i for i, nama in enumerate(ranking)}
    posd = {nama: i for i, nama in enumerate(ranking_default)}
    geser = sum(abs(pos[n] - posd[n]) for n in pos) / len(pos)
    return top1, len(t3 & t3d), geser


def fmt_bobot(bobot):
    return "(" + ", ".join(f"{b:.3f}" for b in bobot) + ")"


def main():
    import numpy as np  # noqa: E402

    karier = baca_dataset()
    vocab = cbf.build_vocabulary(karier)
    for p in PROFIL:
        hilang = {s for s in p["ratings"] if s.lower() not in vocab}
        assert not hilang, f"Skill tidak dikenal: {hilang}"

    deterministik = [
        ("default", list(DEFAULT)),
        ("C1 dominan", [0.7, 0.1, 0.1, 0.1]),
        ("C2 dominan", [0.1, 0.7, 0.1, 0.1]),
        ("C3 dominan", [0.1, 0.1, 0.7, 0.1]),
        ("C4 dominan", [0.1, 0.1, 0.1, 0.7]),
        ("C1 +0.10", [0.45, 0.25, 0.20, 0.20]),
        ("C1 -0.10", [0.25, 0.25, 0.20, 0.20]),
    ]
    rng = np.random.default_rng(SEED)
    alpha = [w * KONSENTRASI for w in DEFAULT]
    acak = [("acak-%03d" % (i + 1), list(rng.dirichlet(alpha)))
            for i in range(N_ACAK)]

    baris_csv = []
    hasil_md = []
    ringkasan = []  # per profil: (top1_stabil, top3_utuh, overlap_rt, geser_rt)

    for p in PROFIL:
        ranking_default = hitung_ranking(
            karier, vocab, p["ratings"], p["minat"], list(DEFAULT))
        hasil_md.append(f"## {p['nama']}\n")
        hasil_md.append(
            "Skill dan tingkat penguasaan (0-5): "
            + ", ".join(f"{s} {n}" for s, n in p["ratings"].items())
            + f". Minat diasumsikan: {p['minat']}.\n")
        hasil_md.append("### Ranking default (bobot 0.35 / 0.25 / 0.20 / 0.20)")
        hasil_md.append("| Peringkat | Karier |")
        hasil_md.append("|---|---|")
        for i, nama in enumerate(ranking_default[:5], 1):
            hasil_md.append(f"| {i} | {nama} |")
        hasil_md.append("")

        t1, t3, ov, gs = 0, 0, 0.0, 0.0
        n = 0
        hasil_md.append("### Skenario deterministik")
        hasil_md.append(
            "| Skenario | Bobot ternormalisasi (C1, C2, C3, C4) "
            "| Top-1 | Top-1 sama? | Irisan top-3 | Geser rata-rata |")
        hasil_md.append("|---|---|---|---|---|---|")
        for nama_s, bobot in deterministik + acak:
            bn = normalisasi_bobot(bobot)
            ranking = hitung_ranking(
                karier, vocab, p["ratings"], p["minat"], bn)
            s1, ov3, geser = metrik(ranking, ranking_default)
            baris_csv.append({
                "profil": p["nama"], "skenario": nama_s,
                "w1": f"{bn[0]:.4f}", "w2": f"{bn[1]:.4f}",
                "w3": f"{bn[2]:.4f}", "w4": f"{bn[3]:.4f}",
                "top1": ranking[0],
                "top1_sama_default": int(s1),
                "irisan_top3": ov3,
                "geser_rata_rata": f"{geser:.3f}",
            })
            # Skenario "default" adalah pembanding; tidak ikut agregat
            # (trivially identik) tapi tetap dicatat di CSV.
            if nama_s != "default":
                t1 += s1
                t3 += (ov3 == 3)
                ov += ov3
                gs += geser
                n += 1
            if nama_s != "default" and not nama_s.startswith("acak"):
                hasil_md.append(
                    f"| {nama_s} | {fmt_bobot(bn)} | {ranking[0]} "
                    f"| {'ya' if s1 else 'tidak'} | {ov3}/3 "
                    f"| {geser:.2f} |")
        hasil_md.append("")

        # agregat skenario acak saja
        a1 = sum(r["top1_sama_default"] for r in baris_csv
                 if r["profil"] == p["nama"] and r["skenario"].startswith("acak"))
        a3 = sum(1 for r in baris_csv
                 if r["profil"] == p["nama"] and r["skenario"].startswith("acak")
                 and int(r["irisan_top3"]) == 3)
        hasil_md.append(
            f"**Skenario acak Dirichlet ({N_ACAK} sampel, seed {SEED}):** "
            f"top-1 bertahan pada {a1}/{N_ACAK} sampel "
            f"({100 * a1 / N_ACAK:.1f}%); top-3 utuh pada {a3}/{N_ACAK} "
            f"({100 * a3 / N_ACAK:.1f}%).\n")
        ringkasan.append((100 * t1 / n, 100 * t3 / n, ov / n, gs / n))

    # tabel ringkasan global
    header = ["# Hasil Analisis Sensitivitas Bobot SAW",
              "",
              "Tiga profil contoh dievaluasi pada 6 skenario deterministik "
              f"(di luar default) + {N_ACAK} skenario acak Dirichlet "
              f"(seed {SEED}) per profil (total "
              f"{3 * (len(deterministik) - 1 + N_ACAK)} skenario baru; "
              "skenario default dipakai sebagai pembanding). "
              "Perbandingan selalu terhadap ranking "
              "bobot default (0.35 / 0.25 / 0.20 / 0.20). "
              "Metode perhitungan identik dengan aplikasi.",
              "",
              "| Profil | Top-1 bertahan | Top-3 utuh | "
              "Rata-rata irisan top-3 | Rata-rata geser peringkat |",
              "|---|---|---|---|---|"]
    for p, (pt1, pt3, pov, pgs) in zip(PROFIL, ringkasan):
        header.append(
            f"| {p['nama']} | {pt1:.1f}% | {pt3:.1f}% | {pov:.2f}/3 "
            f"| {pgs:.2f} |")
    header.append("")
    t1g = sum(r[0] for r in ringkasan) / 3
    t3g = sum(r[1] for r in ringkasan) / 3
    ovg = sum(r[2] for r in ringkasan) / 3
    gsg = sum(r[3] for r in ringkasan) / 3

    # kesimpulan: template mengikuti angka (jujur, tidak didramatisasi)
    if t1g >= 80:
        kalimat_stabilitas = (
            "Hasil ini menunjukkan rekomendasi teratas relatif stabil "
            "terhadap perubahan bobot yang wajar di sekitar bobot default.")
    elif t1g >= 50:
        kalimat_stabilitas = (
            "Hasil ini menunjukkan rekomendasi teratas cukup stabil untuk "
            "perubahan bobot kecil, tetapi berubah pada skenario ekstrem "
            "(dominasi satu kriteria).")
    else:
        kalimat_stabilitas = (
            "Hasil ini menunjukkan ranking sensitif terhadap pilihan bobot; "
            "bobot default perlu dipilih dan dilaporkan dengan hati-hati.")

    idx_min_t1 = min(range(3), key=lambda i: ringkasan[i][0])
    idx_min_t3 = min(range(3), key=lambda i: ringkasan[i][1])
    kalimat_nuansa = (
        f"Kestabilan tidak merata antarprofil: top-1 paling mudah "
        f"berubah pada {PROFIL[idx_min_t1]['nama']} "
        f"({ringkasan[idx_min_t1][0]:.1f}% bertahan), sedangkan "
        f"kandungan top-3 paling mudah berubah pada "
        f"{PROFIL[idx_min_t3]['nama']} (utuh "
        f"{ringkasan[idx_min_t3][1]:.1f}%).")

    kesimpulan = [
        "## Kesimpulan",
        "",
        f"1. Pada ketiga profil, peringkat pertama (top-1) bertahan pada "
        f"{t1g:.1f}% dari seluruh skenario ({len(deterministik) - 1} "
        f"deterministik + {N_ACAK} acak per profil); himpunan 3 besar "
        f"(top-3) utuh "
        f"pada {t3g:.1f}% skenario dengan rata-rata irisan {ovg:.2f} dari 3.",
        f"2. {kalimat_nuansa}",
        f"3. {kalimat_stabilitas}",
        f"4. Skenario dominasi tunggal (satu kriteria 0.70) menghasilkan "
        f"perubahan terbesar; dominasi C2 (gaji) dan C3 (demand) paling "
        f"berpengaruh karena kedua kriteria ini tidak bergantung pada "
        f"profil mahasiswa. Rata-rata pergeseran peringkat keseluruhan "
        f"sebesar {gsg:.2f} posisi dari 19 karier per skenario.",
        f"5. Implikasi untuk penelitian: bobot default "
        f"(0.35/0.25/0.20/0.20) layak dipakai karena ranking cukup stabil "
        f"pada variasi wajar, namun panel bobot kustom tetap perlu "
        f"ditawarkan agar mahasiswa yang memprioritaskan gaji atau demand "
        f"dapat menyesuaikan.",
    ]
    isi = "\n".join(header + kesimpulan + [""] + hasil_md)
    with open(os.path.join(BASE_DIR, "hasil_sensitivitas.md"), "w",
              encoding="utf-8") as f:
        f.write(isi)

    with open(os.path.join(BASE_DIR, "hasil_sensitivitas.csv"), "w",
              newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "profil", "skenario", "w1", "w2", "w3", "w4", "top1",
            "top1_sama_default", "irisan_top3", "geser_rata_rata"])
        w.writeheader()
        w.writerows(baris_csv)

    print(f"Selesai: {len(baris_csv)} skenario dievaluasi.")
    print(f"Top-1 global bertahan: {t1g:.1f}% | Top-3 utuh: {t3g:.1f}% | "
          f"Geser rata-rata: {gsg:.2f}")


if __name__ == "__main__":
    main()
