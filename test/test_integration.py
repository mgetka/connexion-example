import logging
import socket
from multiprocessing import Process
from textwrap import dedent
from time import sleep
from unittest.mock import patch

import pytest

import conexample.application
import conexample.entrypoint

SUBPROCESS_WAIT = 3


def _port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", int(port))) == 0


class TestIntegration:
    def test_entry_endpoints(self, stateful_api_client):

        entries = [
            {"name": "python", "rating": 5},
            {"name": "flask", "rating": 4},
            {"name": "cassandra", "rating": 1},
        ]

        # Step 1. Consumer adds some entries
        for entry in entries:
            response = stateful_api_client.post("/v1/entry", json=entry)
            assert response.status_code == 201

        # Step 2. User is very pleased to see that he's entries are stored
        response = stateful_api_client.get("/v1/entry")
        assert response.status_code == 200
        assert len(response.json) == len(entries)

        # Step 3. Then he changed his mind, and concludes that he doesn't like flask that much :/
        response = stateful_api_client.post("/v1/entry/flask", json={"rating": 3})
        assert response.status_code == 200

        # Step 4. Later that night he got drunk and decided that he loves cassandra. But our system
        # will not let anyone make such mistake!
        response = stateful_api_client.post("/v1/entry/cassandra", json={"rating": 10})
        assert response.status_code == 400

        # Step 5. Next morning, he's only concern is fighting hangover, since he sees that
        # cassandra is still rated at 1
        response = stateful_api_client.get("/v1/entry/cassandra")
        assert response.status_code == 200
        assert response.json["rating"] == 1

        # Step 6. Suddenly he found out that there are other NoSQL databases that he instantly
        # wanted to rate!
        response = stateful_api_client.post("/v1/entry/mongo", json={"rating": 4})
        assert response.status_code == 201

        # Step 7. After gaining some experience with NoSQL he decided that he no longer wants to
        # know anything about this technology.
        for entry in ("cassandra", "mongo"):
            response = stateful_api_client.delete("/v1/entry/" + entry)
            assert response.status_code == 200

        # Step 8. He was especially mad about cassandra. Even though he deleted the entry moment
        # before, he deleted it again. Just to be sure!
        response = stateful_api_client.delete("/v1/entry/cassandra")
        assert response.status_code == 404


class TestEntrypoints:
    def test_fall_back_on_invalid_logging_level(self):

        conexample.SETTINGS["LOGGING_LEVEL"] = "XDDDD"
        conexample.application.ConnexionExample()
        assert logging.getLogger().level == logging.INFO

    @patch("conexample.application.Db")
    @patch("conexample.application.Core")
    @patch("conexample.application.Api")
    def test_entrypoint_starts_services(self, api, core, db):

        api.return_value = api
        core.return_value = core
        db.return_value = db

        app = conexample.application.ConnexionExample()

        app.start()

        try:

            assert api.called
            assert core.called
            assert db.called

            app.stop()

            # If there are any cleanup actions in stop, check here if they are executed

        finally:
            app.stop()

    def test_entrypoint_exits_clearly(self, test_config):

        proc = Process(target=conexample.entrypoint.run_dev)

        try:
            proc.start()
            sleep(SUBPROCESS_WAIT)

            assert proc.is_alive()

            proc.terminate()
            proc.join(SUBPROCESS_WAIT)

            assert proc.exitcode == 0

        finally:
            try:
                proc.kill()
            except AttributeError():
                pass

    def test_control_wsgi_entrypoint_syntax(self, test_config):
        import conexample.wsgi.api


class TestPackage:
    def test_dev_app_starts(self, venv_call, test_config):

        venv_call(
            dedent(
                """\
                from conexample.entrypoint import run_dev
                run_dev()
                """
            )
        )

        sleep(SUBPROCESS_WAIT)

        assert _port_in_use(5000)
