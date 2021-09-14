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

**Documentation**: <a href="https://fastapi-oidc.readthedocs.io/" target="_blank">https://fastapi-oidc.readthedocs.io/</a>

**Source Code**: <a href="https://github.com/HarryMWinters/fastapi-oidc" target="_blank">https://github.com/HarryMWinters/fastapi-oidc</a>

---

Verify and decrypt 3rd party OpenID Connect tokens to protect your
[FastAPI](https://github.com/tiangolo/fastapi) endpoints.

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

See this example for how to use `docker-compose` to set up authentication with
fastapi-oidc + keycloak.

### Standard usage

```python3
from typing import Optional

from fastapi import Depends
from fastapi import FastAPI
from fastapi import Security
from fastapi import status

from fastapi_oidc import Auth
from fastapi_oidc import KeycloakIDToken

auth = Auth(
    openid_connect_url="http://localhost:8080/auth/realms/my-realm/.well-known/openid-configuration",
    issuer="http://localhost:8080/auth/realms/my-realm",  # optional, verification only
    client_id="my-client",  # optional, verification only
    scopes=["email"],  # optional, verification only
    idtoken_model=KeycloakIDToken,  # optional, verification only
)

app = FastAPI(
    title="Example",
    version="dev",
    dependencies=[Depends(auth.implicit_scheme)],
    # multiple available schemes:
    # - oidc_scheme (displays all schemes supported by the auth server in docs)
    # - password_scheme
    # - implicit_scheme
    # - authcode_scheme
)

@app.get("/protected")
def protected(id_token: KeycloakIDToken = Security(auth.required)):
    return dict(message=f"You are {id_token.email}")
```

### Optional: Custom token validation

The IDToken class will accept any number of extra fields but you can also
validate fields in the token like this:

```python3
class MyAuthenticatedUser(IDToken):
    custom_field: str
    custom_default: float = 3.14

auth = Auth(
    ...,
    idtoken_model=MyAuthenticatedUser,
)
```
