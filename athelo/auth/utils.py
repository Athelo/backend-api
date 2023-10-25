from flask import Request
from models.database import db
from models.user_profile import UserProfile
from werkzeug.exceptions import Unauthorized


def get_user_from_request(request: Request):
    return db.session.execute(
        db.select(UserProfile).filter_by(email=request.email)
    ).scalar_one()


def is_current_user_or_403(request, user_id):
    user = get_user_from_request(request)
    if user_id != user.id:
        raise Unauthorized()
