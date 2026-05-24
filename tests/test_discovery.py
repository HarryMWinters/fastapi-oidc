from fastapi_oidc import discovery
import pytest

def test_discover_auth_server():
    # Simulamos una llamada al servidor de descubrimiento
    # Esto cubrirá la parte de 'discovery.py' que tiene poca cobertura
    with pytest.raises(Exception):
        discovery.configure(cache_ttl=3600).auth_server(base_url="https://invalid-url.test")
