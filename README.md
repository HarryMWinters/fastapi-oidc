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

```python3
from fastapi import Depends
from fastapi import FastAPI

from fastapi_oidc import IDToken
from fastapi_oidc import get_auth


app = FastAPI()

authenticate_user = get_auth(
    openid_connect_url="https://dev-123456.okta.com/.well-known/openid-configuration",
    issuer="dev-126594.okta.com",  # optional, verification only
    audience="https://yourapi.url.com/api",  # optional, verification only
    signature_cache_ttl=3600,  # optional
)

@app.get("/protected")
def protected(id_token: IDToken = Depends(authenticate_user)):
    return {"Hello": "World", "user_email": id_token.email}
```

### Optional: Custom token validation

The IDToken class will accept any number of extra fields but you can also
validate fields in the token like this:

```python3
class MyAuthenticatedUser(IDToken):
    custom_field: str
    custom_default: float = 3.14


app = FastAPI()

authenticate_user = get_auth(...)

@app.get("/protected")
def protected(user: MyAuthenticatedUser = Depends(authenticate_user)):
    return {"Hello": "World", "custom_field": user.custom_field}
```
