"""Example Connexion application package"""
import sys
from collections import defaultdict
from os import environ, path

from dotenv import load_dotenv

from .version import __version__

if "CONEXAMPLE_CONFIG" in environ and path.isfile(environ["CONEXAMPLE_CONFIG"]):
    load_dotenv(dotenv_path=environ["CONEXAMPLE_CONFIG"])
else:
    load_dotenv()

load_dotenv(path.join(__path__[0], "defaults.env"))

SETTINGS = defaultdict(lambda: None, environ)
