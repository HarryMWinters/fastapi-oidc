---
name: Bug Report
about: Report a bug or unexpected behavior
title: '[BUG] '
labels: bug
assignees: ''
---

## Description

A clear and concise description of the bug.

## Steps to Reproduce

1. Configure with '...'
2. Call endpoint '...'
3. See error

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Environment

- **fastapi-oidc version**: [e.g., 0.0.11]
- **Python version**: [e.g., 3.11.5]
- **FastAPI version**: [e.g., 0.104.0]
- **Authentication provider**: [e.g., Okta, Auth0, Google]
- **Operating system**: [e.g., Ubuntu 22.04, macOS 14.0, Windows 11]

## Code Sample

```python
# Minimal code to reproduce the issue
from fastapi_oidc import get_auth

authenticate_user = get_auth(
    # your configuration
)
```

## Error Output

```
Paste any error messages or stack traces here
```

## Additional Context

Any other relevant information, screenshots, or logs that might help diagnose the issue.

## Checklist

- [ ] I have searched existing issues to ensure this is not a duplicate
- [ ] I have included all relevant information above
- [ ] I have provided a minimal code example to reproduce the issue
- [ ] I have checked the [troubleshooting guide](https://github.com/HarryMWinters/fastapi-oidc#troubleshooting)
