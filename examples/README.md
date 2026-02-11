# FastAPI OIDC Examples

This directory contains working examples for various OIDC providers.

## Available Examples

- [Okta](okta/) - Integration with Okta OIDC ✅ Complete
- [Auth0](auth0/) - Integration with Auth0 (Coming soon)
- [Google OAuth](google/) - Integration with Google OAuth 2.0 (Coming soon)
- [Azure AD](azure_ad/) - Integration with Microsoft Azure AD / Entra ID (Coming soon)
- [Custom Token](custom_token/) - Using custom token models with additional fields (Coming soon)

## Running Examples

Each example directory contains:
- `main.py` - Working FastAPI application
- `README.md` - Setup instructions and configuration details
- `.env.example` - Example environment variables

### General Steps

1. **Navigate to the example directory**
   ```bash
   cd examples/okta  # or your chosen provider
   ```

2. **Copy `.env.example` to `.env` and fill in your credentials**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Install dependencies** (from project root)
   ```bash
   cd ../..  # Back to project root
   poetry install
   ```

4. **Run the application**
   ```bash
   cd examples/okta
   poetry run uvicorn main:app --reload
   ```

5. **Visit** `http://localhost:8000/docs` for the interactive API documentation

## General Setup for All Providers

### 1. Register Your Application

With your OIDC provider:
- Create a new application
- Configure redirect URIs (usually `http://localhost:8000/auth/callback` for local development)
- Get your credentials: `client_id`, `client_secret` (if applicable), and `issuer`

### 2. Configure Environment Variables

Each example uses environment variables for configuration. Never commit `.env` files with real credentials.

### 3. Test the Endpoints

All examples include:
- `/` - Public endpoint (no authentication required)
- `/protected` - Protected endpoint (requires valid OIDC token)
- `/user-info` - Returns all token claims
- `/docs` - Interactive API documentation (FastAPI automatic docs)

## Getting Tokens for Testing

### Option 1: Using Provider's Test Tools

Most providers offer testing tools:
- **Okta**: Okta Dashboard → Applications → OAuth 2.0 Playground
- **Auth0**: Auth0 Dashboard → Applications → Quick Start → Test
- **Google**: Google OAuth 2.0 Playground
- **Azure AD**: Microsoft Graph Explorer

### Option 2: Using curl

```bash
# Example for client credentials flow (adjust for your provider)
curl -X POST "https://your-auth-server.com/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "scope=openid profile email"
```

### Option 3: Using the Interactive Docs

1. Run the example application
2. Go to `http://localhost:8000/docs`
3. Click "Authorize" button
4. Enter your token
5. Test the protected endpoints

## Testing Protected Endpoints

Once you have a token:

```bash
# Test protected endpoint
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/protected

# Test user info endpoint
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/user-info
```

## Common Configuration Parameters

All examples use these common parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `OIDC_CLIENT_ID` | Your application's client ID | `0oa1e3pv9opbyq2Gm4x7` |
| `OIDC_AUDIENCE` | Token audience (often equals client_id) | `https://api.example.com` |
| `OIDC_BASE_URI` | Base URL of your auth server | `https://dev-123456.okta.com` |
| `OIDC_ISSUER` | Token issuer identifier | `dev-123456.okta.com` |
| `OIDC_CACHE_TTL` | Cache duration for signing keys (seconds) | `3600` |

## Security Notes

⚠️ **Important Security Practices:**

- Never commit `.env` files or credentials to version control
- Always use HTTPS in production
- Use environment variables for all sensitive configuration
- Set appropriate cache TTL values (3600-7200 seconds recommended)
- Validate the issuer matches your authentication server
- Monitor authentication logs for suspicious activity

## Troubleshooting

### "Unauthorized: Signature verification failed"

Check:
- Your `client_id` and `issuer` are correct
- The token hasn't expired
- Network connectivity to your auth server

### "Unauthorized: Invalid audience"

The token's `aud` claim doesn't match your configuration. Set the `OIDC_AUDIENCE` environment variable to match your token's audience.

### "Connection timeout"

Check:
- Network connectivity to your auth server
- Firewall rules allow outbound HTTPS
- The base URI is correct (no trailing slash)

## Contributing Examples

We welcome examples for additional OIDC providers! To contribute:

1. Create a new directory under `examples/`
2. Include `main.py`, `README.md`, and `.env.example`
3. Follow the pattern from existing examples
4. Test your example thoroughly
5. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

## Additional Resources

- [fastapi-oidc Documentation](https://fastapi-oidc.readthedocs.io)
- [OpenID Connect Specification](https://openid.net/specs/openid-connect-core-1_0.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
