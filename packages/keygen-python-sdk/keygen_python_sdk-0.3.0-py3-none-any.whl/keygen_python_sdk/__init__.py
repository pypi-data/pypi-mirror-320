# SPDX-FileCopyrightText: 2024, Marcello Massaro
#
# SPDX-License-Identified: Apache-2.0
"""*****************
Keygen Python SDK
*****************

An **unofficial** Python SDK for the `Keygen <https://keygen.sh>`_ API, build with
`pydantic <https://docs.pydantic.dev/latest/>`_ models.

.. important::

    This library is not officially endorsed nor supported by
    `Keygen LLC <https://keygen.sh>`_.

.. toctree::
   :hidden:
   :maxdepth: 1

   API <api/api>

Quickstart
==========

Configure :mod:`keygen_python_sdk` by creating a ``.env`` file to populate the
default :data:`.config` object. These are the bare-minimum, see :class:`.Config`
for more configuration options.

.. code-block:: bash

    KEYGEN_ACCOUNT_ID="aaaaaaaa-bbbb-cccc-dddd-dsadsadsadsa"
    KEYGEN_PRODUCT_ID="aaaaaaaa-bbbb-cccc-dddd-asddsaasddsa"
    KEYGEN_PUB_KEY="someverysuperduperlongstring"
    KEYGEN_AUTH_TOKEN="prod-randomv3"

Validate a licence key and get an object that represents it:

.. code-block:: python

    import keygen_python_sdk as kg

    lic_obj = kg.validate("SOME-LICENCE-V3")
    assert lic_obj.key == "SOME-LICENCE-V3"

You can get the :class:`.License` owner as a :class:`.User` object:

.. code-block:: python

    if owner := lic_obj.owner:
        print(owner.full_name)
    else:
        print("This licence has no owner")

.. note::

   Not all :class:`.License` objects have an owner, in which case the
   property returns ``None``.

You can find more information in the :doc:`full API <api/api>` docs.
"""

import logging
from importlib.metadata import version

from keygen_python_sdk.functional import validate_key
from keygen_python_sdk.models import Entitlement, License, Token, User

__all__ = ["Entitlement", "License", "Token", "User", "validate_key"]
__author__ = "Marcello Massaro"
__version__ = version(__name__)

logger = logging.getLogger(__name__)
