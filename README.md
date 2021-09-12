# FastAPI OIDC

<p align="left">
    <a href="https://github.com/HarryMWinters/fastapi-oidc/actions?query=workflow%3ATest"
       target="_blank">
       <img src="https://github.com/HarryMWinters/fastapi-oidc/workflows/Test/badge.svg"  
            alt="Test">
    </a>
    <a href='https://fastapi-oidc.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/fastapi-oidc/badge/?version=latest' alt='Documentation Status' />
    </a>
    <a href="https://pypi.org/project/fastapi-oidc" 
       target="_blank">
       <img src="https://img.shields.io/pypi/v/fastapi-oidc?color=%2334D058&label=pypi%20package" 
            alt="Package version">
    </a>
</p>

---

Verify and decrypt 3rd party OpenID Connect tokens to protect your
[fastapi](https://github.com/tiangolo/fastapi) endpoints.

Easily used with authenticators such as:
- [Keycloak](https://www.keycloak.org/) (open source)
- [SuperTokens](https://supertokens.io/) (open source)
- [Auth0](https://auth0.com/)
- [Okta](https://www.okta.com/products/authentication/)

FastAPI's generated interactive documentation supports the grant flows
`authorization_code`, `implicit`, `password` and `client_credentials`.

## Installation

```
poetry add fastapi-oidc
```

Or, for the old-timers:

```
pip install fastapi-oidc
```

## Usage

See the [API reference documentation](https://fastapi-oidc.readthedocs.io/en/latest/) 
for more information.

```python3
from fastapi import Depends
from fastapi import FastAPI
from fastapi_oidc import get_auth
from fastapi_oidc.types import IDToken


app = FastAPI()

# e.g. local keycloak development server
discovery_url = "http://localhost:8080/auth/realms/my-realm/.well-known/openid-configuration"
issuer = "http://localhost:8080/auth/realms/my-realm"

authenticate_user = get_auth(
    discovery_url=discovery_url,
    issuer=issuer,  # optional, verification only
    audience="my-service",  # optional, verification only
    signature_cache_ttl=3600,  # optional
)


@app.get("/protected")
def protected(
    authenticated_user: IDToken = Depends(authenticate_user),
):
    return authenticated_user
```

### Optional: Predefined and custom validation of tokens

You can use other predefined token types or create your own to validate the 
token's contents.

Predefined Okta token:
```python3
from fastapi_oidc.types import OktaIDToken


@app.get("/protected")
def protected(authenticated_user: OktaIDToken = Depends(authenticate_user)):
    return authenticated_user
```

Custom token:
```python3
from fastapi_oidc.types import IDToken


class CustomIDToken(IDToken):
    custom_field: str
    custom_default: float = 3.14


@app.get("/protected")
def protected(authenticated_user: CustomIDToken = Depends(authenticate_user)):
    return authenticated_user
```

### FastAPI + Keycloak

**TODO**

Example of using Keycloak with FastAPI.
```
app/
    __init__.py
    main.py
Dockerfile
docker-compose.yml
```
