import json
import os
import time
import uuid

import jwt
import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

FIXTURES_DIRECTORY = os.path.join(os.path.dirname(__file__), "fixtures")


KEY = rsa.generate_private_key(
    backend=default_backend(), public_exponent=65537, key_size=2048
)


@pytest.fixture
def oidc_discovery():
    with open(FIXTURES_DIRECTORY + "/AuthServerDiscovery.json") as f:
        OIDC_DISCOVERY_RESPONSE = json.load(f)

    return OIDC_DISCOVERY_RESPONSE


@pytest.fixture
def test_email():
    return "AnticipationOfANewLoversArrivalThe@VeryLittleGravitasIndeed"


@pytest.fixture
def key():
    # keeping the key global so it isn't regenerated with each fixture use.
    return KEY


@pytest.fixture
def private_key(key):
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode("UTF-8")


@pytest.fixture
def public_key(key):
    return (
        key.public_key()
        .public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.PKCS1)
        .decode("UTF-8")
    )


@pytest.fixture
def config_w_aud():
    return {
        "audience": "NeverAgain",
        "openid_connect_url": "WhatAreTheCivilianApplications?",
        "issuer": "PokeItWithAStick",
        "signature_cache_ttl": 6e3,
    }


@pytest.fixture
def no_audience_config():
    return {
        "openid_connect_url": "WhatAreTheCivilianApplications?",
        "issuer": "PokeItWithAStick",
        "signature_cache_ttl": 6e3,
    }


@pytest.fixture
def token_with_audience(private_key, config_w_aud, test_email) -> str:
    audience: str = str(config_w_aud["audience"])
    issuer: str = str(config_w_aud["issuer"])
    now = int(time.time())

    return jwt.encode(
        {
            "aud": audience,
            "iss": issuer,
            "email": test_email,
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


@pytest.fixture
def token_without_audience(private_key, no_audience_config, test_email) -> str:
    # Make a token where audience is client_id
    issuer: str = str(no_audience_config["issuer"])
    now = int(time.time())

    return jwt.encode(
        {
            "aud": "NoAudience",
            "iss": issuer,
            "email": test_email,
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


@pytest.fixture
def mock_discovery(oidc_discovery, public_key):
    class functions:
        auth_server = lambda **_: oidc_discovery
        public_keys = lambda _: public_key
        signing_algos = lambda x: x["id_token_signing_alg_values_supported"]
        authorization_url = lambda x: x["authorization_endpoint"]
        token_url = lambda x: x["token_endpoint"]

    return lambda *args, **kwargs: functions
