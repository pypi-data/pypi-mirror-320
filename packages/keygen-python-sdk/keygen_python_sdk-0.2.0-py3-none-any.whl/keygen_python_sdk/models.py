# SPDX-FileCopyrightText: 2024, Marcello Massaro
#
# SPDX-License-Identified: Apache-2.0
"""ORM-like models for the Keygen API."""

from __future__ import annotations

import datetime
import enum
import json
import logging
import typing
from collections.abc import Mapping
from functools import cached_property

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated

from keygen_python_sdk import exceptions, functional
from keygen_python_sdk.config import config

logger = logging.getLogger(__name__)


class JSONAPIRelationshipObject(typing.TypedDict, total=False):
    r"""A relationship object from the JSON:API spec.

    Examples:
        The relationships of some license file, after checking out a :class:`.License`:

        .. code-block:: json

            {
              "data": {
                // ...
                },
                "relationships": {
                  "account": { // the object starting here is a relationship object
                    "links": {
                      "related": "/v1/accounts/<account>"
                    },
                    "data": {
                      "type": "accounts",
                      "id": "<account>"
                    }
                  },
                  "license": {
                    // another relationship object
                  }
                }
              }
            }
    """

    data: dict[str, str] | None
    """Data object."""
    links: dict[str, str | None]
    """Links object."""
    meta: dict[str, typing.Any] | None
    """Meta object."""


class CamelCasedModel(BaseModel):
    """Base model that uses :func:`pydantic.alias_generators.to_camel` as default alias
    generator."""

    model_config = ConfigDict(alias_generator=to_camel)

    @classmethod
    def _validate_payload_for_model(
        cls, json_data: dict[str, typing.Any]
    ) -> dict[str, typing.Any]:
        """Check that the given ``json_data`` can be parsed by the current class."""
        data: dict[str, typing.Any] | None = json_data.get("data", None)
        if data is None:
            if "errors" in json_data:
                raise exceptions.KeygenError("cannot parse an error response")
            raise exceptions.KeygenError("no 'data' field in response")
        if not isinstance(data, Mapping):
            raise exceptions.KeygenError(
                f"'data' field in response is not a mapping: {type(data)}"
            )
        typ = data.get("type", None)
        if typ is None:
            raise exceptions.KeygenError("no 'type' field in 'data' object")
        if typ != f"{cls.__name__.lower()}s":  # Plural lowercase
            raise exceptions.KeygenError(
                f"'{typ}' type cannot be parsed as {cls.__name__}"
            )
        return data


class TokenRelationships(CamelCasedModel):
    account: JSONAPIRelationshipObject
    environment: JSONAPIRelationshipObject
    bearer: JSONAPIRelationshipObject


class TokenKind(enum.StrEnum):
    """Token types that can be used in the Keygen API."""

    ACTIVATION = "activation-token"
    """Activation token."""
    PRODUCT = "product-token"
    """Product token.

    .. important::

         **Keep this token safe!**
    """
    USER = "user-token"
    """User token."""
    SUPPORT = "support-token"
    """Token related to a user with a support role."""
    DEVELOPER = "developer-token"
    """Token related to a user with a developer role."""
    ADMIN = "admin-token"
    """Admin token.

    .. important::

         **Keep this token safe!**
    """


class Token(CamelCasedModel, alias_generator=to_camel):
    """A generic token object from the Keygen API."""

    id: str
    """The unique ID."""
    kind: TokenKind
    """What type of token this is. Tokens can be associated with
    licenses, users, products, etc."""
    token: str
    """The actual string-value of the token that needs to be
    passed in the ``Authentication`` header of API requests."""
    created: datetime.datetime
    """When this token was created."""
    updated: datetime.datetime
    """Last time this token was updated for any reason."""
    permissions: list[str] | None = None
    """The permissions that this token has."""
    name: str | None = None
    """Token's name for identification."""
    expiry: datetime.datetime | None = None
    """The timestamp for when the token expires.

    Requests using an expired token will be rejected."""
    max_activations: int | None = Field(default=None, ge=0)
    """The maximum number of machine activations this token may perform.

    This attribute applies only to license tokens.
    """
    activations: int | None = Field(default=None, ge=0)
    """The number of machine activations that have been performed by this token.

    This attribute applies only to licence tokens.
    """
    max_deactivations: int | None = Field(default=None, ge=0)
    """The maximum number of machine deactivations this token may perform.

    This attribute applies to licence tokens.
    """
    deactivations: int | None = Field(default=None, ge=0)
    """The number of machine deactivations that have been performed by this token.

    This attribute applies only to license tokens.
    """
    relationships: TokenRelationships
    """The relationships of this token."""

    @classmethod
    def from_response(cls, json_data: dict[str, typing.Any]) -> Token:
        """Parse a *complete* JSON object from the API into a new instance."""
        data = cls._validate_payload_for_model(json_data)

        return cls(
            id=data["id"],
            **data["attributes"],
        )


class Entitlement(CamelCasedModel):
    id: str
    name: str
    code: str
    created: datetime.datetime
    updated: datetime.datetime
    metadata: dict[str, typing.Any] | None = None

    def __str__(self) -> str:
        return self.code

    @classmethod
    def from_response(cls, json_data: dict[str, typing.Any]) -> Entitlement:
        """Parse a licence JSON response into a new instance."""
        data = cls._validate_payload_for_model(json_data)

        attrs = data["attributes"]
        return cls(id=data["id"], **attrs, metadata=data.get("metadata", None))


class LicenseStatus(enum.StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRING = "EXPIRING"
    EXPIRED = "EXPIRED"
    SUSPENDED = "SUSPENDED"
    BANNED = "BANNED"


class LicenseRelationships(CamelCasedModel):
    account: JSONAPIRelationshipObject
    environment: JSONAPIRelationshipObject
    product: JSONAPIRelationshipObject
    policy: JSONAPIRelationshipObject
    owner: JSONAPIRelationshipObject
    users: JSONAPIRelationshipObject
    group: JSONAPIRelationshipObject
    machines: JSONAPIRelationshipObject
    entitlements: JSONAPIRelationshipObject


class License(CamelCasedModel):
    """A licence object from the Keygen API.

    This class maps the JSON Keygen API object to a Python object. All attributes from
    the `licence object <https://keygen.sh/docs/api/licenses/#licenses-object>`_ are
    available but are transformed from ``camelCase`` to ``snake_case``.
    """

    id: str
    key: str
    expiry: datetime.datetime
    status: LicenseStatus
    uses: Annotated[int, Field(strict=True, ge=0, lt=2147483647, default=0)]
    protected: bool
    suspended: bool
    encrypted: bool
    floating: bool
    strict: bool
    max_machines: int
    require_heartbeat: bool
    require_check_in: bool
    metadata: dict[str, typing.Any]
    created: datetime.datetime
    updated: datetime.datetime
    relationships: LicenseRelationships
    name: str | None = None
    version: str | None = None
    scheme: str | None = None
    max_processes: int | None = None
    max_users: int | None = None
    max_cores: int | None = None
    max_uses: int | None = None
    last_validated: datetime.datetime | None = None
    last_check_out: datetime.datetime | None = None
    last_check_in: datetime.datetime | None = None
    next_check_in: datetime.datetime | None = None
    permissions: list[str] | None = None

    @classmethod
    def from_response(cls, json_data: dict) -> License:
        """Parse a license JSON response into a new instance."""
        data = cls._validate_payload_for_model(json_data)

        return cls(
            id=data["id"], **data["attributes"], relationships=data["relationships"]
        )

    @cached_property
    def entitlements(self) -> list[Entitlement]:
        """Get the list of entitlements that are available for this license."""
        entitlements_link = self.relationships.entitlements.get("links", {}).get(
            "related", None
        )

        if entitlements_link is None:
            return []

        code, payload = functional.request_and_validate(
            f"https://api.keygen.sh{entitlements_link}",
            headers=config.request_headers(authorization=f"License {self.key}"),
        )
        if code != 200:
            raise exceptions.KeygenAPIError(
                "couldn't retrieve entitlements", resp=payload
            )

        if not (entitlements := payload.get("data", [])):
            return []
        return [Entitlement.from_response({"data": ent}) for ent in entitlements]

    @cached_property
    def owner(self) -> User | None:
        """The owner of this licence, if present."""
        owner_link = self.relationships.owner.get("links", {}).get("related", None)

        if owner_link is None:
            return None

        code, payload = functional.request_and_validate(
            f"https://api.keygen.sh{owner_link}", "get"
        )

        if code != 200:
            raise exceptions.KeygenAPIError(
                "could not retrieve license's owner", resp=payload
            )

        return User.from_response(payload)

    @cached_property
    def users(self) -> list[User] | None:
        """Get the list of users that have access to this licence.

        Notes:
            :attr:`.owner` is part of this list.
        """
        users_link = self.relationships.users.get("links", {}).get("related", None)

        if users_link is None:
            return None

        code, users_rel = functional.request_and_validate(
            f"https://api.keygen.sh{users_link}", "get"
        )
        if code != 200:
            raise exceptions.KeygenError("couldn't retrieve users")

        return [User.from_response({"data": u}) for u in users_rel["data"]]


class UserRole(enum.Enum):
    """Available user roles in the Keygen API.

    Attributes:
        USER: A normal user of one or more products. Can manage their own resources
            but not others'.
        SUPPORT_AGENT: Administrative user with read-only access to most resources.
            Cannot create, update or delete.
        SALES_AGENT: Administrative user that can read most data and manage specific
            resources only.
        DEVELOPER: Administrative user that can manage all resources except billing.
        READ_ONLY: Administrative user that can only read all resources (except billing).
        ADMIN: Administrative user with full account management permissions.
    """

    USER = "user"
    SUPPORT_AGENT = "support-agent"
    SALES_AGENT = "sales-agent"
    DEVELOPER = "developer"
    READ_ONLY = "read-only"
    ADMIN = "admin"

    def can_read(self) -> bool:
        """Whether the role has general read permissions."""
        return True  # All roles can read

    def can_write(self) -> bool:
        """Whether the role has general write permissions."""
        return self in {UserRole.DEVELOPER, UserRole.ADMIN, UserRole.SALES_AGENT}

    def can_manage_billing(self) -> bool:
        """Whether the role can manage billing information."""
        return self == UserRole.ADMIN

    def is_administrative(self) -> bool:
        """Whether this is an administrative role.

        Notes:
            Not **all** administrative roles can write! :attr:`SUPPORT_AGENT`
            is an administrative role, but can't write (e.g. issue new
            licenses, or revoke old ones, etc.).
        """
        return self != UserRole.USER


class User(CamelCasedModel):
    first_name: str
    last_name: str
    email: str
    role: UserRole = Field(default=UserRole.USER)
    metadata: dict[str, typing.Any] = Field(default_factory=dict)
    password: str | None = None
    id: str | None = None
    full_name: str | None = None
    status: str | None = None
    created: datetime.datetime | None = None
    updated: datetime.datetime | None = None

    @classmethod
    def from_response(cls, json_data: dict[str, typing.Any]) -> User:
        """Parse a user JSON response into a new instance.

        Args:
            json_data: The full JSON response containing a "data" field.

        Returns:
            A new User instance populated with the response data.

        Raises:
            KeygenError: If the given ``json_data`` contains a ``type`` field with
                a value other than ``users``, an error response is passed, or if the
                ``data`` field is missing.
        """
        data = cls._validate_payload_for_model(json_data)

        return cls(id=data["id"], **data["attributes"])

    def can_read(self) -> bool:
        """Whether this user has general read permissions."""
        return self.role.can_read()

    def can_write(self) -> bool:
        """Whether this user has general write permissions."""
        return self.role.can_write()

    def can_manage_billing(self) -> bool:
        """Whether this user can manage billing information."""
        return self.role.can_manage_billing()

    def is_administrative(self) -> bool:
        """Whether this user has an administrative role."""
        return self.role.is_administrative()

    def request_new_password(self, deliver=False):
        """Initiate a reset-password flow.

        Args:
            deliver: If ``True``, Keygen will automatically email the user a link
                with which the password can be reset. If ``False``, this does not
                happen, and you need to have a web-hook listener somewhere to react
                to this request yourself (e.g. if you want to provide your own
                password-recovery UI/workflow).
        """
        code, payload = functional.request_and_validate(
            "/passwords",
            "post",
            config.request_headers(),
            {"meta": {"email": self.email, "deliver": deliver}},
        )

        if code > 300:
            raise exceptions.KeygenAPIError(
                "request could not be fulfilled", resp=payload
            )
        logger.debug(json.dumps(payload))

    def fulfill_password_reset(self, new_pw: str, reset_token: str) -> None:
        """Update a user's password **after a reset request**.

        Args:
            new_pw: New password for the user. Must be a minimum of eight characters.
            reset_token: The password reset token sent to the user.
        """
        code, payload = functional.request_and_validate(
            f"/users/{self.id}/actions/reset-password",
            "post",
            config.request_headers(),
            {
                "meta": {
                    "passwordResetToken": reset_token,
                    "newPassword": new_pw,
                }
            },
        )

        if code != 200:
            raise exceptions.KeygenAPIError("password reset failed", resp=payload)

    @cached_property
    def licenses(self):
        """Recover all licenses of the current user."""
        code, payload = functional.request_and_validate(f"/users/{self.id}/licenses")

        if code != 200:
            raise exceptions.KeygenAPIError("listing licenses failed.", resp=payload)

        return [License.from_response(license_json) for license_json in payload["data"]]
