import logging
from functools import cached_property
from http.client import HTTPConnection
from typing import Union
from urllib.parse import ParseResult, urlparse, urlunparse

from requests import Request, Session

from .auth import Auth
from .signatures.sign_request import sign_request


class Client:
    """Library main class"""

    def __init__(
        self,
        base_url,
        token=None,
        user_token=None,
        logger=logging.getLogger("alloniarest"),
        trace=False,
    ):
        """Permits connection to AllOnIA public APIs.

        You can use either token (Supertokens) or user_token based on the type
        of connection you want to have with the API.
        Currently, `token` uses a Supertoken based token and `user_token` uses
        an HMAC-SHA256 based signature.

        Args:
            base_url (str):
                Base URL used to send request to.
            token (str):
                Used for logged in connection. Is sent as a cookie.
            user_token (dict):
                Used to sign messages. This is another form of connection.
            logger:
                Python logger.
            trace:
                For trace HTTPConnection debugging
        """
        self._parsed_url = urlparse(base_url)
        self._token = token
        self._user_token = user_token
        self.logger = logger

        if trace:
            HTTPConnection.debuglevel = 1

    @cached_property
    def auth(self):
        return Auth(self)

    @property
    def headers(self):
        headers = {"accept": "application/json", "user-agent": "aleia_rest"}

        if self._token is not None:
            headers["cookie"] = self._token

        return headers

    @property
    def scheme(self):
        return self._parsed_url.scheme

    @property
    def hostname(self):
        return self._parsed_url.hostname

    @property
    def user_token(self):
        return self._user_token

    def make_url(self, path):
        url = ParseResult(
            self._parsed_url.scheme,
            self._parsed_url.netloc,
            path,
            self._parsed_url.params,
            self._parsed_url.query,
            self._parsed_url.fragment,
        )
        return urlunparse(url)

    @sign_request
    def prepare_request(
        self,
        method: str,
        path: str,
        headers: Union[dict, None] = None,
        **kwargs,
    ):
        """Sets up the arguments to pass to `requests.request`."""
        url = self.make_url(path)
        self.logger.debug(f"{method} {url} {kwargs}")
        request = Request(
            method,
            url,
            headers={**self.headers, **(headers or {})},
            **kwargs,
        )
        return request.prepare()

    def request(self, *args, **kwargs):
        """Performs the request to AllOnIA API."""
        session = Session()
        prepared_request = self.prepare_request(*args, **kwargs)
        return session.send(prepared_request)
