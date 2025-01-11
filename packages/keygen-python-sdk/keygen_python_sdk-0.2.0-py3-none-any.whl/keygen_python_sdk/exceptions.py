# SPDX-FileCopyrightText: 2024, Marcello Massaro
#
# SPDX-License-Identified: Apache-2.0
"""Exceptions
**********

The SDK has two main exception classes described below, plus more specialized exceptions
that inherit from them.

.. autoclass:: KeygenError

.. autoclass:: KeygenAPIError

Specialised SDK errors
======================

These exceptions inherit from :class:`KeygenError` but provide more information.

.. autoclass:: InvalidLicenseError

.. autoclass:: ExpiredLicenseError

.. autoclass:: InvalidLicenseFormatError

.. autoclass:: InvalidAlgorithmError

.. autoclass:: LicenseActivationError

.. autoclass:: LicenseCheckoutError

Specialised API errors
======================

These exceptions inherit from :class:`KeygenAPIError` but provide more information.

.. autoclass:: InvalidTokenError
"""

from __future__ import annotations

import json
import typing
from typing import TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from keygen_python_sdk.models import License


class KeygenError(Exception):
    """Base exception related to the Keygen library in general.

    Raised when an error occurs *locally*, meaning that this is a literal error
    response from the API, with a payload containing an ``"errors"`` field. This is
    usually raised when input parameters are incompatible, or when you required to
    do or assert something that was not possible. For example, validating a
    :class:`.License` may result in a :class:`KeygenError` because it turns out to
    not be valid anymore, but this is not an API error.
    """

    pass


class _KeygenAPIErrorSourceObject(BaseModel):
    pointer: str | None = None
    parameter: str | None = None


class _KeygenAPIErrorObject(BaseModel):
    title: str
    detail: str
    code: str = "UNKNOWN"
    source: _KeygenAPIErrorSourceObject | None = None


class KeygenAPIError(KeygenError):
    """Base exception related to the Keygen API in general.

    If the API returns multiple errors, the details of the first one are
    loaded into the attributes of this exception, and the rest are stored in
    :attr:`other_errors`. This is because the case of multiple errors is rare,
    so having access to the usually-only-one error is more useful.

    Attributes:
        title: Main error title.
        detail: Error detail message, for display purposes.
        code: Fixed, machine-readable code representing the error.
        source: Source URI of the exception.
        other_errors: List of further errors from the loaded response. Returning
            multiple errors is rare.

    Notes:
        Something that might look like an error but is actually a valid response will
        **not** be caught by this exception. It will be a child of :class:`KeygenError`
        instead. For example, a :class:`.License` not passing validation is not an API
        error: the API correctly answered to a validation request.

    .. automethod:: __init__
    """

    def __init__(self, *args, resp: dict[str, str]):
        """Initialize a new exception from an error response.

        Args:
            *args: Arguments passed directly to :class:`Exception`.
            resp: The body from a response returning an error. It will be used to
                populate the attributes of this exception to provide more information to
                client code catching it.
        """
        super().__init__(*args)
        all_errors = [
            _KeygenAPIErrorObject.model_validate_json(json.dumps(e))
            for e in (resp or {}).get("errors", {})
        ]
        main_err = all_errors.pop(0)
        self.title = main_err.title
        self.detail = main_err.detail
        self.code = main_err.code
        self.source = main_err.source
        self.other_errors = all_errors


class InvalidLicenseError(KeygenError):
    def __init__(self, msg: str, lic: "License"):
        super().__init__(msg or "Invalid license")
        self.license = lic


class InvalidLicenseFormatError(InvalidLicenseError):
    """The given license key is not in a valid format."""

    def __init__(self, msg: str, lic: "License"):
        super().__init__(msg or "the given license key is not in a valid format", lic)


class InvalidAlgorithmError(KeygenError):
    """The given license is signed with an unexpected algorithm."""

    def __init__(self, exp: str, act: str):
        """Mention what algorithm is expected, and which was found."""
        super().__init__(f"expected `{exp}`, got `{act}`")


class InvalidTokenError(KeygenAPIError):
    """The given token is not valid for the request."""

    def __init__(self, resp: dict[str, typing.Any]):
        _obj = _KeygenAPIErrorObject.model_validate_json(json.dumps(resp["errors"][0]))
        super().__init__(_obj.detail, resp=resp)


class ExpiredLicenseError(InvalidLicenseError):
    """A license is valid, but it's expired.

    Here "valid" means that it exists and has passed signature checks, but it needs
    to be renewed or replaced.
    """

    def __init__(self, lic: "License"):
        super().__init__(f"license expired on {lic.expiry}", lic)


class LicenseActivationError(KeyError):
    """A valid license could not activate a new machine in its pool."""

    def __init__(self):
        super().__init__("current machine could not be activated")


class LicenseCheckoutError(KeyError):
    """A license file could not be checked-out for offline use."""

    def __init__(self, msg=""):
        super().__init__(msg or "could not download a license file")
