# Football Edge Agent — Domeneshop Domain and Hosting Assessment — 08:33, 27.04.2026 Europe/Oslo

## Decision

Use Domeneshop primarily for domain registration, DNS administration, and email/DNS management. Do not assume Domeneshop is sufficient for the Phase 2 FastAPI + PostgreSQL backend unless the specific purchased plan confirms long-running Python application support, PostgreSQL availability, scheduled jobs, HTTPS/TLS termination, environment variables, and process management.

## Current Suitability Assessment

Domeneshop publicly documents web-hosting features including PHP, CGI scripts, SSH, and MySQL/MariaDB, and it also offers DNS/API functionality. This is useful for domain and DNS operations, but it does not, by itself, confirm a production-grade long-running FastAPI + PostgreSQL runtime.

## Recommended Architecture

```text
Domeneshop domain/DNS
        ↓
api.your-domain.no CNAME/A record
        ↓
External backend host running FastAPI + PostgreSQL
```

## Cheapest Practical Backend Options

Preferred fallback order:

1. Render
2. Railway
3. Fly.io
4. Hetzner VPS
5. DigitalOcean Droplet/App Platform
6. Major cloud providers only if required later

## Minimum Backend Host Requirements

| Requirement | Mandatory |
|---|---|
| Python 3.11+ or Docker runtime | Yes |
| Long-running FastAPI process | Yes |
| PostgreSQL database | Yes |
| Scheduled jobs or cron-equivalent | Yes |
| HTTPS/TLS | Yes |
| Environment variables/secrets | Yes |
| Logs and restart policy | Yes |
| GitHub deployment integration | Preferred |

## DNS Setup Pattern

When backend provider is selected:

1. Create backend service with FastAPI app.
2. Create PostgreSQL database.
3. Configure environment variables from `.env.example`.
4. Set backend custom domain, for example `api.your-domain.no`.
5. In Domeneshop DNS, create the required `CNAME` or `A` record according to the backend host.
6. Enable HTTPS/TLS at the backend host.
7. Confirm `/health` and `/docs` load.

## Phase 2 Decision

Domeneshop remains suitable as registrar/DNS. A dedicated backend host should be used unless Domeneshop support explicitly confirms all FastAPI/PostgreSQL runtime requirements for the relevant hosting plan.
