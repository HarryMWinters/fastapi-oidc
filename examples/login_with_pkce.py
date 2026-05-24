from fastapi import FastAPI
from fastapi_oidc import generate_code_verifier, generate_code_challenge

app = FastAPI()

@app.get("/login")
def login():
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)
    # Aquí el desarrollador redireccionaría al usuario al servidor OIDC
    # enviando el 'challenge' en la URL
    return {"code_verifier": verifier, "code_challenge": challenge}
