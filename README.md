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

Verify and decrypt 3rd party OIDC ID tokens to protect your
[fastapi](https://github.com/tiangolo/fastapi) endpoints.

**Documentation:** [ReadTheDocs](https://fastapi-oidc.readthedocs.io/en/latest/)

**Source code:** [Github](https://github.com/HarryMWinters/fastapi-oidc)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Supported Providers](#supported-providers)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

## Features

- ✅ Verify JWT tokens from any OIDC-compliant provider
- ✅ Automatic discovery of provider configuration via `.well-known` endpoints
- ✅ Caching of signing keys and configuration for performance
- ✅ Type-safe token validation with Pydantic
- ✅ Support for custom token models with additional fields
- ✅ FastAPI-native dependency injection
- ✅ Python 3.10+ with modern type hints
- ✅ Comprehensive test coverage
- ✅ Production-ready and actively maintained

:warning: **Note:** For a simple roll-your-own example of checking OIDC tokens, see [this issue](https://github.com/HarryMWinters/fastapi-oidc/issues/1).

## Installation

```bash
pip install fastapi-oidc
```

Or with Poetry:

```bash
poetry add fastapi-oidc
```

## Quick Start

Here's a minimal example to get you started:

```python3
from fastapi import Depends, FastAPI
from fastapi_oidc import IDToken, get_auth

# Configure OIDC authentication
authenticate_user = get_auth(
    client_id="your-client-id",
    base_authorization_server_uri="https://your-auth-server.com",
    issuer="your-auth-server.com",
    signature_cache_ttl=3600,
)

app = FastAPI()

@app.get("/")
def public():
    return {"message": "This endpoint is public"}

@app.get("/protected")
def protected(token: IDToken = Depends(authenticate_user)):
    return {"message": f"Hello {token.email}!"}
```

## Supported Providers

fastapi-oidc works with any OIDC-compliant authentication provider:

- ✅ **Okta** - Enterprise identity management
- ✅ **Auth0** - Authentication and authorization platform
- ✅ **Google OAuth 2.0** - Google identity services
- ✅ **Microsoft Azure AD / Entra ID** - Microsoft identity platform
- ✅ **Keycloak** - Open-source identity and access management
- ✅ **AWS Cognito** - Amazon's user identity and data synchronization
- ✅ **Any OIDC-compliant provider** - Supports OpenID Connect Discovery

See the [examples directory](examples/) for provider-specific configurations (coming soon).

## Configuration

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `client_id` | `str` | OAuth client ID from your provider |
| `base_authorization_server_uri` | `str` | Base URL of your auth server (e.g., `https://dev-123456.okta.com`) |
| `issuer` | `str` | Token issuer identifier (usually matches base URI domain) |
| `signature_cache_ttl` | `int` | Cache duration for signing keys in seconds (recommended: 3600) |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audience` | `str` | `client_id` | Token audience claim to validate |
| `token_type` | `Type[IDToken]` | `IDToken` | Custom token model (must inherit from `IDToken`) |

### Configuration Examples

**Basic Configuration:**
```python3
authenticate_user = get_auth(
    client_id="0oa1e3pv9opbyq2Gm4x7",
    base_authorization_server_uri="https://dev-126594.okta.com",
    issuer="dev-126594.okta.com",
    signature_cache_ttl=3600,
)
```

**With Custom Audience:**
```python3
authenticate_user = get_auth(
    client_id="your-client-id",
    audience="https://yourapi.url.com/api",
    base_authorization_server_uri="https://auth.example.com",
    issuer="auth.example.com",
    signature_cache_ttl=3600,
)
```

**Using Environment Variables (Recommended):**
```python3
import os

authenticate_user = get_auth(
    client_id=os.getenv("OIDC_CLIENT_ID"),
    audience=os.getenv("OIDC_AUDIENCE"),
    base_authorization_server_uri=os.getenv("OIDC_BASE_URI"),
    issuer=os.getenv("OIDC_ISSUER"),
    signature_cache_ttl=int(os.getenv("OIDC_CACHE_TTL", "3600")),
)
```

### Security Recommendations

- ✅ Always use HTTPS in production
- ✅ Store credentials in environment variables, not in code
- ✅ Set cache TTL between 3600-7200 seconds for optimal balance
- ✅ Validate the issuer matches your authentication server
- ✅ Use short token expiration times (5-15 minutes recommended)
- ✅ Implement application-level rate limiting
- ✅ Monitor authentication logs for suspicious activity

See [SECURITY.md](SECURITY.md) for comprehensive security guidelines.

## Usage Examples

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

## Troubleshooting

### Common Issues

#### "Unauthorized: Signature verification failed"

**Causes:**
- Incorrect `client_id` or `issuer` configuration
- Token is expired
- Authentication server is unreachable
- Token signed with different key than expected

**Solutions:**
```python3
# Verify your configuration
print(f"Client ID: {client_id}")
print(f"Issuer: {issuer}")
print(f"Base URI: {base_authorization_server_uri}")

# Check token expiration
import jwt
decoded = jwt.decode(token, options={"verify_signature": False})
print(f"Token expires at: {decoded['exp']}")

# Verify network connectivity
import requests
response = requests.get(f"{base_authorization_server_uri}/.well-known/openid-configuration")
print(f"OIDC Discovery Status: {response.status_code}")
```

#### "Unauthorized: Invalid audience"

**Cause:** The token's `aud` claim doesn't match your configuration.

**Solution:**
```python3
# Set the audience parameter explicitly
authenticate_user = get_auth(
    client_id="your-client-id",
    audience="your-expected-audience",  # Must match token's 'aud' claim
    base_authorization_server_uri="https://auth.example.com",
    issuer="auth.example.com",
    signature_cache_ttl=3600,
)

# Or check what audience your token contains
import jwt
decoded = jwt.decode(token, options={"verify_signature": False})
print(f"Token audience: {decoded['aud']}")
```

#### "Connection timeout"

**Causes:**
- Network connectivity issues
- Firewall blocking outbound HTTPS
- Incorrect base URI

**Solutions:**
```bash
# Test connectivity
curl https://your-auth-server.com/.well-known/openid-configuration

# Check firewall rules allow HTTPS to your auth server
# Verify the base URI is correct (no trailing slash)
```

#### "Module not found" or Import Errors

**Solution:**
```bash
# Ensure fastapi-oidc is installed
pip install fastapi-oidc

# Verify installation
python -c "import fastapi_oidc; print(fastapi_oidc.__version__)"

# Reinstall if needed
pip install --force-reinstall fastapi-oidc
```

### Debugging Tips

Enable detailed logging:
```python3
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("fastapi_oidc")
logger.setLevel(logging.DEBUG)
```

### Getting Help

- 📖 Check the [documentation](https://fastapi-oidc.readthedocs.io)
- 🔍 Search [existing issues](https://github.com/HarryMWinters/fastapi-oidc/issues)
- 💬 Open a [new issue](https://github.com/HarryMWinters/fastapi-oidc/issues/new/choose)
- 📧 See [SECURITY.md](SECURITY.md) for security-related concerns

## Contributing

Contributions are welcome! We appreciate bug fixes, documentation improvements, and new features.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`poetry run pytest`)
5. Run code quality checks (`poetry run pre-commit run --all-files`)
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/HarryMWinters/fastapi-oidc.git
cd fastapi-oidc

# Install dependencies
poetry install

# Set up pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=fastapi_oidc
```

## Security

Security is a top priority. Please report security vulnerabilities privately to harrymcwinters@gmail.com.

See [SECURITY.md](SECURITY.md) for:
- Security best practices
- Supported versions
- Vulnerability reporting process
- Known security considerations

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Token validation via [python-jose](https://github.com/mpdavis/python-jose)
- Type validation with [Pydantic](https://pydantic-docs.helpmanual.io/)

---

**Made with ❤️ by Harry M. Winters**
