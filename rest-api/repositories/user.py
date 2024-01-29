from models.users import Users
from models.database import db


def get_user_by_email(email: str) -> Users:
    return db.session.query(Users).filter(Users.email == email).one_or_none()
