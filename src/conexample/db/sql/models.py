"""ORM models for key registry tables"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base

from ...interface import DatabaseEntry

Base = declarative_base()  # pylint: disable=invalid-name


class Entry(Base):  # pylint: disable=too-few-public-methods
    """Entry model"""

    __tablename__ = "entries"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)
    rating = Column(Integer, nullable=False)

    created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def as_database_entry(self):
        """Returns the entry as a DatabaseEntry data object"""

        return DatabaseEntry(
            name=self.name,
            rating=self.rating,
            created=self.created,
            modified=self.modified,
        )
