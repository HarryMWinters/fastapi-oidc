# Contributing to fastapi-oidc

Thank you for your interest in contributing to fastapi-oidc! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Poetry package manager
- Git

### Setup Steps

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fastapi-oidc.git
   cd fastapi-oidc
   ```

2. **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**
   ```bash
   poetry install
   ```

4. **Set up pre-commit hooks**
   ```bash
   poetry run pre-commit install
   ```

## Running Tests

### Run all tests
```bash
poetry run pytest
```

### Run with coverage
```bash
poetry run pytest --cov=fastapi_oidc --cov-report=term-missing
```

### Run specific test file
```bash
poetry run pytest tests/test_auth.py
```

### Run specific test function
```bash
poetry run pytest tests/test_auth.py::test_authenticate_user
```

## Code Quality

We use several tools to maintain code quality. These are automatically run by pre-commit hooks:

### Tools

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Static type checking
- **flake8**: Linting
- **bandit**: Security checks

### Run all quality checks manually
```bash
poetry run pre-commit run --all-files
```

### Run individual tools
```bash
# Format code
poetry run black fastapi_oidc tests

# Check types
poetry run mypy fastapi_oidc

# Lint code
poetry run flake8 fastapi_oidc tests

# Security scan
poetry run bandit -r fastapi_oidc
```

## Pull Request Process

1. **Create a feature branch** from `master`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, concise code
   - Add tests for new functionality
   - Update documentation as needed
   - Follow existing code style and patterns

3. **Ensure all tests pass**
   ```bash
   poetry run pytest
   ```

4. **Ensure pre-commit checks pass**
   ```bash
   poetry run pre-commit run --all-files
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Submit a pull request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill out the pull request template
   - Submit for review

## Coding Standards

### General Guidelines

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings for public APIs (Google style)
- Maintain 100% backward compatibility for public APIs
- Keep functions focused and single-purpose
- Prefer clarity over cleverness

### Type Hints

Use modern Python 3.10+ type hints:

```python
# Good
def process_data(items: list[str]) -> dict[str, Any]:
    pass

# Avoid (old style)
from typing import List, Dict
def process_data(items: List[str]) -> Dict[str, Any]:
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def authenticate_user(token: str, issuer: str) -> IDToken:
    """Validate and parse an OIDC ID token.

    Args:
        token: Base64-encoded JWT token string.
        issuer: Expected token issuer.

    Returns:
        Validated and parsed ID token.

    Raises:
        HTTPException: If token validation fails.
    """
    pass
```

### Testing

- Write tests for all new features
- Write tests for bug fixes
- Aim for 80%+ code coverage
- Use descriptive test names
- Test edge cases and error conditions

```python
def test_authenticate_user_with_valid_token():
    """Test that valid tokens are correctly authenticated."""
    pass

def test_authenticate_user_rejects_expired_token():
    """Test that expired tokens are rejected with 401 error."""
    pass
```

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format
```
<type>: <description>

[optional body]

[optional footer]
```

### Types

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions or modifications
- `refactor:` Code refactoring without functional changes
- `style:` Code style changes (formatting, etc.)
- `chore:` Build process or tooling changes
- `perf:` Performance improvements

### Examples

```bash
feat: add support for Azure AD tokens

fix: handle expired tokens correctly

docs: update README with Auth0 example

test: add integration tests for token validation
```

## What to Contribute

### Areas We Welcome

- Bug fixes
- Documentation improvements
- Additional OIDC provider examples
- Test coverage improvements
- Performance optimizations
- Type hint improvements

### Before Starting Large Changes

For significant changes:
1. Open an issue first to discuss the approach
2. Get feedback from maintainers
3. Ensure the change aligns with project goals

## Questions?

- Check existing [GitHub Issues](https://github.com/HarryMWinters/fastapi-oidc/issues)
- Review the [documentation](https://fastapi-oidc.readthedocs.io)
- Open a new issue with the `question` label

## Code of Conduct

Be respectful, inclusive, and professional in all interactions. We're all here to build something great together.

## License

By contributing to fastapi-oidc, you agree that your contributions will be licensed under the MIT License.
