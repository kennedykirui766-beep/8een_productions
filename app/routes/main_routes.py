from flask import Blueprint, render_template, redirect, url_for, request, abort, flash
from flask import abort
from app.models import Payment
from app.models.project import Movie, Trailer, Gallery
from app.models import Contact
from app import db


main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("index.html")

@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        service = request.form.get("service")
        subject = request.form.get("subject")
        message = request.form.get("message")

        # Save to database
        new_contact = Contact(
            name=name,
            email=email,
            phone=phone,
            service=service,
            subject=subject,
            message=message
        )

        db.session.add(new_contact)
        db.session.commit()

        flash("Message sent successfully!", "success")
        return redirect(url_for("main_bp.contact"))

    return render_template("contact.html")

@main_bp.route("/services")
def services():
    movies = Movie.query.order_by(Movie.created_at.desc()).all()
    trailers = Trailer.query.order_by(Trailer.created_at.desc()).all()
    galleries = Gallery.query.order_by(Gallery.created_at.desc()).all()

    return render_template(
        "services.html",
        movies=movies,
        trailers=trailers,
        galleries=galleries
    )
    
@main_bp.route("/portfolio")
def portfolio():
    movies = Movie.query.order_by(Movie.created_at.desc()).all()
    trailers = Trailer.query.order_by(Trailer.created_at.desc()).all()
    galleries = Gallery.query.order_by(Gallery.created_at.desc()).all()

    return render_template(
        "portfolio.html",   # create this template
        movies=movies,
        trailers=trailers,
        galleries=galleries
    )

@main_bp.route("/testimonials")
def testimonials():
    return render_template("testimonials.html")

@main_bp.route('/watch/movie/<int:id>')
def watch_movie(id):
    # fetch the movie from DB
    from app.models import Project
    movie = Project.query.get_or_404(id)
    return render_template('watch_movie.html', movie=movie)





@main_bp.route("/play/<int:movie_id>")
def play_movie(movie_id):

    payment = Payment.query.filter_by(
        item_type="movie",
        item_id=movie_id,
        status="paid"
    ).first()

    if not payment:
        abort(403)

    return render_template("play_movie.html")

