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

from collections.abc import Iterable
from typing import Any
from typing import Callable
from typing import Optional
from typing import Type

import jwt
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OpenIdConnect
from jwt import PyJWK
from jwt.exceptions import InvalidAlgorithmError
from jwt.exceptions import InvalidKeyError
from jwt.exceptions import PyJWTError

from fastapi_oidc import discovery
from fastapi_oidc.exceptions import TokenSpecificationError
from fastapi_oidc.types import IDToken


def _select_signing_key(keys: Any, id_token: str, algorithms: list[str]) -> Any:
    """Pick the key that should verify ``id_token`` out of ``keys``.

    ``keys`` is normally the JWKS document served by the auth server's
    ``jwks_uri`` (a dict with a ``"keys"`` list). In that case the key is chosen
    by matching the token header's ``kid``. A JWKS with a single key is accepted
    for tokens that carry no ``kid``. Anything that is not a JWKS document (a PEM
    string, an already-built :class:`jwt.PyJWK`, ...) is handed to PyJWT
    unchanged.

    Args:
        keys: The JWKS document, or a single key understood by :func:`jwt.decode`.
        id_token: The compact-serialized JWT being verified.
        algorithms: The signing algorithms the auth server advertises. The token's
            ``alg`` header must be one of them.

    Returns:
        A key acceptable by :func:`jwt.decode`.

    Raises:
        jwt.exceptions.PyJWTError: If the token's ``alg`` is not allowed or no
            usable key matches the token.
    """
    if not isinstance(keys, dict) or "keys" not in keys:
        return keys

    header = jwt.get_unverified_header(id_token)
    alg = header.get("alg")
    if alg not in algorithms:
        raise InvalidAlgorithmError("The specified alg value is not allowed")

    jwks = keys["keys"]
    if not isinstance(jwks, list):
        raise InvalidKeyError("Invalid JWK Set: 'keys' is not a list")
    candidates = [k for k in jwks if isinstance(k, dict)]

    kid = header.get("kid")
    if kid is not None:
        candidates = [k for k in candidates if k.get("kid") == kid]
        if not candidates:
            raise InvalidKeyError(f"No signing key found for kid={kid!r}")
    elif len(candidates) != 1:
        raise InvalidKeyError(
            "Token has no 'kid' header and the JWKS does not contain exactly one key"
        )

    jwk = candidates[0]
    # PyJWT binds a PyJWK to one algorithm and refuses tokens whose header "alg"
    # differs. A JWK that omits "alg" would be bound to a per-kty default (RS256
    # for RSA), rejecting RS384/RS512/PS* tokens that python-jose accepted. Bind
    # such keys to the token's alg instead: it was checked against the server's
    # allow-list above, and a key/alg family mismatch (e.g. HS256 against an RSA
    # key) still fails inside PyJWK.
    return PyJWK(jwk, algorithm=jwk.get("alg") or alg)


def get_auth(
    *,
    client_id: str,
    audience: Optional[str] = None,
    base_authorization_server_uri: str,
    issuer: str | Iterable[str],
    signature_cache_ttl: int,
    token_type: Type[IDToken] = IDToken,
) -> Callable[[str], IDToken]:
    """Take configurations and return the authenticate_user function.

    This function should only be invoked once at the beginning of your
    server code. The function it returns should be used to check user credentials.

    Args:
        client_id: This string is provided when you register with your resource server.
        base_authorization_server_uri: Everything before /.wellknow in your auth server
            URL. I.E. https://dev-123456.okta.com
        issuer: The expected value(s) of the token's ``iss`` claim. Pass a single
            string to accept one issuer, or an iterable of strings to accept tokens
            from any of several issuers (useful when the same auth server is reachable
            under more than one issuer identifier).
        signature_cache_ttl: How many seconds your app should cache the authorization
            server's public signatures.
        audience: The audience string configured by your auth server. If not set
            defaults to client_id
        token_type: An optional class to be returned by the authenticate_user function.


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

    oauth2_scheme = OpenIdConnect(
        openIdConnectUrl=f"{base_authorization_server_uri}/.well-known/openid-configuration"
    )

    discover = discovery.configure(cache_ttl=signature_cache_ttl)

    # PyJWT accepts a str or a container of str for the issuer. Materialise
    # arbitrary iterables (generators, sets, ...) so membership checks work.
    expected_issuer: str | list[str] = (
        issuer if isinstance(issuer, str) else list(issuer)
    )

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
        keys = discover.public_keys(OIDC_discoveries)
        algorithms = discover.signing_algos(OIDC_discoveries)

        try:
            key = _select_signing_key(keys, id_token, algorithms)
            token = jwt.decode(
                id_token,
                key,
                algorithms=algorithms,
                audience=audience if audience else client_id,
                issuer=expected_issuer,
                # python-jose never compared "iat" to the clock, and PyJWT allows
                # no leeway by default, so a provider whose clock runs a little
                # ahead of ours would make every fresh token fail with 401.
                # Keep the old contract; "exp" and "nbf" are still enforced.
                options={"verify_iat": False},
            )
            return token_type.model_validate(token)

        except PyJWTError as err:
            raise HTTPException(status_code=401, detail=f"Unauthorized: {err}")

    return authenticate_user
