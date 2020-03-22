"""Application objects of example Connexion application package"""
import logging

from . import SETTINGS, __version__
from .core import ApplicationCore as Core
from .db.sqlite import SQLiteDatabase as Db
from .api.rest import RestApi as Api

LOGGER = logging.getLogger(__package__)


class ConnexionExample:
    """Main application objet of Connexion application package"""

    def __init__(self):

        self.database = None
        self.core = None
        self.api = None

        logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s")
        root_loggger = logging.getLogger()

        try:
            root_loggger.setLevel(SETTINGS["LOGGING_LEVEL"].upper())
        except ValueError:
            LOGGER.error(
                "Failed to set logging level '%s'. Falling back to default INFO level.",
                SETTINGS["LOGGING_LEVEL"],
            )
            root_loggger.setLevel(logging.INFO)

        # Connexion, pls, shut up
        logging.getLogger("connexion").setLevel(logging.ERROR)
        logging.getLogger("openapi_spec_validator").setLevel(logging.ERROR)

        LOGGER.info("Connexion example version: %s", __version__)

    def prepare(self):
        """Prepares the service"""

        LOGGER.info("Starting conexample service.")

        LOGGER.info("Starting database interface")
        self.database = Db()

        LOGGER.info("Starting core logic.")
        self.core = Core(database=self.database)

        LOGGER.info("Starting API provider.")
        self.api = Api(core=self.core)

    def start(self):
        """Starts connexion example application developement server in a blocking manner"""

        self.prepare()

        LOGGER.warning(
            "Starting development server. DO NOT USE IN A PRODUCTION ENVIRONMENT!"
        )
        # self.api.run()

    def stop(self):  # pylint: disable=no-self-use
        """Stops the service"""

        LOGGER.info("Terminating conexample service.")

        # Terminate and free resources managed by any of application modules

        LOGGER.info("System finished gracefully.")
