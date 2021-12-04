from enum import Enum


class GrantType(str, Enum):
    """Grant types that can be used in the interactive documentation."""

    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    IMPLICIT = "implicit"
    PASSWORD = "password"  # nosec
