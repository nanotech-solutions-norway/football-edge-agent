# Football Edge / Atlas — Deployment Safety Checklist

Generated: 21:27, 28.04.2026 Europe/Oslo

## Confirmed implementation gates

- SQL import completed.
- SQL safety state confirmed.
- PHP/PDO API health confirmed.
- Read-only endpoints validated.
- Old public credential-bearing health-check removed.
- Sensitive files inaccessible.
- Paper-trading route still blocked.
- Static frontend dashboard validated.

## Repository safety

`.gitignore` must include:

```gitignore
.env
.env.*
!.env.example
api_config.php
.htpasswd
.htpasswd*
*.htpasswd
football_edge_db_healthcheck.php
*_healthcheck.php
*_db_healthcheck.php
*.sql
*.sql.gz
*.dump
*.bak
*_dump.sql
*_backup.sql
*_export.sql
```

Do not commit:

- `.env`
- database credentials
- SQL dumps
- `api_config.php` if it contains local paths
- `.htpasswd`
- temporary diagnostics
- public PHP files containing credentials

## Live server safety

Run after each backend deployment:

```sql
SELECT 
    `enabled`,
    `provider_name`,
    `dry_run`,
    `legal_review_completed`,
    `compliance_review_completed`,
    `risk_review_completed`
FROM `auto_betting_control`
ORDER BY `control_id` DESC
LIMIT 1;
```

Required:

```text
enabled = 0
provider_name = none
dry_run = 1
legal_review_completed = 0
compliance_review_completed = 0
risk_review_completed = 0
```

## Frontend/API boundary

Correct:

```text
Frontend → Backend/API → Domeneshop MariaDB
```

Incorrect:

```text
Frontend → MySQL/MariaDB
```

## Step 3 approval boundary

Step 3 may prepare controlled paper-trading logging and metric endpoints only. It must not enable real-money execution, automation, provider execution, or browser-based database administration.
