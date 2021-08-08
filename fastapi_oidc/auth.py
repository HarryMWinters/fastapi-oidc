# -*- coding: utf-8 -*-
"""
Module for validating OIDC ID Tokens. Configured via config.py 

Usage
=====

.. code-block:: python3

    # This assumes you've already configured get_auth in your_app.py
    from you_app.auth import authenticate_user

    @app.get("/auth")
    def test_auth(authenticated_user: AuthenticatedUser = Depends(authenticate_user)):
        name = authenticated_user.preferred_username
        return f"Hello {name}"
"""

from typing import Callable
from typing import Optional
from typing import Type

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OpenIdConnect
from jose import ExpiredSignatureError
from jose import JWTError
from jose import jwt
from jose.exceptions import JWTClaimsError

from fastapi_oidc import discovery
from fastapi_oidc.exceptions import TokenSpecificationError
from fastapi_oidc.types import IDToken


def get_auth(
    *_,
    client_id: str,
    audience: Optional[str] = None,
    base_authorization_server_uri: str,
    issuer: str,
    signature_cache_ttl: int,
    token_type: Type[IDToken] = IDToken,
) -> Callable[[str], IDToken]:
    """Take configurations and return the authenticate_user function.

    This function should only be invoked once at the beggining of your
    server code. The function it returns should be used to check user credentials.

    Args:
        client_id (str): This string is provided when you register with your resource
            server.
        base_authorization_server_uri(URL): Everything before /.wellknow in your auth
            server URL. I.E. https://dev-123456.okta.com
        issuer (URL): Same as base_authorization. This is used to generating OpenAPI3.0
            docs which is broken (in OpenAPI/FastAPI) right now.
        signature_cache_ttl (int): How many seconds your app should cache the
            authorization server's public signatures.
        audience (str): (Optional) The audience string configured by your auth server.
            If not set defaults to client_id
        token_type (IDToken or subclass): (Optional) An optional class to be returned by
            the authenticate_user function.


    Returns:
        func: authenticate_user(auth_header: str) -> IDToken (or token_type)

    Raises:
        Nothing intentional
    """

    if not issubclass(token_type, IDToken):
        raise TokenSpecificationError(
            "Invalid argument for token_type. "
            "Token type must be a subclass of fastapi_oidc.type.IDToken. "
            f"Received {token_type=}"
        )

    # As far as I can tell the oauth2_scheme does two things.
    # 1. Extracts and returns the Authorization header.
    # 2. Integrates with the OpenAPI3.0 doc generation in FastAPI.
    #    This integration doesn't matter much now since OpenAPI
    #    doesn't support OpenIDConnect yet.
    #
    # Some relevant examples https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
    oauth2_scheme = OpenIdConnect(openIdConnectUrl=issuer)

    discover = discovery.configure(cache_ttl=signature_cache_ttl)

    def authenticate_user(auth_header: str = Depends(oauth2_scheme)) -> IDToken:
        """Validate and parse OIDC ID token against issuer in config.
        Note this function caches the signatures and algorithms of the issuing server
        for signature_cache_ttl seconds.

        Args:
            auth_header (str): Base64 encoded OIDC Token. This is invoked behind the
                scenes by Depends.

        Return:
            IDToken (types.IDToken):

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
                audience=audience if audience else client_id,
                issuer=issuer,
                # Disabled at_hash check since we aren't using the access token
                options={"verify_at_hash": False},
            )
            return token_type.parse_obj(token)

        except (ExpiredSignatureError, JWTError, JWTClaimsError) as err:
            raise HTTPException(status_code=401, detail=f"Unauthorized: {err}")

    return authenticate_user
