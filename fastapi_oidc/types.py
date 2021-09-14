from typing import List
from typing import Union

from pydantic import BaseModel
from pydantic import Extra


class IDToken(BaseModel):
    """Pydantic model representing an OIDC ID Token.

    ID Tokens are polymorphic and may have many attributes not defined in the spec thus this model accepts
    all addition fields. Only required fields are listed in the attributes section of this docstring or
    enforced by pydantic.

    See the specifications here. https://openid.net/specs/openid-connect-core-1_0.html#IDToken

    Attributes:
        iss (str): Issuer Identifier for the Issuer of the response.
        sub (str): Subject Identifier.
        aud (str): Audience(s) that this ID Token is intended for.
        exp (str): Expiration time on or after which the ID Token MUST NOT be accepted for processing.
        iat (iat): Time at which the JWT was issued.

    """

    iss: str
    sub: str
    aud: Union[str, List[str]]
    exp: int
    iat: int

    class Config:
        extra = Extra.allow


class OktaIDToken(IDToken):
    """Pydantic Model for the IDToken returned by Okta's OIDC implementation."""

    auth_time: int
    ver: int
    jti: str
    amr: List[str]
    idp: str
    nonce: str
    at_hash: str
    name: str
    email: str
    preferred_username: str


class KeycloakIDToken(IDToken):
    """Pydantic Model for the IDToken returned by Keycloak's OIDC implementation."""

    auth_time: int
    jti: str
    name: str
    email: str
    email_verified: bool
    preferred_username: str
