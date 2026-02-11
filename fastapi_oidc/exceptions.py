class TokenSpecificationError(Exception):
    """Raised when an invalid token type is provided to get_auth().

    This exception indicates a programming error where the token_type
    parameter is not a subclass of IDToken.
    """

    pass
