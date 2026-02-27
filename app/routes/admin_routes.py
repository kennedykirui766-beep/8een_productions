from flask import Blueprint, render_template, redirect, url_for, request, abort
from flask_login import login_user, login_required, logout_user, current_user
from app.models import project
from app.models.user import User
from app import db
from app.models import Payment, Movie
from app.utils import normalize_phone

admin_bp = Blueprint("admin", __name__, url_prefix="/secure-admin-8een")

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("admin.dashboard"))

    return render_template("admin/login.html")

# app/routes/admin_routes.py
import os
import cloudinary.uploader
from flask import Blueprint, request, redirect, url_for, flash, render_template
from werkzeug.utils import secure_filename
from app import db
from app.models.project import Movie, Gallery, Trailer
from datetime import datetime



# ----------------------
# Configure upload folders
# ----------------------
import os

from flask import current_app

def get_upload_path(folder):
    return os.path.join(current_app.root_path, "static/uploads", folder)



ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mkv", "avi", "webm"}
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename, allowed_exts):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_exts


# ----------------------
# Movie Route
# ----------------------
@admin_bp.route("/add_movie", methods=["GET", "POST"])
def add_movie():
    if request.method == "POST":
        try:
            title = request.form.get("title")
            original_title = request.form.get("original_title")
            synopsis = request.form.get("synopsis")
            release_date = request.form.get("release_date") or None
            language = request.form.get("language")
            duration = request.form.get("duration") or None
            pricing_type = request.form.get("pricing_type", "free")
            price = request.form.get("price") or 0
            rental_duration = request.form.get("rental_duration") or None
            genres = request.form.get("genres")

            movie_file = request.files.get("movie_file")
            poster_file = request.files.get("poster_file")
            trailer_file = request.files.get("trailer_file")

            if not movie_file or not allowed_file(movie_file.filename, ALLOWED_VIDEO_EXTENSIONS):
                flash("Movie file is required and must be a valid video.", "danger")
                return redirect(request.url)
            if not poster_file or not allowed_file(poster_file.filename, ALLOWED_IMAGE_EXTENSIONS):
                flash("Poster file is required and must be a valid image.", "danger")
                return redirect(request.url)

            movie_filename = secure_filename(movie_file.filename)
            poster_filename = secure_filename(poster_file.filename)
            trailer_filename = secure_filename(trailer_file.filename) if trailer_file else None

            # Upload movie to Cloudinary
            movie_upload = cloudinary.uploader.upload(
                movie_file,
                resource_type="video",
                folder="movies"
            )
            movie_filename = movie_upload["secure_url"]

            # Upload poster to Cloudinary
            poster_upload = cloudinary.uploader.upload(
                poster_file,
                folder="posters"
            )
            poster_filename = poster_upload["secure_url"]

            # Upload trailer if exists
            if trailer_file:
                trailer_upload = cloudinary.uploader.upload(
                    trailer_file,
                    resource_type="video",
                    folder="trailers"
                )
                trailer_filename = trailer_upload["secure_url"]


            movie = Movie(
                title=title,
                original_title=original_title,
                synopsis=synopsis,
                release_date=datetime.strptime(release_date, "%Y-%m-%d") if release_date else None,
                language=language,
                duration=int(duration) if duration else None,
                pricing_type=pricing_type,
                price=float(price),
                rental_duration=int(rental_duration) if rental_duration else None,
                genres=genres,
                movie_file=movie_filename,
                poster_file=poster_filename,
                trailer_file=trailer_filename
            )

            db.session.add(movie)
            db.session.commit()
            flash("Movie added successfully!", "success")
            return redirect(url_for("admin.add_movie"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding movie: {str(e)}", "danger")
            return redirect(request.url)

    return render_template("admin/projects.html")


# ----------------------
# Gallery Route
# ----------------------
@admin_bp.route("/add_gallery", methods=["GET", "POST"])
def add_gallery():
    if request.method == "POST":
        try:
            title = request.form.get("title")
            description = request.form.get("description")
            category = request.form.get("category")
            add_watermark = bool(request.form.get("add_watermark"))
            movie_id = request.form.get("movie_id") or None

            image_files = request.files.getlist("image_files")
            if not image_files:
                flash("At least one image is required.", "danger")
                return redirect(request.url)

            saved_files = []
            for img in image_files:
                if img and allowed_file(img.filename, ALLOWED_IMAGE_EXTENSIONS):
                    filename = secure_filename(img.filename)
                    upload_result = cloudinary.uploader.upload(
                    img,
                    folder="galleries"
                )
                saved_files.append(upload_result["secure_url"])

            gallery = Gallery(
                title=title,
                description=description,
                category=category,
                add_watermark=add_watermark,
                image_files=",".join(saved_files),
                movie_id=int(movie_id) if movie_id else None
            )

            db.session.add(gallery)
            db.session.commit()
            flash("Gallery added successfully!", "success")
            return redirect(url_for("admin.add_gallery"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding gallery: {str(e)}", "danger")
            return redirect(request.url)

    return render_template("admin/projects.html")


# ----------------------
# Trailer Route
# ----------------------
@admin_bp.route("/add_trailer", methods=["GET", "POST"])
def add_trailer():
    if request.method == "POST":
        try:
            title = request.form.get("title")
            description = request.form.get("description")
            trailer_type = request.form.get("trailer_type")
            release_date = request.form.get("release_date")
            movie_id = request.form.get("movie_id") or None

            trailer_file = request.files.get("trailer_file")
            thumbnail_file = request.files.get("thumbnail_file")

            if not trailer_file or not allowed_file(trailer_file.filename, ALLOWED_VIDEO_EXTENSIONS):
                flash("Trailer video is required and must be valid.", "danger")
                return redirect(request.url)
            if not thumbnail_file or not allowed_file(thumbnail_file.filename, ALLOWED_IMAGE_EXTENSIONS):
                flash("Trailer thumbnail is required and must be valid.", "danger")
                return redirect(request.url)

            trailer_filename = secure_filename(trailer_file.filename)
            thumbnail_filename = secure_filename(thumbnail_file.filename)

            # Upload trailer video
            trailer_upload = cloudinary.uploader.upload(
                trailer_file,
                resource_type="video",
                folder="trailers"
            )
            trailer_filename = trailer_upload["secure_url"]

            # Upload thumbnail image
            thumbnail_upload = cloudinary.uploader.upload(
                thumbnail_file,
                folder="thumbnails"
            )
            thumbnail_filename = thumbnail_upload["secure_url"]


            trailer = Trailer(
                title=title,
                description=description,
                trailer_type=trailer_type,
                release_date=datetime.strptime(release_date, "%Y-%m-%d") if release_date else None,
                movie_id=int(movie_id) if movie_id else None,
                trailer_file=trailer_filename,
                thumbnail_file=thumbnail_filename
            )

            db.session.add(trailer)
            db.session.commit()
            flash("Trailer added successfully!", "success")
            return redirect(url_for("admin.add_trailer"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error adding trailer: {str(e)}", "danger")
            return redirect(request.url)

    return render_template("admin/projects.html")


@admin_bp.route("/add_project")
@login_required
def add_project():
    return render_template("admin/add_project.html")







from flask import render_template, abort
from flask_login import login_required, current_user
from app.models import Payment
from app import db
from sqlalchemy import func

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if not current_user.is_admin:
        abort(403)

    # Get all payments (latest first)
    payments = Payment.query.order_by(Payment.created_at.desc()).all()

    # Summary stats
    total_payments = Payment.query.count()
    total_revenue = db.session.query(func.sum(Payment.amount))\
        .filter(Payment.status == "paid")\
        .scalar() or 0

    total_paid = Payment.query.filter_by(status="paid").count()
    total_pending = Payment.query.filter_by(status="pending").count()
    total_failed = Payment.query.filter_by(status="failed").count()

    return render_template(
        "admin/dashboard.html",
        payments=payments,
        total_payments=total_payments,
        total_revenue=total_revenue,
        total_paid=total_paid,
        total_pending=total_pending,
        total_failed=total_failed
    )




from flask import url_for

from flask import url_for

@admin_bp.route("/projects")
@login_required
def projects():
    from cloudinary.utils import cloudinary_url

    # Fetch all content
    movies = Movie.query.order_by(Movie.created_at.desc()).all()
    trailers = Trailer.query.order_by(Trailer.created_at.desc()).all()
    galleries = Gallery.query.order_by(Gallery.created_at.desc()).all()

    unified_projects = []

    # Movies
    for m in movies:
        poster_url, _ = cloudinary_url(m.poster_file) if m.poster_file else (None, None)
        movie_url, _ = cloudinary_url(m.movie_file) if m.movie_file else (None, None)
        unified_projects.append({
            "id": m.id,
            "title": m.title,
            "content_type": "movie",
            "poster_file": poster_url,
            "movie_file": movie_url,
            "trailer_file": None,
            "release_date": m.release_date,
            "pricing_type": m.pricing_type,
            "price": m.price
        })

    # Trailers
    for t in trailers:
        thumb_url, _ = cloudinary_url(t.thumbnail_file) if t.thumbnail_file else (None, None)
        trailer_url, _ = cloudinary_url(t.trailer_file) if t.trailer_file else (None, None)
        unified_projects.append({
            "id": t.id,
            "title": t.title,
            "content_type": "trailer",
            "poster_file": thumb_url,
            "movie_file": None,
            "trailer_file": trailer_url,
            "release_date": t.release_date,
            "pricing_type": "free",
            "price": 0
        })

    # Galleries
    for g in galleries:
        images = g.image_files.split(',') if g.image_files else []
        poster_url, _ = cloudinary_url(images[0].strip()) if images else (None, None)
        unified_projects.append({
            "id": g.id,
            "title": g.title,
            "content_type": "gallery",
            "poster_file": poster_url,
            "movie_file": None,
            "trailer_file": None,
            "release_date": g.created_at,
            "pricing_type": "free",
            "price": 0
        })

    return render_template("admin/projects.html", projects=unified_projects)


@admin_bp.route("/delete_movie/<int:id>", methods=["POST"])
@login_required
def delete_movie(id):
    movie = Movie.query.get_or_404(id)
    db.session.delete(movie)
    db.session.commit()
    flash("Movie deleted successfully.", "success")
    return redirect(url_for("admin.projects"))


@admin_bp.route("/delete_trailer/<int:id>", methods=["POST"])
@login_required
def delete_trailer(id):
    trailer = Trailer.query.get_or_404(id)
    db.session.delete(trailer)
    db.session.commit()
    flash("Trailer deleted successfully.", "success")
    return redirect(url_for("admin.projects"))


@admin_bp.route("/delete_gallery/<int:id>", methods=["POST"])
@login_required
def delete_gallery(id):
    gallery = Gallery.query.get_or_404(id)
    db.session.delete(gallery)
    db.session.commit()
    flash("Gallery deleted successfully.", "success")
    return redirect(url_for("admin.projects"))






@admin_bp.route("/payments")
@login_required
def payments():
    if not current_user.is_admin:
        abort(403)

    # Optional filter by status
    status_filter = request.args.get("status")

    query = Payment.query

    if status_filter:
        query = query.filter(Payment.status == status_filter)

    payments = query.order_by(Payment.created_at.desc()).all()

    # Summary stats
    total_payments = Payment.query.count()
    total_paid = Payment.query.filter_by(status="paid").count()
    total_pending = Payment.query.filter_by(status="pending").count()
    total_failed = Payment.query.filter_by(status="failed").count()

    total_revenue = db.session.query(func.sum(Payment.amount))\
        .filter(Payment.status == "paid")\
        .scalar() or 0

    return render_template(
        "admin/payments.html",
        payments=payments,
        total_payments=total_payments,
        total_paid=total_paid,
        total_pending=total_pending,
        total_failed=total_failed,
        total_revenue=total_revenue,
        current_filter=status_filter
    )


@admin_bp.route("/users")
@login_required
def users():
    return render_template("admin/users.html")



@admin_bp.route("/analytics")
@login_required
def analytics():
    if not current_user.is_admin:
        abort(403)

    # Total revenue (paid only)
    total_revenue = db.session.query(func.sum(Payment.amount))\
        .filter(Payment.status == "paid")\
        .scalar() or 0

    total_paid = Payment.query.filter_by(status="paid").count()
    total_failed = Payment.query.filter_by(status="failed").count()
    total_pending = Payment.query.filter_by(status="pending").count()
    total_transactions = Payment.query.count()

    # Revenue grouped by item type
    raw_revenue_by_type = db.session.query(
        Payment.item_type,
        func.sum(Payment.amount)
    ).filter(Payment.status == "paid")\
    .group_by(Payment.item_type)\
    .all()

    revenue_by_type = [
        {"type": row[0], "amount": float(row[1] or 0)}
        for row in raw_revenue_by_type
    ]


    # -------- DAILY REVENUE --------
    raw_daily = db.session.query(
        func.date(Payment.created_at),
        func.sum(Payment.amount)
    ).filter(Payment.status == "paid")\
     .group_by(func.date(Payment.created_at))\
     .order_by(func.date(Payment.created_at))\
     .all()

    daily_revenue = [
        {"date": row[0], "amount": float(row[1] or 0)}
        for row in raw_daily
    ]

    # -------- MONTHLY REVENUE --------
    raw_monthly = db.session.query(
        func.strftime("%Y-%m", Payment.created_at),
        func.sum(Payment.amount)
    ).filter(Payment.status == "paid")\
     .group_by(func.strftime("%Y-%m", Payment.created_at))\
     .order_by(func.strftime("%Y-%m", Payment.created_at))\
     .all()

    monthly_revenue = [
        {"month": row[0], "amount": float(row[1] or 0)}
        for row in raw_monthly
    ]

    # Success rate
    success_rate = 0
    if total_transactions > 0:
        success_rate = (total_paid / total_transactions) * 100

    return render_template(
        "admin/analytics.html",
        total_revenue=total_revenue,
        total_paid=total_paid,
        total_failed=total_failed,
        total_pending=total_pending,
        total_transactions=total_transactions,
        revenue_by_type=revenue_by_type,
        daily_revenue=daily_revenue,
        monthly_revenue=monthly_revenue,
        success_rate=round(success_rate, 2)
    )


@admin_bp.route("/media")
@login_required
def media():
    return render_template("admin/media.html")

@admin_bp.route("/settings")
@login_required
def settings():
    return render_template("admin/settings.html")


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))




@admin_bp.route("/edit_project/<string:project_type>/<int:id>", methods=["GET", "POST"])
@login_required
def edit_project(project_type, id):
    # 1️⃣ Load the correct object
    if project_type == "movie":
        project = Movie.query.get_or_404(id)
    elif project_type == "trailer":
        project = Trailer.query.get_or_404(id)
    elif project_type == "gallery":
        project = Gallery.query.get_or_404(id)
    else:
        flash("Invalid project type!", "danger")
        return redirect(url_for("admin.projects"))

    if request.method == "POST":
        try:
            # Common fields
            project.title = request.form.get("title")
            project.description = request.form.get("description") if hasattr(project, "description") else None

            # --------------------------
            # Movie-specific fields
            # --------------------------
            if project_type == "movie":
                project.original_title = request.form.get("original_title")
                project.synopsis = request.form.get("synopsis")
                release_date = request.form.get("release_date")
                project.release_date = datetime.strptime(release_date, "%Y-%m-%d") if release_date else None
                project.language = request.form.get("language")
                duration = request.form.get("duration")
                project.duration = int(duration) if duration else None
                project.genres = request.form.get("genres")
                project.pricing_type = request.form.get("pricing_type")
                price = request.form.get("price")
                project.price = float(price) if price else 0
                rental_duration = request.form.get("rental_duration")
                project.rental_duration = int(rental_duration) if rental_duration else None

                # Optional file uploads
                movie_file = request.files.get("movie_file")
                poster_file = request.files.get("poster_file")
                trailer_file = request.files.get("trailer_file")

                if movie_file and movie_file.filename != "" and allowed_file(movie_file.filename, ALLOWED_VIDEO_EXTENSIONS):
                    filename = secure_filename(movie_file.filename)
                    movie_file.save(os.path.join(get_upload_path("movies"), filename))
                    project.movie_file = filename

                if poster_file and poster_file.filename != "" and allowed_file(poster_file.filename, ALLOWED_IMAGE_EXTENSIONS):
                    filename = secure_filename(poster_file.filename)
                    poster_file.save(os.path.join(get_upload_path("posters"), filename))
                    project.poster_file = filename

                if trailer_file and trailer_file.filename != "" and allowed_file(trailer_file.filename, ALLOWED_VIDEO_EXTENSIONS):
                    filename = secure_filename(trailer_file.filename)
                    trailer_file.save(os.path.join(get_upload_path("trailers"), filename))
                    project.trailer_file = filename

            # --------------------------
            # Trailer-specific fields
            # --------------------------
            elif project_type == "trailer":
                project.trailer_type = request.form.get("trailer_type")
                release_date = request.form.get("release_date")
                project.release_date = datetime.strptime(release_date, "%Y-%m-%d") if release_date else None
                movie_id = request.form.get("movie_id")
                project.movie_id = int(movie_id) if movie_id else None

                trailer_file = request.files.get("trailer_file")
                thumbnail_file = request.files.get("thumbnail_file")

                if trailer_file and trailer_file.filename != "" and allowed_file(trailer_file.filename, ALLOWED_VIDEO_EXTENSIONS):
                    filename = secure_filename(trailer_file.filename)
                    trailer_file.save(os.path.join(get_upload_path("trailers"), filename))
                    project.trailer_file = filename

                if thumbnail_file and thumbnail_file.filename != "" and allowed_file(thumbnail_file.filename, ALLOWED_IMAGE_EXTENSIONS):
                    filename = secure_filename(thumbnail_file.filename)
                    thumbnail_file.save(os.path.join(get_upload_path("thumbnails"), filename))
                    project.thumbnail_file = filename

            # --------------------------
            # Gallery-specific fields
            # --------------------------
            elif project_type == "gallery":
                project.category = request.form.get("category")
                project.add_watermark = bool(request.form.get("add_watermark"))
                movie_id = request.form.get("movie_id")
                project.movie_id = int(movie_id) if movie_id else None

                image_files = request.files.getlist("image_files")
                if image_files and image_files[0].filename != "":
                    saved_files = []
                    for img in image_files:
                        if img and img.filename != "" and allowed_file(img.filename, ALLOWED_IMAGE_EXTENSIONS):
                            filename = secure_filename(img.filename)
                            img.save(os.path.join(get_upload_path("galleries"), filename))
                            saved_files.append(filename)
                    if saved_files:
                        project.image_files = ",".join(saved_files)

            # Commit changes
            db.session.commit()
            flash(f"{project_type.title()} updated successfully!", "success")
            return redirect(url_for("admin.projects"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating {project_type}: {str(e)}", "danger")

    # GET request → render the edit form
    return render_template(
        "admin/edit_project.html",
        project=project,
        project_type=project_type,
        form_action=url_for("admin.edit_project", project_type=project_type, id=id),
        movies=Movie.query.order_by(Movie.title).all()  # For linking dropdowns if needed
    )




