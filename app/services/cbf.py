"""Content-Based Filtering: cosine similarity profil vs karier."""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def build_vocabulary(careers):
    """Bangun kosakata unik dari seluruh skill karier (huruf kecil)."""
    vocab = []
    for career in careers:
        for skill in career.skill_list():
            key = skill.lower()
            if key not in vocab:
                vocab.append(key)
    return vocab


def vectorize(skills, vocabulary):
    """Ubah daftar skill menjadi vektor biner sesuai kosakata."""
    owned = {s.strip().lower() for s in skills if s.strip()}
    return np.array([1.0 if term in owned else 0.0 for term in vocabulary])


def cosine_sim(vec_a, vec_b):
    """Cosine similarity dua vektor. Mengembalikan 0.0 bila salah satu kosong."""
    a = np.asarray(vec_a, dtype=float).reshape(1, -1)
    b = np.asarray(vec_b, dtype=float).reshape(1, -1)
    if not a.any() or not b.any():
        return 0.0
    return float(cosine_similarity(a, b)[0][0])
