"""Example FastAPI application with Okta OIDC authentication.

This example demonstrates:
- Basic authentication with Okta
- Protected and public endpoints
- Extracting user information from tokens
- Error handling
"""

import os

from fastapi import Depends
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from fastapi_oidc import IDToken
from fastapi_oidc import get_auth

# Load configuration from environment
OKTA_DOMAIN = os.getenv("OKTA_DOMAIN", "dev-123456.okta.com")
CLIENT_ID = os.getenv("OKTA_CLIENT_ID", "your-client-id")
AUDIENCE = os.getenv("OKTA_AUDIENCE")  # Optional, defaults to CLIENT_ID
CACHE_TTL = int(os.getenv("OKTA_CACHE_TTL", "3600"))

# Configure OIDC authentication
authenticate_user = get_auth(
    client_id=CLIENT_ID,
    audience=AUDIENCE if AUDIENCE else CLIENT_ID,
    base_authorization_server_uri=f"https://{OKTA_DOMAIN}",
    issuer=OKTA_DOMAIN,
    signature_cache_ttl=CACHE_TTL,
)

# Create FastAPI application
app = FastAPI(
    title="FastAPI OIDC - Okta Example",
    description="Example application demonstrating Okta OIDC authentication with fastapi-oidc",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
def root():
    """Public endpoint - no authentication required.

    Returns:
        Welcome message with application information.
    """
    return {
        "message": "Welcome to FastAPI OIDC Example",
        "provider": "Okta",
        "status": "running",
        "docs": "Visit /docs for interactive API documentation",
        "endpoints": {
            "public": ["/"],
            "protected": ["/protected", "/user-info"],
        },
    }


@app.get("/protected")
def protected(id_token: IDToken = Depends(authenticate_user)):
    """Protected endpoint - requires valid OIDC token.

    Args:
        id_token: Validated ID token from Okta.

    Returns:
        User information extracted from the token.
    """
    return {
        "message": "Successfully authenticated!",
        "user": {
            "email": getattr(id_token, "email", None),
            "name": getattr(id_token, "name", None),
            "sub": id_token.sub,
        },
        "token_info": {
            "issuer": id_token.iss,
            "audience": id_token.aud,
            "issued_at": id_token.iat,
            "expires_at": id_token.exp,
        },
    }


@app.get("/user-info")
def user_info(id_token: IDToken = Depends(authenticate_user)):
    """Return all available user information from the token.

    Args:
        id_token: Validated ID token from Okta.

    Returns:
        Complete token contents as a dictionary.
    """
    return {
        "user_info": id_token.model_dump(),
        "note": "This includes all claims present in your token",
    }


@app.exception_handler(401)
def unauthorized_handler(request, exc):
    """Custom handler for unauthorized requests.

    Args:
        request: The incoming request.
        exc: The exception that was raised.

    Returns:
        JSON response with error details.
    """
    return JSONResponse(
        status_code=401,
        content={
            "error": "Unauthorized",
            "message": "Invalid or missing authentication token",
            "hint": "Include 'Authorization: Bearer <token>' header with a valid Okta OIDC token",
            "docs": "See https://fastapi-oidc.readthedocs.io for more information",
        },
    )


@app.exception_handler(403)
def forbidden_handler(request, exc):
    """Custom handler for forbidden requests.

    Args:
        request: The incoming request.
        exc: The exception that was raised.

    Returns:
        JSON response with error details.
    """
    return JSONResponse(
        status_code=403,
        content={
            "error": "Forbidden",
            "message": "Authentication required to access this resource",
            "hint": "Obtain a token from Okta and include it in the Authorization header",
        },
    )


if __name__ == "__main__":
    import uvicorn

    print("Starting FastAPI OIDC Example with Okta")
    print(f"Okta Domain: {OKTA_DOMAIN}")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Audience: {AUDIENCE if AUDIENCE else CLIENT_ID}")
    print(f"Cache TTL: {CACHE_TTL} seconds")
    print("\nVisit http://localhost:8000/docs for interactive API documentation")

    uvicorn.run(app, host="0.0.0.0", port=8000)  # nosec B104
