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

Example
-------

Basic configuration for verifying OIDC tokens.

.. code-block:: python3

   from fastapi import Depends
   from fastapi import FastAPI

   # Set up our OIDC
   from fastapi_oidc import IDToken
   from fastapi_oidc import get_auth

   OIDC_config = {
      "client_id": "0oa1e3pv9opbyq2Gm4x7",
      "base_authorization_server_uri": "https://dev-126594.okta.com",
      "issuer": "dev-126594.okta.com",
      "signature_cache_ttl": 3600,
   }

   authenticate_user: Callable = get_auth(**OIDC_config)

   app = FastAPI()

   @app.get("/protected")
   def protected(id_token: IDToken = Depends(authenticate_user)):
      return {"Hello": "World", "user_email": id_token.email}


API References
--------------

.. automodule:: fastapi_oidc
   :members:

Discovery
---------

.. automodule:: fastapi_oidc.discovery
   :members:

Types
------------
.. automodule:: fastapi_oidc.types
   :members:
