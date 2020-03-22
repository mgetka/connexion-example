from textwrap import dedent
from time import sleep
import socket
import logging
from unittest.mock import patch
from multiprocessing import Process

import pytest

import conexample.application
import conexample.entrypoint

SUBPROCESS_WAIT = 3


def _port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", int(port))) == 0


class TestIntegration:
    pass


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

    @pytest.mark.skip(reason="Not yet implemented")
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


@pytest.mark.skip(reason="Not yet implemented")
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
