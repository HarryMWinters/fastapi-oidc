"""FastAPI OIDC - Verify and decrypt 3rd party OIDC ID tokens.

This package provides utilities for validating OIDC ID tokens issued by
third-party authentication servers in FastAPI applications.

Example:
    >>> from fastapi_oidc import get_auth, IDToken
    >>> from fastapi import Depends, FastAPI
    >>>
    >>> authenticate_user = get_auth(
    ...     client_id="your-client-id",
    ...     base_authorization_server_uri="https://auth.example.com",
    ...     issuer="auth.example.com",
    ...     signature_cache_ttl=3600,
    ... )
    >>>
    >>> app = FastAPI()
    >>>
    >>> @app.get("/protected")
    >>> def protected(token: IDToken = Depends(authenticate_user)):
    ...     return {"user": token.email}
"""

from fastapi_oidc.auth import get_auth
from fastapi_oidc.types import IDToken
from fastapi_oidc.types import OktaIDToken

__all__ = ["get_auth", "IDToken", "OktaIDToken"]
__version__ = "0.0.11"
