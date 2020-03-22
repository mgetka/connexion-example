import os
import subprocess
import tempfile

import pytest
import virtualenv
from dotenv import dotenv_values
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import conexample
import conexample.db.sql.db
import conexample.db.sql.models


@pytest.fixture(scope="function")
def test_config():

    original_settings = conexample.SETTINGS.copy()
    conexample.SETTINGS.update(
        dotenv_values(os.path.join(os.path.dirname(__file__), "testing.env"))
    )

    yield conexample.SETTINGS

    conexample.SETTINGS.clear()
    conexample.SETTINGS.update(original_settings)


@pytest.fixture(scope="session")
def venv():

    with tempfile.TemporaryDirectory() as env_dir:

        virtualenv.create_environment(env_dir)
        venv = env_dir + "/bin/python"

        # Install requirements
        args = [venv, "setup.py", "install"]
        subprocess.call(args)

        yield venv


@pytest.fixture(scope="function")
def venv_call(venv, test_config):

    processes = []

    def venv_subprocess_call(script):
        proc = subprocess.Popen(
            venv,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=test_config,
        )

        processes.append(proc)
        proc.stdin.write(script.encode())
        proc.stdin.close()

    yield venv_subprocess_call

    for proc in processes:
        if not proc.poll():
            proc.terminate()
            proc.wait()


@pytest.fixture(scope="function")
def db_connection(test_config):
    engine = conexample.db.sql.db.create_engine(
        connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    conn = engine.connect()
    conexample.db.sql.models.Base.metadata.create_all(engine)
    yield conn
    conexample.db.sql.models.Base.metadata.drop_all(engine)
    conn.close()


@pytest.fixture(scope="function")
def db_session(db_connection):
    transaction = db_connection.begin()
    sess = conexample.db.sql.db.Session(bind=db_connection)
    yield sess
    sess.close()
    conexample.db.sql.db.Session = sessionmaker()
    transaction.rollback()


@pytest.fixture(scope="function")
def coupled_db_session(db_connection):
    transaction = db_connection.begin()
    conexample.db.sql.db.session_bind(db_connection)
    sess = conexample.db.sql.db.Session()
    yield sess
    sess.close()
    conexample.db.sql.db.Session = sessionmaker()
    transaction.rollback()
