"""Alur utama mahasiswa: profil, hitung rekomendasi, hasil."""
import csv
import io
import json
from datetime import datetime

from flask import (
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required

from app import db
from app.models import Career, Criterion, RecommendationResult, StudentProfile
from app.services import cbf, saw
from app.spk import bp
from app.spk.forms import ProfileForm


def _vocabulary():
    return cbf.build_vocabulary(Career.query.all())


# Skala tingkat penguasaan skill pada form profil (dinilai sendiri
# oleh mahasiswa): 0 berarti tidak menguasai sama sekali.
SKALA_SKILL = [
    (0, "Tidak menguasai"),
    (1, "Pemula"),
    (2, "Dasar"),
    (3, "Menengah"),
    (4, "Mahir"),
    (5, "Ahli"),
]
MIN_SKILL_TERISI = 3


def _baris_skill(vocab, label, nilai_map):
    """Baris input rating untuk template: satu dict per skill.

    nilai_map: {kunci_lower: nilai} — nilai boleh float (dari
    skill_scores) atau int (dari form); selalu ditampilkan sebagai
    bilangan bulat 0-5, default 0 bila skill belum dinilai.
    """
    return [
        {
            "nama_input": f"skill_{i}",
            "label": label.get(kunci, kunci),
            "nilai": int(nilai_map.get(kunci, 0)),
        }
        for i, kunci in enumerate(vocab)
    ]


def _baca_rating_skill(vocab):
    """Baca & validasi rating skill dari form HTML biasa.

    Mengembalikan (nilai_map, pesan_error): nilai_map berisi
    {kunci_lower: int 0-5} untuk skill yang berhasil dibaca;
    pesan_error None bila seluruhnya sah. Aturan: tiap nilai harus
    bilangan bulat 0-5 dan minimal MIN_SKILL_TERISI skill bernilai
    lebih dari 0. Field yang tidak terkirim dianggap 0.
    """
    nilai_map = {}
    for i, kunci in enumerate(vocab):
        mentah = request.form.get(f"skill_{i}")
        if mentah is None or mentah == "":
            nilai_map[kunci] = 0
            continue
        try:
            nilai = int(mentah)
        except (TypeError, ValueError):
            return nilai_map, (
                "Nilai penguasaan tiap skill harus bilangan bulat "
                "0 sampai 5."
            )
        if nilai < 0 or nilai > 5:
            return nilai_map, (
                "Nilai penguasaan tiap skill harus antara 0 sampai 5."
            )
        nilai_map[kunci] = nilai
    terisi = sum(1 for v in nilai_map.values() if v > 0)
    if terisi < MIN_SKILL_TERISI:
        return nilai_map, (
            "Isi tingkat penguasaan untuk minimal 3 skill "
            "(nilai lebih dari 0)."
        )
    return nilai_map, None


def _normalisasi_bobot(bobot):
    """Kembalikan (bobot_ternormalisasi, dinormalisasi).

    Kaidah SAW: total bobot harus 1. Bila total berbeda dari 1,
    bobot diskalakan proporsional agar hasil tetap sah. Bila total
    0 (tidak sah), kembalikan apa adanya tanpa perubahan.
    """
    total = sum(bobot)
    if total > 0 and abs(total - 1.0) > 1e-9:
        return [b / total for b in bobot], True
    return list(bobot), False


def _bobot_default():
    """Bobot default (urutan kode C1..C4)."""
    return [
        c.bobot for c in Criterion.query.order_by(Criterion.kode).all()
    ]


def _bobot_aktif():
    """Bobot yang sedang berlaku di sesi user.

    Bobot kustom hasil panel "Atur Bobot" (session) didahulukan;
    bila belum pernah diatur, pakai bobot default.
    Bobot kustom TIDAK PERNAH ditulis ke tabel Criterion.
    """
    kustom = session.get("bobot_custom")
    if isinstance(kustom, list) and len(kustom) == 4:
        try:
            return [float(x) for x in kustom]
        except (TypeError, ValueError):
            session.pop("bobot_custom", None)
    return _bobot_default()


def _bobot_dari_batch(rows):
    """Bobot tersimpan pada baris batch (JSON, sudah dinormalisasi).

    Mengembalikan list 4 float, atau None bila batch lama belum
    menyimpan bobot (kolom NULL).
    """
    if not rows or not rows[0].bobot:
        return None
    try:
        nilai = json.loads(rows[0].bobot)
        if isinstance(nilai, list) and len(nilai) == 4:
            return [float(x) for x in nilai]
    except (TypeError, ValueError):
        pass
    return None


def _sama_bobot(a, b):
    """Dua daftar bobot dianggap sama bila selisih tiap entri < 0.0001."""
    return len(a) == len(b) and all(abs(x - y) < 1e-4 for x, y in zip(a, b))


def _batch_terakhir(profile_id):
    """Kembalikan batch_id perhitungan terbaru untuk profil ini, atau None."""
    baris = (
        RecommendationResult.query.filter_by(profile_id=profile_id)
        .order_by(RecommendationResult.created_at.desc())
        .first()
    )
    return baris.batch_id if baris else None


def _hasil_batch_terakhir(profile_id):
    """Kembalikan baris-baris hasil dari batch perhitungan terbaru."""
    batch_id = _batch_terakhir(profile_id)
    if batch_id is None:
        return []
    return (
        RecommendationResult.query.filter_by(
            profile_id=profile_id, batch_id=batch_id
        )
        .order_by(RecommendationResult.peringkat)
        .all()
    )


def _compute(profile, bobot=None):
    """Hitung CBF lalu SAW. Kembalikan detail lengkap untuk transparansi.

    bobot: daftar 4 bobot mentah (urutan C1..C4); None berarti pakai
    bobot default. Bobot selalu dinormalisasi ke total 1
    sebelum dipakai (perilaku lama dipertahankan).

    Melempar ValueError bila data master belum sah untuk dihitung.
    """
    careers = Career.query.order_by(Career.id).all()
    criteria = Criterion.query.order_by(Criterion.kode).all()
    if not careers or not criteria:
        raise ValueError("Data karier atau kriteria belum lengkap.")
    if len(criteria) != 4:
        raise ValueError("Jumlah kriteria harus tepat 4 agar perhitungan SAW sah.")
    vocab = _vocabulary()
    vec_mhs = cbf.vectorize(profile.skill_scores(), vocab)

    # Tahap 1: Content-Based Filtering -> skor kecocokan skill (C1).
    # Kedua vektor BERBOBOT dan simetris: karier memakai skor
    # kepentingan 1-5, mahasiswa memakai tingkat penguasaan 0-5.
    skor_cbf = []
    for career in careers:
        vec_karier = cbf.career_vector(career, vocab)
        skor_cbf.append(cbf.cosine_sim(vec_mhs, vec_karier))

    # Tahap 2: matriks keputusan SAW
    # C1 kecocokan skill, C2 prospek gaji, C3 demand pasar, C4 kesesuaian minat
    matrix = []
    for i, career in enumerate(careers):
        minat = 1.0 if career.id in profile.minat_ids() else 0.2
        matrix.append([skor_cbf[i], float(career.gaji_max), float(career.demand), minat])

    # Kaidah SAW: total bobot harus 1. Bila total yang diberikan
    # berbeda, bobot dinormalisasi otomatis agar hasil tetap sah.
    bobot = [c.bobot for c in criteria] if bobot is None else list(bobot)
    bobot_n, dinormalisasi = _normalisasi_bobot(bobot)
    hasil_saw = saw.hitung(matrix, bobot_n)
    return {
        "careers": careers,
        "criteria": criteria,
        "matrix": matrix,
        "skor_cbf": skor_cbf,
        "saw": hasil_saw,
        "bobot": bobot,
        "bobot_n": bobot_n,
        "bobot_dinormalisasi": dinormalisasi,
    }


@bp.route("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))
    if current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    hasil = []
    if profile:
        hasil = _hasil_batch_terakhir(profile.id)[:3]
    return render_template("spk/index.html", profile=profile, hasil=hasil)


@bp.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    careers = Career.query.order_by(Career.nama).all()
    if not careers:
        flash("Data karier belum tersedia. Hubungi admin.", "warning")
        return redirect(url_for("spk.index"))
    vocab = _vocabulary()
    label = cbf.skill_labels(Career.query.all())
    form = ProfileForm()
    form.minat.choices = [(c.id, c.nama) for c in careers]

    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if form.validate_on_submit():
        nilai_map, galat = _baca_rating_skill(vocab)
        if galat is None:
            if not profile:
                profile = StudentProfile(user_id=current_user.id)
                db.session.add(profile)
            profile.nama = form.nama.data.strip()
            # Simpan hanya skill bernilai > 0, format "Skill:nilai"
            # (konsisten dengan format Career.skills).
            profile.skills = ", ".join(
                f"{label.get(k, k)}:{nilai_map[k]}"
                for k in vocab
                if nilai_map.get(k, 0) > 0
            )
            profile.minat = ", ".join(str(i) for i in form.minat.data)
            # batch lama tidak dihapus; batch baru akan dibuat saat hitung ulang
            # sehingga halaman Riwayat tetap menyimpan hasil-hasil terdahulu
            db.session.commit()
            flash("Profil tersimpan. Sistem menghitung rekomendasi.", "success")
            return redirect(url_for("spk.hitung"))
        # Rating tidak sah: tampilkan form lagi dengan nilai yang
        # sudah dikirim agar mahasiswa tidak mengisi dari nol.
        return render_template(
            "spk/profil.html",
            form=form,
            skill_rows=_baris_skill(vocab, label, nilai_map),
            skala=SKALA_SKILL,
            skill_error=galat,
        )

    if profile and not form.is_submitted():
        form.nama.data = profile.nama
        form.minat.data = profile.minat_ids()
        nilai_awal = profile.skill_scores()
    elif form.is_submitted():
        # POST tetapi form tidak lolos validasi (mis. nama kosong):
        # pertahankan rating yang dikirim.
        nilai_awal, _ = _baca_rating_skill(vocab)
    else:
        nilai_awal = {}
    return render_template(
        "spk/profil.html",
        form=form,
        skill_rows=_baris_skill(vocab, label, nilai_awal),
        skala=SKALA_SKILL,
        skill_error=None,
    )


@bp.route("/rekomendasi")
@login_required
def hitung():
    """Hitung CBF lalu SAW, simpan hasilnya dalam satu batch baru.

    Bobot yang dipakai = bobot sesi aktif: kustom bila mahasiswa
    pernah mengaturnya lewat panel "Atur Bobot", selain itu bobot
    default. Bobot yang benar-benar dipakai (sudah
    dinormalisasi) disimpan pada setiap baris batch.
    """
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash("Isi profil terlebih dahulu.", "warning")
        return redirect(url_for("spk.profil"))
    kustom = "bobot_custom" in session
    try:
        detail = _compute(profile, bobot=_bobot_aktif())
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("spk.index"))

    # satu id batch untuk seluruh baris perhitungan ini (unik per waktu,
    # termasuk mikrodetik agar dua perhitungan beruntun tetap berbeda)
    batch_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    bobot_json = json.dumps([round(b, 4) for b in detail["bobot_n"]])
    for peringkat, idx in enumerate(detail["saw"]["ranking"], start=1):
        db.session.add(
            RecommendationResult(
                profile_id=profile.id,
                career_id=detail["careers"][idx].id,
                skor_cbf=round(detail["skor_cbf"][idx], 4),
                skor_saw=round(detail["saw"]["skor"][idx], 4),
                peringkat=peringkat,
                batch_id=batch_id,
                bobot=bobot_json,
            )
        )
    db.session.commit()
    if kustom:
        flash(
            "Hasil dihitung dengan bobot kustom sesi Anda "
            "(bobot default tidak berubah).",
            "info",
        )
    return redirect(url_for("spk.hasil"))


@bp.route("/hasil/bobot", methods=["POST"])
@login_required
def atur_bobot():
    """Simpan bobot kustom di session, lalu hitung ulang.

    Input dibaca dari form HTML biasa (bukan WTForms) dan divalidasi
    seluruhnya di server: 4 angka, masing-masing antara 0 dan 1,
    total lebih dari 0.
    """
    mentah = [request.form.get(f"b{i}") for i in range(1, 5)]
    try:
        nilai = [float(x) for x in mentah]
    except (TypeError, ValueError):
        flash("Bobot harus berupa angka antara 0 dan 1.", "danger")
        return redirect(url_for("spk.hasil"))
    if any(x < 0 or x > 1 for x in nilai):
        flash("Setiap bobot harus antara 0 dan 1.", "danger")
        return redirect(url_for("spk.hasil"))
    if sum(nilai) <= 0:
        flash("Total bobot harus lebih dari 0.", "danger")
        return redirect(url_for("spk.hasil"))
    session["bobot_custom"] = [round(x, 4) for x in nilai]
    return redirect(url_for("spk.hitung"))


@bp.route("/hasil/bobot/reset", methods=["POST"])
@login_required
def reset_bobot():
    """Hapus bobot kustom sesi, kembali ke bobot default."""
    session.pop("bobot_custom", None)
    flash("Bobot dikembalikan ke bobot default.", "info")
    return redirect(url_for("spk.hitung"))


@bp.route("/hasil")
@login_required
def hasil():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return redirect(url_for("spk.profil"))
    rows = _hasil_batch_terakhir(profile.id)
    if not rows:
        return redirect(url_for("spk.hitung"))
    # Detail harus cocok dengan baris batch yang ditampilkan, jadi
    # bobot yang dipakai adalah bobot TERSIMPAN pada batch ini
    # (bukan bobot sesi saat ini). Batch lama (tanpa bobot): default.
    bobot_batch = _bobot_dari_batch(rows)
    if bobot_batch is None:
        bobot_batch = _bobot_default()
    try:
        detail = _compute(profile, bobot=bobot_batch)
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("spk.index"))
    default_n, _ = _normalisasi_bobot(_bobot_default())
    return render_template(
        "spk/hasil.html",
        profile=profile,
        rows=rows,
        detail=detail,
        bobot_batch=bobot_batch,
        bobot_sesi=_bobot_aktif(),
        batch_kustom=not _sama_bobot(bobot_batch, default_n),
        kustom_aktif="bobot_custom" in session,
    )


@bp.route("/riwayat")
@login_required
def riwayat():
    """Daftar batch perhitungan terdahulu untuk mahasiswa yang login."""
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return redirect(url_for("spk.profil"))

    batch_ids = [
        b[0]
        for b in db.session.query(RecommendationResult.batch_id)
        .filter_by(profile_id=profile.id)
        .distinct()
        .all()
        if b[0]
    ]
    default_n, _ = _normalisasi_bobot(_bobot_default())
    riwayat = []
    for bid in batch_ids:
        baris = (
            RecommendationResult.query.filter_by(
                profile_id=profile.id, batch_id=bid
            )
            .order_by(RecommendationResult.peringkat)
            .all()
        )
        if baris:
            bobot_batch = _bobot_dari_batch(baris) or default_n
            riwayat.append(
                {
                    "batch_id": bid,
                    "waktu": baris[0].created_at,
                    "teratas": baris[:3],
                    "bobot": bobot_batch,
                    "kustom": not _sama_bobot(bobot_batch, default_n),
                }
            )
    # batch terbaru paling atas
    riwayat.sort(key=lambda b: b["waktu"] or datetime.min, reverse=True)
    return render_template("spk/riwayat.html", riwayat=riwayat)


@bp.route("/export-csv")
@login_required
def export_csv():
    """Unduh hasil rekomendasi batch terbaru sebagai CSV."""
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return redirect(url_for("spk.profil"))
    rows = _hasil_batch_terakhir(profile.id)
    bobot_batch = _bobot_dari_batch(rows)
    if bobot_batch is None:
        bobot_batch, _ = _normalisasi_bobot(_bobot_default())
    default_n, _ = _normalisasi_bobot(_bobot_default())
    buffer = io.StringIO()
    penulis = csv.writer(buffer)
    # Baris metadata (diawali #) mencatat bobot yang dipakai batch ini
    # agar file ekspor dapat ditelusuri asalnya.
    penulis.writerow(
        [
            "# Bobot yang dipakai (C1;C2;C3;C4): "
            + ";".join(f"{b:.4f}" for b in bobot_batch)
        ]
    )
    penulis.writerow(
        [
            "# Sumber bobot: "
            + (
                "kustom (diatur mahasiswa)"
                if not _sama_bobot(bobot_batch, default_n)
                else "default"
            )
        ]
    )
    penulis.writerow(["peringkat", "karier", "skor_cbf", "skor_saw"])
    for r in rows:
        penulis.writerow([r.peringkat, r.career.nama, r.skor_cbf, r.skor_saw])
    return Response(
        buffer.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=hasil-rekomendasi.csv"
        },
    )
