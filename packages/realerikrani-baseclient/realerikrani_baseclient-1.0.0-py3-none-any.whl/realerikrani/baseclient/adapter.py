from typing import Any, Self

import requests
from urllib3 import Retry


class BaseAdapter(requests.adapters.HTTPAdapter):
    def __init__(self: Self, *args: Any, **kwargs: Any) -> None:
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        else:
            self.timeout = (2, 60)  # connect timeout, read timeout in seconds
            self.max_retries = Retry(
                total=4, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
            )
        super().__init__(*args, **kwargs)

    def send(  # type:ignore[override]
        self: Self, request: requests.PreparedRequest, **kwargs: Any
    ) -> requests.Response:
        kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)
