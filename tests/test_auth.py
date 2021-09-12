from fastapi_oidc import auth
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
    id_token = authenticate_user(auth_header=f"Bearer {token}")

    assert id_token["email"] == test_email  # nosec
    assert id_token["aud"] == config_w_aud["audience"]


# Ensure that when no audience is supplied, that the audience defaults to client ID
def test__authenticate_user_no_audience(
    monkeypatch,
    mock_discovery,
    token_without_audience,
    no_audience_config,
    test_email,
):

    monkeypatch.setattr(auth.discovery, "configure", mock_discovery)

    token = token_without_audience

    authenticate_user = auth.get_auth(**no_audience_config)

    id_token = authenticate_user(auth_header=f"Bearer {token}")


def test__authenticate_user_returns_custom_tokens(
    monkeypatch, mock_discovery, token_without_audience, no_audience_config
):
    class CustomToken(IDToken):
        custom_field: str = "OnlySlightlyBent"

    monkeypatch.setattr(auth.discovery, "configure", mock_discovery)

    token = token_without_audience

    authenticate_user = auth.get_auth(**no_audience_config)

    custom_token = CustomToken(
        **authenticate_user(auth_header=f"Bearer {token}")
    )

    assert custom_token.custom_field == "OnlySlightlyBent"
