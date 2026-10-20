"""Content-Based Filtering: cosine similarity profil vs karier.

Model VEKTOR BERBOBOT (bukan biner). Setiap karier direpresentasikan
sebagai vektor berdimensi N (N = jumlah skill dalam kosakata) yang
entrinya adalah SKOR KEPENTINGAN skill tersebut untuk karier itu
(skala 1-5, dari Dataset Lowongan IT Indonesia; 0 bila skill tidak
relevan). Vektor mahasiswa tetap biner: 1 bila skill dicentang di
form profil, 0 bila tidak.

Kenapa berbobot, bukan biner (perbaikan kekurangan model lama):
model biner lama memakai ambang importance >= 3.0 sehingga nuansa
data hilang — skill berskor 4.75 dan 3.50 diperlakukan sama (1.0).
Akibat nyata: vektor Programmer vs DevOps Engineer menjadi identik
(cosine = 1.0) padahal profil skill aslinya berbeda. Dengan vektor
berbobot, perbedaan itu lestari dan cosine similarity dapat
membedakan keduanya. Cosine similarity menormalisasi panjang vektor
sendiri, sehingga skala 1-5 tidak perlu dinormalisasi manual.
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


def vectorize(skills, vocabulary):
    """Ubah daftar skill mahasiswa menjadi vektor BINER sesuai kosakata.

    1.0 bila mahasiswa mencentang skill itu, 0.0 bila tidak.
    """
    owned = {s.strip().lower() for s in skills if s.strip()}
    return np.array([1.0 if term in owned else 0.0 for term in vocabulary])


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
