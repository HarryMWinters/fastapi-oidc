from typing import Optional

import uvicorn
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Security
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from fastapi_oidc import Auth
from fastapi_oidc import KeycloakIDToken

auth = Auth(
    openid_connect_url="http://localhost:8080/auth/realms/my-realm/.well-known/openid-configuration",
    issuer="http://localhost:8080/auth/realms/my-realm",  # optional, verification only
    client_id="my-client",  # optional, verification only
    idtoken_model=KeycloakIDToken,  # optional
)

app = FastAPI(
    title="Example",
    version="dev",
    dependencies=[Depends(auth.implicit_scheme)],
)

# CORS errors instead of seeing internal exceptions
# https://stackoverflow.com/questions/63606055/why-do-i-get-cors-error-reason-cors-request-did-not-succeed
cors = CORSMiddleware(
    app=app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", status_code=status.HTTP_303_SEE_OTHER)
def redirect_to_docs():
    return RedirectResponse(url="/docs")


@app.get("/protected")
def protected(id_token: KeycloakIDToken = Security(auth.required)):
    return dict(message=f"You are {id_token.email}")


@app.get("/mixed")
def mixed(
    id_token: Optional[KeycloakIDToken] = Security(auth.optional),
):
    if id_token is None:
        return dict(message="You are not authenticated")
    else:
        return dict(message=f"You are {id_token.email}")


if __name__ == "__main__":
    uvicorn.run(
        "example.main:cors", host="0.0.0.0", port=8000, loop="asyncio", reload=True
    )
