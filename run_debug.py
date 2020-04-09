#!python
"""Running this scripts starts Flask developement server with autoreloading"""
from conexample.wsgi.api import app

app.run(use_reloader=True)
