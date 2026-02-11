# Security Policy

## Supported Versions

We actively support the following versions of fastapi-oidc with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.0.x   | :white_check_mark: |
| < 0.0.x | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in fastapi-oidc, please report it privately. **Do not** open a public GitHub issue for security vulnerabilities.

### How to Report

1. **Email the maintainer**: harrymcwinters@gmail.com
2. **Include the following information**:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact and severity
   - Suggested fix (if any)
   - Your contact information (optional)

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Updates**: Regular status updates as we investigate and address the issue
- **Resolution Timeline**: We aim to address critical vulnerabilities within 7 days
- **Credit**: Recognition in the security advisory (if you wish)

## Security Best Practices

When using fastapi-oidc in production, follow these security best practices:

### 1. Always Use HTTPS

```python
# Good - HTTPS
base_authorization_server_uri="https://auth.example.com"

# Bad - HTTP (insecure)
base_authorization_server_uri="http://auth.example.com"  # DON'T DO THIS
```

HTTPS prevents token interception and man-in-the-middle attacks.

### 2. Validate the Issuer

Always specify and validate the expected token issuer:

```python
authenticate_user = get_auth(
    client_id="your-client-id",
    issuer="auth.example.com",  # Must match token's 'iss' claim
    base_authorization_server_uri="https://auth.example.com",
    signature_cache_ttl=3600,
)
```

This prevents token substitution attacks from malicious issuers.

### 3. Use Appropriate Cache TTL

Set signature cache TTL to balance security and performance:

```python
# Recommended: 1 hour (3600 seconds)
signature_cache_ttl=3600

# Acceptable: 30 minutes to 2 hours
signature_cache_ttl=1800  # 30 minutes
signature_cache_ttl=7200  # 2 hours

# Not recommended: Too long (security risk) or too short (performance impact)
signature_cache_ttl=86400  # 24 hours - keys may rotate before cache expires
signature_cache_ttl=60     # 1 minute - excessive OIDC server requests
```

### 4. Keep Dependencies Updated

Use Dependabot (now configured) to stay current with security patches:

```bash
# Regularly update dependencies
poetry update

# Check for security vulnerabilities
poetry run bandit -r fastapi_oidc
```

### 5. Secure Credential Management

Never hard-code credentials or secrets:

```python
# Bad - Hard-coded secrets
client_id = "abc123"  # DON'T DO THIS

# Good - Environment variables
import os
client_id = os.getenv("OIDC_CLIENT_ID")
```

### 6. Monitor Authentication Logs

Implement logging and monitoring for authentication events:

```python
import logging

logger = logging.getLogger(__name__)

@app.get("/protected")
def protected(token: IDToken = Depends(authenticate_user)):
    logger.info(f"User {token.sub} accessed protected endpoint")
    return {"message": "Success"}
```

### 7. Rotate Signing Keys Regularly

Work with your authentication provider to:
- Rotate signing keys regularly (recommended: every 90 days)
- Use strong key sizes (RSA 2048-bit minimum, 4096-bit preferred)
- Implement key rollover procedures

## Known Security Considerations

### Token Validation

This library validates:
- ✅ JWT signature using provider's public keys
- ✅ Token expiration (`exp` claim)
- ✅ Token issuer (`iss` claim)
- ✅ Token audience (`aud` claim)

This library does **not** validate:
- ❌ Token revocation (use short expiration times)
- ❌ User session state (implement separately if needed)
- ❌ Rate limiting (implement in your application)

### Token Revocation

fastapi-oidc does not support token revocation checking. To mitigate this:
- Use short token expiration times (5-15 minutes recommended)
- Implement refresh token rotation
- Add application-level session management if needed

### Caching Behavior

- Signing keys are cached for the configured TTL
- OIDC configuration is cached for the same TTL
- Cache is per-process (not shared across instances)
- Cache does not persist across restarts

### Network Requests

The library makes network requests to:
- OIDC discovery endpoint (`/.well-known/openid-configuration`)
- JWKS endpoint (for public signing keys)

These requests:
- Have a 15-second timeout
- Are made during token validation
- Are cached according to `signature_cache_ttl`
- May fail if network connectivity is lost

## Security Audit History

No formal security audits have been conducted yet. We welcome community security reviews.

## Cryptographic Dependencies

This library relies on:
- `python-jose[cryptography]` - JWT handling and verification
- `cryptography` - Cryptographic primitives

These are well-established, actively maintained libraries with strong security track records.

## Responsible Disclosure

We follow responsible disclosure practices:
1. Security issues are handled privately
2. Fixes are developed and tested
3. Releases are coordinated with reporters
4. Public disclosure after fixes are available
5. Credit given to reporters (if desired)

## Contact

For security-related questions or concerns:
- **Email**: harrymcwinters@gmail.com
- **GitHub Issues**: For non-sensitive security discussions only

Thank you for helping keep fastapi-oidc secure!
