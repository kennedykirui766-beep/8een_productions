from flask_login import current_user
from flask import request
from app import db
from app.models.user_activity import UserActivity


def log_activity(action, item_type=None, item_id=None, payment_type=None):

    if not current_user.is_authenticated:
        return

    activity = UserActivity(
        user_id=current_user.id,
        username=current_user.username,
        action=action,
        item_type=item_type,
        item_id=item_id,
        payment_type=payment_type,
        page=request.path,
        ip_address=request.remote_addr
    )

    db.session.add(activity)
    db.session.commit()