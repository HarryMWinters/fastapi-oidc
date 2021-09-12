Welcome to fastapi-oidc's documentation!
========================================

Verify ID Tokens Issued by Third Party

This is great if you just want to use something like Okta or google to handle
your auth. All you need to do is verify the token and then you can extract
user ID info from it.

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

   pip install fastapi-oidc
   
Or, if you you're feeling hip...

.. code-block:: bash

   poetry add fastapi-oidc

Example
-------

Basic configuration for verifying OIDC tokens.

.. code-block:: python3

   from fastapi import Depends
   from fastapi import FastAPI
   from fastapi_oidc import get_auth
   from fastapi_oidc.types import IDToken


   app = FastAPI()

   # e.g. local keycloak development server
   discovery_url = "http://localhost:8080/auth/realms/my-realm/.well-known/openid-configuration"
   issuer = "http://localhost:8080/auth/realms/my-realm"

   authenticate_user = get_auth(
      discovery_url=discovery_url,
      issuer=issuer,  # optional, verification only
      audience="my-service",  # optional, verification only
      signature_cache_ttl=3600,  # optional
   )


   @app.get("/protected")
   def protected(
      user: IDToken = Depends(authenticate_user),
   ):
      return user


API Reference
=============

Auth
----

.. automodule:: fastapi_oidc.auth
   :members:


Discovery
---------

.. automodule:: fastapi_oidc.discovery
   :members:

Types
------------
.. automodule:: fastapi_oidc.types
   :members:
