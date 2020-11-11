# -*- coding: utf-8 -*-
"""
Module for validating OIDC ID Tokens. Configured via config.py 
#. Usage
.. code-block:: python3
    from app.auth import authenticate_user
    @app.get("/auth")
    def test_auth(authenticated_user: AuthenticatedUser = Depends(authenticate_user)):
        name = authenticated_user.preferred_username
        return f"Hello {name}"
"""

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OpenIdConnect
from jose import ExpiredSignatureError
from jose import JWTError
from jose import jwt
from jose.exceptions import JWTClaimsError

from fastapi_oidc import discovery
from fastapi_oidc.types import IDToken


def get_auth(
    *_,
    client_id: str,
    base_authorization_server_uri: str,
    issuer: str,
    signature_cache_ttl: int,
):

    # As far as I can tell this does two things.
    # 1. Extracts and returns the Authorization header.
    # 2. Integrates with the OpenAPI3.0 doc generation in FastAPI.
    #    This integration doesn't matter much now since OpenAPI
    #    doesn't support OpenIDConnect yet.
    #
    # Some relevant examples https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
    oauth2_scheme = OpenIdConnect(openIdConnectUrl=issuer)

    discover = discovery.configure(cache_ttl=signature_cache_ttl)

    def authenticate_user(
        auth_header: str = Depends(oauth2_scheme),
        client_id: str = client_id,
        base_authorization_server_uri: str = base_authorization_server_uri,
        issuer: str = issuer,
        signature_cache_ttl: int = signature_cache_ttl,
    ) -> IDToken:
        """Validate and parse OIDC ID token against issuer in config.
        Note this function caches the signatures and algorithms of the issuing server
        for signature_cache_ttl seconds.

        return:
            IDToken:

        raises:
            HTTPException(status_code=401, detail=f"Unauthorized: {err}")
        """
        id_token = auth_header.split(" ")[-1]
        OIDC_discoveries = discover.auth_server(base_url=base_authorization_server_uri)
        key = discover.public_keys(OIDC_discoveries)
        algorithms = discover.signing_algos(OIDC_discoveries)

        try:
            token = jwt.decode(
                id_token,
                key,
                algorithms,
                # TODO Check that client ID will always equal audience
                audience=client_id,
                issuer=issuer,
                # Disabled at_hash check since we aren't using the access token
                options={"verify_at_hash": False},
            )
            return IDToken.parse_obj(token)

        except (ExpiredSignatureError, JWTError, JWTClaimsError) as err:
            raise HTTPException(status_code=401, detail=f"Unauthorized: {err}")

    return authenticate_user
