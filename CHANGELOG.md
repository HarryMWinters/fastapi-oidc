# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `Release` GitHub workflow that builds and publishes to PyPI via Trusted
  Publishing when a GitHub release is published (no PyPI token in the repo).
  It refuses to publish if the release tag does not match the package version.
- Dependabot now groups minor/patch updates into one weekly PR per ecosystem.
- Tests for JWKS fetching: HTTP errors propagate and results are cached by URI.

### Fixed
- The JWKS fetch in `discovery.py` now calls `raise_for_status()`, so an error
  response from the provider is raised instead of being parsed and cached as a
  key set.
- `OIDCConfig.signature_cache_ttl` is typed as `int` (it was `str`).

### Changed
- **Replaced `python-jose` with `PyJWT` for token verification.** `python-jose`
  pulls in `ecdsa`, `rsa` and `pyasn1`, which have carried unfixable or
  slow-to-fix security advisories (notably the Minerva timing attack in
  `python-ecdsa`, which upstream will not fix). PyJWT with the `crypto` extra
  needs only `cryptography`. The public `get_auth()` API and the
  `authenticate_user` dependency it returns are unchanged; invalid tokens still
  raise `HTTPException(401)`.
- Signing keys are now selected from the provider's JWKS by the token's `kid`
  header. A JWKS with a single key is still accepted for tokens without a `kid`.
- The minimum PyJWT version is 2.13.0, which includes fixes for algorithm
  allow-list bypass and key-confusion issues when verifying with JWK keys.
- Refreshed the dependency lock: cryptography 46.0.7 → 50.0.1 (clears four
  advisories), fastapi 0.137 → 0.141, starlette 1.3 → 1.6, pydantic 2.13.5,
  requests 2.34, cachetools 7.1.
- Dev tooling: pre-commit 4.x, pylint 4.x, uvicorn 0.52, `httpx2` replaces
  `httpx` for `TestClient` (Starlette 1.3+ deprecates `httpx` there).
- Pre-commit hook pins updated to match the Poetry-managed tool versions
  (black 26.5, isort 9, mypy 2.3, flake8 7.3, bandit 1.9, poetry 2.4). The
  `poetry-lock --check` hook became `poetry-check --lock` (Poetry 2 syntax).
- CI: the test workflow declares read-only `permissions`, cancels superseded
  runs of the same ref, and passes a token to `setup-task` so it stops hitting
  the anonymous GitHub API rate limit.
- `task publish` now expects a PyPI API token in `PYPI_TOKEN` instead of a
  username/password pair, which PyPI no longer accepts. `.env` is no longer
  tracked; copy `.env.example` instead.

### Removed
- `python-jose[cryptography]` runtime dependency and the `types-python-jose`
  dev dependency.

## [0.1.0] - 2026-06-14

### Added
- Support for multiple accepted issuers: `get_auth(issuer=...)` now accepts an
  iterable of issuer strings in addition to a single string
- `types-python-jose` stubs so mypy can type-check the `jose` imports
- Comprehensive modernization of development tooling and dependencies
- Coverage reporting in CI/CD pipeline with Codecov integration
- Dependabot configuration for automated dependency updates
- Enhanced pre-commit hooks (YAML/TOML/JSON validation, Poetry checks)
- pytest and coverage configuration in pyproject.toml
- Comprehensive docstrings for discovery module functions
- Module-level docstring and explicit `__all__` exports in `__init__.py`
- `__version__` attribute for programmatic version access
- Community health files: CHANGELOG.md, CONTRIBUTING.md, SECURITY.md
- GitHub issue templates (bug report, feature request, question)
- Pull request template with checklist
- Integration tests with FastAPI TestClient
- Edge case tests for error handling scenarios
- Examples directory with working applications for multiple OIDC providers

### Changed
- Added Python 3.13 and 3.14 to the CI test matrix (the dependency ecosystem now
  ships prebuilt wheels for these versions, so the temporary exclusion is removed)
- Bumped dependencies (consolidating outstanding Dependabot updates):
  - fastapi: 0.111.1 → 0.137.0 (pulls in starlette 1.x)
  - sphinx: 7.4.7 → 8.1.3
  - types-cachetools: 0.1.10 → 6.2.0
  - pyasn1: 0.6.2 → 0.6.3; h11: 0.14.0 → 0.16.0
  - codecov/codecov-action: v6 → v7
- Added `httpx` and `uvicorn[standard]` as explicit dev dependencies. Newer
  fastapi no longer installs them transitively, but `TestClient` requires `httpx`
  and the example apps (`examples/`) are run with `uvicorn`
- Updated Poetry configuration to modern format (`poetry.core`, `group.dev.dependencies`)
- Updated all dev dependencies to current versions:
  - black: 19.10b0 → 24.0.0
  - pytest: 6.0.1 → 8.0.0
  - mypy: 0.910 → 1.11.0
  - pylint: 2.6.0 → 3.0.0
  - sphinx: 3.3.1 → 7.0.0
  - pyjwt: 1.7.1 → 2.0.0
  - pre-commit: 2.13.0 → 3.0.0
- Updated GitHub Actions to latest versions (checkout@v4, setup-python@v5, setup-task@v2)
- Standardized type hints to use modern Python 3.10+ syntax (`dict`, `list` instead of `Dict`, `List`)
- Modernized test utilities to use `pathlib.Path` instead of `os.path`
- Enhanced README.md with comprehensive documentation sections

### Fixed
- **BREAKING**: `TokenSpecificationError` now correctly inherits from `Exception` instead of `BaseException`
- Typo in `get_auth` docstring: "beggining" → "beginning"
- Version mismatch between pyproject.toml and docs/conf.py (now both 0.0.11)

### Removed
- Obsolete UTF-8 encoding comment from auth.py (unnecessary in Python 3)
- `# noqa` comments from `__init__.py` (replaced with explicit `__all__`)

## [0.0.11] - 2024-XX-XX

### Added
- py.typed file to mark package as typed (PEP 561)

### Changed
- get_auth function signature uses bare `*` for keyword-only arguments

[Unreleased]: https://github.com/HarryMWinters/fastapi-oidc/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/HarryMWinters/fastapi-oidc/compare/v0.0.11...v0.1.0
[0.0.11]: https://github.com/HarryMWinters/fastapi-oidc/releases/tag/v0.0.11
