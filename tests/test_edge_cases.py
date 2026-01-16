"""Test edge cases and error conditions."""

import time
import uuid
from unittest.mock import Mock
from unittest.mock import patch

import jwt
import pytest
import requests

from fastapi_oidc import discovery
from fastapi_oidc.auth import get_auth
from fastapi_oidc.exceptions import TokenSpecificationError
from fastapi_oidc.types import IDToken


def test_discovery_handles_network_timeout():
    """Test that discovery handles network timeouts gracefully."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.Timeout("Connection timeout")

        discover = discovery.configure(cache_ttl=100)

        with pytest.raises(requests.Timeout):
            discover.auth_server(base_url="https://example.com")


def test_discovery_handles_http_error():
    """Test that discovery handles HTTP errors."""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        discover = discovery.configure(cache_ttl=100)

        with pytest.raises(requests.HTTPError):
            discover.auth_server(base_url="https://example.com")


def test_discovery_handles_connection_error():
    """Test that discovery handles connection errors."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError(
            "Failed to establish connection"
        )

        discover = discovery.configure(cache_ttl=100)

        with pytest.raises(requests.ConnectionError):
            discover.auth_server(base_url="https://example.com")


def test_get_auth_rejects_non_idtoken_subclass():
    """Test that get_auth validates token_type is IDToken subclass."""

    class NotAnIDToken:
        pass

    config = {
        "client_id": "test",
        "base_authorization_server_uri": "https://example.com",
        "issuer": "example.com",
        "signature_cache_ttl": 3600,
    }

    with pytest.raises(TokenSpecificationError) as exc_info:
        get_auth(**config, token_type=NotAnIDToken)

    assert "must be a subclass of" in str(exc_info.value)
    assert "NotAnIDToken" in str(exc_info.value)


def test_get_auth_accepts_idtoken_subclass():
    """Test that get_auth accepts valid IDToken subclasses."""

    class ValidToken(IDToken):
        custom_field: str = "test"

    config = {
        "client_id": "test",
        "base_authorization_server_uri": "https://example.com",
        "issuer": "example.com",
        "signature_cache_ttl": 3600,
    }

    # Should not raise an exception
    result = get_auth(**config, token_type=ValidToken)
    assert callable(result)


def test_multiple_audience_values(
    monkeypatch, mock_discovery, config_w_aud, test_email, private_key
):
    """Test handling tokens with multiple audience values."""
    monkeypatch.setattr("fastapi_oidc.auth.discovery.configure", mock_discovery)

    now = int(time.time())
    # Token with array of audiences
    multi_aud_token = jwt.encode(
        {
            "aud": ["audience1", "audience2", config_w_aud["audience"]],
            "iss": config_w_aud["issuer"],
            "email": test_email,
            "sub": "test-sub",
            "exp": now + 300,
            "iat": now,
            "auth_time": now,
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

    authenticate_user = get_auth(**config_w_aud)
    result = authenticate_user(auth_header=f"Bearer {multi_aud_token}")

    assert result.email == test_email
    assert config_w_aud["audience"] in result.aud


def test_single_audience_as_string(
    monkeypatch, mock_discovery, config_w_aud, test_email, private_key
):
    """Test handling tokens with single audience as string."""
    monkeypatch.setattr("fastapi_oidc.auth.discovery.configure", mock_discovery)

    now = int(time.time())
    single_aud_token = jwt.encode(
        {
            "aud": config_w_aud["audience"],  # String, not list
            "iss": config_w_aud["issuer"],
            "email": test_email,
            "sub": "test-sub",
            "exp": now + 300,
            "iat": now,
            "auth_time": now,
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

    authenticate_user = get_auth(**config_w_aud)
    result = authenticate_user(auth_header=f"Bearer {single_aud_token}")

    assert result.email == test_email
    assert result.aud == config_w_aud["audience"]


def test_token_with_extra_fields(
    monkeypatch, mock_discovery, config_w_aud, test_email, private_key
):
    """Test that tokens with extra fields are handled correctly."""
    monkeypatch.setattr("fastapi_oidc.auth.discovery.configure", mock_discovery)

    now = int(time.time())
    token_with_extras = jwt.encode(
        {
            "aud": config_w_aud["audience"],
            "iss": config_w_aud["issuer"],
            "email": test_email,
            "sub": "test-sub",
            "exp": now + 300,
            "iat": now,
            # Extra fields not in IDToken model
            "custom_claim_1": "value1",
            "custom_claim_2": 12345,
            "custom_claim_3": {"nested": "data"},
        },
        private_key,
        algorithm="RS256",
    )

    authenticate_user = get_auth(**config_w_aud)
    result = authenticate_user(auth_header=f"Bearer {token_with_extras}")

    # Base claims should work
    assert result.email == test_email
    assert result.sub == "test-sub"

    # Extra fields should be accessible (Pydantic extra="allow")
    assert hasattr(result, "custom_claim_1")
    assert result.custom_claim_1 == "value1"


def test_wrong_issuer(
    monkeypatch, mock_discovery, config_w_aud, test_email, private_key
):
    """Test that tokens with wrong issuer are rejected."""
    monkeypatch.setattr("fastapi_oidc.auth.discovery.configure", mock_discovery)

    now = int(time.time())
    wrong_issuer_token = jwt.encode(
        {
            "aud": config_w_aud["audience"],
            "iss": "wrong-issuer.com",  # Wrong issuer
            "email": test_email,
            "sub": "test-sub",
            "exp": now + 300,
            "iat": now,
            "auth_time": now,
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

    authenticate_user = get_auth(**config_w_aud)

    with pytest.raises(Exception):  # Should raise HTTPException or JWTError
        authenticate_user(auth_header=f"Bearer {wrong_issuer_token}")


def test_wrong_audience(
    monkeypatch, mock_discovery, config_w_aud, test_email, private_key
):
    """Test that tokens with wrong audience are rejected."""
    monkeypatch.setattr("fastapi_oidc.auth.discovery.configure", mock_discovery)

    now = int(time.time())
    wrong_audience_token = jwt.encode(
        {
            "aud": "wrong-audience",  # Wrong audience
            "iss": config_w_aud["issuer"],
            "email": test_email,
            "sub": "test-sub",
            "exp": now + 300,
            "iat": now,
            "auth_time": now,
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

    authenticate_user = get_auth(**config_w_aud)

    with pytest.raises(Exception):  # Should raise HTTPException or JWTClaimsError
        authenticate_user(auth_header=f"Bearer {wrong_audience_token}")


def test_token_about_to_expire(
    monkeypatch, mock_discovery, config_w_aud, test_email, private_key
):
    """Test tokens that are about to expire but still valid."""
    monkeypatch.setattr("fastapi_oidc.auth.discovery.configure", mock_discovery)

    now = int(time.time())
    # Token expires in 1 second
    almost_expired_token = jwt.encode(
        {
            "aud": config_w_aud["audience"],
            "iss": config_w_aud["issuer"],
            "email": test_email,
            "sub": "test-sub",
            "exp": now + 1,  # Expires in 1 second
            "iat": now,
            "auth_time": now,
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

    authenticate_user = get_auth(**config_w_aud)
    # Should still be valid
    result = authenticate_user(auth_header=f"Bearer {almost_expired_token}")
    assert result.email == test_email


def test_bearer_token_extraction(
    monkeypatch, mock_discovery, token_with_audience, config_w_aud
):
    """Test that bearer token is correctly extracted from auth header."""
    monkeypatch.setattr("fastapi_oidc.auth.discovery.configure", mock_discovery)

    authenticate_user = get_auth(**config_w_aud)

    # Test with 'Bearer ' prefix
    result = authenticate_user(auth_header=f"Bearer {token_with_audience}")
    assert result is not None

    # Test with just the token (should still work due to split logic)
    result = authenticate_user(auth_header=token_with_audience)
    assert result is not None


def test_token_specification_error_inherits_from_exception():
    """Test that TokenSpecificationError correctly inherits from Exception."""
    error = TokenSpecificationError("test error")

    # Should be catchable as Exception
    assert isinstance(error, Exception)

    # Should not be BaseException only
    assert type(error).__bases__[0] == Exception
