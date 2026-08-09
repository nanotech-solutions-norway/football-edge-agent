# Football Edge / Atlas — Export and Archive Procedure — 12:52, 29.04.2026 Europe/Oslo

## Purpose

This procedure defines how weekly Football Edge paper-trading exports are downloaded, named, validated, and archived without exposing operational data publicly.

## Export source

CSV endpoint:

```text
https://www.atlas-ai.no/api/reporting/paper-trading/export.csv?from=YYYY-MM-DD&to=YYYY-MM-DD
```

Weekly JSON endpoint:

```text
https://www.atlas-ai.no/api/reporting/paper-trading/weekly?from=YYYY-MM-DD&to=YYYY-MM-DD
```

## File naming convention

Use this naming pattern:

```text
football_edge_weekly_validation_YYYY-MM-DD_to_YYYY-MM-DD_HHMM_DDMMYYYY.csv
football_edge_weekly_validation_YYYY-MM-DD_to_YYYY-MM-DD_HHMM_DDMMYYYY.json
football_edge_weekly_validation_YYYY-MM-DD_to_YYYY-MM-DD_HHMM_DDMMYYYY.md
```

Example:

```text
football_edge_weekly_validation_2026-04-23_to_2026-04-29_1252_29042026.csv
```

## Archive location

Preferred:

```text
Private local folder or private Drive folder with restricted access.
```

Do not store generated exports in:

```text
Public GitHub repository
Public web root
GitHub Pages
Frontend assets
Browser-visible directories
```

## Minimum archive contents

Each reporting period should include:

```text
1. CSV export
2. JSON weekly endpoint response, if saved
3. Completed markdown/PDF/DOCX report
4. Admin page screenshot
5. SQL safety-check note
```

## CSV validation checklist

Before archiving, check:

- file opens correctly;
- expected reporting period is present;
- known test artifacts are visible or summarized;
- settled records match weekly endpoint summary;
- no credentials or tokens are present;
- no private server paths are present;
- real-money execution remains false.

## Retention policy

Recommended minimum retention:

```text
24 months for paper-trading validation evidence.
```

If the project later enters regulated or investor-facing operation, extend retention according to legal/compliance review.

## GitHub policy

Generated exports are intentionally excluded from GitHub by `.gitignore`.

Do not override this unless a sanitized sample file is deliberately created and reviewed.
