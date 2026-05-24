
from fastapi import FastAPI, Depends
from fastapi_oidc import get_auth
from fastapi_oidc.types import IDToken

app = FastAPI()

# Configuración mínima para probar
authenticate_user = get_auth(
    client_id="YOUR_CLIENT_ID",
    base_authorization_server_uri="https://your-auth-server.com",
    issuer="https://your-auth-server.com",
    signature_cache_ttl=3600
)

@app.get("/protected")
def protected_route(token: IDToken = Depends(authenticate_user)):
    return {"sub": token.sub}
