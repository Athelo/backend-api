from models.base import Base
from models.database import db
from sqlalchemy.exc import IntegrityError, DatabaseError
from flask import current_app as app


def commit_entity(entity: Base):
    try:
        db.session.add(entity)
        db.session.commit()
        return True

    except IntegrityError as e:
        app.logger.error(
            f"Cannot create db entity because {e.orig.args[0]['M']}",
        )
        raise e
    except DatabaseError as e:
        app.logger.error(
            f"Cannot create db entiy because {e.orig.args[0]['M']}",
        )
        raise e
