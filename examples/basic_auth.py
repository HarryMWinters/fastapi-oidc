from fastapi import FastAPI, Depends
from fastapi_oidc import IDToken
from pydantic import BaseModel

app = FastAPI()

# Configuración básica de ejemplo
oidc_scheme = IDToken(
    issuer="https://tu-proveedor-oidc.com",
    client_id="tu-client-id",
)

class User(BaseModel):
    sub: str
    email: str

@app.get("/secure-data")
def secure_endpoint(user: User = Depends(oidc_scheme)):
    return {"message": f"Acceso concedido para el usuario: {user.email}"}

@app.get("/public")
def public_endpoint():
    return {"message": "Este es un endpoint público."}
