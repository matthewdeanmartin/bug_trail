# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

- Added for new features.
- Changed for changes in existing functionality.
- Deprecated for soon-to-be removed features.
- Removed for now removed features.
- Fixed for any bug fixes.
- Security in case of vulnerabilities.

## [Unreleased]

### Changed

- Use plain Uvicorn on Python >=3.15 so the HTTP/SSE server can run without missing native accelerator wheels.
- Require the corrected bug-trail-core >=3.2.0 companion; prevent incompatible Pydantic 1 downgrades on Python >=3.15.

- Migrate direct HTTP clients/tests/dependencies to HTTPX2; current releases use OS trust-store HTTPS verification.

## [3.0.1] - 2025-99-99

### Added

- 
