# SPDX-FileCopyrightText: 2024, Marcello Massaro
#
# SPDX-License-Identified: Apache-2.0
"""Functional API
**************

This part of the API relies on the minimum amount of input data possible. Most of the
calls are ID-based and authentication is "pluggable", meaning that you can always pass
a different authentication token to calls that require it. Otherwise, the API calls
will default to what's defined in the :data:`.config` global object.

.. autofunction:: checkout_license

.. autofunction:: create_new_user

.. autofunction:: decode_license_file

.. autofunction:: list_license_entitlements

.. autofunction:: request_password_reset

.. autofunction:: request_and_validate

.. autofunction:: revoke_token

.. autofunction:: user_and_token_from_password

.. autofunction:: validate_key

.. autofunction:: verify_api_signature

.. autofunction:: verify_local_license_file

.. autofunction:: verify_local_license_file_contents

.. autofunction:: verify_signature
"""

import base64
import datetime
import email.utils as eut
import hashlib
import json
import logging
import pathlib
import typing

import nacl.exceptions
import requests as rq
from nacl.encoding import HexEncoder
from nacl.signing import VerifyKey

from keygen_python_sdk import exceptions
from keygen_python_sdk.config import config
from keygen_python_sdk.exceptions import (
    InvalidTokenError,
    InvalidAlgorithmError,
    KeygenError,
)
from keygen_python_sdk import models

logger = logging.getLogger(__name__)


def _fmt_errors(req: dict[str, typing.Any]) -> list[str]:
    """Format all errors in ``req`` for display.

    The format is::

        CODE(TITLE): DETAIL
    """
    if "errors" not in req:
        return []
    return [
        f"{e.get('code', 'UNSET')}({e.get('title', 'No title')}): {e.get('detail', 'No details')}"
        for e in req["errors"]
    ]


def checkout_license(license_id: str, license_key: str | None = None) -> str:
    """Get a new license file for offline validation.

    Args:
        license_id: The ID of the license.
        license_key: The license key for authorization purposes. If ``None``, the
            value from :attr:`.Config.auth_token` is used.

    Returns:
        The new license file contents.

    Raises:
        LicenseCheckoutError: If the request for the new license is invalid.
    """
    auth = f"License {license_key}" if license_key else f"Bearer {config.auth_token}"
    code, payload = request_and_validate(
        f"/licenses/{license_id}/actions/check-out",
        "get",
        config.request_headers(authorization=auth),
    )
    logger.debug("API replied with %d", code)

    if code != 200:
        if "errors" in payload:
            raise exceptions.KeygenAPIError(resp=payload)
        raise exceptions.KeygenError("could not check-out license")
    return typing.cast(str, payload)


def create_new_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str | None = None,
    auth_token: str | None = None,
) -> dict[str, typing.Any]:
    """Create a new user.

    Args:
        first_name: User's given name.
        last_name: User's surname name.
        email: User's e-mail address.
        password: An optional password.
        auth_token: Token with the authorization to create new users. If ``None``,
            the value from :attr:`.Config.auth_token` is used.

    Returns:
        The response from the creation request.

    Raises:
        KeygenError: If the user could not be created for some reason.

    Notes:
        Users don’t **necessarily** need a password to be created. If that's the case,
        these are referred to as "managed users", whose authentication is delegated to
        some other system.
    """

    attrs: dict[str, str] = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
    }
    if password:
        attrs["password"] = password

    code, payload = request_and_validate(
        "/users",
        "post",
        config.request_headers(authorization=f"Bearer {auth_token}"),
        {
            "data": {
                "type": "users",
                "attributes": attrs,
            }
        },
    )

    if code > 300:
        raise exceptions.KeygenAPIError(resp=payload)
    return payload


def decode_license_file(license_file: pathlib.Path | str) -> dict[str, typing.Any]:
    """Remove the header and footer from a license file, and return its decoded content.

    The license file are base64-encoded, and that encoded text is framed by a the
    following header and footer::

        -----BEGIN LICENSE FILE-----
        base64-encoded-text
        -----END LICENSE FILE-----

    Note that there is an empty line at the end of the file.

    Args:
        license_file: Either a :class:`pathlib.Path` where the license to decode is,
            or the textual contents of said file.

    Returns:
        The decoded license JSON object.

    See Also:
        https://keygen.sh/docs/api/cryptography/#cryptographic-lic-payload
    """
    if isinstance(license_file, pathlib.Path):
        contents = license_file.read_text()
    else:
        contents = license_file
    return json.loads(
        base64.b64decode(
            contents.strip()
            .removeprefix("-----BEGIN LICENSE FILE-----")
            .removesuffix("-----END LICENSE FILE-----")
            .replace("\n", "")
        ).decode()
    )


# def get_license_file_info(
#     license_file: pathlib.Path | str,
# ) -> dict[str, typing.Any]:
#     """Get general information about a given license **file** for display purposes.

#     Args:
#         license_file: License file to analyze. If it's a :class:`pathlib.Path` type,
#             then the file is opened, decoded, and validated. If it's a string, it's
#             assumed to be the contents of the license file simply after being
#             base64-decoded.

#     Returns:
#         License: The parsed object.

#     Raises:
#         InvalidLicenseError: If the license file cannot be validated.
#     """
#     if isinstance(license_file, str):
#         lic = verify_local_license_file_contents(json.loads(license_file))
#     elif isinstance(license_file, pathlib.Path):
#         lic = verify_local_license_file(license_file)
#     else:
#         raise KeygenError("license file is expired or invalid")
#     return models.License.from_response(lic)


def list_license_entitlements(
    lic_id: str, license_key: str | None = None
) -> list[dict[str, typing.Any]]:
    """List entitlements associated to a license.

    Args:
        lic_id: License ID of which to list the entitlements.
        license_key: Key used for authentication. If ``None``, the value from
            :attr:`.Config.auth_token` is used instead.
    """
    license_request = request_and_validate(
        f"/licenses/{lic_id}/entitlements",
        "get",
        config.request_headers(
            authorization=f"License {license_key}"
            if license_key
            else f"Bearer {config.auth_token}"
        ),
    )

    _, payload = license_request
    if "errors" in payload:
        raise exceptions.KeygenAPIError("invalid auth token", resp=payload)

    return payload["data"]


def request_password_reset(user: models.User | str, deliver=True) -> None:
    """Request a password reset for a given user.

    Args:
        user: User for which to reset the password, or its email.
        deliver: Tell keygen to automatically email the user to
            allow them to reset the password.

    Raises:
        KeygenError: If the request failed because of validation issues of the
            response, or if another error happened (e.g. email doesn’t exist).

    Notes:
        If ``deliver == False``, then you need to listen to a specific event through
        a webhook from keygen. This is *probably* not what you want to do.
    """
    if isinstance(user, models.User):
        user = user.email
    code, payload = request_and_validate(
        "/passwords",
        "post",
        config.request_headers(),
        {"meta": {"email": user, "deliver": deliver}},
    )

    if code > 300:
        raise exceptions.KeygenAPIError("request could not be fulfilled", resp=payload)
    logger.debug(json.dumps(payload))


def request_and_validate(
    url: str,
    method: str = "get",
    headers: dict | None = None,
    data: dict | None = None,
) -> tuple[int, dict]:
    """Make an API request and validate its response signature.

    All interactions with the API will be answered with signed responses **or** with
    an error that is not necessarily signed. This function is a wrapper around
    :func:`requests.get` and :func:`requests.post` to make sure that *each* request
    is properly validated.

    Args:
        url: The url of the API call. If this starts with a slash (``/``), it's
            interpreted as relative to ``https://api.keygen.sh/v1/accounts/<account>``.
        method: The method to use for the request.
        headers: Headers to pass to :mod:`requests`. They will be merged with those
            set by :meth:`.Config.request_headers` by passing them as unpacked
            dictionary to said method.
        data: Data to pass to :mod:`requests`.

    Returns:
        The response code and body (as JSON) if the request's signature is valid,
        otherwise ``None``.

    Notes:
        The API might return some error, but the caller of this function will not be
        informed of the reason *why* validation failed.
    """
    if url.startswith("/"):
        url = f"https://api.keygen.sh/v1/accounts/{config.account_id}{url}"
    if headers is None:
        headers = {}
    logger.debug("doing request: %s %s", method.upper(), url)
    resp = rq.request(
        method=method.upper(),
        url=url,
        headers=config.request_headers(**headers),
        json=data,
    )
    # Some code taken from
    # https://github.com/keygen-sh/example-python-machine-activation/blob/master/main.py
    logger.debug("API responded %d", resp.status_code)

    if resp.status_code >= 400:
        # Unsuccessful response (codes NOT in 2xx-3xx) are not signed in some cases,
        # so we don't even bother with trying to continue.
        logger.error(
            "Request failed. Errors: %s",
            ",".join(_fmt_errors(resp.json())) or "unknown",
        )
        response_data = resp.json()
        if response_data["errors"][0]["code"] == "TOKEN_INVALID":
            raise InvalidTokenError(response_data)
        return resp.status_code, resp.json()

    validation_request = verify_api_signature(resp)
    if validation_request is None:
        logger.error("Validation of the request failed.")
        raise KeygenError("API response signature verification failed")

    return resp.status_code, validation_request


def revoke_token(token: str):
    """Invalidate a given token immediately."""
    code, payload = request_and_validate(
        "/tokens",
        "delete",
        config.request_headers(authorization=f"Bearer {token}"),
    )

    if code != 204:
        raise exceptions.KeygenAPIError(
            f"token {token} could not be revoked", resp=payload
        )


def user_and_token_from_password(
    u: str, p: str, valid_for: datetime.timedelta = datetime.timedelta(days=14)
) -> tuple[models.User, models.Token]:
    """Generate a new user token, authenticating with username and password.

    Returns:
        A :class:`.User` and :class:`.Token` objects.
    """
    usrpw = base64.b64encode(f"{u}:{p}".encode()).decode()
    # We always set expiry of 2 weeks for all tokens.
    expiry = (datetime.datetime.now(datetime.UTC) + valid_for).strftime(
        "%Y-%m-%dT%H:%M:%S.00Z"
    )
    code, payload = request_and_validate(
        "/tokens",
        "post",
        config.request_headers(authorization=f"Basic {usrpw}"),
        # field "type" is not explicitly mentioned as required in Keygen's
        # docs, but you need it
        {"data": {"type": "tokens", "attributes": {"expiry": expiry}}},
    )

    if code > 300:
        raise exceptions.KeygenAPIError(
            "user token could not be generated", resp=payload
        )

    token = models.Token.from_response(payload)
    # A token object does have a "links" field
    assert "links" in token.relationships.bearer
    api_endpoint = token.relationships.bearer["links"]["related"]
    code, payload = request_and_validate(
        f"https://api.keygen.sh{api_endpoint}",
        "get",
        {"Authorization": f"Bearer {token.token}", **config.request_headers()},
    )

    if code > 300:
        raise exceptions.KeygenAPIError(
            "user object could not be retrieved", resp=payload
        )

    return models.User.from_response(payload), token


def validate_key(license_key: str) -> models.License:
    """Validate a license key, checking that it exists and is not suspended/expired.

    Returns:
        License: The object parsed from the validated response.

    Raises:
        ExpiredLicenseError: If the license has already expired.
        KeygenError: When validation fails for a reason not related to its expiry.
    """
    code, payload = request_and_validate(
        "/licenses/actions/validate-key",
        method="post",
        data={"meta": {"key": license_key}},
        headers=config.request_headers(),
    )
    if code > 300:
        raise exceptions.KeygenAPIError("license could not be validated", resp=payload)
    lic = models.License.from_response(payload)
    if not payload["meta"]["valid"]:
        logger.error(f"License is not valid. Reason: {payload['meta']['detail']}")
        if payload["meta"]["code"] == "EXPIRED":
            raise exceptions.ExpiredLicenseError(lic)
        raise exceptions.KeygenError(
            f"License is not valid. Reason: {payload['meta']['detail']}"
        )
    return lic


def verify_api_signature(resp: rq.Response, host: str | None = None) -> dict | None:
    """Verify that the response to an API call has a valid signature.

    Args:
        resp: The response containing the signature to validate.
        host: When verifying webhooks, the hostname of the endpoint.

    Returns:
        The body of the response if validation is successful, ``None`` otherwise.
    """
    host = host or "api.keygen.sh"
    date_raw = resp.headers["Date"]
    parsed_time_tuple = eut.parsedate_tz(date_raw)

    assert parsed_time_tuple is not None
    assert parsed_time_tuple[-1] is not None

    date_parsed = datetime.datetime(
        *parsed_time_tuple[:6],
        tzinfo=datetime.timezone(datetime.timedelta(hours=parsed_time_tuple[-1])),
    )
    # Response and local time must agree within 5 minutes
    time_offset = abs(date_parsed - datetime.datetime.now(datetime.UTC))
    if time_offset > datetime.timedelta(minutes=2.5):
        logger.error(
            "Response cannot be verified due to a timing error.",
            extra={"offset": time_offset},
        )
        return None

    kg_sig_raw = resp.headers["Keygen-Signature"]
    # The Keygen-Signature header has some structure, which we need to parse
    kg_sig_components = {}
    for item in kg_sig_raw.split(","):
        # Signatures might end in multiple `=` signs, so we just need to split on the
        # first one that appears
        field, quoted_value = item.split("=", 1)
        kg_sig_components[field.strip()] = quoted_value.strip('"')

    if kg_sig_components["algorithm"] != config.signature_alg:
        logger.error("API response used a wrong signing algorithm.")
        logger.debug(
            "algorithm=%s, config=%s",
            kg_sig_components["algorithm"],
            config.signature_alg,
        )
        return None

    # We need to re-create the signing data. We assume that it's in the
    # form "(request-target) host date digest" because this is what the docs say and
    # nowhere there is suggested that this format can change.
    # So let's check this actually
    if kg_sig_components["headers"] != "(request-target) host date digest":
        logger.critical(
            "Headers' order for signature verification is not as expected. "
            "This is a bug!",
            extra={"headers": kg_sig_components["headers"]},
        )
        return None

    # We need a base64 encoded version of the sha256 hash of the response body. This
    # must match the hash/digest that the response contains.
    hashed_body = base64.b64encode(hashlib.sha256(resp.content).digest()).decode()

    # Response digest and whatever we calculate must match exactly. This ensures data
    # integrity, but not that the response actually came from where it says it does.
    digest_ours = f"sha-256={hashed_body}"
    digest_raw = resp.headers["Digest"]
    if digest_raw != digest_ours:
        logger.error(
            "Response digest differs from the locally calculated one.",
            extra={"resp_digest": digest_raw, "local_digest": digest_ours},
        )
        return None

    assert resp.request.method is not None, "request has no method"
    sig_data = (
        f"(request-target): {resp.request.method.lower()} {resp.request.path_url}\n"
        f"host: {host}\n"
        f"date: {date_raw}\n"
        f"digest: {digest_ours}"
    )
    if not verify_signature(
        sig_data.encode(),
        # I'm not sure, but it looks like ALL signatures in the API are url-base64
        # encoded, and we always have to decode them first.
        base64.urlsafe_b64decode(kg_sig_components["signature"]),
    ):
        logger.error("Response has an invalid signature.")
        return None
    logger.debug("API signature successfully validated")
    # Now we can return the response body, safe and sound
    body = {} if not len(resp.content) else resp.json()
    logger.debug("validated API body: %s", str(body))
    return body


def verify_local_license_file_contents(
    lic: dict[str, typing.Any],
) -> dict[str, typing.Any]:
    """Check that a given license is still valid.

    Args:
        lic: License file's **contents**, after being base64-decoded and parsed from
            JSON to a Python :class:`dict`.

    Returns:
        The parsed data contained in the license if it's valid.

    Raises:
        InvalidAlgorithmError: If the crypto algorithm is not the expected one.
    """
    expected_algorithm = "base64+ed25519"
    if lic["alg"] != expected_algorithm:
        raise InvalidAlgorithmError(expected_algorithm, lic["alg"])

    # This is the encoded JSON payload that contains the "actual" license data
    enc: str = lic["enc"]
    # This is the signature used to verify the `enc` property
    sig = base64.b64decode(lic["sig"])
    if not verify_signature(f"license/{enc}".encode(), sig):
        raise KeygenError("license signature verification failed")
    return json.loads(base64.urlsafe_b64decode(enc).decode())


def verify_local_license_file(path: pathlib.Path) -> dict[str, typing.Any]:
    """Check that a local license exists and it's still valid.

    Args:
        path: Path to the license file.

    Returns:
        The data contained in the license file.

    Raises:
        KeygenError: If the given path is not a file.
    """
    if not path.is_file():
        raise KeygenError(f"{path!s} is not a file")
    with open(path) as license_file:
        return verify_local_license_file_contents(
            json.loads(
                base64.b64decode(
                    license_file.read()
                    .strip()
                    .removeprefix("-----BEGIN LICENSE FILE-----")
                    .removesuffix("-----END LICENSE FILE-----")
                    .replace("\n", "")
                ).decode()
            )
        )


def verify_signature(msg: bytes, sig: bytes) -> bool:
    """Verify that the given message has a valid signature.

    Args:
        msg: Original message that was signed.
        sig: The signature used for signing.

    Returns:
            ``True`` or ``False`` depending on whether the message has a valid signature.
    """
    # Our key is hex-encoded, and by default "VerifyKey" does not know about it
    verify_key = VerifyKey(config.pub_key.encode(), HexEncoder)
    try:
        verify_key.verify(msg, sig)
        return True
    except nacl.exceptions.BadSignatureError as e:
        logger.error("signature verification failed: %s", str(e))
        return False
