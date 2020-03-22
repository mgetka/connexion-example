"""Interfaces definitions for internal application interactions."""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


class ConexampleException(Exception):
    """Generic conexample application exception."""


##
# Database classes
##


class DatabaseException(ConexampleException):
    """Generic database exception."""


class DatabaseStorageUnavailable(DatabaseException):
    """Database storage engine is unavailable."""


class DatabaseWriteFailed(DatabaseException):
    """Failed to write database data."""


class DatabaseReadFailed(DatabaseException):
    """Failed to read database data."""


class DatabaseInvalidRequest(DatabaseException):
    """Provided arguments are invalid."""


class DatabaseEntryNotFound(DatabaseReadFailed):
    """Requested entry doesn't exist."""


@dataclass(frozen=True)
class DatabaseEntry:
    """Database entry data."""

    name: str
    rating: int
    created: datetime


class Database(metaclass=ABCMeta):
    """Defines interface for database handler."""

    @abstractmethod
    def get_entry(self, name: str) -> DatabaseEntry:
        """Returns database entry for the provided entry name. If the entry does not exist raises
        DatabaseEntryNotFound exception."""

    @abstractmethod
    def set_entry_rating(self, name: str, rating: int) -> bool:
        """Sets rating for the entry with the provided name. If the entry already exists when called
        returns False, otherwise True."""

    @abstractmethod
    def delete_entry(self, name: str) -> bool:
        """Deletes registry entry with the provided name. Returns True if the entry existed,
        otherwise False."""

    @abstractmethod
    def get_entries(self) -> Iterable[DatabaseEntry, ...]:
        """Returns all entries from the database."""


##
# Core specific classes
##


class CoreException(ConexampleException):
    """Generic core exception."""


class CoreRequestUnsuccessful(CoreException):
    """Request could not be executed."""


class CoreInternalError(CoreRequestUnsuccessful):
    """Request could not be executed due to internal error."""


class CoreInvalidRequest(CoreRequestUnsuccessful):
    """Request payload is invalid."""


class CoreEntryNotFound(CoreRequestUnsuccessful):
    """the request concerns inexistent entry."""


@dataclass(frozen=True)
class CoreEntry:
    """Core entry data."""

    name: str
    rating: int


class Core(metaclass=ABCMeta):
    """Defines interface for core logic."""

    @abstractmethod
    def __init__(self, database: Database) -> None:
        """Class constructor template."""

    @abstractmethod
    def get_rating(self, name: str) -> int:
        """Returns raing for the entry with provided name. If the entry does not exist raises
        CoreEntryNotFound exception."""

    @abstractmethod
    def set_entry_rating(self, name: str, rating: int) -> bool:
        """Sets rating for the entry with the provided name. If the entry already exists when called
        returns False, otherwise True."""

    @abstractmethod
    def delete_entry(self, name: str) -> None:
        """If the entry does not exist raises CoreEntryNotFound exception."""

    @abstractmethod
    def get_entries(self) -> Iterable[CoreEntry, ...]:
        """Returns all entries from the database."""


##
# API handler specific classes
##


class ApiException(ConexampleException):
    """Generic API handler exception."""


class Api(metaclass=ABCMeta):
    """Defines interface for API handler."""

    # pylint: disable=too-few-public-methods

    @abstractmethod
    def __init__(self, core: Core) -> None:
        """Class constructor template"""
