#!/usr/bin/env python3
"""Phase 2 repository validation.

This script validates the static repository scaffold before provider credentials are added.
It does not call external provider APIs.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = Path("scripts/validate_phase2.py")

REQUIRED_FILES = [
    "README.md",
    ".env.example",
    ".gitignore",
    "docker-compose.yml",
    "requirements.txt",
    "pyproject.toml",
    "backend/Dockerfile",
    "backend/app/main.py",
    "backend/app/config.py",
    "backend/app/api/routes.py",
    "backend/app/db/init/001_schema.sql",
    "backend/app/db/init/002_seed_competitions.sql",
    "backend/app/providers/clients.py",
    "backend/app/services/auto_betting_service.py",
    "backend/app/services/data_quality_service.py",
    "docs/api_contract.md",
    "docs/database_schema.md",
    "docs/domain_and_hosting_domeneshop.md",
    "docs/implementation_instructions.md",
    "docs/provider_setup.md",
    "docs/validation_checklist.md",
    "docs/phase2_completion_report_template.md",
]

REQUIRED_TERMS = [
    "NOR_ELITESERIEN",
    "Eliteserien",
    "historical odds",
    "xG",
    "NO BET",
    "AUTO_BETTING_HARD_LOCK=true",
]

PROHIBITED_TERMS = ["Tippeligaen"]


def should_scan(path: Path) -> bool:
    relative_path = path.relative_to(ROOT)
    if relative_path == VALIDATOR_PATH:
        return False
    if ".git" in path.parts or "__pycache__" in path.parts:
        return False
    return path.is_file()


def read_all_text() -> str:
    parts: list[str] = []
    for path in ROOT.rglob("*"):
        if should_scan(path):
            try:
                parts.append(path.read_text(encoding="utf-8"))
            except UnicodeDecodeError:
                continue
    return "\n".join(parts)


def main() -> int:
    missing = [file for file in REQUIRED_FILES if not (ROOT / file).exists()]
    if missing:
        print("Missing required files:")
        for item in missing:
            print(f" - {item}")
        return 1

    corpus = read_all_text()
    missing_terms = [term for term in REQUIRED_TERMS if term not in corpus]
    prohibited = [term for term in PROHIBITED_TERMS if term in corpus]

    if missing_terms:
        print("Missing required governance terms:")
        for item in missing_terms:
            print(f" - {item}")
        return 1

    if prohibited:
        print("Prohibited terms found:")
        for item in prohibited:
            print(f" - {item}")
        return 1

    print("Phase 2 static validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
