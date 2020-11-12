from typing import Dict

import requests
from cachetools import TTLCache
from cachetools import cached


def configure(*_, cache_ttl: int):
    @cached(TTLCache(1, cache_ttl), key=lambda d: d["jwks_uri"])
    def get_authentication_server_public_keys(OIDC_spec: Dict):
        """
        Retrieve the public keys used by the authentication server
        for signing OIDC ID tokens.
        """
        keys_uri = OIDC_spec["jwks_uri"]
        r = requests.get(keys_uri)
        keys = r.json()
        return keys

    def get_signing_algos(OIDC_spec: Dict):
        algos = OIDC_spec["id_token_signing_alg_values_supported"]
        return algos

    @cached(TTLCache(1, cache_ttl))
    def discover_auth_server(*_, base_url: str) -> Dict:
        discovery_url = f"{base_url}/.well-known/openid-configuration"
        r = requests.get(discovery_url)
        # If the auth server is failing we can't verify tokens.
        # Soooo panic I guess?
        r.raise_for_status()
        configuration = r.json()
        return configuration

    class functions:
        auth_server = discover_auth_server
        public_keys = get_authentication_server_public_keys
        signing_algos = get_signing_algos

    return functions
