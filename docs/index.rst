Welcome to fastapi-oidc's documentation!
========================================

Verify and decrypt 3rd party OpenID Connect tokens to protect your
`FastAPI <https://github.com/tiangolo/fastapi>`_ endpoints.

Easily used with authenticators such as:

- `Keycloak <https://www.keycloak.org/>`_ (open source)
- `SuperTokens <https://supertokens.io/>`_ (open source)
- `Auth0 <https://auth0.com/>`_
- `Okta <https://www.okta.com/products/authentication/>`_


FastAPI's generated interactive documentation supports the grant types
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
   from fastapi import Security
   from fastapi import status

   from fastapi_oidc import Auth
   from fastapi_oidc import GrantType
   from fastapi_oidc import KeycloakIDToken

   auth = Auth(
      openid_connect_url="http://localhost:8080/auth/realms/my-realm/.well-known/openid-configuration",
      issuer="http://localhost:8080/auth/realms/my-realm",  # optional, verification only
      client_id="my-client",  # optional, verification only
      scopes=["email"],  # optional, verification only
      grant_types=[GrantType.IMPLICIT],  # optional, docs only
      idtoken_model=KeycloakIDToken,  # optional, verification only
   )

   app = FastAPI(
      title="Example",
      version="dev",
      dependencies=[Depends(auth)],
   )

   @app.get("/protected")
   def protected(id_token: KeycloakIDToken = Security(auth.required)):
      return dict(message=f"You are {id_token.email}")


API Reference
=============

Auth
----
.. automodule:: fastapi_oidc.auth
   :members:

Grant Types
-----------
.. automodule:: fastapi_oidc.grant_types
   :members:
   :undoc-members:

IDToken Types
-------------
.. automodule:: fastapi_oidc.idtoken_types
   :members:
