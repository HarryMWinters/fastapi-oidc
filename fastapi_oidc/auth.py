# -*- coding: utf-8 -*-
"""
Module for validating Open ID Connect tokens.

Usage
=====

.. code-block:: python3

    # This assumes you've already configured Auth in your_app/auth.py
    from your_app.auth import auth

    @app.get("/auth")
    def test_auth(authenticated_user: IDToken = Security(auth.required)):
        return f"Hello {authenticated_user.preferred_username}"
"""

from typing import List
from typing import Optional
from typing import Type

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlowClientCredentials
from fastapi.openapi.models import OAuthFlowImplicit
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.models import OAuthFlows
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from fastapi.security import OAuth2
from fastapi.security import SecurityScopes
from jose import ExpiredSignatureError
from jose import JWTError
from jose import jwt
from jose.exceptions import JWTClaimsError

from fastapi_oidc import discovery
from fastapi_oidc.grant_types import GrantType
from fastapi_oidc.idtoken_types import IDToken


class Auth(OAuth2):
    def __init__(
        self,
        openid_connect_url: str,
        issuer: Optional[str] = None,
        client_id: Optional[str] = None,
        scopes: List[str] = list(),
        grant_types: List[GrantType] = [GrantType.IMPLICIT],
        signature_cache_ttl: int = 3600,
        idtoken_model: Type[IDToken] = IDToken,
    ):
        """Configure authentication and use method :func:`require` or :func:`optional`
        to check user credentials.

        Args:
            openid_connect_url (URL): URL to the "well known" openid connect config
                e.g. https://dev-123456.okta.com/.well-known/openid-configuration
            issuer (URL): (Optional) The issuer URL from your auth server.
            client_id (str): (Optional) The client_id configured by your auth server.
            scopes (Dict[str, str]): (Optional) A dictionary of scopes and their descriptions.
            grant_types (List[GrantType]): (Optional) Grant types shown in docs.
            signature_cache_ttl (int): (Optional) How many seconds your app should
                cache the authorization server's public signatures.
            idtoken_model (Type[IDToken]): (Optional) The model to use for validating the ID Token.

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

        flows = OAuthFlows()
        if GrantType.AUTHORIZATION_CODE in grant_types:
            flows.authorizationCode = OAuthFlowAuthorizationCode(
                authorizationUrl=self.discover.authorization_url(oidc_discoveries),
                tokenUrl=self.discover.token_url(oidc_discoveries),
            )

        if GrantType.CLIENT_CREDENTIALS in grant_types:
            flows.clientCredentials = OAuthFlowClientCredentials(
                tokenUrl=self.discover.token_url(oidc_discoveries),
            )

        if GrantType.PASSWORD in grant_types:
            flows.password = OAuthFlowPassword(
                tokenUrl=self.discover.token_url(oidc_discoveries),
            )

        if GrantType.IMPLICIT in grant_types:
            flows.implicit = OAuthFlowImplicit(
                authorizationUrl=self.discover.authorization_url(oidc_discoveries),
            )

        super().__init__(
            scheme_name="OIDC",
            flows=flows,
            auto_error=False,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        """Overriding OAuth2 method since we validate the token manually."""
        return None

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
            self.idtoken_model: Dictionary with IDToken information

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
            self.idtoken_model: Dictionary with IDToken information

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
            self.idtoken_model: Dictionary with IDToken information

        raises:
            HTTPException(status_code=401, detail=f"Unauthorized: {err}")
        """

        if (
            authorization_credentials is None
            or authorization_credentials.scheme.lower() != "bearer"
        ):
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

            if (
                type(id_token["aud"]) == list
                and len(id_token["aud"]) >= 1
                and "azp" not in id_token
            ):
                raise JWTError(
                    'Missing authorized party "azp" in IDToken when there '
                    "are multiple audiences"
                )

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
