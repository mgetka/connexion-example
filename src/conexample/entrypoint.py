"""Example Connexion application entrypoints"""
import signal
import sys

from .application import ConnexionExample


def run_dev():
    """Starts connexion example application developement server"""

    def signal_handler(*_):
        sys.exit()

    signal.signal(signal.SIGTERM, signal_handler)

    app = ConnexionExample()
    failed = False

    try:
        try:
            app.start()
            # Flask developement server is blocking. But if the application will not be blocking,
            # use the following code:
            # while True:
            #     sleep(60)
        except (KeyboardInterrupt, SystemExit):
            pass
        else:
            failed = True

    finally:
        app.stop()

    if failed:
        sys.exit(1)
