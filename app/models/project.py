from app import db
from datetime import datetime

class Movie(db.Model):
    __tablename__ = "movie"

    id = db.Column(db.Integer, primary_key=True)

    # Basic Information
    title = db.Column(db.String(200), nullable=False)
    original_title = db.Column(db.String(200), nullable=True)
    synopsis = db.Column(db.Text, nullable=True)

    release_date = db.Column(db.Date, nullable=True)
    language = db.Column(db.String(10), nullable=True)
    duration = db.Column(db.Integer, nullable=True)

    # Pricing
    pricing_type = db.Column(db.String(20), default="free")
    price = db.Column(db.Float, default=0)
    rental_duration = db.Column(db.Integer, nullable=True)

    # Genres
    genres = db.Column(db.String(255), nullable=True)

    # Media
    movie_file = db.Column(db.String(255), nullable=False)
    poster_file = db.Column(db.String(255), nullable=False)
    trailer_file = db.Column(db.String(255), nullable=True)

    # Status
    is_published = db.Column(db.Boolean, default=True)
    is_draft = db.Column(db.Boolean, default=False)

    # Relationships
    trailers = db.relationship(
        "Trailer",
        backref="movie",
        cascade="all, delete-orphan",
        lazy=True
    )

    galleries = db.relationship(
        "Gallery",
        backref="movie",
        cascade="all, delete-orphan",
        lazy=True
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )





class Gallery(db.Model):
    __tablename__ = "gallery"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)  # poster, still, behind, artwork, promo

    add_watermark = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    is_draft = db.Column(db.Boolean, default=False)

    # store multiple images as comma-separated paths
    image_files = db.Column(db.Text, nullable=True)

    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Trailer(db.Model):
    __tablename__ = "trailer"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    trailer_type = db.Column(db.String(50), nullable=True)
    release_date = db.Column(db.Date, nullable=True)

    trailer_file = db.Column(db.String(255), nullable=False)
    thumbnail_file = db.Column(db.String(255), nullable=False)

    movie_id = db.Column(
        db.Integer,
        db.ForeignKey("movie.id"),
        nullable=True
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

