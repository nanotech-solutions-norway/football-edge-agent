# Football Edge / Atlas — Step 4 Reporting 500 Hotfix Checkpoint

Generated: 12:25, 29.04.2026 Europe/Oslo

## Issue

The Step 4 weekly reporting endpoint returned an internal server error:

```json
{
  "status": "error",
  "message": "Internal server error",
  "details": null
}
```

Endpoint:

```text
GET /api/reporting/paper-trading/weekly
```

## Root-cause assessment

The Step 4 package added a new controller:

```text
football_edge_api_private/src/Api/ReportingController.php
```

The private backend does not use Composer autoloading. Controllers are explicitly included from:

```text
football_edge_api_private/src/bootstrap.php
```

The likely failure is that `ReportingController.php` was uploaded, but `bootstrap.php` was not updated to require it.

## Hotfix

A replacement private backend bootstrap file was prepared. It adds:

```php
require_once __DIR__ . '/Api/ReportingController.php';
```

Upload target:

```text
football_edge_api_private/src/bootstrap.php
```

Do not upload this file to `www`.

## Required post-hotfix validation

With private `.env` set as follows:

```env
FOOTBALL_EDGE_REPORTING_ENDPOINTS_ENABLED=true
FOOTBALL_EDGE_PAPER_TRADING_ENDPOINTS_ENABLED=false
```

Validate:

```text
GET /api/reporting/paper-trading/weekly
GET /api/reporting/paper-trading/artifacts
GET /api/reporting/paper-trading/audit
GET /api/reporting/paper-trading/export.csv
```

Confirm Step 3 endpoints remain disabled:

```text
GET /api/paper-trading/recommendations
GET /api/paper-trading/results
GET /api/paper-trading/metrics
```

Finally, re-run SQL safety-state check.

## Continued exclusions

- Real-money execution remains disabled.
- Auto-betting remains disabled.
- Provider execution integration remains disabled.
- Frontend write tokens remain prohibited.
- Direct frontend database access remains prohibited.
