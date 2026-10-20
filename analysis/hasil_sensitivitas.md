# Hasil Analisis Sensitivitas Bobot SAW

Tiga profil contoh dievaluasi pada 6 skenario deterministik (di luar default) + 200 skenario acak Dirichlet (seed 42) per profil (total 618 skenario baru; skenario default dipakai sebagai pembanding). Perbandingan selalu terhadap ranking bobot default (0.35 / 0.25 / 0.20 / 0.20). Metode perhitungan identik dengan aplikasi.

| Profil | Top-1 bertahan | Top-3 utuh | Rata-rata irisan top-3 | Rata-rata geser peringkat |
|---|---|---|---|---|
| Profil 1 (Backend/Data) | 75.7% | 98.1% | 2.98/3 | 0.70 |
| Profil 2 (Jaringan) | 99.5% | 82.0% | 2.82/3 | 0.80 |
| Profil 3 (Frontend) | 99.5% | 43.7% | 2.42/3 | 0.66 |

## Kesimpulan

1. Pada ketiga profil, peringkat pertama (top-1) bertahan pada 91.6% dari seluruh skenario (6 deterministik + 200 acak per profil); himpunan 3 besar (top-3) utuh pada 74.6% skenario dengan rata-rata irisan 2.74 dari 3.
2. Kestabilan tidak merata antarprofil: top-1 paling mudah berubah pada Profil 1 (Backend/Data) (75.7% bertahan), sedangkan kandungan top-3 paling mudah berubah pada Profil 3 (Frontend) (utuh 43.7%).
3. Hasil ini menunjukkan rekomendasi teratas relatif stabil terhadap perubahan bobot yang wajar di sekitar bobot default.
4. Skenario dominasi tunggal (satu kriteria 0.70) menghasilkan perubahan terbesar; dominasi C2 (gaji) dan C3 (demand) paling berpengaruh karena kedua kriteria ini tidak bergantung pada profil mahasiswa. Rata-rata pergeseran peringkat keseluruhan sebesar 0.72 posisi dari 19 karier per skenario.
5. Implikasi untuk penelitian: bobot default (0.35/0.25/0.20/0.20) layak dipakai karena ranking cukup stabil pada variasi wajar, namun panel bobot kustom tetap perlu ditawarkan agar mahasiswa yang memprioritaskan gaji atau demand dapat menyesuaikan.

## Profil 1 (Backend/Data)

Skill dan tingkat penguasaan (0-5): Python 4, SQL 4, JavaScript 3, Git 3, Docker 2. Minat diasumsikan: Data Engineer.

### Ranking default (bobot 0.35 / 0.25 / 0.20 / 0.20)
| Peringkat | Karier |
|---|---|
| 1 | Data Engineer |
| 2 | Data Scientist |
| 3 | QA Engineer |
| 4 | Web Developer |
| 5 | Cybersecurity Analyst |

### Skenario deterministik
| Skenario | Bobot ternormalisasi (C1, C2, C3, C4) | Top-1 | Top-1 sama? | Irisan top-3 | Geser rata-rata |
|---|---|---|---|---|---|
| C1 dominan | (0.700, 0.100, 0.100, 0.100) | Data Engineer | ya | 3/3 | 2.63 |
| C2 dominan | (0.100, 0.700, 0.100, 0.100) | Data Scientist | tidak | 1/3 | 2.74 |
| C3 dominan | (0.100, 0.100, 0.700, 0.100) | System Administrator | tidak | 2/3 | 3.37 |
| C4 dominan | (0.100, 0.100, 0.100, 0.700) | Data Engineer | ya | 3/3 | 0.74 |
| C1 +0.10 | (0.409, 0.227, 0.182, 0.182) | Data Engineer | ya | 3/3 | 0.74 |
| C1 -0.10 | (0.278, 0.278, 0.222, 0.222) | Data Engineer | ya | 3/3 | 0.32 |

**Skenario acak Dirichlet (200 sampel, seed 42):** top-1 bertahan pada 152/200 sampel (76.0%); top-3 utuh pada 198/200 (99.0%).

## Profil 2 (Jaringan)

Skill dan tingkat penguasaan (0-5): TCP/IP 4, Firewall 3, Routing & Switching 4, Linux 3. Minat diasumsikan: Network Architect.

### Ranking default (bobot 0.35 / 0.25 / 0.20 / 0.20)
| Peringkat | Karier |
|---|---|
| 1 | Network Architect |
| 2 | Cybersecurity Analyst |
| 3 | Security Engineer |
| 4 | System Administrator |
| 5 | Network Support |

### Skenario deterministik
| Skenario | Bobot ternormalisasi (C1, C2, C3, C4) | Top-1 | Top-1 sama? | Irisan top-3 | Geser rata-rata |
|---|---|---|---|---|---|
| C1 dominan | (0.700, 0.100, 0.100, 0.100) | Network Architect | ya | 2/3 | 2.74 |
| C2 dominan | (0.100, 0.700, 0.100, 0.100) | Data Scientist | tidak | 1/3 | 4.00 |
| C3 dominan | (0.100, 0.100, 0.700, 0.100) | Network Architect | ya | 2/3 | 3.37 |
| C4 dominan | (0.100, 0.100, 0.100, 0.700) | Network Architect | ya | 3/3 | 0.63 |
| C1 +0.10 | (0.409, 0.227, 0.182, 0.182) | Network Architect | ya | 3/3 | 0.95 |
| C1 -0.10 | (0.278, 0.278, 0.222, 0.222) | Network Architect | ya | 3/3 | 0.32 |

**Skenario acak Dirichlet (200 sampel, seed 42):** top-1 bertahan pada 200/200 sampel (100.0%); top-3 utuh pada 166/200 (83.0%).

## Profil 3 (Frontend)

Skill dan tingkat penguasaan (0-5): HTML 4, CSS 4, JavaScript 4, React 3. Minat diasumsikan: Web Developer.

### Ranking default (bobot 0.35 / 0.25 / 0.20 / 0.20)
| Peringkat | Karier |
|---|---|
| 1 | Web Developer |
| 2 | UI/UX Designer |
| 3 | Software Developer |
| 4 | Programmer |
| 5 | Data Scientist |

### Skenario deterministik
| Skenario | Bobot ternormalisasi (C1, C2, C3, C4) | Top-1 | Top-1 sama? | Irisan top-3 | Geser rata-rata |
|---|---|---|---|---|---|
| C1 dominan | (0.700, 0.100, 0.100, 0.100) | Web Developer | ya | 3/3 | 1.89 |
| C2 dominan | (0.100, 0.700, 0.100, 0.100) | Web Developer | ya | 1/3 | 3.47 |
| C3 dominan | (0.100, 0.100, 0.700, 0.100) | System Administrator | tidak | 0/3 | 3.26 |
| C4 dominan | (0.100, 0.100, 0.100, 0.700) | Web Developer | ya | 2/3 | 0.95 |
| C1 +0.10 | (0.409, 0.227, 0.182, 0.182) | Web Developer | ya | 3/3 | 0.21 |
| C1 -0.10 | (0.278, 0.278, 0.222, 0.222) | Web Developer | ya | 2/3 | 0.74 |

**Skenario acak Dirichlet (200 sampel, seed 42):** top-1 bertahan pada 200/200 sampel (100.0%); top-3 utuh pada 88/200 (44.0%).
