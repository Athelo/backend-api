import logging
from models.base import Base
from models.database import db
from sqlalchemy.exc import IntegrityError, DatabaseError


logger = logging.getLogger()


def try_commit_entity(entity: Base):
    try:
        db.session.add(entity)
        db.session.commit()
        return True

    except IntegrityError as e:
        logger.error(
            f"Cannot create db entity because {e.orig.args[0]['M']}",
        )
        return False
    except DatabaseError as e:
        logger.error(
            f"Cannot create db entiy because {e.orig.args[0]['M']}",
        )
        return False
