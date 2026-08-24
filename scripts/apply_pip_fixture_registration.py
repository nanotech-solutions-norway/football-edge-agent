#!/usr/bin/env python3
"""Apply one protected PIP fixture registration without logging SQL or identifiers."""
from __future__ import annotations

import argparse
import os
import ssl
from pathlib import Path
from typing import Any


class RegistrationWriteError(RuntimeError):
    """Stable fail-closed write error with no provider or database values."""


def _connector_error_code(error: Exception) -> str:
    """Reduce connector failures to stable codes without exposing exception text."""
    errno = getattr(error, "errno", None)
    categories = {
        1044: "database_authorization_failed",
        1045: "database_authentication_failed",
        1049: "database_name_invalid",
        1054: "database_schema_incompatible",
        1062: "database_conflict",
        1146: "database_schema_incompatible",
        2003: "database_network_unreachable",
        2005: "database_host_unresolved",
        2006: "database_connection_lost",
        2013: "database_connection_lost",
        2026: "database_tls_failed",
        2055: "database_connection_lost",
        3159: "database_tls_failed",
    }
    return categories.get(errno, "database_write_failed")


def _split_sql(document: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    quoted = False
    index = 0
    while index < len(document):
        character = document[index]
        if character == "'":
            current.append(character)
            if quoted and index + 1 < len(document) and document[index + 1] == "'":
                current.append("'")
                index += 2
                continue
            quoted = not quoted
        elif character == ";" and not quoted:
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        else:
            current.append(character)
        index += 1
    if quoted:
        raise RegistrationWriteError("registration_sql_invalid")
    trailing = "".join(current).strip()
    if trailing:
        statements.append(trailing)
    return statements


def _without_comments(statement: str) -> str:
    return "\n".join(line for line in statement.splitlines() if not line.lstrip().startswith("--")).strip()


def validated_write_statements(document: str) -> list[str]:
    if "Protected automatic discovery in temporary single-provider mode" not in document:
        raise RegistrationWriteError("single_provider_marker_missing")
    statements = [_without_comments(statement) for statement in _split_sql(document)]
    statements = [statement for statement in statements if statement]
    fixture_inserts = [statement for statement in statements if statement.startswith("INSERT INTO pip_fixtures")]
    mapping_inserts = [
        statement for statement in statements if statement.startswith("INSERT INTO pip_provider_fixture_mappings")
    ]
    variable_sets = [statement for statement in statements if statement == "SET @pip_fixture_id = LAST_INSERT_ID()"]
    if len(fixture_inserts) != 1 or len(mapping_inserts) != 1 or len(variable_sets) != 1:
        raise RegistrationWriteError("registration_sql_shape_invalid")
    allowed_prefixes = (
        "START TRANSACTION",
        "INSERT INTO pip_fixtures",
        "SET @pip_fixture_id",
        "INSERT INTO pip_provider_fixture_mappings",
        "SELECT fixture_id",
        "SELECT provider",
        "COMMIT",
    )
    if any(not statement.startswith(allowed_prefixes) for statement in statements):
        raise RegistrationWriteError("registration_sql_statement_rejected")
    return [fixture_inserts[0], variable_sets[0], mapping_inserts[0]]


def _connection_config(environment: dict[str, str]) -> dict[str, Any]:
    required = ("PIP_DB_HOST", "PIP_DB_NAME", "PIP_DB_USER", "PIP_DB_PASSWORD")
    if any(not environment.get(name, "").strip() for name in required):
        raise RegistrationWriteError("database_secret_missing")
    try:
        port = int(environment.get("PIP_DB_PORT", "3306"))
    except ValueError as error:
        raise RegistrationWriteError("database_port_invalid") from error
    if not 1 <= port <= 65535:
        raise RegistrationWriteError("database_port_invalid")
    ca_file = ssl.get_default_verify_paths().cafile
    if not ca_file or not Path(ca_file).is_file():
        raise RegistrationWriteError("system_ca_unavailable")
    return {
        "host": environment["PIP_DB_HOST"],
        "port": port,
        "database": environment["PIP_DB_NAME"],
        "user": environment["PIP_DB_USER"],
        "password": environment["PIP_DB_PASSWORD"],
        "connection_timeout": 15,
        "read_timeout": 30,
        "write_timeout": 30,
        "ssl_disabled": False,
        "ssl_ca": ca_file,
        "ssl_verify_cert": True,
        "ssl_verify_identity": True,
        "tls_versions": ["TLSv1.2", "TLSv1.3"],
        "use_pure": True,
    }


def apply_registration(document: str, connector: Any, environment: dict[str, str]) -> None:
    write_statements = validated_write_statements(document)
    connection = None
    cursor = None
    try:
        connection = connector.connect(**_connection_config(environment))
        cursor = connection.cursor(buffered=True)
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'pip_fixtures' "
            "AND COLUMN_NAME IN ('fixture_id','fixture_code','canonical_event_key','competition_key',"
            "'kickoff_at','home_team_key','away_team_key')",
            (environment["PIP_DB_NAME"],),
        )
        if cursor.fetchone() != (7,):
            raise RegistrationWriteError("database_schema_incompatible")
        cursor.execute(
            "SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME IN ('pip_fixtures','pip_provider_fixture_mappings')",
            (environment["PIP_DB_NAME"],),
        )
        engines = dict(cursor.fetchall())
        if engines != {"pip_fixtures": "InnoDB", "pip_provider_fixture_mappings": "InnoDB"}:
            raise RegistrationWriteError("database_transaction_engine_invalid")
        connection.start_transaction()
        for statement in write_statements:
            cursor.execute(statement)
            if statement.startswith("INSERT INTO") and cursor.rowcount != 1:
                raise RegistrationWriteError("database_insert_count_invalid")
        cursor.execute("SELECT COUNT(*) FROM pip_fixtures WHERE fixture_id = @pip_fixture_id")
        fixture_count = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM pip_provider_fixture_mappings WHERE fixture_id = @pip_fixture_id")
        mapping_count = cursor.fetchone()
        if fixture_count != (1,) or mapping_count != (1,):
            raise RegistrationWriteError("database_post_write_verification_failed")
        connection.commit()
    except RegistrationWriteError:
        if connection is not None:
            connection.rollback()
        raise
    except Exception as error:
        if connection is not None:
            connection.rollback()
        raise RegistrationWriteError(_connector_error_code(error)) from error
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sql", type=Path)
    args = parser.parse_args()
    try:
        document = args.sql.read_text(encoding="utf-8-sig")
        import mysql.connector

        apply_registration(document, mysql.connector, dict(os.environ))
    except (OSError, UnicodeError, RegistrationWriteError) as error:
        code = str(error) if isinstance(error, RegistrationWriteError) else "registration_artifact_unreadable"
        print(f"write_status=review error_code={code}")
        print("database_values_logged=false sql_logged=false credentials_logged=false")
        return 2
    print("write_status=pass fixture_rows=1 provider_mapping_rows=1")
    print("database_values_logged=false sql_logged=false credentials_logged=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
