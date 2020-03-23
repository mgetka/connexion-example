#!python
"""Running this scripts starts Flask developement server with autoreloading for control interface"""
from conexample.wsgi.api import app

app.run(use_reloader=True)
