import datetime
import decimal
import json
import os
import uuid

from arkhos.templates import render_template
from arkhos.utils import DjangoJSONEncoder
from arkhos.version import __version__


class Request:
    """Represents an Arkhos request"""

    def __init__(self, proxy_event):
        self.method = proxy_event.get("method")
        self.headers = proxy_event.get("headers", {})
        self.GET = proxy_event.get("GET", {})
        self.body = proxy_event.get("body", "")
        self.parsed_json = False  # cached parsed json of request body
        self.path = proxy_event.get("path")

    @property
    def json(self):
        """Parse the request body. This will throw an error if request.body
        isn't valid json"""
        self.parsed_json = self.parsed_json or json.loads(self.body)
        return self.parsed_json

    def __str__(self):
        object_values = {
            "method": self.method,
            "headers": self.headers,
            "GET": self.GET,
            # "body": self.body,
        }
        return object_values


class HttpResponseBase(object):
    def __init__(self, content, status=200, headers=None):
        self.content = content

        self.headers = {}
        if headers:
            self.headers = headers

        if "content-type" not in self.headers:
            self.headers["content-type"] = "text/html"

        self.headers["arkhos_version"] = __version__

        if status is not None:
            try:
                self.status = int(status)
            except (ValueError, TypeError):
                raise TypeError("HTTP status code must be an integer.")

            if not 100 <= self.status <= 599:
                raise ValueError("HTTP status code must be an integer from 100 to 599.")

    def serialize(self):
        # todo: this isn't actually "serialized", maybe we should try serializing the pieces
        response = {
            "status": self.status,
            "body": self.content,
            "headers": self.headers,
        }
        return response

    def __repr__(self):
        return f"<{self.__class__.__name__} status={self.status} {self.headers['content-type']}>"


class HttpResponse(HttpResponseBase):
    def __init__(self, content, status=200, headers=None):
        if not isinstance(content, str):
            try:
                content = str(content)
            except (ValueError, TypeError):
                raise TypeError(
                    "HttpResponse content %s could not be converted to a string"
                    % (type(content),)
                )
        super(HttpResponse, self).__init__(content, status=status, headers=headers)


class JsonResponse(HttpResponseBase):
    def __init__(self, data, status=200, headers=None):
        response_headers = {}
        if headers:
            response_headers = headers

        if "content-type" not in response_headers:
            response_headers["content-type"] = "application/json"

        content = json.dumps(data, cls=DjangoJSONEncoder)
        super(JsonResponse, self).__init__(
            content, status=status, headers=response_headers
        )


def render(template_path, context=None, status=200, headers=None):
    """
    Return an HttpResponse from a template and context eg.
    arkhos.render(
      "path/to/template.html",
      {"key": "value", ...},
      status = 200,
      headers = {...}
    )
    """
    if not context:
        context = {}
    hydrated_template = render_template(template_path, context)
    return HttpResponse(hydrated_template, status, headers)


def render_static(url_path):
    """Returns the contents of a static file with the correct content-type header"""
    """Take the url path, eg. /static/css/styles.css
    and tries to find that file."""
    local_path = url_path.removeprefix("/")  # static should be in the current dir
    if not os.path.isfile(local_path):
        return HttpResponse(f"{local_path} could not be found", 404)

    with open(local_path, "rb") as fh:
        file_content = fh.read()

    # let's set the content-type header
    import mimetypes

    content_type = mimetypes.guess_type(local_path)[0]

    return HttpResponse(file_content, headers={"content-type": content_type})
