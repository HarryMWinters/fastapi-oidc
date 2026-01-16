"""Integration tests using FastAPI TestClient."""

import time
import uuid

import jwt
from fastapi import Depends
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_oidc import IDToken
from fastapi_oidc import get_auth


def test_integration_with_fastapi_app(
    monkeypatch, mock_discovery, token_with_audience, config_w_aud
):
    """Test full integration with a FastAPI application."""
    monkeypatch.setattr("fastapi_oidc.auth.discovery.configure", mock_discovery)

    # Create FastAPI app with authentication
    app = FastAPI()
    authenticate_user = get_auth(**config_w_aud)

    @app.get("/protected")
    def protected_endpoint(token: IDToken = Depends(authenticate_user)):
        return {"email": getattr(token, "email", None), "sub": token.sub}

    @app.get("/public")
    def public_endpoint():
        return {"message": "public"}

    # Test with TestClient
    client = TestClient(app)

    # Test public endpoint (no auth required)
    response = client.get("/public")
    assert response.status_code == 200
    assert response.json() == {"message": "public"}

    # Test protected endpoint with valid token
    response = client.get(
        "/protected", headers={"Authorization": f"Bearer {token_with_audience}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "sub" in data

    # Test protected endpoint without token
    response = client.get("/protected")
    assert response.status_code == 403  # OpenIdConnect requires auth


def test_integration_custom_token_type(
    monkeypatch, mock_discovery, token_with_audience, config_w_aud
):
    """Test integration with custom token type."""

    class CustomToken(IDToken):
        custom_field: str = "default_value"

    monkeypatch.setattr("fastapi_oidc.auth.discovery.configure", mock_discovery)

    app = FastAPI()
    authenticate_user = get_auth(**config_w_aud, token_type=CustomToken)

    @app.get("/custom")
    def custom_endpoint(token: CustomToken = Depends(authenticate_user)):
        return {
            "custom_field": token.custom_field,
            "email": getattr(token, "email", None),
        }

    client = TestClient(app)
    response = client.get(
        "/custom", headers={"Authorization": f"Bearer {token_with_audience}"}
    )
    assert response.status_code == 200
    assert "custom_field" in response.json()


def test_integration_expired_token(
    monkeypatch, mock_discovery, config_w_aud, test_email, private_key
):
    """Test that expired tokens are rejected."""
    monkeypatch.setattr("fastapi_oidc.auth.discovery.configure", mock_discovery)

    # Create an expired token (exp in the past)
    now = int(time.time())
    expired_token = jwt.encode(
        {
            "aud": config_w_aud["audience"],
            "iss": config_w_aud["issuer"],
            "email": test_email,
            "sub": "test-sub",
            "exp": now - 100,  # Expired 100 seconds ago
            "iat": now - 200,
            "auth_time": now - 200,
            "ver": "1",
            "jti": str(uuid.uuid4()),
            "amr": [],
            "idp": "",
            "nonce": "",
            "at_hash": "",
        },
        private_key,
        algorithm="RS256",
    )

    app = FastAPI()
    authenticate_user = get_auth(**config_w_aud)

    @app.get("/protected")
    def protected(token: IDToken = Depends(authenticate_user)):
        return {"email": getattr(token, "email", None)}

    client = TestClient(app)
    response = client.get(
        "/protected", headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "Unauthorized" in response.json()["detail"]


def test_integration_invalid_token(monkeypatch, mock_discovery, config_w_aud):
    """Test that malformed tokens are rejected."""
    monkeypatch.setattr("fastapi_oidc.auth.discovery.configure", mock_discovery)

    app = FastAPI()
    authenticate_user = get_auth(**config_w_aud)

    @app.get("/protected")
    def protected(token: IDToken = Depends(authenticate_user)):
        return {"email": getattr(token, "email", None)}

    client = TestClient(app)

    # Test with invalid token
    response = client.get(
        "/protected", headers={"Authorization": "Bearer invalid.jwt.token"}
    )
    assert response.status_code == 401


def test_integration_missing_required_claims(
    monkeypatch, mock_discovery, config_w_aud, private_key
):
    """Test that tokens missing required claims are rejected."""
    monkeypatch.setattr("fastapi_oidc.auth.discovery.configure", mock_discovery)

    now = int(time.time())
    # Token missing 'sub' claim
    incomplete_token = jwt.encode(
        {
            "aud": config_w_aud["audience"],
            "iss": config_w_aud["issuer"],
            "email": "test@example.com",
            # Missing 'sub' field
            "exp": now + 300,
            "iat": now,
        },
        private_key,
        algorithm="RS256",
    )

    app = FastAPI()
    authenticate_user = get_auth(**config_w_aud)

    @app.get("/protected")
    def protected(token: IDToken = Depends(authenticate_user)):
        return {"sub": token.sub}

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        "/protected", headers={"Authorization": f"Bearer {incomplete_token}"}
    )
    # Should fail validation due to missing required field
    # ValidationError results in 500 internal server error in this test context
    assert response.status_code == 500


def test_integration_multiple_endpoints(
    monkeypatch, mock_discovery, token_with_audience, config_w_aud
):
    """Test application with multiple protected endpoints."""
    monkeypatch.setattr("fastapi_oidc.auth.discovery.configure", mock_discovery)

    app = FastAPI()
    authenticate_user = get_auth(**config_w_aud)

    @app.get("/public")
    def public():
        return {"access": "public"}

    @app.get("/profile")
    def profile(token: IDToken = Depends(authenticate_user)):
        return {"sub": token.sub}

    @app.get("/settings")
    def settings(token: IDToken = Depends(authenticate_user)):
        return {"email": getattr(token, "email", None)}

    @app.post("/update")
    def update(token: IDToken = Depends(authenticate_user)):
        return {"updated": True}

    client = TestClient(app)

    # Public endpoint works without auth
    response = client.get("/public")
    assert response.status_code == 200

    # All protected endpoints work with valid token
    headers = {"Authorization": f"Bearer {token_with_audience}"}

    response = client.get("/profile", headers=headers)
    assert response.status_code == 200

    response = client.get("/settings", headers=headers)
    assert response.status_code == 200

    response = client.post("/update", headers=headers)
    assert response.status_code == 200

    # Protected endpoints fail without token
    response = client.get("/profile")
    assert response.status_code == 403

    response = client.post("/update")
    assert response.status_code == 403
