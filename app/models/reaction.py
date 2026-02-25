from datetime import datetime
from app import db

class PortfolioActivity(db.Model):
    __tablename__ = "portfolio_activities"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    item_id = db.Column(db.Integer, nullable=False)
    item_type = db.Column(db.String(50), nullable=False)  # movie, trailer, gallery

    activity_type = db.Column(db.String(20), nullable=False)  
    # like / dislike / comment

    content = db.Column(db.Text, nullable=True)  # only used for comments

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="portfolio_activities")

    __table_args__ = (
        db.Index("idx_item_lookup", "item_id", "item_type"),
    )