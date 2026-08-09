# Football Edge / Atlas — Move status page to `/admin/football-edge-status.html`

Generated: 21:27, 28.04.2026 Europe/Oslo

## Objective

Move the validated read-only backend status page from the temporary root-level location to:

```text
https://www.atlas-ai.no/admin/football-edge-status.html
```

The page remains operational-only, noindex, and read-only. It must not contain credentials, SQL, database internals, write controls, execution controls, or private server paths.

## Correct Domeneshop folder mapping

Domeneshop public web root:

```text
www/
```

Target folder:

```text
www/admin/
```

Final server structure:

```text
www/
├── api/
│   └── index.php
└── admin/
    ├── football-edge-status.html
    └── assets/
        ├── css/
        │   └── football-edge-status.css
        └── js/
            ├── football-edge-api-client.js
            └── football-edge-status-widget.js
```

## Upload procedure

1. Connect to Domeneshop by SFTP.
2. Open the public web root folder `www`.
3. Create a new folder named `admin` if it does not exist.
4. Upload these files into `www/admin`:

```text
admin/football-edge-status.html
admin/assets/css/football-edge-status.css
admin/assets/js/football-edge-api-client.js
admin/assets/js/football-edge-status-widget.js
```

5. Open:

```text
https://www.atlas-ai.no/admin/football-edge-status.html
```

6. Confirm:

```text
API status: Online
Safety lock: Locked dry-run
Competition count: 8
Model version: football-edge-v0.3.0
Real-money execution status: disabled_locked_dry_run
```

7. After validation, delete the old temporary root-level page:

```text
www/football-edge-status.html
```

8. Confirm the old URL is inaccessible:

```text
https://www.atlas-ai.no/football-edge-status.html
```

## Required page hardening

The page must include:

```html
<meta name="robots" content="noindex,nofollow,noarchive,nosnippet">
<meta name="referrer" content="no-referrer">
```

## Boundary

Allowed:

- GET-only API reads.
- Operational dashboard visibility.
- Safety-state visibility.
- Active model visibility.
- Seed competition visibility.

Not allowed:

- Direct database access from frontend.
- Credentials in HTML, JavaScript, or GitHub.
- Write buttons.
- Execution controls.
- SQL tools.
- Public diagnostics.
