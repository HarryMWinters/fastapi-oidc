import json
import os
import time
import uuid

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from fastapi_oidc import auth


class Fixtures:
    _fixtures_directory = os.path.join(os.path.dirname(__file__), "fixtures")

    with open(_fixtures_directory + "/AuthServerDiscovery.json") as f:
        OIDC_DISCOVERY_RESPONSE = json.load(f)

    _key = rsa.generate_private_key(
        backend=default_backend(), public_exponent=65537, key_size=2048
    )

    TESTING_PRIVATE_KEY = _key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode("UTF-8")

    TESTING_PUBLIC_KEY = (
        _key.public_key()
        .public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.PKCS1)
        .decode("UTF-8")
    )


TEST_CONFIG = {
    "client_id": "CongenitalOptimist",
    "audience": "NeverAgain",
    "base_authorization_server_uri": "WhatAreTheCivilianApplications?",
    "issuer": "PokeItWithAStick",
    "signature_cache_ttl": 6e3,
}

# Test configuration without audience
TEST_CONFIG_NO_AUD = {
    "client_id": "CongenitalOptimist",
    "base_authorization_server_uri": "WhatAreTheCivilianApplications?",
    "issuer": "PokeItWithAStick",
    "signature_cache_ttl": 6e3,
}


def _make_token(
    email: str,
    private_key: str = Fixtures.TESTING_PRIVATE_KEY,
    client_id: str = str(TEST_CONFIG["client_id"]),
    audience: str = str(TEST_CONFIG["audience"]),
    issuer: str = str(TEST_CONFIG["issuer"]),
) -> str:
    now = int(time.time())
    return jwt.encode(
        {
            "aud": audience,
            "iss": issuer,
            "email": email,
            "name": "SweetAndFullOfGrace",
            "preferred_username": "Sweet",
            "exp": now + 30,
            "auth_time": now,
            "sub": "foo",
            "ver": "1",
            "iat": now,
            "jti": str(uuid.uuid4()),
            "amr": [],
            "idp": "",
            "nonce": "",
            "at_hash": "",
        },
        private_key,
        algorithm="RS256",
    ).decode("UTF-8")


# Make a token where audience is client_id
def _make_token_no_aud(
    email: str,
    private_key: str = Fixtures.TESTING_PRIVATE_KEY,
    client_id: str = str(TEST_CONFIG_NO_AUD["client_id"]),
    issuer: str = str(TEST_CONFIG_NO_AUD["issuer"]),
) -> str:
    now = int(time.time())
    return jwt.encode(
        {
            "aud": client_id,
            "iss": issuer,
            "email": email,
            "name": "SweetAndFullOfGrace",
            "preferred_username": "Sweet",
            "exp": now + 30,
            "auth_time": now,
            "sub": "foo",
            "ver": "1",
            "iat": now,
            "jti": str(uuid.uuid4()),
            "amr": [],
            "idp": "",
            "nonce": "",
            "at_hash": "",
        },
        private_key,
        algorithm="RS256",
    ).decode("UTF-8")


def test__authenticate_user(monkeypatch):
    def mock_discovery(*args, **kwargs):
        class functions:
            auth_server = lambda **_: Fixtures.OIDC_DISCOVERY_RESPONSE
            public_keys = lambda _: Fixtures.TESTING_PUBLIC_KEY
            signing_algos = lambda x: x["id_token_signing_alg_values_supported"]

        return functions

    monkeypatch.setattr(auth.discovery, "configure", mock_discovery)
    email = "AnticipationOfANewLoversArrivalThe@VeryLittleGravitasIndeed"
    token = _make_token(email=email)
    authenticate_user = auth.get_auth(**TEST_CONFIG)
    IDToken = authenticate_user(auth_header=f"Bearer {token}")
    assert IDToken.email == email  # nosec


# Ensure that when no audience is supplied, that the audience defaults to client ID
def test__authenticate_user_no_aud(monkeypatch):
    def mock_discovery(*args, **kwargs):
        class functions:
            auth_server = lambda **_: Fixtures.OIDC_DISCOVERY_RESPONSE
            public_keys = lambda _: Fixtures.TESTING_PUBLIC_KEY
            signing_algos = lambda x: x["id_token_signing_alg_values_supported"]

        return functions

    monkeypatch.setattr(auth.discovery, "configure", mock_discovery)
    email = "AnticipationOfANewLoversArrivalThe@VeryLittleGravitasIndeed"
    token = _make_token_no_aud(email=email)
    authenticate_user = auth.get_auth(**TEST_CONFIG_NO_AUD)
    IDToken = authenticate_user(auth_header=f"Bearer {token}")
    assert IDToken.email == email  # nosec
    assert IDToken.aud == TEST_CONFIG_NO_AUD["client_id"]
