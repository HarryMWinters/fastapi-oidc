# Okta OIDC Example

This example demonstrates integrating fastapi-oidc with Okta.

## Prerequisites

1. An Okta account (free at [developer.okta.com](https://developer.okta.com))
2. Python 3.10+
3. Poetry (or pip)

## Setup

### 1. Configure Okta

1. **Log in to your Okta admin console** at `https://YOUR-DOMAIN.okta.com/admin`

2. **Create a new app integration:**
   - Go to **Applications** → **Create App Integration**
   - Choose **OIDC - OpenID Connect**
   - Choose **Web Application** or **API Services** (for machine-to-machine)

3. **Configure the application:**
   - **App name**: "FastAPI OIDC Example"
   - **Grant type**:
     - ✅ Client Credentials (for machine-to-machine)
     - ✅ Authorization Code (for user authentication)
   - **Sign-in redirect URIs**: `http://localhost:8000/auth/callback` (if using authorization code flow)
   - **Sign-out redirect URIs**: `http://localhost:8000`
   - **Controlled access**: Choose appropriate access level

4. **Save and note your credentials:**
   - **Client ID**: Found on the application page
   - **Client Secret**: Found on the application page (keep this secret!)
   - **Okta Domain**: Your Okta domain (e.g., `dev-123456.okta.com`)

### 2. Configure Environment Variables

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your Okta credentials:**
   ```bash
   OKTA_DOMAIN=dev-123456.okta.com
   OKTA_CLIENT_ID=0oa1e3pv9opbyq2Gm4x7
   OKTA_AUDIENCE=api://default  # or your custom audience
   OKTA_CACHE_TTL=3600
   ```

   **Finding your Okta domain:**
   - It's in the top-right of your Okta admin console
   - Format: `dev-XXXXXX.okta.com` or `YOURCOMPANY.okta.com`

   **About audience:**
   - For API applications, use `api://default` or your custom authorization server audience
   - If not specified, defaults to `client_id`

### 3. Install Dependencies

From the project root:
```bash
poetry install
```

### 4. Run the Application

```bash
cd examples/okta
poetry run uvicorn main:app --reload
```

The application will be available at `http://localhost:8000`.

## Testing

### Get a Token from Okta

**Option 1: Using Okta API (Client Credentials Flow)**

```bash
curl -X POST "https://${OKTA_DOMAIN}/oauth2/default/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=${OKTA_CLIENT_ID}" \
  -d "client_secret=${OKTA_CLIENT_SECRET}" \
  -d "scope=openid profile email"
```

**Option 2: Using Okta Dashboard**

1. Go to **Security** → **API** → **Tokens**
2. Create a new token
3. Copy the token value

**Option 3: Using Okta's OAuth 2.0 Playground**

1. Visit your Okta org URL
2. Navigate to the OAuth 2.0 playground
3. Follow the authorization flow
4. Copy the access token

### Test the Endpoints

**Public endpoint (no authentication):**
```bash
curl http://localhost:8000/
```

**Protected endpoint (requires authentication):**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/protected
```

**User info endpoint:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/user-info
```

**Interactive API documentation:**
Visit `http://localhost:8000/docs` in your browser.

## API Endpoints

- `GET /` - Public endpoint, returns welcome message
- `GET /protected` - Protected endpoint, returns user email and subject
- `GET /user-info` - Protected endpoint, returns all token claims
- `GET /docs` - Interactive API documentation (FastAPI automatic docs)
- `GET /redoc` - ReDoc API documentation

## Troubleshooting

### "Unauthorized: Signature verification failed"

**Causes:**
- Incorrect Okta domain
- Token expired
- Client ID mismatch

**Solutions:**
```bash
# Verify your configuration
echo $OKTA_DOMAIN
echo $OKTA_CLIENT_ID

# Check if Okta discovery endpoint is accessible
curl https://${OKTA_DOMAIN}/.well-known/openid-configuration

# Decode your token to check claims (without verification)
# Visit https://jwt.io and paste your token
```

### "Unauthorized: Invalid audience"

**Cause:** The token's `aud` claim doesn't match your configuration.

**Solution:**
```bash
# Set the audience explicitly in .env
OKTA_AUDIENCE=your_actual_audience

# Check what audience your token has
# Decode the token at https://jwt.io
```

### "Connection timeout"

**Causes:**
- Network connectivity issues
- Firewall blocking HTTPS to Okta
- Incorrect domain format

**Solutions:**
```bash
# Test connectivity
curl https://${OKTA_DOMAIN}/.well-known/openid-configuration

# Ensure domain doesn't include https://
# Correct: dev-123456.okta.com
# Incorrect: https://dev-123456.okta.com
```

### Token Expired

Okta tokens typically expire after 1 hour. Get a new token using the methods above.

## Okta-Specific Configuration

### Authorization Servers

Okta supports multiple authorization servers:

- **Default**: Use `https://${OKTA_DOMAIN}/oauth2/default`
- **Custom**: Use `https://${OKTA_DOMAIN}/oauth2/{authServerId}`

Update `OKTA_BASE_URI` in your `.env` if using a custom authorization server.

### Scopes

Common Okta scopes:
- `openid` - Required for OIDC
- `profile` - User profile information
- `email` - User email
- `offline_access` - Refresh tokens
- `groups` - User group membership

### Custom Claims

To add custom claims to your tokens:
1. Go to **Security** → **API** → **Authorization Servers**
2. Select your authorization server
3. Go to **Claims** tab
4. Add custom claims

Then use a custom token model:
```python
from fastapi_oidc import IDToken

class CustomOktaToken(IDToken):
    groups: list[str] = []
    department: str = ""

authenticate_user = get_auth(**OIDC_CONFIG, token_type=CustomOktaToken)
```

## Production Considerations

### Security

- ✅ Use HTTPS in production
- ✅ Store credentials in secure secret management (AWS Secrets Manager, Azure Key Vault, etc.)
- ✅ Rotate client secrets regularly
- ✅ Use appropriate token expiration times
- ✅ Implement rate limiting
- ✅ Monitor authentication logs in Okta

### Performance

- Set appropriate `OKTA_CACHE_TTL` (3600 seconds recommended)
- Consider using Okta's rate limiting best practices
- Cache frequently accessed user data at application level

### High Availability

- Okta has built-in high availability
- Consider fallback mechanisms for network issues
- Implement retry logic with exponential backoff

## Additional Resources

- [Okta Developer Documentation](https://developer.okta.com/docs/)
- [Okta API Reference](https://developer.okta.com/docs/reference/)
- [Okta OIDC & OAuth 2.0 Guide](https://developer.okta.com/docs/concepts/oauth-openid/)
- [fastapi-oidc Documentation](https://fastapi-oidc.readthedocs.io)

## Support

For Okta-specific issues:
- [Okta Developer Forums](https://devforum.okta.com/)
- [Okta Support](https://support.okta.com/)

For fastapi-oidc issues:
- [GitHub Issues](https://github.com/HarryMWinters/fastapi-oidc/issues)
