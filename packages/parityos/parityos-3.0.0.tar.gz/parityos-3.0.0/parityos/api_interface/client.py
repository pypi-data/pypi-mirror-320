"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2022.
All rights reserved.

Tools to connect to the ParityOS cloud services.
"""

from json.decoder import JSONDecodeError
from typing import Any, Optional

from attrs import define, field
from requests import Response, Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry  # pyright: ignore[reportMissingImports]

from parityos.api_interface.authentication import generate_credentials
from parityos.api_interface.exceptions import ParityOSAuthError, ParityOSRequestError


@define
class HTTPClient:
    """
    Client class that sets up HTTP parameters (authentication, API endpoints, and so on).

    :param username: username to connect with the ParityOS cloud services, if left empty
        the username will be received from the environment or prompted.
    :param host: the base url of the parity cloud service
    :param int http_retries: Number of http retries.
    :param int http_timeout: Maximum time in seconds to wait for a http response.
    :param float http_backoff_factor: Http exponential backoff factor.
    :param int retries: Maximum number of retries with different passwords.
    :param Session session: Request Session to use for communicating with the Parity API
    """

    username: str = field(default="")
    host: str = field(default="https://api.parityqc.com")
    http_retries: int = field(default=3)
    http_timeout: int = field(default=10)
    http_backoff_factor: float = field(default=0.02)
    retries: int = field(default=3)
    session: Session = field(factory=Session, init=False)

    def __attrs_post_init__(self):
        """
        Connects to the ParityAPI server, logs the user in and stores the session token.
        """
        # Credentials are instantiated here so that the password information
        # is garbage collected as soon as this method terminates.
        adapter = HTTPAdapter(
            max_retries=Retry(total=self.http_retries, backoff_factor=self.http_backoff_factor)
        )
        self.session.mount("https://", adapter)

        # The credentials object allows for a number of intents to provide the password.
        authentication_intents = generate_credentials(self.username, retries=self.retries)
        for credentials_data in authentication_intents:
            response = self.session.post(f"{self.host}/auth", data=credentials_data)
            data = response.json()
            if "token" in data:
                self.username = credentials_data["username"]
                self.session.headers["Authorization"] = f"Token {data['token']}"
                return

        # No authentication intents left after failed logins
        raise ParityOSAuthError(f"Failed login for user {self.username} on {self.host}.")

    def send_request(
        self, method: str, url: str, data: Optional[dict[str, Any]] = None
    ) -> Response:
        """
        Send a http request

        :param method: request method to use ('GET', 'POST', 'PUT', ... )
        :param url: target url
        :param data: payload data as a dictionary
        :return: requests.Response object
        """
        try:
            response = self.session.request(method, url=url, json=data, timeout=self.http_timeout)
        except Exception as err:
            message = f"Failed to receive valid response after at most {self.http_retries} retries."
            err.args = (*err.args, message)
            raise err

        if response.ok:
            return response
        else:
            try:
                error_data = response.json()
            except JSONDecodeError:
                error_data = "None"

            raise ParityOSRequestError(
                f"{method} on {url}: {response.status_code}, {error_data}",
                response=response,
            )
