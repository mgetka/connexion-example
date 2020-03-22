from datetime import datetime, timedelta
from time import sleep
from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

import conexample.db.sql
import conexample.db.sql.db
import conexample.db.sql.models


class TestDbConnection:
    def test_configures_session(self, coupled_db_session):
        db = conexample.db.sql.SQLDatabase()

        # Connection engine is created on first request
        db.get_entries()

        assert conexample.db.sql.db.Session.kw["bind"]

    @patch("conexample.db.sql.db.create_engine_full")
    def test_configures_pool_parameters(
        self, create_engine_full, db_session, test_config
    ):
        db = conexample.db.sql.SQLDatabase()

        pool_size = 5
        pool_overflow = 10

        test_config["DATABASE_SQL_CONNECTION_POOL"] = str(pool_size)
        test_config["DATABASE_SQL_POOL_OVERFLOW"] = str(pool_overflow)

        # Connection engine is created on first request
        db.get_entries()

        assert create_engine_full is conexample.db.sql.db.create_engine_full

        create_engine_full.assert_called_with(
            test_config["DATABASE_SQL_DATABASE_URI"],
            pool_size=pool_size,
            max_overflow=pool_overflow,
        )

    def test_fails_on_db_unreachable(self):

        db = conexample.db.sql.SQLDatabase()

        with pytest.raises(conexample.interface.DatabaseStorageUnavailable):
            db.get_entries()


class TestCalls:
    @patch("sqlalchemy.orm.query.Query")
    def test_generic_error_handler(self, query):
        query.configure_mock(side_effect=SQLAlchemyError)
        db = conexample.db.sql.SQLDatabase()

        with pytest.raises(conexample.interface.DatabaseException) as excinfo:
            db.get_entries()
        assert type(excinfo.value.args[0]) is SQLAlchemyError

    class TestSetEntryRating:
        def test_on_success(self, coupled_db_session):
            db = conexample.db.sql.SQLDatabase()

            name = "python"
            rating = 5

            ret = db.set_entry_rating(name, rating)

            assert ret

            entry = coupled_db_session.query(
                conexample.db.sql.models.Entry
            ).one_or_none()

            assert entry.name == name
            assert entry.rating == rating
            assert entry.created == entry.modified
            assert datetime.utcnow() - entry.created < timedelta(seconds=1)

        def test_updates_entry_when_already_exists(self, coupled_db_session):

            db = conexample.db.sql.SQLDatabase()

            name = "python"
            rating = 5

            ret = db.set_entry_rating(name, rating)

            assert ret

            sleep(2)

            new_rating = 6

            ret = db.set_entry_rating(name, new_rating)

            assert not ret

            entry = coupled_db_session.query(
                conexample.db.sql.models.Entry
            ).one_or_none()

            assert entry.name == name
            assert entry.rating == new_rating
            assert entry.created != entry.modified
            assert datetime.utcnow() - entry.modified < timedelta(seconds=1)

    class TestGetEntry:
        def test_on_success(self, coupled_db_session):

            db = conexample.db.sql.SQLDatabase()

            name = "python"
            rating = 5

            db.set_entry_rating(name, rating)

            ret = db.get_entry(name)

            assert ret.name == name
            assert ret.rating == rating

        def test_on_no_entry(self, coupled_db_session):

            db = conexample.db.sql.SQLDatabase()

            with pytest.raises(conexample.interface.DatabaseEntryNotFound):
                db.get_entry("python")

    class TestDeleteEntry:
        def test_on_success(self, coupled_db_session):

            db = conexample.db.sql.SQLDatabase()

            name = "python"

            db.set_entry_rating(name, 5)

            assert db.delete_entry(name)
            assert not coupled_db_session.query(
                conexample.db.sql.models.Entry
            ).one_or_none()

        def test_on_no_entry(self, coupled_db_session):

            db = conexample.db.sql.SQLDatabase()
            assert not db.delete_entry("python")

    class TestGetEntries:
        def test_on_empty_db(self, coupled_db_session):

            db = conexample.db.sql.SQLDatabase()

            assert len(db.get_entries()) == 0

        def test_on_success(self, coupled_db_session):

            db = conexample.db.sql.SQLDatabase()

            entries = [
                {"name": "python", "rating": 5},
                {"name": "flask", "rating": 4},
                {"name": "cassandra", "rating": 0},
            ]

            for entry in entries:
                db.set_entry_rating(**entry)

            ret = db.get_entries()

            for entry in ret:
                assert {"name": entry.name, "rating": entry.rating} in entries
            assert len(ret) == len(entries)
