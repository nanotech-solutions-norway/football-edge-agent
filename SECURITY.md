# Security Policy

## Project Scope

This repository supports the Atlas / Football Edge project, including frontend, API, deployment, documentation, and validation components.

## Reporting Security Issues

Do not open public GitHub issues for vulnerabilities, exposed credentials, endpoint weaknesses, database access issues, or deployment security concerns.

Report security concerns directly to the repository owner.

## Sensitive Information

The following must never be committed:

- Database credentials
- API keys
- Access tokens
- `.env` files
- Private PHP configuration files
- Domeneshop or MariaDB credentials
- SQL dumps or database exports
- Server logs
- Paper-trading credentials
- Betting execution credentials
- Private diagnostics
- `.htpasswd` files
- Raw healthcheck files exposing server configuration

## Public Repository Rule

If this repository remains public, it must only contain public-safe static files, documentation, templates, and non-sensitive code.

Operational credentials and private backend configuration must be stored outside the repository or in approved secret storage.

## GitHub Pages Rule

GitHub Pages must be treated as public. No secrets, admin controls, database credentials, or private diagnostics may be deployed through GitHub Pages.

## Vulnerability Handling

When a potential vulnerability is found:

1. Do not disclose it publicly.
2. Remove or disable the affected public endpoint if necessary.
3. Rotate any exposed secret immediately.
4. Patch the issue in a private branch.
5. Validate the fix before deployment.
6. Document the issue internally.

## Supported Security Baseline

The project should maintain:

- `.gitignore` protection for credentials, logs, dumps, and local files
- Secret scanning
- Push protection where available
- Code scanning where available
- Minimal GitHub Actions permissions
- Protected `main` branch against deletion and force-push
