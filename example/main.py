from typing import Optional

import uvicorn
from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from fastapi_oidc import Auth
from fastapi_oidc import KeycloakIDToken

auth = Auth(
    openid_connect_url="http://localhost:8080/auth/realms/my-realm/.well-known/openid-configuration",
    issuer="http://localhost:8080/auth/realms/my-realm",  # optional, verification only
    audience="my-audience",  # optional, verification only
    auto_error=False,  # optional
    idtoken_model=KeycloakIDToken,  # optional
)

app = FastAPI(title="Example", version="dev")

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


@app.get("/protected", dependencies=[Depends(auth.oidc_scheme)])
def protected(id_token: Optional[KeycloakIDToken] = Depends(auth.authenticate_user)):
    if id_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return dict(message=f"You are {id_token.email}")


@app.get("/mixed", dependencies=[Depends(auth.oidc_scheme)])
def mixed(id_token: Optional[KeycloakIDToken] = Depends(auth.authenticate_user)):
    if id_token is None:
        return dict(message="You are not authenticated")
    else:
        return dict(message=f"You are {id_token.email}")


if __name__ == "__main__":
    uvicorn.run(
        "example.main:cors", host="0.0.0.0", port=8000, loop="asyncio", reload=True
    )
