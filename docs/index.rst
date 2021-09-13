Welcome to fastapi-oidc's documentation!
========================================

Verify and decrypt 3rd party OpenID Connect tokens to protect your
`FastAPI <https://github.com/tiangolo/fastapi>`_ endpoints.

Easily used with authenticators such as:

- `Keycloak <https://www.keycloak.org/>`_ (open source)
- `SuperTokens <https://supertokens.io/>`_ (open source)
- `Auth0 <https://auth0.com/>`_
- `Okta <https://www.okta.com/products/authentication/>`_


FastAPI's generated interactive documentation supports the grant flows
``authorization_code``, ``implicit``, ``password`` and ``client_credentials``.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Installation
------------

.. code-block:: bash

   poetry add fastapi-oidc
   
Or, for the old-timers:

.. code-block:: bash

   pip install fastapi-oidc

Example
-------

Basic configuration for verifying OIDC tokens.

.. code-block:: python3

   from fastapi import Depends
   from fastapi import FastAPI

   from fastapi_oidc import IDToken
   from fastapi_oidc import get_auth


   app = FastAPI()

   authenticate_user = get_auth(
      openid_connect_url="https://dev-123456.okta.com/.well-known/openid-configuration",
      issuer="dev-126594.okta.com",  # optional, verification only
      audience="https://yourapi.url.com/api",  # optional, verification only
      signature_cache_ttl=3600,  # optional
   )

   @app.get("/protected")
   def protected(id_token: IDToken = Depends(authenticate_user)):
      return {"Hello": "World", "user_email": id_token.email}


API Reference
=============

Auth
----

.. automodule:: fastapi_oidc.auth
   :members:

Types
------------
.. automodule:: fastapi_oidc.types
   :members:
