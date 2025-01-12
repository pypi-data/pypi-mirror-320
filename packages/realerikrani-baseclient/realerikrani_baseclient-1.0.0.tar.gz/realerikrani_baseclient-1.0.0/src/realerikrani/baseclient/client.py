from dataclasses import dataclass
from typing import Any, Self
from urllib.parse import urlparse

import requests
from requests.auth import AuthBase

from .adapter import BaseAdapter


@dataclass
class BaseClient:
    session: requests.Session
    adapter: BaseAdapter
    url: str
    auth: AuthBase | None = None

    def __post_init__(self: Self) -> None:
        parsed_url = urlparse(self.url)
        if parsed_url.scheme == "http":
            self.session.mount("http://", self.adapter)
        elif parsed_url.scheme == "https":
            self.session.mount("https://", self.adapter)
        else:
            raise ValueError("Invalid URL scheme!")
        self.session.hooks = {"response": self.raise_for_status}

    def raise_for_status(
        self, response: requests.Response, *args: Any, **kwargs: Any
    ) -> None:
        """Raise an error for unsuccessful responses."""
        response.raise_for_status()

    def _set_auth(self, auth: AuthBase | None = None) -> None:
        """Set the session's authentication based on the provided auth."""
        if auth is not None:
            self.session.auth = auth  # Use the provided auth
        else:
            self.session.auth = self.auth  # Use the default auth

    def post(
        self: Self,
        endpoint: str,
        data: dict,
        auth: AuthBase | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        self._set_auth(auth)
        return self.session.post(endpoint, json=data, **kwargs)

    def get(
        self: Self, endpoint: str, auth: AuthBase | None = None, **kwargs: Any
    ) -> requests.Response:
        self._set_auth(auth)
        return self.session.get(endpoint, **kwargs)

    def patch(
        self: Self,
        endpoint: str,
        data: dict,
        auth: AuthBase | None = None,
        **kwargs: Any,
    ) -> requests.Response:
        self._set_auth(auth)
        return self.session.patch(endpoint, json=data, **kwargs)

    def delete(
        self: Self, endpoint: str, auth: AuthBase | None = None, **kwargs: Any
    ) -> requests.Response:
        self._set_auth(auth)
        return self.session.delete(endpoint, **kwargs)
