# -*- coding: utf-8 -*-
"""
Module for validating Open ID Connect tokens.

Usage
=====

.. code-block:: python3

    # This assumes you've already configured get_auth in your_app.py
    from your_app.auth import auth

    @app.get("/auth")
    def test_auth(authenticated_user: IDToken = Depends(auth.required)):
        return f"Hello {authenticated_user.preferred_username}"
"""

from typing import List
from typing import Optional
from typing import Type

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.openapi.models import OAuthFlows
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from fastapi.security import OAuth2
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OpenIdConnect
from fastapi.security import SecurityScopes
from jose import ExpiredSignatureError
from jose import JWTError
from jose import jwt
from jose.exceptions import JWTClaimsError

from fastapi_oidc import discovery
from fastapi_oidc.types import IDToken


class OAuth2Facade(OAuth2):
    async def __call__(self, request: Request) -> Optional[str]:
        return None


class Auth:
    def __init__(
        self,
        openid_connect_url: str,
        issuer: Optional[str] = None,
        client_id: Optional[str] = None,
        scopes: List[str] = list(),
        signature_cache_ttl: int = 3600,
        idtoken_model: Type = IDToken,
    ):
        """Configure authentication and use method :func:`require` or :func:`optional`
        to check user credentials.

        Args:
            openid_connect_url (URL): URL to the "well known" openid connect config
                e.g. https://dev-123456.okta.com/.well-known/openid-configuration
            issuer (URL): (Optional) The issuer URL from your auth server.
            client_id (str): (Optional) The client_id configured by your auth server.
            scopes (Dict[str, str]): (Optional) A dictionary of scopes and their descriptions.
            signature_cache_ttl (int): (Optional) How many seconds your app should
                cache the authorization server's public signatures.
            idtoken_model (Type): (Optional) The model to use for validating the ID Token.

        Raises:
            Nothing intentional
        """

        self.openid_connect_url = openid_connect_url
        self.issuer = issuer
        self.client_id = client_id
        self.idtoken_model = idtoken_model
        self.scopes = scopes

        self.discover = discovery.configure(cache_ttl=signature_cache_ttl)
        oidc_discoveries = self.discover.auth_server(
            openid_connect_url=self.openid_connect_url
        )
        scopes_dict = {
            scope: "" for scope in self.discover.supported_scopes(oidc_discoveries)
        }

        self.oidc_scheme = OpenIdConnect(
            openIdConnectUrl=openid_connect_url,
            auto_error=False,
        )
        self.password_scheme = OAuth2PasswordBearer(
            tokenUrl=self.discover.token_url(oidc_discoveries),
            scopes=scopes_dict,
            auto_error=False,
        )
        self.implicit_scheme = OAuth2Facade(
            flows=OAuthFlows(
                implicit={
                    "authorizationUrl": self.discover.authorization_url(
                        oidc_discoveries
                    ),
                    "scopes": scopes_dict,
                }
            ),
            scheme_name="OAuth2ImplicitBearer",
            auto_error=False,
        )
        self.authcode_scheme = OAuth2AuthorizationCodeBearer(
            authorizationUrl=self.discover.authorization_url(oidc_discoveries),
            tokenUrl=self.discover.token_url(oidc_discoveries),
            # refreshUrl=self.discover.refresh_url(oidc_discoveries),
            scopes=scopes_dict,
            auto_error=False,
        )

    def required(
        self,
        security_scopes: SecurityScopes,
        authorization_credentials: Optional[HTTPAuthorizationCredentials] = Depends(
            HTTPBearer()
        ),
    ) -> IDToken:
        """Validate and parse OIDC ID token against configuration.
        Note this function caches the signatures and algorithms of the issuing
        server for signature_cache_ttl seconds.

        Args:
            security_scopes (SecurityScopes): Security scopes
            auth_header (str): Base64 encoded OIDC Token. This is invoked
                behind the scenes by Depends.

        Return:
            IDToken: Dictionary with IDToken information

        raises:
            HTTPException(status_code=401, detail=f"Unauthorized: {err}")
            IDToken validation errors
        """

        id_token = self.authenticate_user(
            security_scopes,
            authorization_credentials,
            auto_error=True,
        )
        if id_token is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
        else:
            return id_token

    def optional(
        self,
        security_scopes: SecurityScopes,
        authorization_credentials: Optional[HTTPAuthorizationCredentials] = Depends(
            HTTPBearer(auto_error=False)
        ),
    ) -> Optional[IDToken]:
        """Optionally validate and parse OIDC ID token against configuration.
        Will not raise if the user is not authenticated. Note this function
        caches the signatures and algorithms of the issuing server for
        signature_cache_ttl seconds.

        Args:
            security_scopes (SecurityScopes): Security scopes
            auth_header (str): Base64 encoded OIDC Token. This is invoked
                behind the scenes by Depends.

        Return:
            IDToken: Dictionary with IDToken information

        raises:
            IDToken validation errors
        """

        return self.authenticate_user(
            security_scopes,
            authorization_credentials,
            auto_error=False,
        )

    def authenticate_user(
        self,
        security_scopes: SecurityScopes,
        authorization_credentials: Optional[HTTPAuthorizationCredentials],
        auto_error: bool,
    ) -> Optional[IDToken]:
        """Validate and parse OIDC ID token against against configuration.
        Note this function caches the signatures and algorithms of the issuing server
        for signature_cache_ttl seconds.

        Args:
            security_scopes (SecurityScopes): Security scopes
            auth_header (str): Base64 encoded OIDC Token
            auto_error (bool): If True, will raise an HTTPException if the user
                is not authenticated.

        Return:
            IDToken: Dictionary with IDToken information

        raises:
            HTTPException(status_code=401, detail=f"Unauthorized: {err}")
        """
        if authorization_credentials is None:
            if auto_error:
                raise HTTPException(
                    status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token"
                )
            else:
                return None

        oidc_discoveries = self.discover.auth_server(
            openid_connect_url=self.openid_connect_url
        )
        key = self.discover.public_keys(oidc_discoveries)
        algorithms = self.discover.signing_algos(oidc_discoveries)

        try:
            id_token = jwt.decode(
                authorization_credentials.credentials,
                key,
                algorithms,
                issuer=self.issuer,
                audience=self.client_id,
                options={
                    # Disabled at_hash check since we aren't using the access token
                    "verify_at_hash": False,
                    "verify_iss": self.issuer is not None,
                    "verify_aud": self.client_id is not None,
                },
            )

            if self.client_id is not None:
                token_audience = id_token["aud"]
                if "azp" in id_token:
                    if id_token["azp"] != self.client_id:
                        raise JWTError(
                            f"""Invalid authorized party "azp": {id_token["azp"]}"""
                        )
                elif type(token_audience) == list and len(token_audience) >= 1:
                    raise JWTError('Missing authorized party "azp" in IDToken')

        except (ExpiredSignatureError, JWTError, JWTClaimsError) as error:
            raise HTTPException(status_code=401, detail=f"Unauthorized: {error}")

        expected_scopes = set(self.scopes + security_scopes.scopes)
        token_scopes = id_token.get("scope", "").split(" ")
        if not expected_scopes.issubset(token_scopes):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail=(
                    f"Missing scope token, expected {expected_scopes} to be a "
                    f"subset of received {token_scopes}",
                ),
            )

        return self.idtoken_model(**id_token)
