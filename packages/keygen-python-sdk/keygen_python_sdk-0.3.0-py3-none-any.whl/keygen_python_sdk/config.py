# SPDX-FileCopyrightText: 2024, Marcello Massaro
#
# SPDX-License-Identified: Apache-2.0
"""Configuration
*************

This module defines the single global object, :attr:`config` used by the rest of the
package to fill out API calls to Keygen.

All optional and mandatory configuration parameters can be set via environment
variables. For example, to set the account ID to ``"my-account"``, you can set the
environment variable ``KEYGEN_ACCOUNT_ID="my-account"``.

Additionally, these environment variables can be set in a ``.env`` file in the current
working directory. The location and name of this file cannot be customized.

.. autodata:: config

.. autoclass:: Config
"""

import os
import platform
from importlib.metadata import version

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import machineid
import requests as rq


# Check that a secrets folder exists, default to docker's
_secrets_folder = os.environ.get("KEYGEN_CFG_SECRETS_FOLDER", "/run/secrets")

settings_config = (
    SettingsConfigDict(
        extra="ignore",
        env_prefix="KEYGEN_",
        env_file=".env",
        secrets_dir=_secrets_folder,
    )
    if os.path.exists(_secrets_folder)
    else SettingsConfigDict(extra="ignore", env_prefix="KEYGEN_", env_file=".env")
)


class Config(BaseSettings):
    """Container for all API-related data necessary to communicate.

    You can set configuration attributes via environment variables, for example::

        KEYGEN_VARIABLE_NAME="your value here"

    This sets the attribute ``Config.variable_name``, if present. You cannot
    dynamically attach new configuration attributes like this.

    Attributes:
        account_id: The ID of your Keygen' account, or its slug.
        api_version: The API version to use. It needs to start with "v". It defaults to
            ``v1.7``.
        api_headers: Additional API headers to use in requests. These are passed
            directly to the ``requests`` module. These additional headers will be sent
            with **each** request.

            ``Content-Type`` and ``Accept`` are fixed by the API and cannot be changed.
        auth_token: A token with all necessary permissions to do what you want.
            Usually a product token.
        fingerprint: The machine fingerprint. If not given, the ``machineid`` module
            will be used as suggested in the Keygen docs.
        product_id: The product ID that you want to use in your session.
        pub_key: The hex-encoded public key used to validate responses from Keygen, encoded
            to bytes (yes, there are two different "encoded" in this sentence).
        signature_alg: Algorithm used to sign API responses.
        user_agent: The User-Agent to send to Keygen with each request.

    .. automethod:: request_headers
    """

    model_config = settings_config

    account_id: str = ""
    api_version: str = "v1.7"
    auth_token: str = ""
    license_file_alg: str = "base64+ed25519"
    pub_key: str = ""
    product_id: str = ""
    signature_alg: str = "ed25519"
    user_agent: str = f"keygen-python-sdk/{version('keygen-python-sdk')} {platform.platform()}/{platform.version()} requests/{rq.__version__}"
    fingerprint: str = Field(
        default_factory=lambda data: machineid.hashed_id(data["product_id"])
    )
    api_headers: dict[str, str] = Field(
        default_factory=lambda data: {"Authorization": f"Bearer {data['auth_token']}"}
    )

    def request_headers(self, **kwargs: str) -> dict[str, str]:
        """Return the complete headers to pass to a request.

        You can pass multiple keyword arguments as ``**kwargs``, and they will be
        added to the headers, overwriting :attr:`api_headers` if
        applicable.

        ``kwargs`` keys will be transformed as follows: underscores
        will be replaced by dashes, and words split by underscores will be
        capitalized.

        Notes:
            The headers ``Content-Type``, ``Accept``, are hard-coded and cannot be
            changed. ``User-Agent`` and ``Keygen-Version`` can be changed by assigning
            different values to :attr:`user_agent` and :attr:`api_version`.
        """
        headers = {
            "-".join([part.capitalize() for part in k.split("_")]): v
            for k, v in kwargs.items()
        }
        return (
            self.api_headers
            | headers
            | {
                "Content-Type": "application/vnd.api+json",
                "Accept": "application/vnd.api+json",
                "User-Agent": self.user_agent,
                "Keygen-Version": self.api_version,
            }
        )


config = Config()
"""The default configuration object, initialized on first import.

Configuration of this object is done via environment variables.

.. seealso:: :class:`Config`
"""
