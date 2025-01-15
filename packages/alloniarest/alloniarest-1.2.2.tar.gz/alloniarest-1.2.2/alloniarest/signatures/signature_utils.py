"""Helper file to help adding signature to http request header."""

import json
from typing import NamedTuple

from werkzeug.datastructures import MultiDict


class RequestInfo(NamedTuple):
    """Defines fields that are going to be accessed by the SignatureBuilder."""

    method: str
    headers: dict
    path: str
    args: MultiDict
    data: bytes


def get_data_from_kwargs(**kwargs):
    """Helper function to retrieve data from a request call kwargs.

    For now, only `json` key is taken into account.
    """
    json_data = kwargs.get("json")
    if json_data is not None:
        return json.dumps(json_data).encode("utf-8")
    return b""


def args_multidict_from_params(params: dict):
    """Creates a MultiDict instance from params for SignatureBuilder."""
    return MultiDict(params)


def fill_signature_headers(headers, signature):
    """Fills headers with user signature."""
    for key, value in signature.items():
        headers[key] = value


def make_request_info(headers, method, path, **kwargs):
    """Creates a RequestInfo instance for SignatureBuilder."""
    return RequestInfo(
        method=method,
        headers=headers,
        path=path,
        args=args_multidict_from_params(kwargs.get("params", {})),
        data=get_data_from_kwargs(**kwargs),
    )
