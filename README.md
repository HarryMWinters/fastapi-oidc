# WIP | COMING SOON

# FastAPI OIDC

![Tests](https://github.com/HarryMWinters/fastapi-oidc/workflows/Test/badge.svg)

Verify and decrypt 3rd party OIDC ID tokens to protect your [fastapi](https://github.com/tiangolo/fastapi) endpoints.

ReadTheDocs:

Source code: [github](https://github.com/HarryMWinters/fastapi-oidc)

## Table of Contents

- Quick start
- Troubleshooting
- ReadTheDocs
- Example

### Quick Start

`pip install fastapi-oidc`

#### Verify ID Tokens Issued by Third Party

This is great if you just want to use something like Okta or google to handle
your auth. All you need to do is verify the token and then you can extract user
ID info from it.

```python3
from fastapi import Depends
from fastapi import FastAPI

# Set up our OIDC
from fastapi_oidc import IDToken
from fastapi_oidc import get_auth

OIDC_config = {
    "client_id": "",
    "base_authorization_server_uri": "",
    "issuer": "",
    "signature_cache_ttl": int,
}

authenticate_user: Callable = get_auth(**OIDC_config)

app = FastAPI()

@app.get("/protected")
def protected(id_token: IDToken = Depends(authenticate_user)):
    return {"Hello": "World", "user_email": id_token.email}
```
