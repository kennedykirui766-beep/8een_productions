from app import db
from datetime import datetime

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=True)
    username = db.Column(db.String(100))

    action = db.Column(db.String(50))
    # login, logout, register, watch_movie, watch_trailer, view_gallery, visit_page, payment

    item_type = db.Column(db.String(50))
    # movie, trailer, gallery, page

    item_id = db.Column(db.Integer)

    page = db.Column(db.String(200))

    payment_type = db.Column(db.String(50))
    
    target_type = db.Column(db.String(50))  # e.g., "auth", "page", etc.

    ip_address = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)