from flask import Blueprint, render_template
from app.models.project import Movie, Trailer, Gallery  # import the correct classes
from flask import send_from_directory
from flask import Blueprint, render_template, request, jsonify, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models.reaction import PortfolioActivity  # adjust path if different


project_bp = Blueprint(
    "projects",
    __name__,
    template_folder="../templates/projects"
)

# ----------------------
# View a single movie/gallery/trailer
# ----------------------
@project_bp.route("/projects/movie/<int:id>")
def view_movie(id):
    movie = Movie.query.get_or_404(id)
    return render_template("project_detail.html", project=movie)

@project_bp.route("/projects/trailer/<int:id>")
def view_trailer(id):
    trailer = Trailer.query.get_or_404(id)
    return render_template("project_detail.html", project=trailer)

@project_bp.route("/projects/gallery/<int:id>")
def view_gallery(id):
    gallery = Gallery.query.get_or_404(id)
    return render_template("project_detail.html", project=gallery)


@project_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

# ----------------------
# List all movies, trailers, galleries
# ----------------------
@project_bp.route("/")
def all_projects():
    movies = Movie.query.order_by(Movie.created_at.desc()).all()
    trailers = Trailer.query.order_by(Trailer.created_at.desc()).all()
    galleries = Gallery.query.order_by(Gallery.created_at.desc()).all()

    return render_template(
        "projects.html",
        movies=movies,
        trailers=trailers,
        galleries=galleries
    )





@project_bp.route("/api/portfolio/interactions")
def get_interactions():
    item_id = request.args.get("item_id")
    item_type = request.args.get("item_type")

    activities = PortfolioActivity.query.filter_by(
        item_id=item_id,
        item_type=item_type
    ).all()

    likes = sum(1 for a in activities if a.activity_type == "like")
    dislikes = sum(1 for a in activities if a.activity_type == "dislike")

    comments = [a for a in activities if a.activity_type == "comment"]

    user_liked = False
    user_disliked = False

    if current_user.is_authenticated:
        for a in activities:
            if a.user_id == current_user.id:
                if a.activity_type == "like":
                    user_liked = True
                if a.activity_type == "dislike":
                    user_disliked = True

    return jsonify({
        "likes": likes,
        "dislikes": dislikes,
        "user_liked": user_liked,
        "user_disliked": user_disliked,
        "comments": [
            {
                "author": c.user.username,
                "text": c.content,
                "date": c.created_at.strftime("%b %d, %Y")
            }
            for c in comments
        ]
    })
    
    
@project_bp.route("/api/portfolio/interact", methods=["POST"])
@login_required
def interact():
    data = request.get_json()

    item_id = data.get("item_id")
    item_type = data.get("item_type")
    action = data.get("action")

    existing = PortfolioActivity.query.filter_by(
        user_id=current_user.id,
        item_id=item_id,
        item_type=item_type,
        activity_type=action
    ).first()

    if existing:
        db.session.delete(existing)
    else:
        opposite = "dislike" if action == "like" else "like"

        PortfolioActivity.query.filter_by(
            user_id=current_user.id,
            item_id=item_id,
            item_type=item_type,
            activity_type=opposite
        ).delete()

        new_activity = PortfolioActivity(
            user_id=current_user.id,
            item_id=item_id,
            item_type=item_type,
            activity_type=action
        )
        db.session.add(new_activity)

    db.session.commit()

    return jsonify({"success": True})


@project_bp.route("/api/portfolio/comment", methods=["POST"])
@login_required
def post_comment():
    data = request.get_json()

    item_id = data.get("item_id")
    item_type = data.get("item_type")
    content = data.get("content")

    if not content:
        return jsonify({"error": "Empty comment"}), 400

    comment = PortfolioActivity(
        user_id=current_user.id,
        item_id=item_id,
        item_type=item_type,
        activity_type="comment",
        content=content
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        "comment": {
            "author": current_user.username,
            "text": comment.content,
            "date": comment.created_at.strftime("%b %d, %Y")
        }
    })