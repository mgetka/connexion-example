"""example Connexion application WSGI application entrypoint"""
from ...application import ConnexionExample

# pylint: disable=invalid-name

conexample = ConnexionExample()
conexample.prepare()
app = conexample.api
