"""SQL database handler implementation"""
import logging
from contextlib import contextmanager

import sqlalchemy.exc
from sqlalchemy.orm import scoped_session

from ...interface import (
    Database,
    DatabaseEntryNotFound,
    DatabaseException,
    DatabaseStorageUnavailable,
)
from . import db
from .models import Entry

LOGGER = logging.getLogger("db.sql")


class SQLDatabase(Database):
    """SQLAlchemy based database handler"""

    def __init__(self):
        # Create connection pool on first access, thus, after forking
        self._session_maker = None

    @property
    def session_maker(self):
        """Returns SQLAlchemy session maker object."""
        if self._session_maker is None:
            if db.Session.kw["bind"] is None:
                engine = db.create_engine()
                db.session_bind(engine)
            self._session_maker = scoped_session(db.Session)
        return self._session_maker

    @contextmanager
    def session(self, write=False):
        """Provide a transactional scope around a series of operations."""

        session = self.session_maker()  # pylint: disable=not-callable

        try:
            yield session
            if write:
                session.commit()
        except sqlalchemy.exc.OperationalError as ex:
            session.rollback()
            raise DatabaseStorageUnavailable(ex)
        except sqlalchemy.exc.SQLAlchemyError as ex:  # WTF case
            session.rollback()
            raise DatabaseException(ex)
        finally:
            session.close()

    def get_entry(self, name):
        with self.session() as session:
            entry = session.query(Entry).filter(Entry.name == name).one_or_none()

            if not entry:
                raise DatabaseEntryNotFound()

            return entry.as_database_entry()

    def set_entry_rating(self, name: str, rating: int):
        with self.session(write=True) as session:
            entry = session.query(Entry).filter(Entry.name == name).one_or_none()

            if entry:
                entry.rating = rating
                return False

            session.add(Entry(name=name, rating=rating))
            return True

    def delete_entry(self, name: str):
        with self.session(write=True) as session:
            entry = session.query(Entry).filter(Entry.name == name).one_or_none()

            if not entry:
                return False

            session.delete(entry)
            return True

    def get_entries(self):
        with self.session() as session:
            entries = session.query(Entry).all()
            return [entry.as_database_entry() for entry in entries]
