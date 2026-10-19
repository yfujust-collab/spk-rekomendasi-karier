from flask import flash, redirect, render_template, url_for

from app import db
from app.admin import bp
from app.admin.forms import CareerForm, CriterionForm
from app.decorators import admin_required
from app.models import Career, Criterion, RecommendationResult, StudentProfile


@bp.route("/")
@admin_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        n_karier=Career.query.count(),
        n_kriteria=Criterion.query.count(),
        n_profil=StudentProfile.query.count(),
    )


@bp.route("/karier")
@admin_required
def careers():
    return render_template("admin/careers.html", careers=Career.query.all())


@bp.route("/karier/tambah", methods=["GET", "POST"])
@admin_required
def career_add():
    form = CareerForm()
    if form.validate_on_submit():
        db.session.add(
            Career(
                nama=form.nama.data.strip(),
                deskripsi=form.deskripsi.data.strip(),
                skills=form.skills.data.strip(),
                gaji_min=form.gaji_min.data or 0,
                gaji_max=form.gaji_max.data or 0,
                demand=form.demand.data or 5,
            )
        )
        db.session.commit()
        flash("Data karier ditambahkan.", "success")
        return redirect(url_for("admin.careers"))
    return render_template("admin/career_form.html", form=form, judul="Tambah Karier")


@bp.route("/karier/ubah/<int:cid>", methods=["GET", "POST"])
@admin_required
def career_edit(cid):
    career = Career.query.get_or_404(cid)
    form = CareerForm(obj=career)
    if form.validate_on_submit():
        form.populate_obj(career)
        db.session.commit()
        flash("Data karier diperbarui.", "success")
        return redirect(url_for("admin.careers"))
    return render_template("admin/career_form.html", form=form, judul="Ubah Karier")


@bp.route("/karier/hapus/<int:cid>", methods=["POST"])
@admin_required
def career_delete(cid):
    career = Career.query.get_or_404(cid)
    # hapus hasil rekomendasi terkait agar tidak menjadi data yatim
    RecommendationResult.query.filter_by(career_id=career.id).delete()
    db.session.delete(career)
    db.session.commit()
    flash("Data karier dihapus.", "info")
    return redirect(url_for("admin.careers"))


@bp.route("/kriteria", methods=["GET", "POST"])
@admin_required
def criteria():
    criteria = Criterion.query.order_by(Criterion.kode).all()
    form = CriterionForm()
    if form.validate_on_submit():
        # kode dari nomor terbesar yang ada + 1, agar tidak duplikat
        # bila kriteria pernah dihapus
        nomor = 0
        for c in Criterion.query.all():
            if c.kode and c.kode.startswith("C") and c.kode[1:].isdigit():
                nomor = max(nomor, int(c.kode[1:]))
        kode = f"C{nomor + 1}"
        db.session.add(
            Criterion(nama=form.nama.data.strip(), bobot=form.bobot.data, kode=kode)
        )
        db.session.commit()
        flash("Kriteria ditambahkan.", "success")
        return redirect(url_for("admin.criteria"))
    total = round(sum(c.bobot for c in criteria), 4)
    return render_template(
        "admin/criteria.html", criteria=criteria, form=form, total_bobot=total
    )


@bp.route("/kriteria/ubah/<int:cid>", methods=["GET", "POST"])
@admin_required
def criterion_edit(cid):
    criterion = Criterion.query.get_or_404(cid)
    form = CriterionForm(obj=criterion)
    if form.validate_on_submit():
        form.populate_obj(criterion)
        db.session.commit()
        flash("Kriteria diperbarui.", "success")
        return redirect(url_for("admin.criteria"))
    return render_template(
        "admin/criterion_form.html", form=form, criterion=criterion
    )


@bp.route("/kriteria/hapus/<int:cid>", methods=["POST"])
@admin_required
def criterion_delete(cid):
    criterion = Criterion.query.get_or_404(cid)
    db.session.delete(criterion)
    db.session.commit()
    flash("Kriteria dihapus.", "info")
    return redirect(url_for("admin.criteria"))
