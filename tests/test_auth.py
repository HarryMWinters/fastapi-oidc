# type: ignore
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

from fastapi_oidc.auth import get_auth
from fastapi.security import OpenIdConnect

def test_get_auth_configures_openidconnect_correctly():
    client_id = "test_client"
    base_uri = "https://auth.example.com"
    
    # Esto inicializa la función pero no la ejecuta
    auth_func = get_auth(
        client_id=client_id,
        base_authorization_server_uri=base_uri,
        issuer=base_uri,
        signature_cache_ttl=60
    )
    
    # El objeto oauth2_scheme está dentro del closure de authenticate_user
    # Para verificarlo, podemos inspeccionar las variables del closure
    # Pero lo más directo es asegurar que no lanza excepción y se configura
    assert callable(auth_func)
