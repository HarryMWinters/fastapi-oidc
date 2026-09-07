# type: ignore
import jwt
import pytest

from fastapi_oidc import auth
from fastapi_oidc.exceptions import TokenSpecificationError
from fastapi_oidc.types import IDToken


def test__authenticate_user(
    monkeypatch,
    mock_discovery,
    token_with_audience,
    config_w_aud,
    test_email,
):

    monkeypatch.setattr(auth.discovery, "configure", mock_discovery)

    token = token_with_audience

    authenticate_user = auth.get_auth(**config_w_aud)
    id_token: IDToken = authenticate_user(auth_header=f"Bearer {token}")

    assert id_token.email == test_email  # nosec
    assert id_token.aud == config_w_aud["audience"]


# Ensure that when no audience is supplied, that the audience defaults to client ID
def test__authenticate_user_no_aud(
    monkeypatch,
    mock_discovery,
    token_without_audience,
    no_audience_config,
    test_email,
):

    monkeypatch.setattr(auth.discovery, "configure", mock_discovery)

    token = token_without_audience

    authenticate_user = auth.get_auth(**no_audience_config)

    id_token: IDToken = authenticate_user(auth_header=f"Bearer {token}")

    assert id_token.email == test_email  # nosec
    assert id_token.aud == no_audience_config["client_id"]


def test__get_auth_raises_if_token_type_is_not_subclass_of_IDToken(no_audience_config):
    class BadToken:
        pass

    with pytest.raises(TokenSpecificationError):
        auth.get_auth(**no_audience_config, token_type=BadToken)


def test__authenticate_user_returns_custom_tokens(
    monkeypatch, mock_discovery, token_without_audience, no_audience_config
):
    class CustomToken(IDToken):
        custom_field: str = "OnlySlightlyBent"

    monkeypatch.setattr(auth.discovery, "configure", mock_discovery)

    token = token_without_audience

    authenticate_user = auth.get_auth(**no_audience_config, token_type=CustomToken)

    custom_token: CustomToken = authenticate_user(auth_header=f"Bearer {token}")

    assert custom_token.custom_field == "OnlySlightlyBent"


def test__authenticate_user_selects_jwks_key_by_kid(
    monkeypatch, mock_discovery_jwks, make_token, config_w_aud, test_email
):
    """A real provider serves a JWKS; the key is chosen by the token's kid."""
    from tests.conftest import KID

    monkeypatch.setattr(auth.discovery, "configure", mock_discovery_jwks)

    authenticate_user = auth.get_auth(**config_w_aud)
    id_token = authenticate_user(
        auth_header=f"Bearer {make_token(headers={'kid': KID})}"
    )

    assert id_token.email == test_email


def test__authenticate_user_accepts_single_key_jwks_without_kid(
    monkeypatch, mock_discovery_jwks, make_token, config_w_aud, test_email
):
    monkeypatch.setattr(auth.discovery, "configure", mock_discovery_jwks)

    authenticate_user = auth.get_auth(**config_w_aud)
    id_token = authenticate_user(auth_header=f"Bearer {make_token()}")

    assert id_token.email == test_email


def test__authenticate_user_rejects_unknown_kid(
    monkeypatch, mock_discovery_jwks, make_token, config_w_aud
):
    from fastapi import HTTPException

    monkeypatch.setattr(auth.discovery, "configure", mock_discovery_jwks)

    authenticate_user = auth.get_auth(**config_w_aud)

    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(auth_header=f"Bearer {make_token(headers={'kid': 'nope'})}")

    assert exc_info.value.status_code == 401
    assert "kid" in exc_info.value.detail


def test__authenticate_user_rejects_multi_key_jwks_without_kid(
    monkeypatch, oidc_discovery, jwks, make_token, config_w_aud
):
    from fastapi import HTTPException

    two_keys = {"keys": [jwks["keys"][0], {**jwks["keys"][0], "kid": "second"}]}

    class functions:
        auth_server = lambda **_: oidc_discovery
        public_keys = lambda _: two_keys
        signing_algos = lambda x: x["id_token_signing_alg_values_supported"]

    monkeypatch.setattr(auth.discovery, "configure", lambda *a, **k: functions)

    authenticate_user = auth.get_auth(**config_w_aud)

    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(auth_header=f"Bearer {make_token()}")

    assert exc_info.value.status_code == 401


def test__authenticate_user_rejects_wrong_signing_key(
    monkeypatch, mock_discovery_jwks, config_w_aud, test_email
):
    """A token signed by a key that is not in the JWKS is rejected with 401."""
    import time

    from cryptography.hazmat.primitives.asymmetric import rsa
    from fastapi import HTTPException

    from tests.conftest import KID

    monkeypatch.setattr(auth.discovery, "configure", mock_discovery_jwks)

    rogue_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = int(time.time())
    forged = jwt.encode(
        {
            "aud": config_w_aud["audience"],
            "iss": config_w_aud["issuer"],
            "email": test_email,
            "sub": "foo",
            "exp": now + 30,
            "iat": now,
        },
        rogue_key,
        algorithm="RS256",
        headers={"kid": KID},
    )

    authenticate_user = auth.get_auth(**config_w_aud)

    with pytest.raises(HTTPException) as exc_info:
        authenticate_user(auth_header=f"Bearer {forged}")

    assert exc_info.value.status_code == 401


def test__authenticate_user_accepts_issuer_generator(
    monkeypatch, mock_discovery, make_token, config_w_aud, test_email
):
    """Any iterable of issuers works, not just lists."""
    monkeypatch.setattr(auth.discovery, "configure", mock_discovery)

    config = {**config_w_aud, "issuer": (i for i in ["other", config_w_aud["issuer"]])}
    authenticate_user = auth.get_auth(**config)
    id_token = authenticate_user(auth_header=f"Bearer {make_token()}")

    assert id_token.email == test_email
