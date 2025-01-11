"""
Parity Quantum Computing GmbH
Rennweg 1 Top 314
6020 Innsbruck, Austria

Copyright (c) 2020-2023.
All rights reserved.

Tools to authenticate with the ParityOS cloud services.
"""

import getpass
import os
import warnings
from collections.abc import Iterator

# Environment variables that can hold the credentials for the host.
USERNAME_VARIABLE = "PARITYOS_USER"
PASSWORD_VARIABLE = "PARITYOS_PASS"


def generate_credentials(
    username: str = "",
    retries: int = 3,
) -> Iterator[dict[str, str]]:
    """
    Generates a series of JSON compatible dictionaries with a username and a password.
    The username can be provided as an argument. Otherwise, it is taken from the given system
    variable (this is tried only once), or requested from the user on the prompt.
    For security reasons, the password can not be provided as an argument. It is either taken
    from the given system variable (this is tried only once), or requested from the user on the
    prompt.
    The argument `retries` sets the maximum number of times to ask for a username or password,
    either from the environment or from the prompt.
    To make this generator fully non-interactive, set retries to 1 and set the correct system
    variables.

    :param str username: The username for the account on the server.
    :param int retries: Maximum number of times to ask for a username or password.
    """
    # The credentials object allows for a number of retries to provide the password.
    # First try: get data from the environment variables or else from prompt.
    username = username or _get_username(username)
    password = _get_password()
    yield {"username": username, "password": password}

    # The next tries are always interactive.
    for _ in range(1, retries):
        print("Login failed. Please provide the correct credentials.")
        username = _get_username(username)
        password = _get_password(password)
        yield {"username": username, "password": password}


def _get_username(username: str = "") -> str:
    """
    Ask for a username, either from the provided environment variable or on the prompt.
    If a username argument is given, then this is shown as a suggestion on the prompt
    and returned as the result if the user only types return.
    """

    if not username:
        username = os.getenv(USERNAME_VARIABLE, "")
        if username:
            return username

    username = input(f"ParityOS Username{username}: ") or username
    return username


def _get_password(password: str = "") -> str:
    """
    Ask for a password, either from the provided environment variable or on the prompt.
    If a password argument is given, then "***" is shown as a suggestion on the prompt
    and the given value is returned as the result if the user only types return.
    """
    if not password:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            password = os.getenv(PASSWORD_VARIABLE, "")

        if password:
            return password

    suggestion = " [***]" if password else ""
    password = getpass.getpass(f"ParityOS Password{suggestion}: ") or password
    return password
