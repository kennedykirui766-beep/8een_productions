from app import db
from datetime import datetime
# models.py (Add this class)
class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True)
    checkout_request_id = db.Column(db.String(100), unique=True, nullable=True) # From M-Pesa
    merchant_request_id = db.Column(db.String(100), nullable=True)
    
    phone_number = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    # Link to the content (Movie, Trailer, or Gallery)
    item_type = db.Column(db.String(50), nullable=False) # 'movie', 'trailer', 'gallery'
    item_id = db.Column(db.Integer, nullable=False)
    
    status = db.Column(db.String(20), default="pending") # pending, paid, failed
    result_code = db.Column(db.Integer, nullable=True)
    result_desc = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)