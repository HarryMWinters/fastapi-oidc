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
from typing import Type, Dict

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OpenIdConnect
from jose import ExpiredSignatureError
from jose import JWTError
from jose import jwt
from jose.exceptions import JWTClaimsError
from jose.jws import verify

from fastapi_oidc import discovery


def get_auth(
    discovery_url: str,
    issuer: Optional[str] = None,
    audience: Optional[str] = None,
    signature_cache_ttl: int = 3600,
) -> Callable[[str], Dict]:
    """Take configurations and return the authenticate_user function.

    This function should only be invoked once at the beggining of your
    server code. The function it returns should be used to check user credentials.

    Args:
        discovery_url(URL): Auth server well known configuration URL. E.g.
            http://localhost:8080/auth/realms/my-realm/.well-known/openid-configuration
        issuer(URL): (Optional) Auth server issuer URL. E.g.
            http://localhost:8080/auth/realms/my-realm
        signature_cache_ttl (int): (Optional) How many seconds your app should cache the
            authorization server's public signatures.
        audience (str): (Optional) The audience string configured by your auth server.

    Returns:
        func: authenticate_user(auth_header: str) -> Dict

    Raises:
        Nothing intentional
    """

    oauth2_scheme = OpenIdConnect(openIdConnectUrl=discovery_url)

    discover = discovery.configure(cache_ttl=signature_cache_ttl)

    def authenticate_user(auth_header: str = Depends(oauth2_scheme)) -> Dict:
        """Validate and parse OIDC ID token against issuer in config.
        Note this function caches the signatures and algorithms of the issuing server
        for signature_cache_ttl seconds.

        Args:
            auth_header (str): Base64 encoded OIDC Token. This is invoked behind the
                scenes by Depends.

        Return:
            Dict:

        raises:
            HTTPException(status_code=401, detail=f"Unauthorized: {err}")
        """
        id_token = auth_header.split(" ")[-1]
        oidc_discoveries = discover.auth_server(discovery_url=discovery_url)
        key = discover.public_keys(oidc_discoveries)
        algorithms = discover.signing_algos(oidc_discoveries)

        try:
            token = jwt.decode(
                id_token,
                key,
                algorithms,
                audience=audience,
                issuer=issuer,
                # Disabled at_hash check since we aren't using the access token
                options={
                    "verify_at_hash": False,
                    "verify_aud": audience is not None,
                    "verify_iss": issuer is not None,
                },
            )
            return token
        except (ExpiredSignatureError, JWTError, JWTClaimsError) as err:
            raise HTTPException(status_code=401, detail=f"Unauthorized: {err}")

    return authenticate_user
