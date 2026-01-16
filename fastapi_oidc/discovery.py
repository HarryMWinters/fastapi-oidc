from typing import Any

import requests
from cachetools import TTLCache
from cachetools import cached


def configure(*_, cache_ttl: int):
    """Configure OIDC discovery functions with caching.

    This factory function creates a set of cached discovery functions
    for retrieving OIDC server configuration, public keys, and signing
    algorithms. All functions are cached using TTL-based caching.

    Args:
        cache_ttl: Time-to-live for cached values in seconds.

    Returns:
        A functions namespace object with three methods:
        - auth_server: Discover OIDC server configuration
        - public_keys: Retrieve public signing keys
        - signing_algos: Get supported signing algorithms

    Example:
        >>> discover = configure(cache_ttl=3600)
        >>> config = discover.auth_server(base_url="https://auth.example.com")
    """

    @cached(TTLCache(1, cache_ttl), key=lambda d: d["jwks_uri"])
    def get_authentication_server_public_keys(
        OIDC_spec: dict[str, Any]
    ) -> dict[str, Any]:
        """Retrieve the public keys used by the authentication server.

        Args:
            OIDC_spec: The OIDC discovery document containing the jwks_uri.

        Returns:
            Dictionary containing the public keys in JWKS format.

        Raises:
            requests.RequestException: If the request to fetch keys fails.
        """
        keys_uri = OIDC_spec["jwks_uri"]
        r = requests.get(keys_uri, timeout=15)
        keys = r.json()
        return keys

    def get_signing_algos(OIDC_spec: dict[str, Any]) -> list[str]:
        """Extract the supported signing algorithms from OIDC spec.

        Args:
            OIDC_spec: The OIDC discovery document.

        Returns:
            List of supported signing algorithm identifiers.
        """
        algos = OIDC_spec["id_token_signing_alg_values_supported"]
        return algos

    @cached(TTLCache(1, cache_ttl))
    def discover_auth_server(*_, base_url: str) -> dict[str, Any]:
        """Discover OIDC server configuration via well-known endpoint.

        Args:
            base_url: Base URL of the authorization server.

        Returns:
            Dictionary containing the OIDC server configuration.

        Raises:
            requests.HTTPError: If the discovery endpoint returns an error.
            requests.RequestException: If the network request fails.
        """
        discovery_url = f"{base_url}/.well-known/openid-configuration"
        r = requests.get(discovery_url, timeout=15)
        # If the auth server is failing, token verification is impossible
        r.raise_for_status()
        configuration = r.json()
        return configuration

    class functions:
        auth_server = discover_auth_server
        public_keys = get_authentication_server_public_keys
        signing_algos = get_signing_algos

    return functions
