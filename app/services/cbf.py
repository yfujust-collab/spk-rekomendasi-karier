"""Content-Based Filtering: cosine similarity profil vs karier.

Model VEKTOR BERBOBOT di kedua sisi (bukan biner). Setiap karier
direpresentasikan sebagai vektor berdimensi N (N = jumlah skill dalam
kosakata) yang entrinya adalah SKOR KEPENTINGAN skill tersebut untuk
karier itu (skala 1-5, dari Dataset Lowongan IT Indonesia; 0 bila
skill tidak disyaratkan karier itu). Vektor mahasiswa juga berbobot:
entrinya adalah TINGKAT PENGUASAAN yang dinilai sendiri oleh
mahasiswa pada form profil (skala 0-5; 0 = tidak menguasai).

Simetri kedua vektor adalah inti perbaikan model ini: karier dan
mahasiswa kini berbicara dalam skala yang sama, sehingga cosine
similarity menimbang tidak hanya "skill apa yang sama" tetapi juga
"seberapa penting skill itu bagi karier" dan "seberapa dalam
mahasiswa menguasainya".

Riwayat perbaikan: model awal memakai vektor biner di kedua sisi
(mahasiswa mencentang skill, karier memakai ambang importance
>= 3.0) sehingga nuansa data hilang — skill berskor 4.75 dan 3.50
diperlakukan sama (1.0), dan vektor Programmer vs DevOps Engineer
menjadi identik (cosine = 1.0). Perbaikan dilakukan dua tahap:
vektor karier lebih dulu dibuat berbobot, kemudian vektor mahasiswa
menyusul berbobot lewat skala penguasaan 0-5. Cosine similarity
menormalisasi panjang vektor sendiri, sehingga skala tidak perlu
dinormalisasi manual.
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def build_vocabulary(careers):
    """Bangun kosakata unik dari seluruh skill karier (kunci huruf kecil).

    Urutan = kemunculan pertama; deterministik selama urutan karier
    deterministik (mis. order_by id).
    """
    vocab = []
    for career in careers:
        for skill in career.skill_list():
            key = skill.lower()
            if key not in vocab:
                vocab.append(key)
    return vocab


def skill_labels(careers):
    """Petakan kunci kosakata -> nama tampil asli (huruf apa adanya).

    Dipakai agar label checkbox tidak rusak oleh .title()
    (mis. "CI/CD" bukan "Ci/Cd", "REST API" bukan "Rest Api").
    """
    label = {}
    for career in careers:
        for skill in career.skill_list():
            key = skill.lower()
            if key not in label:
                label[key] = skill
    return label


def _ke_dict_skor(skill_input):
    """Normalisasi input skill menjadi dict {nama_lower: nilai float}.

    Input yang diterima:
    - dict {nama: nilai} (mis. dari StudentProfile.skill_scores()
      atau Career.skill_scores()), atau
    - daftar entri "Skill:nilai" / "Skill" (entri tanpa nilai
      dianggap 3.0, konvensi default yang sama seperti model).
    """
    if isinstance(skill_input, dict):
        return {
            str(k).strip().lower(): float(v)
            for k, v in skill_input.items()
            if str(k).strip()
        }
    hasil = {}
    for entri in skill_input:
        entri = str(entri).strip()
        if not entri:
            continue
        if ":" in entri:
            nama, _, nilai_teks = entri.rpartition(":")
            try:
                nilai = float(nilai_teks.strip())
            except ValueError:
                nilai = 3.0
        else:
            nama, nilai = entri, 3.0
        nama = nama.strip()
        if nama:
            hasil[nama.lower()] = nilai
    return hasil


def vectorize(skill_input, vocabulary):
    """Ubah skill mahasiswa menjadi vektor BERBOBOT sesuai kosakata.

    Entri = tingkat penguasaan 0-5 yang dinilai mahasiswa untuk skill
    itu (0.0 bila tidak diisi). skill_input boleh berupa dict skor
    atau daftar entri "Skill:nilai" (lihat _ke_dict_skor).
    """
    skor = _ke_dict_skor(skill_input)
    return np.array([float(skor.get(term, 0.0)) for term in vocabulary])


def career_vector(career, vocabulary):
    """Ubah skill karier menjadi vektor BERBOBOT sesuai kosakata.

    Entri = skor kepentingan 1-5 dari Career.skill_scores();
    0.0 untuk skill yang tidak relevan bagi karier ini.
    """
    skor = career.skill_scores()
    return np.array([float(skor.get(term, 0.0)) for term in vocabulary])


def cosine_sim(vec_a, vec_b):
    """Cosine similarity dua vektor. Mengembalikan 0.0 bila salah satu kosong."""
    a = np.asarray(vec_a, dtype=float).reshape(1, -1)
    b = np.asarray(vec_b, dtype=float).reshape(1, -1)
    if not a.any() or not b.any():
        return 0.0
    return float(cosine_similarity(a, b)[0][0])
