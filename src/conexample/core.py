"""Application domain logic"""
import logging
from functools import wraps

from .interface import (
    Core,
    CoreEntry,
    CoreEntryNotFound,
    CoreInternalError,
    CoreInvalidRequest,
    DatabaseEntryNotFound,
    DatabaseException,
)

LOGGER = logging.getLogger("core")


def request_context(func):
    """Decorator handling common request errands"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseException as ex:
            LOGGER.error("Internal error: %s", ex)
            raise CoreInternalError(ex)

    return wrapper


class ApplicationCore(Core):
    """Implements application domain core logic. For this example application, core logic is very
    trivial, not to say, nonexistent. But in more complete application, this class is the place to
    implement authentication & authorization and other domain specific logic."""

    def __init__(self, database):
        # pylint: disable=super-init-not-called
        self.database = database

    @request_context
    def get_rating(self, name):
        try:
            return self.database.get_entry(name).rating
        except DatabaseEntryNotFound:
            raise CoreEntryNotFound()

    @request_context
    def set_entry_rating(self, name, rating):

        if name == "cassandra" and rating > 1:
            raise CoreInvalidRequest("cassandra cannot be rated above 1")

        return self.database.set_entry_rating(name, rating)

    @request_context
    def delete_entry(self, name):
        if not self.database.delete_entry(name):
            raise CoreEntryNotFound()

    @request_context
    def get_entries(self):
        return [
            CoreEntry(name=entry.name, rating=entry.rating)
            for entry in self.database.get_entries()
        ]
