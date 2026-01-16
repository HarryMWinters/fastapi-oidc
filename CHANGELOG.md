# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- Added Python 3.13 to CI test matrix
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

[Unreleased]: https://github.com/HarryMWinters/fastapi-oidc/compare/v0.0.11...HEAD
[0.0.11]: https://github.com/HarryMWinters/fastapi-oidc/releases/tag/v0.0.11
