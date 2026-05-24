from fastapi_oidc import IDToken
import pytest

def test_oidc_configuration():
    mock_token_data = {
        "iss": "https://test.com",
        "sub": "test_user",
        "aud": "test_client",
        "exp": 9999999999,
        "iat": 1111111111
    }
    
    oidc = IDToken(**mock_token_data)
    
    assert oidc.iss == "https://test.com"
    assert oidc.sub == "test_user"
