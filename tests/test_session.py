import os
import pytest
from aioshad.session import FileSessionStorage, MemorySessionStorage, SQLiteSessionStorage, Session


def test_session_export_and_from_string():
    session = Session(
        phone_number="989123456789",
        auth="testauthkey123456789012345678901",
        key_hex="abcdef0123456789abcdef0123456789",
        user_guid="u0user12345",
        state=1234567,
    )
    exported = session.export_string()
    assert isinstance(exported, str)

    loaded = Session.from_string(exported)
    assert loaded.phone_number == session.phone_number
    assert loaded.auth == session.auth
    assert loaded.key_hex == session.key_hex
    assert loaded.user_guid == session.user_guid
    assert loaded.state == session.state


def test_file_session_storage(tmp_path):
    storage = FileSessionStorage("test_phone", directory=str(tmp_path))
    session = Session(
        phone_number="test_phone",
        auth="my_auth_token",
        key_hex="0011223344",
        user_guid="u0user_guid",
    )
    storage.save(session)
    assert storage.exists()

    loaded = storage.load("test_phone")
    assert loaded.auth == "my_auth_token"
    assert loaded.user_guid == "u0user_guid"


def test_sqlite_session_storage(tmp_path):
    db_file = tmp_path / "test_sessions.db"
    storage = SQLiteSessionStorage("989123456789", db_path=str(db_file))

    session = Session(
        phone_number="989123456789",
        auth="sqlite_auth_test",
        key_hex="aabbccdd",
        user_guid="u0guid_sqlite",
    )
    storage.save(session)
    assert storage.exists()

    loaded = storage.load("989123456789")
    assert loaded.auth == "sqlite_auth_test"
    assert loaded.user_guid == "u0guid_sqlite"
