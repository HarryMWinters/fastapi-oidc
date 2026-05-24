import base64
import hashlib
import os

def generate_code_verifier() -> str:
    """Generates a high-entropy cryptographically random string."""
    return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')

def generate_code_challenge(verifier: str) -> str:
    """Generates the SHA256 code challenge for the given verifier."""
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
