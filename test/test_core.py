import pytest

import conexample.core
import conexample.interface


class TestCalls:
    class TestGetRating:
        def test_on_succes(self, db):
            core = conexample.core.ApplicationCore(db)
            ret = core.get_rating("python")
            assert ret == db.get_entry.return_value.rating

        def test_on_no_entry(self, db):
            db.get_entry.side_effect = conexample.interface.DatabaseEntryNotFound
            core = conexample.core.ApplicationCore(db)
            with pytest.raises(conexample.interface.CoreEntryNotFound):
                core.get_rating("python")

        def test_on_db_error(self, db):
            db.get_entry.side_effect = conexample.interface.DatabaseException
            core = conexample.core.ApplicationCore(db)
            with pytest.raises(conexample.interface.CoreInternalError):
                core.get_rating("python")

    class TestSetEntryRating:
        def test_on_success(self, db):

            name = "python"
            rating = 6

            core = conexample.core.ApplicationCore(db)
            ret = core.set_entry_rating(name, rating)
            assert ret == db.set_entry_rating.return_value
            db.set_entry_rating.assert_called_once_with(name, rating)

        def test_cassandra_case(self, db):

            core = conexample.core.ApplicationCore(db)
            with pytest.raises(conexample.interface.CoreInvalidRequest):
                core.set_entry_rating("cassandra", 6)

        def test_on_db_error(self, db):

            db.set_entry_rating.side_effect = conexample.interface.DatabaseException
            core = conexample.core.ApplicationCore(db)
            with pytest.raises(conexample.interface.CoreInternalError):
                core.set_entry_rating("python", 6)

    class TestDeleteEntry:
        def test_on_succes(self, db):
            core = conexample.core.ApplicationCore(db)
            core.delete_entry("python")
            db.delete_entry.assert_called_once_with("python")

        def test_on_no_entry(self, db):
            db.delete_entry.return_value = False
            core = conexample.core.ApplicationCore(db)
            with pytest.raises(conexample.interface.CoreEntryNotFound):
                core.delete_entry("python")

        def test_on_db_error(self, db):
            db.delete_entry.side_effect = conexample.interface.DatabaseException
            core = conexample.core.ApplicationCore(db)
            with pytest.raises(conexample.interface.CoreInternalError):
                core.delete_entry("python")

    class TestGetEntries:
        def test_on_succes(self, db):
            core = conexample.core.ApplicationCore(db)
            ret = core.get_entries()
            assert len(ret) == len(db.get_entries.return_value)
            for entry in ret:
                assert isinstance(entry, conexample.interface.CoreEntry)

        def test_on_empty_db(self, db):
            db.get_entries.return_value = []
            core = conexample.core.ApplicationCore(db)
            ret = core.get_entries()
            assert len(ret) == 0

        def test_on_db_error(self, db):
            db.get_entries.side_effect = conexample.interface.DatabaseException
            core = conexample.core.ApplicationCore(db)
            with pytest.raises(conexample.interface.CoreInternalError):
                core.get_entries()
