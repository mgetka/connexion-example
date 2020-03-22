"""Basic SQLAlchemy database entities"""
from sqlalchemy import create_engine as create_engine_full
from sqlalchemy.orm import sessionmaker

from ... import SETTINGS


def create_engine(pool_size=None, max_overflow=None, **kwargs):
    """Creates SQLAlchemy Engine object.

    Please note that engine should be created after process forking!
    See:
    https://docs.sqlalchemy.org/en/13/core/connections.html#basic-usage
    https://docs.sqlalchemy.org/en/13/core/pooling.html#using-connection-pools-with-multiprocessing

    For typical application, engine creation should be followed with global session maker object
    configuration via Session.configure(bind=engine)."""

    if pool_size or SETTINGS["DATABASE_SQL_CONNECTION_POOL"]:
        kwargs["pool_size"] = pool_size or int(SETTINGS["DATABASE_SQL_CONNECTION_POOL"])

    if max_overflow or SETTINGS["DATABASE_SQL_POOL_OVERFLOW"]:
        kwargs["max_overflow"] = max_overflow or int(
            SETTINGS["DATABASE_SQL_POOL_OVERFLOW"]
        )

    return create_engine_full(SETTINGS["DATABASE_SQL_DATABASE_URI"], **kwargs)


# Be conformant with SQLAlchemy naming convention
Session = sessionmaker()  # pylint: disable=invalid-name


def session_bind(engine):
    """Binds specific engine/connection to the global session maker object"""
    Session.configure(bind=engine)
