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

:warning: **See [this issue](https://github.com/HarryMWinters/fastapi-oidc/issues/1) for
simple role-your-own example of checking OIDC tokens.**

Verify and decrypt 3rd party OIDC ID tokens to protect your
[fastapi](https://github.com/tiangolo/fastapi) endpoints.

**Documentation:** [ReadTheDocs](https://fastapi-oidc.readthedocs.io/en/latest/)

**Source code:** [Github](https://github.com/HarryMWinters/fastapi-oidc)

## Installation

`pip install fastapi-oidc`

## Usage

### Verify ID Tokens Issued by Third Party

This is great if you just want to use something like Okta or google to handle
your auth. All you need to do is verify the token and then you can extract user ID info
from it.

```python3
from fastapi import Depends
from fastapi import FastAPI

# Set up our OIDC
from fastapi_oidc import IDToken
from fastapi_oidc import get_auth

OIDC_config = {
    "client_id": "0oa1e3pv9opbyq2Gm4x7",
    # Audience can be omitted in which case the aud value defaults to client_id
    "audience": "https://yourapi.url.com/api",
    "base_authorization_server_uri": "https://dev-126594.okta.com",
    "issuer": "dev-126594.okta.com",
    "signature_cache_ttl": 3600,
}

authenticate_user: Callable = get_auth(**OIDC_config)

app = FastAPI()

@app.get("/protected")
def protected(id_token: IDToken = Depends(authenticate_user)):
    return {"Hello": "World", "user_email": id_token.email}
```

#### Using your own tokens

The IDToken class will accept any number of extra field but if you want to craft your
own token class and validation that's accounted for too.

```python3
class CustomIDToken(fastapi_oidc.IDToken):
    custom_field: str
    custom_default: float = 3.14


authenticate_user: Callable = get_auth(**OIDC_config, token_type=CustomIDToken)

app = FastAPI()


@app.get("/protected")
def protected(id_token: CustomIDToken = Depends(authenticate_user)):
    return {"Hello": "World", "user_email": id_token.custom_default}
```
