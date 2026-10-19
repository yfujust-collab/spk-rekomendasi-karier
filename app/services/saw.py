"""Simple Additive Weighting: normalisasi + skor preferensi."""


def normalize(matrix):
    """Normalisasi matriks keputusan (semua kriteria benefit).

    matrix: list of rows, tiap row = list nilai per kriteria.
    Rumus benefit: r = x / max(x) per kolom.
    """
    if not matrix:
        return []
    kolom = list(zip(*matrix))
    pembagi = [max(c) if max(c) != 0 else 1.0 for c in kolom]
    return [[v / p for v, p in zip(baris, pembagi)] for baris in matrix]


def hitung(matrix, bobot):
    """Hitung skor preferensi SAW dan urutan ranking.

    Mengembalikan dict: ternormalisasi, skor, ranking (indeks terurut menurun).
    """
    ternormalisasi = normalize(matrix)
    skor = [sum(n * b for n, b in zip(baris, bobot)) for baris in ternormalisasi]
    ranking = sorted(range(len(skor)), key=lambda i: skor[i], reverse=True)
    return {"ternormalisasi": ternormalisasi, "skor": skor, "ranking": ranking}
