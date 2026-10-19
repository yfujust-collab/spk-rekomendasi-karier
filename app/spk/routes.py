"""Alur utama mahasiswa: profil, hitung rekomendasi, hasil."""
from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Career, Criterion, RecommendationResult, StudentProfile
from app.services import cbf, saw
from app.spk import bp
from app.spk.forms import ProfileForm


def _vocabulary():
    return cbf.build_vocabulary(Career.query.all())


def _compute(profile):
    """Hitung CBF lalu SAW. Kembalikan detail lengkap untuk transparansi."""
    careers = Career.query.order_by(Career.id).all()
    criteria = Criterion.query.order_by(Criterion.kode).all()
    vocab = _vocabulary()
    vec_mhs = cbf.vectorize(profile.skill_list(), vocab)

    # Tahap 1: Content-Based Filtering -> skor kecocokan skill (C1)
    skor_cbf = []
    for career in careers:
        vec_karier = cbf.vectorize(career.skill_list(), vocab)
        skor_cbf.append(cbf.cosine_sim(vec_mhs, vec_karier))

    # Tahap 2: matriks keputusan SAW
    # C1 kecocokan skill, C2 prospek gaji, C3 demand pasar, C4 kesesuaian minat
    matrix = []
    for i, career in enumerate(careers):
        minat = 1.0 if career.id in profile.minat_ids() else 0.2
        matrix.append([skor_cbf[i], float(career.gaji_max), float(career.demand), minat])

    n_kriteria = len(matrix[0])
    criteria = criteria[:n_kriteria]
    bobot = [c.bobot for c in criteria]
    hasil_saw = saw.hitung(matrix, bobot)
    return {
        "careers": careers,
        "criteria": criteria,
        "matrix": matrix,
        "skor_cbf": skor_cbf,
        "saw": hasil_saw,
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
        hasil = (
            RecommendationResult.query.filter_by(profile_id=profile.id)
            .order_by(RecommendationResult.peringkat)
            .limit(3)
            .all()
        )
    return render_template("spk/index.html", profile=profile, hasil=hasil)


@bp.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    careers = Career.query.order_by(Career.nama).all()
    if not careers:
        flash("Data karier belum tersedia. Hubungi admin.", "warning")
        return redirect(url_for("spk.index"))
    vocab = _vocabulary()
    form = ProfileForm()
    form.skills.choices = [(s, s.title()) for s in vocab]
    form.minat.choices = [(c.id, c.nama) for c in careers]

    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if form.validate_on_submit():
        if not profile:
            profile = StudentProfile(user_id=current_user.id)
            db.session.add(profile)
        profile.nama = form.nama.data.strip()
        profile.nim = (form.nim.data or "").strip()
        profile.skills = ", ".join(form.skills.data)
        profile.minat = ", ".join(str(i) for i in form.minat.data)
        profile.ipk = form.ipk.data or 0.0
        # hasil lama tidak berlaku lagi bila profil berubah
        RecommendationResult.query.filter_by(profile_id=profile.id).delete()
        db.session.commit()
        flash("Profil tersimpan. Sistem menghitung rekomendasi.", "success")
        return redirect(url_for("spk.hitung"))

    if profile and not form.is_submitted():
        form.nama.data = profile.nama
        form.nim.data = profile.nim
        form.skills.data = profile.skill_list()
        form.minat.data = profile.minat_ids()
        form.ipk.data = profile.ipk
    return render_template("spk/profil.html", form=form)


@bp.route("/rekomendasi")
@login_required
def hitung():
    """Hitung CBF lalu SAW, simpan hasilnya."""
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash("Isi profil terlebih dahulu.", "warning")
        return redirect(url_for("spk.profil"))
    detail = _compute(profile)
    if not detail["careers"]:
        flash("Data karier atau kriteria belum lengkap.", "warning")
        return redirect(url_for("spk.index"))

    RecommendationResult.query.filter_by(profile_id=profile.id).delete()
    for peringkat, idx in enumerate(detail["saw"]["ranking"], start=1):
        db.session.add(
            RecommendationResult(
                profile_id=profile.id,
                career_id=detail["careers"][idx].id,
                skor_cbf=round(detail["skor_cbf"][idx], 4),
                skor_saw=round(detail["saw"]["skor"][idx], 4),
                peringkat=peringkat,
            )
        )
    db.session.commit()
    return redirect(url_for("spk.hasil"))


@bp.route("/hasil")
@login_required
def hasil():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return redirect(url_for("spk.profil"))
    rows = (
        RecommendationResult.query.filter_by(profile_id=profile.id)
        .order_by(RecommendationResult.peringkat)
        .all()
    )
    if not rows:
        return redirect(url_for("spk.hitung"))
    detail = _compute(profile)
    return render_template("spk/hasil.html", profile=profile, rows=rows, detail=detail)
