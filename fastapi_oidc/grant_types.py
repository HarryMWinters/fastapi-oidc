from enum import Enum


class GrantType(str, Enum):
    """Grant types shown in docs."""

    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    IMPLICIT = "implicit"
    PASSWORD = "password"  # nosec
