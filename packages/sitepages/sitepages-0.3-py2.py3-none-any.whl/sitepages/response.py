# coding:utf-8

from functools import wraps
import traceback
from typing import Any
from typing import Callable

from flask import Response
from flask import jsonify
from markdown import markdown


class FlaskResponse:

    @classmethod
    def html(cls, func: Callable[..., str]) -> Callable[..., Response]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                content = func(*args, **kwargs)
                return Response(response=content, status=200, mimetype="text/html")  # noqa:E501
            except Exception:
                trace: str = traceback.format_exc()
                return Response(response=trace, status=500, mimetype="text/plain")  # noqa:E501
        return wrapper

    @classmethod
    def json(cls, func: Callable[..., Any]) -> Callable[..., Response]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                content = func(*args, **kwargs)
                return jsonify(content)
            except Exception:
                trace: str = traceback.format_exc()
                return Response(response=trace, status=500, mimetype="text/plain")  # noqa:E501
        return wrapper

    @classmethod
    def plain(cls, func: Callable[..., str]) -> Callable[..., Response]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                content = func(*args, **kwargs)
                return Response(response=content, status=200, mimetype="text/plain")  # noqa:E501
            except Exception:
                trace: str = traceback.format_exc()
                return Response(response=trace, status=500, mimetype="text/plain")  # noqa:E501
        return wrapper

    @classmethod
    def markdown(cls, func: Callable[..., str]) -> Callable[..., Response]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                content = func(*args, **kwargs)
                return Response(response=markdown(content), status=200, mimetype="text/html")  # noqa:E501
            except Exception:
                trace: str = traceback.format_exc()
                return Response(response=trace, status=500, mimetype="text/plain")  # noqa:E501
        return wrapper
