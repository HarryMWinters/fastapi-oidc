from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import SecurityScopes

import fastapi_oidc
from fastapi_oidc import Auth
from fastapi_oidc.idtoken_types import IDToken


def test__authenticate_user(
    monkeypatch,
    mock_discovery,
    token_with_audience,
    config_w_aud,
    test_email,
):
    monkeypatch.setattr(fastapi_oidc.auth.discovery, "configure", mock_discovery)

    token = token_with_audience

    auth = Auth(**config_w_aud)
    id_token = auth.required(
        security_scopes=SecurityScopes(scopes=[]),
        authorization_credentials=HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        ),
    )

    assert id_token.email == test_email  # nosec
    assert id_token.aud == config_w_aud["client_id"]


def test__authenticate_user_no_aud(
    monkeypatch,
    mock_discovery,
    token_without_audience,
    no_audience_config,
    test_email,
):

    monkeypatch.setattr(fastapi_oidc.auth.discovery, "configure", mock_discovery)

    token = token_without_audience

    auth = Auth(**no_audience_config)

    id_token = auth.required(
        security_scopes=SecurityScopes(scopes=[]),
        authorization_credentials=HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        ),
    )

    assert id_token.email == test_email  # nosec


def test__authenticate_user_returns_custom_tokens(
    monkeypatch, mock_discovery, token_without_audience, no_audience_config
):
    class CustomToken(IDToken):
        custom_field: str = "OnlySlightlyBent"

    monkeypatch.setattr(fastapi_oidc.auth.discovery, "configure", mock_discovery)

    token = token_without_audience

    auth = Auth(
        **no_audience_config,
        idtoken_model=CustomToken,
    )

    custom_token = auth.required(
        security_scopes=SecurityScopes(scopes=[]),
        authorization_credentials=HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=token
        ),
    )

    assert custom_token.custom_field == "OnlySlightlyBent"
