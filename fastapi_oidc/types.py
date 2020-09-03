from typing import List

from pydantic import BaseModel
from pydantic import BaseSettings


class OIDCConfig(BaseSettings):
    client_id: str
    base_authorization_server_uri: str
    issuer: str
    signature_cache_ttl: str


class IDToken(BaseModel):
    """
    """

    # TODO Verify the minimum and maximum claim set for ID Tokens.
    name: str
    email: str
    preferred_username: str
    exp: int
    auth_time: int
    sub: str
    ver: int
    iss: str
    aud: str
    iat: int
    jti: str
    amr: List[str]
    idp: str
    nonce: str
    at_hash: str
