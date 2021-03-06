"""Flask & Connexion base REST API implementation"""
import logging
import os
from functools import partial, wraps

import connexion
import connexion.utils
from connexion.resolver import Resolver
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound

from ...interface import Api, CoreEntryNotFound, CoreException, CoreInvalidRequest

LOGGER = logging.getLogger("api.rest")
OPERATION_ID_PREFIX = "conexample.api"


def _make_response(status, details, title, headers=None):
    return (
        {"details": details, "status": status, "title": title, "type": "about:blank"},
        status,
        headers,
    )


def request_context(func):
    """Decorator handling common request errands"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CoreException as ex:
            LOGGER.error("Internal error: %s", ex)
            raise InternalServerError(str(ex))

    return wrapper


class RestApi(Api, connexion.FlaskApp):
    """API handler implemented w/ connexion framework."""

    class entry:  # pylint: disable=invalid-name
        """Container for conexample.api.entry.* routes"""

        @staticmethod
        @request_context
        def get(handler):
            """Implements conexample.api.entry.get"""
            return handler.core.get_entries()

        @staticmethod
        @request_context
        def post(handler, body):
            """Implements conexample.api.entry.post"""
            try:
                created = handler.core.set_entry_rating(
                    name=body["name"], rating=body["rating"]
                )
            except CoreInvalidRequest as ex:
                raise BadRequest(str(ex))

            if created:
                return _make_response(
                    201,
                    "Entry created",
                    "Created",
                    {"Location": "entry/%s" % body["name"]},
                )

            return _make_response(
                200, "Entry updated", "OK", {"Location": "entry/%s" % body["name"]}
            )

        class element:  # pylint: disable=invalid-name
            """Container for conexample.api.entry.element.* routes"""

            @staticmethod
            @request_context
            def get(handler, name):
                """Implements conexample.api.entry.element.get"""

                try:
                    return {"name": name, "rating": handler.core.get_rating(name)}
                except CoreEntryNotFound:
                    raise NotFound("Entry not found")

            @staticmethod
            @request_context
            def post(handler, name, body):
                """Implements conexample.api.entry.element.post"""

                try:
                    created = handler.core.set_entry_rating(
                        name=name, rating=body["rating"]
                    )
                except CoreInvalidRequest as ex:
                    raise BadRequest(str(ex))

                if created:
                    return _make_response(
                        201, "Entry created", "Created", {"Location": "%s" % name}
                    )

                return _make_response(
                    200, "Entry updated", "OK", {"Location": "%s" % name}
                )

            @staticmethod
            @request_context
            def delete(handler, name):
                """Implements conexample.api.entry.element.delete"""

                try:
                    handler.core.delete_entry(name)
                except CoreEntryNotFound:
                    raise NotFound("Entry not found")

                return _make_response(200, "Entry deleted", "OK")

    def __init__(self, core):
        # pylint: disable=super-init-not-called
        self.core = core

        connexion.FlaskApp.__init__(  # pylint: disable=non-parent-init-called
            self, __name__
        )

        self.add_api(
            os.path.join(os.path.dirname(__file__), "api.yml"),
            resolver=Resolver(self.func_resolv),
            strict_validation=True,
        )

    def func_resolv(self, function_name):
        """Resolves request handlers based on OpenAPI specified operation ids"""

        if not function_name.startswith(OPERATION_ID_PREFIX):
            raise ImportError()

        subject = self
        handler_path = function_name[len(OPERATION_ID_PREFIX) + 1 :].split(".")
        for step in handler_path:
            subject = getattr(subject, step)

        return partial(subject, self)
